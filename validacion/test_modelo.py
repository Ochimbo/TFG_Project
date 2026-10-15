#!/usr/bin/env python3
"""Tests de integridad del modelo en estrella de referencia (contrato de diseño §6).

Se ejecutan con `python validacion/test_modelo.py` (no hace falta pytest, aunque pytest
también los encuentra). Leen validacion/salida/*.parquet, que genera `etl_referencia.py`.
Los tests de rotaciones (R03/R04) necesitan además el registro original, que no pasa al
modelo: reconstruyen la tabla de staging desde Datos.csv con las funciones de la ETL de
referencia y la comparan con el texto original del CSV (control negativo).

Cada comprobación falla con un mensaje que dice qué se esperaba y qué se ha encontrado.
"""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

import duckdb

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))

import etl_referencia as etl  # noqa: E402
import kpis_referencia as kpis  # noqa: E402

SALIDA = CARPETA / "salida"
TABLAS = ["DimAnio", "DimContextoCentro", "DimPerfilAlumno", "DimCompetencia", "DimNivelLogro",
          "DimCalidadDato", "FactEvaluacion", "FactPuntuacion"]

# Contrato §6
FILAS_ESPERADAS = {"FactEvaluacion": 1_102_324, "FactPuntuacion": 17_728_085,
                   "DimContextoCentro": 120, "DimPerfilAlumno": 182, "DimCompetencia": 24,
                   "DimNivelLogro": 5, "DimCalidadDato": 16, "DimAnio": 17}
GLOBALES_ESPERADAS = 4_769_851
SUBCOMPETENCIAS_ESPERADAS = 12_958_234
MEDIA_CASTELLANO_2017 = 73.51

FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR = kpis.FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR

# Informe §4.3: pesos de la global sobre sus subcompetencias y tolerancia de coherencia.
TOLERANCIA_PONDERADA = 0.115
UMBRAL_COHERENCIA = 0.99


# =======================================================================================
# Utilidades
# =======================================================================================
_CON: duckdb.DuckDBPyConnection | None = None
_STAGING: duckdb.DuckDBPyConnection | None = None


def con() -> duckdb.DuckDBPyConnection:
    """Conexión con una vista por tabla del modelo (parquet)."""
    global _CON
    if _CON is None:
        faltan = [t for t in TABLAS if not (SALIDA / f"{t}.parquet").exists()]
        assert not faltan, (f"Faltan {faltan} en {SALIDA}: ejecuta antes "
                            f"`python validacion/etl_referencia.py`")
        _CON = duckdb.connect()
        for t in TABLAS:
            _CON.execute(f"CREATE VIEW {t} AS SELECT * FROM read_parquet('{SALIDA / t}.parquet')")
    return _CON


def staging() -> duckdb.DuckDBPyConnection:
    """Staging reconstruido desde Datos.csv con la ETL de referencia (tablas crudo y
    stg_evaluaciones)."""
    global _STAGING
    if _STAGING is None:
        _STAGING = duckdb.connect()
        etl.construir_staging(_STAGING, etl.leer_csv())
    return _STAGING


def uno(sql: str, c: duckdb.DuckDBPyConnection | None = None):
    return (c or con()).execute(sql).fetchone()[0]


def filas(sql: str, c: duckdb.DuckDBPyConnection | None = None):
    return (c or con()).execute(sql).fetchall()


# =======================================================================================
# 1. Recuentos
# =======================================================================================
def test_recuentos_tablas():
    for tabla, esperado in FILAS_ESPERADAS.items():
        n = uno(f"SELECT count(*) FROM {tabla}")
        assert n == esperado, f"{tabla}: {n:,} filas, se esperaban {esperado:,} (contrato §6)"


def test_recuento_globales_y_subcompetencias():
    glob, sub = filas("""SELECT count(*) FILTER (WHERE c.EsGlobal), count(*) FILTER (WHERE NOT c.EsGlobal)
                         FROM FactPuntuacion f JOIN DimCompetencia c USING (CompetenciaKey)""")[0]
    assert glob == GLOBALES_ESPERADAS, f"Puntuaciones globales: {glob:,}, se esperaban {GLOBALES_ESPERADAS:,}"
    assert sub == SUBCOMPETENCIAS_ESPERADAS, (f"Puntuaciones de subcompetencias: {sub:,}, "
                                              f"se esperaban {SUBCOMPETENCIAS_ESPERADAS:,}")


