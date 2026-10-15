#!/usr/bin/env python3
"""Valores de referencia de los 12 KPIs y los 3 semáforos del CMI, calculados en Python.

Propósito
---------
Las medidas DAX de `_Medidas.tmdl` solo se pueden evaluar en Power BI Desktop. Este script
calcula los mismos indicadores sobre la estrella generada por `etl_referencia.py`
(validacion/salida/*.parquet), con la semántica EXACTA del contrato de diseño (§7) y de las
medidas DAX, para poder contrastar cifra a cifra lo que muestra el informe.

Semántica replicada (contrato §7)
---------------------------------
- «global» = DimCompetencia[EsGlobal]; «Cataluña» = sin filtros de DimContextoCentro.
- Mínimo muestral: K01, K02, K03 y K06 devuelven vacío si hay < 30 puntuaciones en el
  contexto (en K03 se cuenta el denominador ya filtrado; en K06, las no censuradas).
- K03 excluye Censurada y NivelNoComparable (numerador y denominador); K06 excluye Censurada.
- K10/K11 navegan por DimAnio[IndiceConvocatoria] (2021 se compara con 2019) y solo usan las
  competencias globales con PeriodoDisenoInicio <= año de la convocatoria de referencia.
- K12 itera por materias globales NO informativas (sin francés) y cuenta K10 >= 1.
- K09: ranking denso por K01 descendente entre todas las áreas salvo «Desconocida»; vacío si
  todas las competencias del contexto son informativas (francés) o si el K01 del área es vacío.
- Las puntuaciones NO están equiparadas entre convocatorias: K10, K11, K12 y los semáforos
  basados en K10 son orientativos.

Uso
---
    python validacion/kpis_referencia.py [--salida-etl CARPETA] [--resultados CARPETA]

Salida (validacion/resultados/, separador coma, 2 decimales, vacío = BLANK de DAX):
  kpi_cataluna_por_anio_materia.csv  Anio, Materia: K01, K03, K06, K04, K05, K08, K10, K11,
                                     Alumnos evaluados, Puntuaciones globales
  kpi_area_2025.csv                  AreaTerritorial x Materia en 2025: K01, K07, K09
  kpi_global_por_anio.csv            por año, sin filtro de materia: K01, K03, K06, K10, K11, K12
  semaforos_2025.csv                 Cataluña y cada área x materia en 2025: Estado K01/K03/K10
  contraste_oficial.csv              media calculada frente a la oficial (contrato §6)
K03 y K12 se expresan en porcentaje (0-100), igual que los muestra el formato "0.0%".
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

CARPETA = Path(__file__).resolve().parent
SALIDA_ETL = CARPETA / "salida"
RESULTADOS = CARPETA / "resultados"
MINIMO_MUESTRAL = 30
TOLERANCIA_OFICIAL = 0.2

# Contrato §6: medias oficiales de Cataluña (Quaderns d'avaluació, puntuación global).
_ABREV = {"CAT": "PCAT", "CAST": "PCAST", "MAT": "PMAT", "ING": "PANG", "FRA": "PFRAN",
          "MED": "PMED"}
_OFICIALES_TEXTO = """
2009 CAT 76,9 CAST 74,7 MAT 78,0 | 2010 CAT 73,7 CAST 71,2 ING 71,4 MAT 78,2 | 2011 CAT 77,2 CAST 73,6 ING 80,6 MAT 80,9 |
2012 CAT 79,6 CAST 76,6 MAT 80,2 ING 74,3 | 2013 CAT 71,1 CAST 73,0 MAT 76,3 ING 73,0 | 2014 CAT 75,5 CAST 75,4 MAT 81,0 ING 75,1 |
2015 CAT 74,5 CAST 75,7 ING 74,5 MAT 80,0 | 2016 CAT 74,5 CAST 74,1 ING 73,7 MAT 77,9 | 2017 CAT 75,8 CAST 73,4 ING 79,9 MAT 77,6 |
2018 CAT 73,6 CAST 77,0 ING 76,3 MAT 79,2 MED 70,2 | 2019 CAT 75,5 CAST 74,4 ING 78,2 MAT 78,2 MED 68,1 |
2021 CAT 76,7 CAST 73,5 ING 73,2 MAT 76,0 MED 75,6 | 2022 CAT 72,5 CAST 74,0 ING 76,9 MAT 71,1 MED 72,8 |
2023 CAT 72,7 CAST 72,1 ING 77,8 MAT 73,6 MED 71,6 | 2024 CAT 74,7 CAST 73,9 ING 73,2 MAT 74,3 MED 74,3 FRA 62,5 |
2025 CAT 73,5 CAST 76,5 ING 75,7 FRA 66,1 MAT 70,4 MED 66,3
"""


def _leer_oficiales() -> dict[tuple[int, str], float]:
    """(Anio, CodigoMateria) -> media oficial."""
    resultado = {}
    for bloque in _OFICIALES_TEXTO.replace("\n", " ").split("|"):
        partes = bloque.split()
        if not partes:
            continue
        anio = int(partes[0])
        for abrev, valor in zip(partes[1::2], partes[2::2]):
            resultado[(anio, _ABREV[abrev])] = float(valor.replace(",", "."))
    return resultado


MEDIAS_OFICIALES = _leer_oficiales()

# Informe de calidad §4.6: discrepancias con los informes oficiales ya documentadas
# (si alguna supera la tolerancia, se marca como «esperada fuera de tolerancia»).
EXCEPCIONES_DOCUMENTADAS = {
    (2017, "PCAST"): "§4.6: rotación PUN-02 corregida (73,51); el CSV tiene 756 alumnos menos",
    (2017, "PANG"): "§4.6: el CSV tiene 791 alumnos menos",
    (2023, "PANG"): "§4.6: n idéntico; la media difiere en 0,16",
    (2024, "PCAT"): "§4.6: el CSV tiene 1.024 alumnos menos",
    (2024, "PMAT"): "§4.6: el CSV tiene 395 alumnos menos",
    (2025, "PMAT"): "§4.6: el CSV tiene 41 alumnos más",
    (2016, "PANG"): "§4.6: 73,94 frente a 73,7; no es redondeo ni error de carga; escala de "
                    "CO/CE comprimida (R27/R28, máximo 95,55); n oficial por contrastar",
    (2024, "PFRAN"): "§4.6: 62,80 frente a 62,5; n = 266, 80 puntos de diferencia total, "
                     "explicable con pocos alumnos de diferencia en la n (PUN-19)",
}

# Diferencias con los Quaderns mayores de 0,2 que el informe §4.6 todavía NO recoge.
# Se listan de forma explícita para que test_modelo.py detecte cualquier diferencia NUEVA;
# hay que añadirlas al informe de calidad §4.6 (o revisar la cifra oficial del contrato §6).
FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR: dict[tuple[int, str], str] = {}


# =======================================================================================
# Base agregada: suficiente para reproducir cualquier filtro de las medidas
# =======================================================================================
def cargar_base(carpeta: Path = SALIDA_ETL) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame,
                                                     pd.DataFrame]:
    """Devuelve (base de puntuaciones agregada, base de evaluaciones, DimAnio, DimCompetencia).

    La base agrega FactPuntuacion por todos los atributos de dimensión que usan las medidas,
    con n, suma y suma de cuadrados de la puntuación en CENTÉSIMAS (enteros exactos), de modo
    que medias y desviaciones típicas se obtienen sin error de redondeo acumulado.
    """
    con = duckdb.connect()
    for tabla in ("FactPuntuacion", "FactEvaluacion", "DimAnio", "DimContextoCentro",
                  "DimPerfilAlumno", "DimCompetencia", "DimCalidadDato"):
        con.execute(f"CREATE VIEW {tabla} AS SELECT * FROM read_parquet('{carpeta / tabla}.parquet')")
    base = con.execute("""
        SELECT a.Anio, c.CodigoMateria, c.Materia, c.CompetenciaKey, c.Subcompetencia, c.EsGlobal, c.EsInformativa,
               c.PeriodoDisenoInicio, x.AreaTerritorial, x.Naturaleza, x.HabitatCodigo,
               p.Genero, f.NivelKey, q.NoValida, q.Censurada, q.NivelNoComparable,
               count(*) AS n,
               sum(CAST(round(f.Puntuacion * 100) AS BIGINT)) AS s,
               sum(CAST(round(f.Puntuacion * 100) AS HUGEINT) * CAST(round(f.Puntuacion * 100) AS HUGEINT))::VARCHAR AS ss
        FROM FactPuntuacion f
        JOIN DimAnio a USING (AnioKey)
        JOIN DimCompetencia c USING (CompetenciaKey)
        JOIN DimContextoCentro x USING (ContextoKey)
        JOIN DimPerfilAlumno p USING (PerfilKey)
        JOIN DimCalidadDato q USING (CalidadKey)
        GROUP BY ALL""").df()
    base["s"] = base["s"].astype(object).map(int)
    base["ss"] = base["ss"].map(int)
    evaluaciones = con.execute("""
        SELECT a.Anio, x.AreaTerritorial, x.Naturaleza, x.HabitatCodigo, p.Genero, count(*) AS n
        FROM FactEvaluacion f JOIN DimAnio a USING (AnioKey)
        JOIN DimContextoCentro x USING (ContextoKey) JOIN DimPerfilAlumno p USING (PerfilKey)
        GROUP BY ALL""").df()
    dim_anio = con.execute("SELECT * FROM DimAnio ORDER BY Anio").df()
    dim_comp = con.execute("SELECT * FROM DimCompetencia ORDER BY CompetenciaKey").df()
    return base, evaluaciones, dim_anio, dim_comp


CONTEXTO_CENTRO = ("AreaTerritorial", "Naturaleza", "HabitatCodigo")


class Modelo:
    """Evalúa las medidas sobre la base agregada. Un «contexto» es un dict columna -> filtro,
    donde el filtro es un valor, una lista de valores o una función que recibe la columna."""

    def __init__(self, base, evaluaciones, dim_anio, dim_comp):
        self.base, self.evaluaciones = base, evaluaciones
        self.dim_anio, self.dim_comp = dim_anio, dim_comp
        con_conv = dim_anio[dim_anio["TieneConvocatoria"]]
        self.indice_de_anio = dict(zip(con_conv["Anio"], con_conv["IndiceConvocatoria"].astype(int)))
        self.anio_de_indice = {i: a for a, i in self.indice_de_anio.items()}

    # --- filtros --------------------------------------------------------------------
    @staticmethod
    def _mascara(df: pd.DataFrame, ctx: dict) -> pd.Series:
        m = pd.Series(True, index=df.index)
        for col, filtro in ctx.items():
            if col not in df.columns:
                continue
            if callable(filtro):
                m &= filtro(df[col])
            elif isinstance(filtro, (list, tuple, set)):
                m &= df[col].isin(list(filtro))
            else:
                m &= df[col] == filtro
        return m

    def _agregado(self, ctx: dict, **extra) -> tuple[int, int, int]:
        b = self.base
        b = b[self._mascara(b, {**ctx, **extra})]
        return int(b["n"].sum()), sum(b["s"]), sum(b["ss"])

    # --- 0. Base --------------------------------------------------------------------------
    def alumnos_evaluados(self, ctx: dict) -> int:
        e = self.evaluaciones
        return int(e[self._mascara(e, ctx)]["n"].sum())

    def puntuaciones_globales(self, ctx: dict) -> int:
        return self._agregado(ctx, EsGlobal=True)[0]

    def puntuacion_media(self, ctx: dict) -> float | None:
        n, s, _ = self._agregado(ctx)
        return float(Fraction(s, n * 100)) if n else None

    # --- 1. Rendimiento académico ---------------------------------------------------------
    def k01(self, ctx: dict) -> float | None:
        n, s, _ = self._agregado(ctx, EsGlobal=True)
        return float(Fraction(s, n * 100)) if n >= MINIMO_MUESTRAL else None

    def cataluna(self, ctx: dict) -> float | None:
        return self.k01(_sin(ctx, *CONTEXTO_CENTRO))

    def k02(self, ctx: dict) -> float | None:
        n, s, _ = self._agregado(ctx, EsGlobal=False, NoValida=False)
        return float(Fraction(s, n * 100)) if n >= MINIMO_MUESTRAL else None

    def puntuaciones_validas_subcompetencia(self, ctx: dict) -> int:
        return self._agregado(ctx, EsGlobal=False, NoValida=False)[0]

    def k03(self, ctx: dict) -> float | None:
        ctx = _sin(ctx, "NivelKey")
        n, _, _ = self._agregado(ctx, EsGlobal=True, Censurada=False, NivelNoComparable=False)
        if n < MINIMO_MUESTRAL:
            return None
        bajo, _, _ = self._agregado(ctx, EsGlobal=True, Censurada=False, NivelNoComparable=False,
                                    NivelKey=1)
        return bajo / n

    # --- 2. Equidad -----------------------------------------------------------------------
    def _brecha(self, ctx: dict, col: str, a, b) -> float | None:
        va, vb = self.k01({**ctx, col: a}), self.k01({**ctx, col: b})
        return None if va is None or vb is None else va - vb

    def k04(self, ctx):
        return self._brecha(ctx, "Genero", "Niño", "Niña")

    def k05(self, ctx):
        return self._brecha(ctx, "Naturaleza", "Pública", "Privada")

    def k06(self, ctx: dict) -> float | None:
        n, s, ss = self._agregado(ctx, EsGlobal=True, Censurada=False)
        if n < MINIMO_MUESTRAL:
            return None
        varianza = Fraction(ss, n) - Fraction(s, n) ** 2      # en centésimas al cuadrado
        return float(np.sqrt(float(varianza))) / 100

    # --- 3. Territorio --------------------------------------------------------------------
    def k07(self, ctx):
        a, b = self.k01(ctx), self.cataluna(ctx)
        return None if a is None or b is None else a - b

    def k08(self, ctx):
        return self._brecha(ctx, "HabitatCodigo", 3, 1)

    def k09(self, ctx: dict) -> float | None:
        area = ctx.get("AreaTerritorial")
        if not isinstance(area, str) or area == "Desconocida":
            return None
        comp = self.dim_comp[self._mascara(self.dim_comp, ctx)]
        if comp["EsInformativa"].all():
            return None
        valor = self.k01(ctx)
        if valor is None:
            return None
        areas = [a for a in self.base["AreaTerritorial"].unique() if a != "Desconocida"]
        valores = {v for a in areas if (v := self.k01({**ctx, "AreaTerritorial": a})) is not None}
        return float(1 + sum(1 for v in valores if v > valor))  # RANKX DESC, DENSE

    # --- 4. Progreso ----------------------------------------------------------------------
    def _anio_unico(self, ctx: dict) -> int | None:
        anio = ctx.get("Anio")
        return anio if isinstance(anio, (int, np.integer)) and anio in self.indice_de_anio else None

    def _variacion(self, ctx: dict, salto: int) -> float | None:
        anio = self._anio_unico(ctx)
        if anio is None or self.indice_de_anio[anio] - salto < 1:
            return None
        anio_ref = self.anio_de_indice[self.indice_de_anio[anio] - salto]
        periodo = {"PeriodoDisenoInicio": lambda c, r=anio_ref: c <= r}
        actual = self.k01({**ctx, **periodo})
        anterior = self.k01({**ctx, "Anio": anio_ref, **periodo})
        return None if actual is None or anterior is None else actual - anterior

    def k10(self, ctx):
        return self._variacion(ctx, 1)

    def k11(self, ctx):
        v = self._variacion(ctx, 4)
        return None if v is None else v / 4

    def k12(self, ctx: dict) -> float | None:
        comp = self.dim_comp[self._mascara(self.dim_comp, ctx)]
        materias = comp[comp["EsGlobal"] & ~comp["EsInformativa"]]["CodigoMateria"].unique()
        variaciones = [v for m in materias if (v := self.k10({**ctx, "CodigoMateria": m})) is not None]
        if not variaciones:
            return None
        return sum(1 for v in variaciones if v >= 1) / len(variaciones)

    # --- 5. Semáforos ---------------------------------------------------------------------
    def estado_k01(self, ctx: dict) -> int | None:
        con_contexto = any(c in ctx for c in CONTEXTO_CENTRO)
        valor = self.k07(ctx) if con_contexto else self.k10(ctx)
        umbral = 1 if con_contexto else 0.5
        return _semaforo(valor, umbral)

    def estado_k03(self, ctx: dict) -> int | None:
        a, b = self.k03(ctx), self.k03(_sin(ctx, *CONTEXTO_CENTRO))
        if a is None or b is None:
            return None
        diferencia = a - b
        return 1 if diferencia <= -0.02 else -1 if diferencia >= 0.02 else 0

    def estado_k10(self, ctx: dict) -> int | None:
        return _semaforo(self.k10(ctx), 0.5)


def _sin(ctx: dict, *columnas) -> dict:
    return {k: v for k, v in ctx.items() if k not in columnas}


def _semaforo(valor, umbral) -> int | None:
    if valor is None:
        return None
    return 1 if valor >= umbral else -1 if valor <= -umbral else 0


def _pct(v):
    return None if v is None else v * 100


# =======================================================================================
# Tablas de resultados
# =======================================================================================
def tabla_cataluna_por_anio_materia(m: Modelo) -> pd.DataFrame:
    filas = []
    materias = m.dim_comp[m.dim_comp["EsGlobal"]].sort_values("MateriaOrden")
    for anio in m.indice_de_anio:
        for _, mat in materias.iterrows():
            ctx = {"Anio": anio, "CodigoMateria": mat["CodigoMateria"]}
            n_glob = m.puntuaciones_globales(ctx)
            if n_glob == 0:
                continue
            filas.append({"Anio": anio, "Materia": mat["Materia"], "K01": m.k01(ctx),
                          "K03": _pct(m.k03(ctx)), "K06": m.k06(ctx), "K04": m.k04(ctx),
                          "K05": m.k05(ctx), "K08": m.k08(ctx), "K10": m.k10(ctx),
                          "K11": m.k11(ctx), "Alumnos evaluados": m.alumnos_evaluados(ctx),
                          "Puntuaciones globales": n_glob})
    return pd.DataFrame(filas)


def tabla_area_2025(m: Modelo, anio: int = 2025) -> pd.DataFrame:
    filas = []
    materias = m.dim_comp[m.dim_comp["EsGlobal"]].sort_values("MateriaOrden")
    areas = (m.base[m.base["Anio"] == anio]["AreaTerritorial"].drop_duplicates().sort_values())
    for area in areas:
        for _, mat in materias.iterrows():
            ctx = {"Anio": anio, "CodigoMateria": mat["CodigoMateria"], "AreaTerritorial": area}
            if m.puntuaciones_globales(ctx) == 0:
                continue
            filas.append({"AreaTerritorial": area, "Materia": mat["Materia"], "K01": m.k01(ctx),
                          "Puntuación media Cataluña": m.cataluna(ctx),
                          "K07": m.k07(ctx), "K09": m.k09(ctx)})
    return pd.DataFrame(filas)


def tabla_global_por_anio(m: Modelo) -> pd.DataFrame:
    filas = []
    for anio in m.dim_anio["Anio"]:
        ctx = {"Anio": int(anio)}
        filas.append({"Anio": int(anio), "Puntuación media": m.puntuacion_media(ctx),
                      "K01": m.k01(ctx), "K03": _pct(m.k03(ctx)),
                      "K06": m.k06(ctx), "K10": m.k10(ctx), "K11": m.k11(ctx),
                      "K12": _pct(m.k12(ctx))})
    return pd.DataFrame(filas)


def tabla_subcompetencia_2025(m: Modelo, anio: int = 2025) -> pd.DataFrame:
    """K02 por materia y subcompetencia (visual p3_barras_k02_subcomp sin otros filtros)."""
    filas = []
    subs = m.dim_comp[~m.dim_comp["EsGlobal"]].sort_values(["MateriaOrden", "SubcompetenciaOrden"])
    for _, comp in subs.iterrows():
        ctx = {"Anio": anio, "CodigoMateria": comp["CodigoMateria"], "Subcompetencia": comp["Subcompetencia"]}
        n = m.puntuaciones_validas_subcompetencia(ctx)
        if n == 0:
            continue
        filas.append({"Materia": comp["Materia"], "Subcompetencia": comp["Subcompetencia"],
                      "K02": m.k02(ctx), "Puntuaciones válidas": n})
    return pd.DataFrame(filas)


def tabla_semaforos(m: Modelo, anio: int = 2025) -> pd.DataFrame:
    filas = []
    materias = m.dim_comp[m.dim_comp["EsGlobal"]].sort_values("MateriaOrden")
    areas = ["(Cataluña)"] + sorted(m.base[m.base["Anio"] == anio]["AreaTerritorial"].unique())
    for area in areas:
        for _, mat in materias.iterrows():
            ctx = {"Anio": anio, "CodigoMateria": mat["CodigoMateria"]}
            if area != "(Cataluña)":
                ctx["AreaTerritorial"] = area
            if m.puntuaciones_globales(ctx) == 0:
                continue
            k03, k03_cat = m.k03(ctx), m.k03(_sin(ctx, *CONTEXTO_CENTRO))
            filas.append({"AreaTerritorial": area, "Materia": mat["Materia"],
                          "K01": m.k01(ctx), "K07": m.k07(ctx) if area != "(Cataluña)" else None,
                          "K10": m.k10(ctx), "K03": _pct(k03), "K03 Cataluña": _pct(k03_cat),
                          "Estado K01": m.estado_k01(ctx), "Estado K03": m.estado_k03(ctx),
                          "Estado K10": m.estado_k10(ctx)})
    return pd.DataFrame(filas)


def tabla_contraste(m: Modelo) -> pd.DataFrame:
    nombres = dict(zip(m.dim_comp["CodigoMateria"], m.dim_comp["Materia"]))
    filas = []
    orden = dict(zip(m.dim_comp["CodigoMateria"], m.dim_comp["MateriaOrden"]))
    for (anio, codigo), oficial in sorted(MEDIAS_OFICIALES.items(), key=lambda kv: (kv[0][0], orden[kv[0][1]])):
        media = m.k01({"Anio": anio, "CodigoMateria": codigo})
        diferencia = None if media is None else media - oficial
        dentro = diferencia is not None and abs(diferencia) <= TOLERANCIA_OFICIAL + 1e-9
        if dentro:
            estado = "dentro de tolerancia"
        elif (anio, codigo) in EXCEPCIONES_DOCUMENTADAS:
            estado = "esperada fuera de tolerancia (informe §4.6)"
        elif (anio, codigo) in FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR:
            estado = "fuera de tolerancia, pendiente de documentar en §4.6"
        else:
            estado = "FALLO: fuera de tolerancia sin explicar"
        nota = (EXCEPCIONES_DOCUMENTADAS.get((anio, codigo))
                or FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR.get((anio, codigo), ""))
        filas.append({"Anio": anio, "Materia": nombres[codigo], "CodigoMateria": codigo,
                      "media_calculada": media, "media_oficial": oficial,
                      "diferencia": diferencia, "dentro_tolerancia": dentro,
                      "estado": estado, "nota": nota})
    return pd.DataFrame(filas)


def escribir_csv(df: pd.DataFrame, ruta: Path) -> None:
    salida = df.copy()
    for col in salida.columns:
        valores = salida[col].dropna()
        if salida[col].dtype == bool or valores.map(lambda v: isinstance(v, str)).any():
            continue
        if valores.map(lambda v: isinstance(v, (int, np.integer)) or float(v).is_integer()).all() \
                and (col.startswith("Estado") or col in ("K09", "Anio", "Alumnos evaluados",
                                                          "Puntuaciones globales", "Puntuaciones válidas")):
            salida[col] = pd.array([None if pd.isna(v) else int(v) for v in salida[col]],
                                   dtype="Int64")
        else:
            salida[col] = pd.to_numeric(salida[col])
    salida.to_csv(ruta, index=False, sep=",", float_format="%.2f", na_rep="",
                  lineterminator="\n")


def construir_modelo(carpeta: Path = SALIDA_ETL) -> Modelo:
    return Modelo(*cargar_base(carpeta))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--salida-etl", type=Path, default=SALIDA_ETL)
    parser.add_argument("--resultados", type=Path, default=RESULTADOS)
    args = parser.parse_args(argv)
    m = construir_modelo(args.salida_etl)
    args.resultados.mkdir(parents=True, exist_ok=True)
    tablas = {
        "kpi_cataluna_por_anio_materia.csv": tabla_cataluna_por_anio_materia(m),
        "kpi_area_2025.csv": tabla_area_2025(m),
        "kpi_global_por_anio.csv": tabla_global_por_anio(m),
        "kpi_subcompetencia_2025.csv": tabla_subcompetencia_2025(m),
        "semaforos_2025.csv": tabla_semaforos(m),
        "contraste_oficial.csv": tabla_contraste(m),
    }
    for nombre, df in tablas.items():
        escribir_csv(df, args.resultados / nombre)
        print(f"  {nombre:<36} {len(df):>4} filas")
    contraste = tablas["contraste_oficial.csv"]
    print(f"Contraste oficial: {int(contraste['dentro_tolerancia'].sum())} de {len(contraste)} "
          f"combinaciones dentro de ±{TOLERANCIA_OFICIAL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