def test_evaluacion_id_es_1_a_n():
    n, mn, mx, distintos = filas("""SELECT count(*), min(EvaluacionID), max(EvaluacionID),
                                           count(DISTINCT EvaluacionID) FROM FactEvaluacion""")[0]
    assert (mn, mx, distintos) == (1, n, n), (f"EvaluacionID debe ser 1..N sin huecos ni repetidos "
                                              f"(R01): min {mn}, max {mx}, distintos {distintos}, N {n}")


def test_competencias_evaluadas_cuadra_con_globales():
    a = uno("SELECT sum(CompetenciasEvaluadas) FROM FactEvaluacion")
    assert a == GLOBALES_ESPERADAS, (f"La suma de FactEvaluacion[CompetenciasEvaluadas] ({a:,}) debe "
                                     f"igualar las puntuaciones globales ({GLOBALES_ESPERADAS:,})")


# =======================================================================================
# 2. Claves: unicidad en dimensiones y huérfanas en hechos
# =======================================================================================
CLAVES = {"DimAnio": "AnioKey", "DimContextoCentro": "ContextoKey", "DimPerfilAlumno": "PerfilKey",
          "DimCompetencia": "CompetenciaKey", "DimNivelLogro": "NivelKey", "DimCalidadDato": "CalidadKey"}
RELACIONES = [("FactPuntuacion", d) for d in CLAVES] + \
             [("FactEvaluacion", d) for d in ("DimAnio", "DimContextoCentro", "DimPerfilAlumno")]


def test_claves_unicas_en_dimensiones():
    for dim, clave in CLAVES.items():
        n, distintas, nulas = filas(f"SELECT count(*), count(DISTINCT {clave}), "
                                    f"count(*) - count({clave}) FROM {dim}")[0]
        assert n == distintas and nulas == 0, (f"{dim}[{clave}] debe ser única y no nula: "
                                               f"{n} filas, {distintas} distintas, {nulas} nulas")


def test_claves_huerfanas_cero():
    for hecho, dim in RELACIONES:
        clave = CLAVES[dim]
        huerfanas = filas(f"""SELECT f.{clave}, count(*) FROM {hecho} f
                              LEFT JOIN {dim} d ON f.{clave} = d.{clave}
                              WHERE d.{clave} IS NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 5""")
        assert not huerfanas, f"{hecho}[{clave}] sin fila en {dim} (clave, filas): {huerfanas}"


# =======================================================================================
# 3. Rotaciones R03 (castellano 2017) y R04 (francés 2016)
# =======================================================================================
def _pct_coherente(c, tabla: str, anio: int, global_: str, pesos: dict[str, float]) -> tuple[float, int]:
    """% de filas del año donde |global - Σ peso·sub| <= tolerancia (informe §4.3)."""
    ponderada = " + ".join(f'{p} * "{col}"' for col, p in pesos.items())
    no_nulas = " AND ".join(f'"{col}" IS NOT NULL' for col in [global_, *pesos])
    pct, n = filas(f"""SELECT avg(CASE WHEN abs("{global_}" - ({ponderada})) <= {TOLERANCIA_PONDERADA}
                                       THEN 1.0 ELSE 0.0 END), count(*)
                       FROM {tabla} WHERE Anio = {anio} AND {no_nulas}""", c)[0]
    return float(pct or 0), n


def _crudo_numerico(c) -> str:
    """Vista del texto ORIGINAL del CSV convertido a número, sin rotaciones (control negativo)."""
    cols = ", ".join(f"""TRY_CAST(replace("{x}", ',', '.') AS DOUBLE) AS "{x}" """
                     for x in etl.CAMPOS_PUNTUACION)
    c.execute(f"""CREATE OR REPLACE VIEW crudo_num AS
                  SELECT EvaluacionID, CAST("ANY" AS BIGINT) AS Anio, {cols} FROM crudo""")
    return "crudo_num"


CASOS_ROTACION = [
    # (regla, año, global, pesos tras la corrección; informe §4.3, columna 2016-2017)
    ("R03 castellano 2017", 2017, "PCAST", {"PCAST_CL": 0.60, "PCAST_EE": 0.40}),
    ("R04 francés 2016", 2016, "PFRAN", {"PFRAN_CO": 0.35, "PFRAN_CE": 0.50, "PFRAN_EE": 0.15}),
]


def test_rotaciones_global_igual_a_ponderada():
    c = staging()
    for regla, anio, glob, pesos in CASOS_ROTACION:
        pct, n = _pct_coherente(c, "stg_evaluaciones", anio, glob, pesos)
        assert n > 0, f"{regla}: no hay filas con global y subcompetencias informadas"
        assert pct >= UMBRAL_COHERENCIA, (
            f"{regla}: tras la corrección la global coincide con la ponderada {pesos} solo en el "
            f"{pct:.2%} de {n:,} filas (se exige >= {UMBRAL_COHERENCIA:.0%}); revisa la rotación")


def test_rotaciones_control_negativo_sin_corregir():
    c = staging()
    tabla = _crudo_numerico(c)
    for regla, anio, glob, pesos in CASOS_ROTACION:
        pct, n = _pct_coherente(c, tabla, anio, glob, pesos)
        assert pct < 0.5, (f"{regla}: SIN corregir, la global ya coincide con la ponderada en el "
                           f"{pct:.2%} de {n:,} filas; el test de rotación no discrimina")


def test_rotaciones_no_tocan_otros_anios():
    c = staging()
    _crudo_numerico(c)
    for campos, anio in ((["PCAST", "PCAST_CL", "PCAST_EE"], 2017),
                         (["PFRAN", "PFRAN_CO", "PFRAN_CE", "PFRAN_EE"], 2016)):
        dif = " OR ".join(f's."{x}" IS DISTINCT FROM CAST(r."{x}" AS DECIMAL(5,2))' for x in campos)
        n = uno(f"""SELECT count(*) FROM stg_evaluaciones s
                    JOIN crudo_num r USING (EvaluacionID)
                    WHERE s.Anio <> {anio} AND ({dif})""", c)
        assert n == 0, f"La rotación de {campos[0]} ha cambiado {n:,} filas de años distintos de {anio}"


def test_media_castellano_2017_corregida():
    media = uno("""SELECT round(avg(Puntuacion), 2) FROM FactPuntuacion
                   WHERE AnioKey = 2017 AND CompetenciaKey = 5""")
    assert float(media) == MEDIA_CASTELLANO_2017, (
        f"Media de castellano 2017 = {media}, se esperaba {MEDIA_CASTELLANO_2017} (74,30 indica que "
        f"no se ha aplicado R03)")


# =======================================================================================
# 4. Códigos sin mapear, rango y años
# =======================================================================================
def test_codigos_sin_mapear_cero():
    c = staging()
    for col in ("GeneroCodigo", "NaturalezaCodigo", "HabitatCodigo", "AreaCodigo",
                "SituacionEdadCodigo", "MesNacimiento", "ContextoKey", "PerfilKey"):
        n = uno(f"SELECT count(*) FROM stg_evaluaciones WHERE {col} IS NULL", c)
        assert n == 0, f"stg_evaluaciones[{col}] tiene {n:,} valores sin mapear (nulos)"
    for col, validos in (("GeneroCodigo", "1, 2"), ("NaturalezaCodigo", "1, 2"),
                         ("HabitatCodigo", "0, 1, 2, 3"),
                         ("AreaCodigo", ", ".join(str(a[0]) for a in etl.AREAS))):
        otros = filas(f"SELECT DISTINCT {col} FROM stg_evaluaciones WHERE {col} NOT IN ({validos})", c)
        assert not otros, f"{col} con códigos fuera de catálogo: {otros}"


def test_area_barcelona_comarques_por_anio():
    c = staging()
    mal = filas("""SELECT AreaCodigo, Anio, count(*) FROM stg_evaluaciones
                   WHERE (AreaCodigo = 3 AND Anio > 2023) OR (AreaCodigo = 4 AND Anio <> 2024)
                   GROUP BY ALL""", c)
    assert not mal, f"R14: Barcelona Comarques debe ser código 3 hasta 2023 y 4 en 2024: {mal}"
    mal = filas("""SELECT s.Anio, s.AreaCodigo, count(*) FROM crudo r JOIN stg_evaluaciones s USING (EvaluacionID)
                   WHERE trim(r.AREA_TERRITORIAL) = 'Barcelona Comarques'
                     AND s.AreaCodigo IS DISTINCT FROM CASE WHEN s.Anio = 2024 THEN 4 WHEN s.Anio <= 2023 THEN 3 END
                   GROUP BY ALL""", c)
    assert not mal, f"R14: filas Barcelona Comarques del origen con código distinto de 3 (<=2023) / 4 (2024): {mal}"


# =======================================================================================
# 4b. Edad, fecha de nacimiento y código de alumno (R16-R19, R21), calculados desde el texto original
# =======================================================================================
_ESPERADO_PERFIL = """
    WITH r AS (
        SELECT EvaluacionID, CAST(trim("ANY") AS BIGINT) AS Anio,
               NULLIF(trim(CODI_ALUMNE), '') AS Codigo,
               TRY_CAST(NULLIF(trim(ANY_NAIXEMENT), '') AS BIGINT) AS AnioNac,
               TRY_CAST(NULLIF(trim(MES_NAIXEMENT), '') AS BIGINT) AS MesNac
        FROM crudo),
    d AS (
        SELECT *, coalesce((Codigo IS NULL AND Anio IN (2016, 2018))
                           OR (Anio = 2016 AND AnioNac = 2001 AND MesNac = 1), FALSE) AS Dudosa
        FROM r)
    SELECT EvaluacionID, Anio, Codigo, MesNac, Dudosa,
           CASE WHEN Anio = 2010 OR Dudosa THEN NULL
                WHEN Anio - AnioNac >= 10 AND Anio - AnioNac <= 14 THEN Anio - AnioNac END AS Edad
    FROM d"""


def test_fecha_nacimiento_dudosa_r19():
    c = staging()
    n_esperadas, n_stg, distintas = filas(f"""
        WITH e AS ({_ESPERADO_PERFIL})
        SELECT count(*) FILTER (WHERE e.Dudosa), count(*) FILTER (WHERE s.FechaNacimientoDudosa),
               count(*) FILTER (WHERE e.Dudosa IS DISTINCT FROM s.FechaNacimientoDudosa)
        FROM e JOIN stg_evaluaciones s USING (EvaluacionID)""", c)[0]
    assert n_esperadas == 83, f"R19: se esperaban 83 filas con fecha de relleno (47+11 sin código y 2016 01/2001), hay {n_esperadas}"
    assert distintas == 0 and n_stg == 83, f"R19: FechaNacimientoDudosa difiere en {distintas} filas (staging marca {n_stg})"
    mal = uno("""SELECT count(*) FROM stg_evaluaciones
                 WHERE FechaNacimientoDudosa AND (EdadAnioNatural IS NOT NULL OR SituacionEdadCodigo <> 9)""", c)
    assert mal == 0, f"R19: {mal} filas con fecha dudosa tienen edad o situación distinta de 9"


def test_edad_y_situacion_fila_a_fila():
    c = staging()
    rango = uno("SELECT count(*) FROM stg_evaluaciones WHERE EdadAnioNatural NOT BETWEEN 10 AND 14", c)
    assert rango == 0, f"R17: {rango} filas con EdadAnioNatural fuera de [10,14]"
    mal = filas(f"""
        WITH e AS ({_ESPERADO_PERFIL})
        SELECT e.Anio, e.Edad, s.EdadAnioNatural, s.SituacionEdadCodigo, count(*)
        FROM e JOIN stg_evaluaciones s USING (EvaluacionID)
        WHERE e.Edad IS DISTINCT FROM s.EdadAnioNatural
           OR s.SituacionEdadCodigo IS DISTINCT FROM CASE WHEN e.Anio = 2010 THEN 8 WHEN e.Edad IS NULL THEN 9
                WHEN e.Edad < 12 THEN 4 WHEN e.Edad = 12 THEN 1 WHEN e.Edad = 13 THEN 2 WHEN e.Edad = 14 THEN 3 END
        GROUP BY ALL LIMIT 10""", c)
    assert not mal, f"R16-R18/R21: edad o situación distinta de la esperada (Anio, esperada, stg, situación, filas): {mal}"
    sin_edad = uno("""SELECT count(*) FROM stg_evaluaciones
                      WHERE Anio <> 2010 AND NOT FechaNacimientoDudosa AND EdadAnioNatural IS NULL""", c)
    assert sin_edad > 0, "Control: debería haber filas con edad desconocida por año de nacimiento ausente o fuera de rango"


def test_mes_nacimiento_cero_si_falta():
    c = staging()
    vacios, mal = filas(f"""
        WITH e AS ({_ESPERADO_PERFIL})
        SELECT count(*) FILTER (WHERE e.MesNac IS NULL),
               count(*) FILTER (WHERE s.MesNacimiento IS DISTINCT FROM
                                CASE WHEN e.MesNac BETWEEN 1 AND 12 THEN e.MesNac ELSE 0 END)
        FROM e JOIN stg_evaluaciones s USING (EvaluacionID)""", c)[0]
    assert vacios == 1335, f"Se esperaban 1.335 filas sin MES_NAIXEMENT, hay {vacios:,}"
    assert mal == 0, f"MesNacimiento debe ser 1..12 o 0 si falta o es inválido: {mal:,} filas incorrectas"


def test_tiene_codigo_alumno():
    c = staging()
    con_codigo, mal = filas(f"""
        WITH e AS ({_ESPERADO_PERFIL})
        SELECT count(e.Codigo), count(*) FILTER (WHERE (e.Codigo IS NOT NULL) IS DISTINCT FROM s.TieneCodigoAlumno)
        FROM e JOIN stg_evaluaciones s USING (EvaluacionID)""", c)[0]
    assert mal == 0, f"TieneCodigoAlumno distinto de «CODI_ALUMNE no nulo» en {mal:,} filas"
    en_modelo = uno("SELECT count(*) FILTER (WHERE TieneCodigoAlumno) FROM FactEvaluacion")
    assert en_modelo == con_codigo, (f"FactEvaluacion: {en_modelo:,} filas con código, el origen tiene "
                                     f"{con_codigo:,} CODI_ALUMNE informados")


# =======================================================================================
# 4c. sortByColumn: cada valor del atributo tiene un único valor de orden, sin nulos
# =======================================================================================
def _sort_by_column_declarados() -> list[tuple[str, str, str]]:
    import re
    tablas = CARPETA.parent / "PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables"
    pares = []
    for f in sorted(tablas.glob("*.tmdl")):
        columna = None
        for linea in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\tcolumn (\S+)$", linea)
            if m:
                columna = m.group(1)
            m = re.match(r"\t\tsortByColumn: (\S+)$", linea)
            if m:
                pares.append((f.stem, columna, m.group(1)))
    return pares


def test_sort_by_column_uno_a_uno():
    pares = _sort_by_column_declarados()
    esperados = {("DimContextoCentro", "AreaTerritorial", "AreaOrden"),
                 ("DimCompetencia", "Subcompetencia", "SubcompetenciaOrden")}
    assert esperados <= set(pares), f"Faltan sortByColumn del contrato §3: {esperados - set(pares)}"
    for tabla, atributo, orden in pares:
        conflictos = filas(f"""SELECT {atributo}, list(DISTINCT {orden}) FROM {tabla}
                               GROUP BY 1 HAVING count(DISTINCT {orden}) > 1 OR count(*) > count({orden})""")
        assert not conflictos, (f"{tabla}[{atributo}] -> {orden}: la actualización fallaría en Power BI "
                                f"porque hay atributos con varios órdenes o nulos: {conflictos}")


def test_habitat_y_edad_no_fiables():
    c = staging()
    n2010 = filas("""SELECT count(*) FILTER (WHERE HabitatCodigo <> 0),
                            count(*) FILTER (WHERE SituacionEdadCodigo <> 8 OR EdadAnioNatural IS NOT NULL)
                     FROM stg_evaluaciones WHERE Anio = 2010""", c)[0]
    assert n2010 == (0, 0), f"R12/R18: en 2010 hábitat y edad deben ser «No fiable» (incumplen: {n2010})"
    n2014 = uno("""SELECT count(*) FROM stg_evaluaciones
                   WHERE Anio = 2014 AND HabitatCodigo = 0""", c)
    assert n2014 == 29, f"R12: el bloque de Baix Llobregat 2014 debe tener 29 filas en hábitat 0, hay {n2014}"


def test_puntuacion_en_rango_0_100():
    mn, mx, nulas = filas("SELECT min(Puntuacion), max(Puntuacion), count(*) - count(Puntuacion) "
                          "FROM FactPuntuacion")[0]
    assert 0 <= mn and mx <= 100, f"Puntuación fuera de [0,100]: min {mn}, max {mx}"
    assert nulas == 0, f"FactPuntuacion no debe tener puntuaciones nulas (despivotado): {nulas}"


def test_2020_sin_datos():
    for hecho in ("FactEvaluacion", "FactPuntuacion"):
        n = uno(f"SELECT count(*) FROM {hecho} WHERE AnioKey = 2020")
        assert n == 0, f"{hecho} tiene {n:,} filas de 2020 (no hubo prueba por la COVID-19)"
    fila = filas("""SELECT TieneConvocatoria, IndiceConvocatoria, NotaConvocatoria
                    FROM DimAnio WHERE AnioKey = 2020""")
    assert fila == [(False, None, "Sin prueba por la COVID-19")], f"DimAnio 2020 incorrecto: {fila}"


def test_indice_convocatoria_consecutivo():
    datos = filas("""SELECT a.Anio, a.IndiceConvocatoria, a.TieneConvocatoria,
                            a.EsUltimaConvocatoria, a.Anio IN (SELECT DISTINCT AnioKey FROM FactEvaluacion)
                     FROM DimAnio a ORDER BY a.Anio""")
    anios = [d[0] for d in datos]
    assert anios == list(range(2009, max(anios) + 1)), f"DimAnio debe ir de 2009 al último año sin huecos: {anios}"
    con_datos = [d for d in datos if d[4]]
    assert [d[1] for d in con_datos] == list(range(1, len(con_datos) + 1)), (
        f"IndiceConvocatoria debe ser 1..N consecutivo en los años con datos: {[(d[0], d[1]) for d in con_datos]}")
    for anio, indice, tiene, ultima, hay_datos in datos:
        assert tiene == hay_datos, f"DimAnio {anio}: TieneConvocatoria={tiene} pero hay_datos={hay_datos}"
        assert hay_datos or indice is None, f"DimAnio {anio}: sin datos debe tener IndiceConvocatoria nulo"
        assert ultima == (anio == con_datos[-1][0]), f"DimAnio {anio}: EsUltimaConvocatoria={ultima}"
    nota_2021 = uno("SELECT NotaConvocatoria FROM DimAnio WHERE Anio = 2021")
    assert nota_2021.startswith("Primera convocatoria tras la COVID-19"), f"Nota 2021: {nota_2021!r}"
    indices = dict((d[0], d[1]) for d in datos)
    assert indices[2021] == indices[2019] + 1, "2021 debe ser la convocatoria siguiente a 2019"


# =======================================================================================
# 5. Niveles de logro (R29) en los límites exactos
# =======================================================================================
def test_umbrales_nivel_en_limites_exactos():
    esperado = {54.99: 1, 55.00: 2, 69.99: 2, 70.00: 3, 84.99: 3, 85.00: 4, 100.00: 4, 0.00: 1}
    datos = filas("""SELECT CAST(f.Puntuacion AS DOUBLE), list(DISTINCT f.NivelKey), count(*)
                     FROM FactPuntuacion f JOIN DimCompetencia c USING (CompetenciaKey)
                     WHERE c.EsGlobal AND f.Puntuacion IN (54.99, 55.00, 69.99, 70.00, 84.99, 85.00, 100.00, 0.00)
                     GROUP BY 1""")
    encontrados = {round(p, 2): (sorted(niveles), n) for p, niveles, n in datos}
    for valor, nivel in esperado.items():
        assert valor in encontrados, f"No hay globales con puntuación exacta {valor} para probar el límite"
        niveles, n = encontrados[valor]
        assert niveles == [nivel], (f"Global = {valor:.2f} debe ir al nivel {nivel} "
                                    f"(<55 Bajo; [55,70) Medio-bajo; [70,85) Medio-alto; >=85 Alto); "
                                    f"hay niveles {niveles} en {n:,} filas")
    nombres = dict(filas("SELECT NivelKey, Nivel FROM DimNivelLogro"))
    assert (nombres[2], nombres[3], nombres[4]) == ("Medio-bajo", "Medio-alto", "Alto"), nombres


def test_nivel_coherente_con_limites_en_todas_las_filas():
    mal = filas("""SELECT c.EsGlobal, f.NivelKey, count(*) FROM FactPuntuacion f
                   JOIN DimCompetencia c USING (CompetenciaKey)
                   JOIN DimNivelLogro n USING (NivelKey)
                   WHERE (NOT c.EsGlobal AND f.NivelKey <> 0)
                      OR (c.EsGlobal AND NOT coalesce(f.Puntuacion >= n.LimiteInferior
                          AND (f.Puntuacion < n.LimiteSuperior OR (n.NivelKey = 4 AND f.Puntuacion <= 100)),
                          FALSE))
                   GROUP BY ALL""")
    assert not mal, f"NivelKey incoherente con DimNivelLogro (EsGlobal, NivelKey, filas): {mal}"


# =======================================================================================
# 6. Máscara de DimCalidadDato (R25-R28)
# =======================================================================================
def _calidad_esperada(campo: str, anio: int) -> int:
    """Reimplementación independiente del contrato §3 (DimCalidadDato)."""
    clave = 0
    if campo == "PANG_EE" and anio == 2015:
        clave |= 1
    if (campo == "PCAT_EE" and anio == 2018) or (campo in ("PANG", "PANG_CO", "PANG_CE") and anio == 2015):
        clave |= 2
    if ((campo in ("PANG_CO", "PCAT_CL") and anio == 2011)
            or (campo == "PANG_EE" and 2013 <= anio <= 2016)
            or (campo in ("PANG_CO", "PANG_CE") and anio in (2015, 2016))
            or (campo in ("PMAT_NC", "PMAT_EFM", "PMAT_CR") and anio == 2015)):
        clave |= 4
    if (campo, anio) in {("PANG", 2015), ("PMAT", 2015), ("PMAT", 2019), ("PCAT", 2018),
                         ("PANG", 2016), ("PFRAN", 2022)}:
        clave |= 8
    return clave


def test_mascara_calidad_casos_concretos():
    casos = {("PANG_EE", 2015): 5, ("PANG", 2015): 10, ("PANG_CO", 2015): 6, ("PANG_CE", 2015): 6,
             ("PCAT_EE", 2018): 2, ("PCAT", 2018): 8, ("PANG_CO", 2011): 4, ("PCAT_CL", 2011): 4,
             ("PANG_EE", 2013): 4, ("PANG_EE", 2016): 4, ("PANG_CO", 2016): 4, ("PMAT_CR", 2015): 4,
             ("PMAT", 2015): 8, ("PMAT", 2019): 8, ("PANG", 2016): 8, ("PFRAN", 2022): 8,
             ("PCAT", 2017): 0, ("PANG_EE", 2017): 0, ("PANG", 2014): 0, ("PCAST_EE", 2018): 0}
    obtenido = {(c, a): k for c, a, k in filas("""
        SELECT DISTINCT c.CampoOrigen, f.AnioKey, f.CalidadKey
        FROM FactPuntuacion f JOIN DimCompetencia c USING (CompetenciaKey)""")}
    for (campo, anio), clave in casos.items():
        assert (campo, anio) in obtenido, f"No hay puntuaciones de {campo} en {anio}"
        assert obtenido[(campo, anio)] == clave, (f"CalidadKey de {campo} {anio} = {obtenido[(campo, anio)]}, "
                                                  f"se esperaba {clave}")


def test_mascara_calidad_todas_las_combinaciones():
    datos = filas("""SELECT c.CampoOrigen, f.AnioKey, list(DISTINCT f.CalidadKey)
                     FROM FactPuntuacion f JOIN DimCompetencia c USING (CompetenciaKey) GROUP BY ALL""")
    mal = [(campo, anio, claves) for campo, anio, claves in datos
           if claves != [_calidad_esperada(campo, anio)]]
    assert not mal, f"CalidadKey distinta de la esperada (campo, año, claves): {mal[:10]}"


def test_dim_calidad_dato_bits():
    for clave, nv, cen, ncs, nnc, desc in filas("SELECT * FROM DimCalidadDato ORDER BY CalidadKey"):
        assert (nv, cen, ncs, nnc) == (bool(clave & 1), bool(clave & 2), bool(clave & 4), bool(clave & 8)), \
            f"DimCalidadDato {clave}: bits incoherentes {(nv, cen, ncs, nnc)}"
        assert (desc == "Válido") == (clave == 0), f"DimCalidadDato {clave}: descripción {desc!r}"


# =======================================================================================
# 7. Medias de Cataluña frente a las oficiales (contrato §6, informe §4.6)
# =======================================================================================
def test_medias_cataluna_frente_a_oficiales():
    medias = {(a, m): float(v) for a, m, v in filas("""
        SELECT f.AnioKey, c.CodigoMateria, avg(f.Puntuacion) FROM FactPuntuacion f
        JOIN DimCompetencia c USING (CompetenciaKey) WHERE c.EsGlobal GROUP BY ALL""")}
    dentro, esperadas, pendientes, fallos = [], [], [], []
    for clave, oficial in sorted(kpis.MEDIAS_OFICIALES.items()):
        assert clave in medias, f"No hay datos para {clave}, que tiene media oficial {oficial}"
        dif = medias[clave] - oficial
        if abs(dif) <= kpis.TOLERANCIA_OFICIAL + 1e-9:
            dentro.append(clave)
        elif clave in kpis.EXCEPCIONES_DOCUMENTADAS:
            esperadas.append((clave, round(dif, 2)))
        elif clave in FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR:
            pendientes.append((clave, round(dif, 2)))
        else:
            fallos.append((clave, round(medias[clave], 2), oficial, round(dif, 2)))
    total = len(kpis.MEDIAS_OFICIALES)
    print(f"    {len(dentro)} de {total} combinaciones dentro de ±{kpis.TOLERANCIA_OFICIAL}")
    for clave, dif in esperadas:
        print(f"    esperada fuera de tolerancia (§4.6) {clave}: {dif:+.2f}")
    for clave, dif in pendientes:
        print(f"    AVISO fuera de tolerancia, pendiente de documentar en §4.6 {clave}: {dif:+.2f} "
              f"({FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR[clave]})")
    assert not fallos, f"Medias fuera de ±{kpis.TOLERANCIA_OFICIAL} no documentadas (clave, CSV, oficial, dif): {fallos}"
    obsoletas = set(FUERA_TOLERANCIA_PENDIENTES_DE_DOCUMENTAR) - {c for c, _ in pendientes}
    assert not obsoletas, f"Ya están dentro de tolerancia; quítalas de la lista de pendientes: {obsoletas}"


# =======================================================================================
# Ejecución
# =======================================================================================
def main() -> int:
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    fallidos = 0
    t0 = time.time()
    for nombre, funcion in tests:
        try:
            funcion()
            print(f"OK    {nombre}")
        except AssertionError as e:
            fallidos += 1
            print(f"FALLO {nombre}\n      {e}")
        except Exception:  # noqa: BLE001
            fallidos += 1
            print(f"ERROR {nombre}\n{traceback.format_exc()}")
    print(f"\n{len(tests) - fallidos} de {len(tests)} tests correctos ({time.time() - t0:.1f} s)")
    return 1 if fallidos else 0


if __name__ == "__main__":
    sys.exit(main())
