"""Perfilado exhaustivo de las columnas no numéricas de Datos.csv.

TFG: Cuadro de Mando Integral (Power BI) - Avaluació de sisè d'educació primària.
Fuente: Portal de Dades Obertes de la Generalitat (dataset rk5x-gny6).

Columnas perfiladas: ANY, CODI_ALUMNE, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT,
AREA_TERRITORIAL, NATURALESA, HÀBITAT.

Uso (desde la raíz del repositorio):
    .venv/bin/python validacion/perfilado/perfil_categoricas.py

Lee Datos.csv en solo lectura (no lo modifica). Imprime todas las cifras por
secciones, guarda una copia de la salida en
validacion/perfilado/salidas_categoricas/perfil_categoricas_salida.txt y las
tablas principales en validacion/perfilado/salidas_categoricas/*.csv.

La sección 8 implementa en pandas las reglas de limpieza propuestas
(limpiar_categoricas) y verifica su resultado sobre el fichero completo.
El equivalente en Power Query (M) está en limpieza_categoricas.pq.
"""

import csv
import os
import sys

import duckdb
import numpy as np
import pandas as pd

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV = os.path.join(RAIZ, "Datos.csv")
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salidas_categoricas")
os.makedirs(SALIDA, exist_ok=True)

pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_rows", 3000)
pd.set_option("display.max_colwidth", 80)

ANIOS_ESPERADOS = list(range(2009, 2026))
CATEG = ["ANY", "CODI_ALUMNE", "GENERE", "MES_NAIXEMENT", "ANY_NAIXEMENT",
         "AREA_TERRITORIAL", "NATURALESA", "HÀBITAT"]
PUNT = ["PCAT", "PCAT_CL", "PCAT_EE", "PCAST", "PCAST_CL", "PCAST_EE", "PMAT",
        "PMAT_NC", "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE", "PFRAN",
        "PFRAN_CO", "PFRAN_CE", "PANG_EE", "PFRAN_EE", "PCAT_CO", "PCAST_CO",
        "PMED", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3"]

AREAS_ESTABLES = ["Baix Llobregat", "Consorci d'Educació de Barcelona", "Girona",
                  "Maresme - Vallès Oriental", "Terres de l'Ebre", "Vallès Occidental"]
GRUPO_LLEIDA = ["Lleida", "Alt Pirineu i Aran"]
GRUPO_BCN = ["Barcelona Comarques", "Barcelonès", "Penedès", "Tarragona", "Catalunya Central"]
NOMBRE_GRUPO_LLEIDA = "Lleida + Alt Pirineu i Aran"
NOMBRE_GRUPO_BCN = "Barcelona Comarques/Barcelonès + Penedès + Tarragona + Catalunya Central"

EDAD_TEORICA = 12
EDAD_MIN_VALIDA, EDAD_MAX_VALIDA = 10, 14
HABITAT_ETIQUETAS = {1: "Hasta 10.000 hab.", 2: "De 10.001 a 100.000 hab.", 3: "Más de 100.000 hab."}
# Combinaciones área x hábitat que solo aparecen en 1-2 convocatorias (ver sección 4.6).
COMBOS_HABITAT_INCOHERENTES = {
    ("Consorci d'Educació de Barcelona", 1), ("Consorci d'Educació de Barcelona", 2),
    ("Catalunya Central", 3), ("Terres de l'Ebre", 3), ("Baix Llobregat", 3),
}


class Tee:
    def __init__(self, *flujos):
        self.flujos = flujos

    def write(self, txt):
        for f in self.flujos:
            f.write(txt)

    def flush(self):
        for f in self.flujos:
            f.flush()


def titulo(txt):
    print("\n" + "=" * 110)
    print(txt)
    print("=" * 110)


def sub(txt):
    print("\n--- " + txt)


def mostrar(df, nombre_csv=None):
    print(df.to_string(index=False) if isinstance(df, pd.DataFrame) else df)
    if nombre_csv:
        df.to_csv(os.path.join(SALIDA, nombre_csv), index=False)


def sql(con, consulta, nombre_csv=None):
    df = con.sql(consulta).df()
    mostrar(df, nombre_csv)
    return df


def hab3_sql(col='"HÀBITAT"'):
    return (f"CASE WHEN {col} LIKE 'Fins a %' THEN 1 WHEN {col} = 'De 10001 a 100000' THEN 2 "
            f"WHEN {col} LIKE 'Més de %' THEN 3 END")


GEN_SQL = "CASE WHEN GENERE IN ('H','Home') THEN 'H' WHEN GENERE IN ('D','Dona') THEN 'D' END"
NAT_SQL = ("CASE WHEN NATURALESA IN ('Públic','Pública') THEN 'Pública' "
           "WHEN NATURALESA IN ('Privat','Privada') THEN 'Privada' END")


def num_sql(col):
    return f"TRY_CAST(REPLACE({col}, ',', '.') AS DOUBLE)"


def _b(serie):
    return serie.fillna(False).to_numpy(dtype=bool)


# ----------------------------------------------------------------------------------------------
# Reglas de limpieza (Python / pandas). Equivalente M en limpieza_categoricas.pq
# ----------------------------------------------------------------------------------------------
def limpiar_categoricas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica las reglas de limpieza a las columnas categóricas.

    `df` debe leerse con dtype=str y keep_default_na=False (las cadenas vacías se
    tratan aquí) y conservar el orden del fichero (EvaluacionID = línea del CSV).
    """
    out = pd.DataFrame(index=df.index)
    txt = {c: df[c].str.strip().replace("", np.nan) for c in CATEG}
    out["EvaluacionID"] = df.index.to_numpy() + 2
    out["Anio"] = pd.to_numeric(txt["ANY"], errors="coerce").astype("Int64")
    out["CodiAlumne"] = txt["CODI_ALUMNE"]
    out["TieneCodigo"] = out["CodiAlumne"].notna()
    out["GeneroCod"] = txt["GENERE"].map({"H": "H", "Home": "H", "D": "D", "Dona": "D"})
    out["Genero"] = out["GeneroCod"].map({"H": "Niño", "D": "Niña"}).fillna("Desconocido")
    out["Naturaleza"] = txt["NATURALESA"].map(
        {"Públic": "Pública", "Pública": "Pública", "Privat": "Privada", "Privada": "Privada"}
    ).fillna("Desconocida")
    h = txt["HÀBITAT"]
    out["HabitatCod"] = pd.Series(
        np.select([h.str.startswith("Fins a ", na=False), h.eq("De 10001 a 100000"),
                   h.str.startswith("Més de ", na=False)], [1, 2, 3], default=0),
        index=df.index).replace(0, pd.NA).astype("Int64")
    out["Habitat"] = out["HabitatCod"].map(HABITAT_ETIQUETAS).fillna("Desconocido")
    out["FlagHabitatTextoAnomalo"] = h.str.match(r"^Fins a \d+$", na=False) & h.ne("Fins a 10000")
    area = txt["AREA_TERRITORIAL"]
    out["AreaTerritorial"] = area.fillna("Desconocida")
    combo = list(zip(out["AreaTerritorial"], out["HabitatCod"].fillna(0).astype(int)))
    out["FlagHabitatIncoherenteArea"] = pd.Series([c in COMBOS_HABITAT_INCOHERENTES for c in combo],
                                                  index=df.index)
    out["HabitatFiable"] = out["Anio"].ne(2010) & ~out["FlagHabitatIncoherenteArea"]
    out["AreaPerimetro2025"] = np.where(
        area.eq("Barcelona Comarques") & out["Anio"].eq(2024), "Barcelonès",
        np.where(area.eq("Barcelona Comarques"), "Barcelona Comarques (perímetro hasta 2023)",
                 out["AreaTerritorial"]))
    out["AreaSerieComparable"] = np.where(
        area.isin(GRUPO_LLEIDA), NOMBRE_GRUPO_LLEIDA,
        np.where(area.isin(GRUPO_BCN), NOMBRE_GRUPO_BCN, out["AreaTerritorial"]))
    out["AreaConRupturaSerie"] = area.isin(GRUPO_LLEIDA + GRUPO_BCN)
    mes = pd.to_numeric(txt["MES_NAIXEMENT"], errors="coerce").astype("Int64")
    out["MesNacimiento"] = mes.where(mes.between(1, 12).fillna(False))
    anio_n = pd.to_numeric(txt["ANY_NAIXEMENT"], errors="coerce").astype("Int64")
    out["AnioNacimiento"] = anio_n
    edad_bruta = out["Anio"] - anio_n
    out["EdadBruta"] = edad_bruta
    valida = edad_bruta.between(EDAD_MIN_VALIDA, EDAD_MAX_VALIDA) & out["Anio"].ne(2010)
    out["EdadPrueba"] = edad_bruta.where(valida.fillna(False))
    out["FlagEdadFueraRango"] = edad_bruta.notna() & ~edad_bruta.between(EDAD_MIN_VALIDA, EDAD_MAX_VALIDA).fillna(False)
    e = out["EdadPrueba"]
    out["SituacionEdad"] = np.select(
        [_b(out["Anio"].eq(2010)), _b(e.isna()), _b(e < EDAD_TEORICA), _b(e == EDAD_TEORICA),
         _b(e == EDAD_TEORICA + 1)],
        ["No fiable (2010)", "Desconocida", "Adelantado", "Edad teórica", "Retraso de 1 año"],
        default="Retraso de 2 años")
    con_cod = out[out["TieneCodigo"]]
    n_anio = con_cod.groupby(["Anio", "CodiAlumne"])["EvaluacionID"].transform("size")
    out["FlagCodigoDuplicadoAnio"] = False
    out.loc[n_anio.index, "FlagCodigoDuplicadoAnio"] = n_anio.gt(1).to_numpy()
    prev = con_cod[["CodiAlumne", "Anio", "GeneroCod", "AnioNacimiento", "MesNacimiento"]].copy()
    prev["Anio"] = prev["Anio"] + 1
    prev = prev.drop_duplicates(["CodiAlumne", "Anio"]).assign(_prev=True)
    m = out[["CodiAlumne", "Anio", "GeneroCod", "AnioNacimiento", "MesNacimiento"]].merge(
        prev, on=["CodiAlumne", "Anio"], how="left", suffixes=("", "_ant"))
    m.index = out.index
    out["CodigoEnConvocatoriaAnterior"] = m["_prev"].eq(True)
    out["RepeticionProbable"] = (
        out["CodigoEnConvocatoriaAnterior"] & m["GeneroCod"].eq(m["GeneroCod_ant"])
        & m["AnioNacimiento"].eq(m["AnioNacimiento_ant"]).fillna(False)
        & m["MesNacimiento"].eq(m["MesNacimiento_ant"]).fillna(False))
    return out


def main():
    con = duckdb.connect()
    con.execute("SET preserve_insertion_order = true")

    # ------------------------------------------------------------------------------------------
    titulo("0. LECTURA Y CONTROLES DEL FICHERO EN BRUTO")
    n_lineas, n_campos_mal, n_comillas_vacias = 0, 0, 0
    with open(CSV, encoding="utf-8", newline="") as f:
        primera = f.readline()
        bom = primera.startswith("﻿")
        f.seek(0)
        for linea in f:
            n_lineas += 1
            n_comillas_vacias += linea.count('""')
    with open(CSV, encoding="utf-8", newline="") as f:
        lector = csv.reader(f)
        cab = next(lector)
        for fila in lector:
            if len(fila) != len(cab):
                n_campos_mal += 1
    print(f"Líneas físicas (incluida cabecera): {n_lineas:,}")
    print(f"Columnas en cabecera: {len(cab)}; filas con nº de campos distinto: {n_campos_mal}")
    print(f"BOM UTF-8 al inicio: {bom}; apariciones del literal \"\" (cadena vacía entre comillas): {n_comillas_vacias}")

    con.execute(f"""CREATE TABLE d AS
        SELECT * FROM read_csv('{CSV}', all_varchar=true, header=true)""")
    con.execute("CREATE TABLE r AS SELECT rowid + 2 AS linea, * FROM d")
    con.execute("DROP TABLE d")
    con.execute("ALTER TABLE r RENAME TO d")
    print(f"Filas de datos leídas por DuckDB: {con.sql('SELECT count(*) FROM d').fetchone()[0]:,}")
    print("(DuckDB lee el campo vacío sin comillas como NULL; Power Query lo lee como \"\" y pandas como NaN)")

    sub("0.1 Vacíos, cadenas vacías y espacios por columna categórica")
    partes = []
    for c in CATEG:
        partes.append(f"""SELECT '{c}' AS columna,
            count(*) FILTER (WHERE "{c}" IS NULL) AS nulos,
            count(*) FILTER (WHERE "{c}" = '') AS cadena_vacia,
            count(*) FILTER (WHERE "{c}" <> trim("{c}")) AS espacios_ini_fin,
            count(*) FILTER (WHERE regexp_matches("{c}", '\\s\\s')) AS espacios_dobles,
            count(*) FILTER (WHERE regexp_matches("{c}", '[\\x00-\\x1F\\xA0]')) AS no_imprimibles,
            count(DISTINCT "{c}") AS distintos FROM d""")
    sql(con, " UNION ALL ".join(partes), "vacios_por_columna.csv")

    # ------------------------------------------------------------------------------------------
    titulo("1. FILAS POR AÑO (ANY) Y AÑOS PRESENTES/AUSENTES 2009-2025")
    por_anio = sql(con, """SELECT "ANY", count(*) AS filas,
            round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct
        FROM d GROUP BY 1 ORDER BY 1""", "filas_por_anio.csv")
    print("Formato de ANY: ", con.sql("""SELECT count(*) FILTER (WHERE NOT regexp_full_match("ANY", '\\d{4}')) AS no_4_digitos,
        count(*) FILTER (WHERE "ANY" IS NULL) AS nulos FROM d""").fetchall())
    presentes = sorted(int(a) for a in por_anio["ANY"])
    ausentes = [a for a in ANIOS_ESPERADOS if a not in presentes]
    print(f"Años presentes ({len(presentes)}): {presentes}")
    print(f"Años ausentes en 2009-2025: {ausentes}")
    print(f"Total filas: {int(por_anio['filas'].sum()):,}")

    # ------------------------------------------------------------------------------------------
    titulo("2. CODI_ALUMNE")
    sub("2.1 Vacíos por año")
    sql(con, """SELECT "ANY", count(*) AS filas, count(CODI_ALUMNE) AS con_codigo,
            count(*) - count(CODI_ALUMNE) AS vacios,
            round(100.0 * (count(*) - count(CODI_ALUMNE)) / count(*), 2) AS pct_vacios,
            count(DISTINCT CODI_ALUMNE) AS codigos_distintos
        FROM d GROUP BY 1 ORDER BY 1""", "codi_vacios_por_anio.csv")

    sub("2.2 Formato: longitud y solo dígitos (filas con código)")
    sql(con, """PIVOT (SELECT "ANY", length(CODI_ALUMNE) AS longitud FROM d WHERE CODI_ALUMNE IS NOT NULL)
        ON longitud USING count(*) ORDER BY "ANY" """, "codi_longitud_por_anio.csv")
    sql(con, """SELECT count(*) AS filas_con_codigo,
            count(*) FILTER (WHERE NOT regexp_full_match(CODI_ALUMNE, '[0-9]+')) AS no_solo_digitos,
            count(*) FILTER (WHERE CODI_ALUMNE LIKE '0%') AS con_cero_inicial,
            min(length(CODI_ALUMNE)) AS long_min, max(length(CODI_ALUMNE)) AS long_max,
            count(DISTINCT CODI_ALUMNE) AS distintos_texto,
            count(DISTINCT TRY_CAST(CODI_ALUMNE AS BIGINT)) AS distintos_numerico
        FROM d WHERE CODI_ALUMNE IS NOT NULL""")

    sub("2.3a Recuento 'ingenuo' de duplicados por año tratando el vacío como un código más ('')")
    sql(con, """WITH g AS (SELECT "ANY", coalesce(CODI_ALUMNE, '') AS codigo, count(*) AS n FROM d
                 WHERE "ANY" >= '2016' GROUP BY ALL HAVING count(*) > 1)
        SELECT "ANY", CASE WHEN codigo = '' THEN '(cadena vacía)' ELSE 'código real' END AS tipo,
               count(*) AS grupos_con_n_mayor_1, sum(n) AS filas_implicadas
        FROM g GROUP BY ALL ORDER BY 1, 2""")
    sub("2.3b Duplicados reales dentro del mismo año (excluido el vacío)")
    dups = sql(con, """SELECT "ANY", CODI_ALUMNE, count(*) AS filas FROM d
        WHERE CODI_ALUMNE IS NOT NULL GROUP BY ALL HAVING count(*) > 1 ORDER BY 1""")
    for _, fila in dups.iterrows():
        det = con.sql(f"""SELECT * FROM d WHERE "ANY" = '{fila['ANY']}'
                          AND CODI_ALUMNE = '{fila['CODI_ALUMNE']}' ORDER BY linea""").df()
        print(f"\nDetalle {fila['ANY']} / {fila['CODI_ALUMNE']} (traspuesto):")
        print(det.T.to_string())
        difieren = [c for c in det.columns if c != "linea" and det[c].nunique(dropna=False) > 1]
        identicas = det.drop(columns="linea").duplicated().any()
        print(f"¿Filas idénticas?: {identicas}. Columnas que difieren ({len(difieren)}): {difieren}")
        compl = [c for c in PUNT if det[c].notna().sum() == 2 and det[c].nunique() > 1]
        print(f"Puntuaciones presentes en ambas filas y con valor distinto: {compl}")

    sub("2.4 Códigos repetidos entre años distintos")
    con.execute("""CREATE TEMP TABLE rep AS
        SELECT CODI_ALUMNE FROM d WHERE CODI_ALUMNE IS NOT NULL
        GROUP BY 1 HAVING count(DISTINCT "ANY") > 1""")
    sql(con, """WITH x AS (SELECT CODI_ALUMNE, count(DISTINCT "ANY") AS n_anios, count(*) AS n_filas
                 FROM d WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1)
        SELECT n_anios, n_filas, count(*) AS codigos FROM x GROUP BY ALL ORDER BY 1, 2""")
    con.execute(f"""CREATE TEMP TABLE par AS
        SELECT CODI_ALUMNE, string_agg("ANY", '-' ORDER BY "ANY") AS par_anios,
               max("ANY"::INT) - min("ANY"::INT) AS salto,
               count(DISTINCT {GEN_SQL}) = 1 AS mismo_genero,
               count(DISTINCT coalesce(ANY_NAIXEMENT, '?')) = 1 AS mismo_anio_nac,
               count(DISTINCT coalesce(MES_NAIXEMENT, '?')) = 1 AS mismo_mes_nac,
               count(DISTINCT AREA_TERRITORIAL) = 1 AS misma_area,
               count(DISTINCT {NAT_SQL}) = 1 AS misma_naturaleza,
               count(DISTINCT {hab3_sql()}) = 1 AS mismo_habitat
        FROM d WHERE CODI_ALUMNE IN (SELECT * FROM rep) GROUP BY 1""")
    sql(con, """SELECT par_anios, salto, count(*) AS codigos,
            sum(mismo_genero::INT) AS mismo_genero,
            sum((mismo_anio_nac AND mismo_mes_nac)::INT) AS misma_fecha_nac,
            sum((mismo_genero AND mismo_anio_nac AND mismo_mes_nac)::INT) AS genero_y_fecha,
            sum(misma_area::INT) AS misma_area, sum(misma_naturaleza::INT) AS misma_naturaleza,
            sum(mismo_habitat::INT) AS mismo_habitat
        FROM par GROUP BY GROUPING SETS ((par_anios, salto), ()) ORDER BY 1 NULLS LAST""", "codi_repetidos_entre_anios.csv")
    sub("2.4b Compatibilidad con repetición de 6º: edad (ANY - ANY_NAIXEMENT) en 1ª y 2ª aparición")
    sql(con, """WITH x AS (SELECT CODI_ALUMNE, "ANY"::INT - TRY_CAST(ANY_NAIXEMENT AS INT) AS edad,
                    row_number() OVER (PARTITION BY CODI_ALUMNE ORDER BY "ANY") AS orden
                 FROM d WHERE CODI_ALUMNE IN (SELECT * FROM rep)),
            p AS (SELECT CODI_ALUMNE, max(edad) FILTER (WHERE orden = 1) AS edad_1a,
                         max(edad) FILTER (WHERE orden = 2) AS edad_2a FROM x GROUP BY 1)
        SELECT edad_1a, edad_2a, count(*) AS codigos FROM p GROUP BY ALL ORDER BY 3 DESC""")
    sub("2.4c Los códigos repetidos cuyo género o fecha de nacimiento no coinciden")
    sql(con, """SELECT "ANY", CODI_ALUMNE, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT, AREA_TERRITORIAL,
            NATURALESA, "HÀBITAT"
        FROM d WHERE CODI_ALUMNE IN (SELECT CODI_ALUMNE FROM par
                                     WHERE NOT (mismo_genero AND mismo_anio_nac AND mismo_mes_nac))
        ORDER BY 2, 1""")

    # ------------------------------------------------------------------------------------------
    titulo("3. VALORES DISTINTOS Y FRECUENCIAS POR AÑO (valores en bruto, entre corchetes)")
    for c in ["GENERE", "NATURALESA"]:
        sub(f"3.x {c}")
        sql(con, f"""PIVOT (SELECT "ANY", coalesce('[' || "{c}" || ']', '<NULO>') AS valor FROM d)
            ON valor USING count(*) ORDER BY "ANY" """, f"freq_{c.lower()}_por_anio.csv")
    sub("3.x HÀBITAT (los 'Fins a N' con N<>10000 se agrupan aquí; detalle en sección 4)")
    sql(con, """PIVOT (SELECT "ANY", CASE WHEN "HÀBITAT" LIKE 'Fins a %' AND "HÀBITAT" <> 'Fins a 10000'
                         THEN '[Fins a N<>10000]' ELSE coalesce('[' || "HÀBITAT" || ']', '<NULO>') END AS valor FROM d)
        ON valor USING count(*) ORDER BY "ANY" """, "freq_habitat_por_anio.csv")
    print("Valores distintos en bruto de HÀBITAT:",
          con.sql('SELECT count(DISTINCT "HÀBITAT") FROM d').fetchone()[0])
    sub("3.x AREA_TERRITORIAL: matriz área x año (conteos)")
    sql(con, """PIVOT (SELECT coalesce(AREA_TERRITORIAL, '<NULO>') AS area, "ANY" FROM d)
        ON "ANY" USING count(*) ORDER BY area""", "matriz_area_anio.csv")
    sql(con, """SELECT coalesce(AREA_TERRITORIAL, '<NULO>') AS area, count(*) AS filas,
            min("ANY") AS primer_anio, max("ANY") AS ultimo_anio, count(DISTINCT "ANY") AS n_anios
        FROM d GROUP BY 1 ORDER BY 1""")

    # ------------------------------------------------------------------------------------------
    titulo("4. HÀBITAT: VALORES 'Fins a N' ANÓMALOS Y COHERENCIA")
    con.execute("""CREATE TEMP TABLE fins AS
        SELECT linea, "ANY", AREA_TERRITORIAL, NATURALESA, "HÀBITAT",
               TRY_CAST(regexp_extract("HÀBITAT", '^Fins a (\\d+)$', 1) AS BIGINT) AS n
        FROM d WHERE "HÀBITAT" LIKE 'Fins a %'""")
    sub("4.1 Rango de N en 'Fins a N' por año")
    sql(con, """SELECT "ANY", count(*) AS filas, count(*) FILTER (WHERE n = 10000) AS n_10000,
            count(*) FILTER (WHERE n <> 10000) AS n_distinto_10000,
            count(DISTINCT n) FILTER (WHERE n <> 10000) AS valores_distintos,
            min(n) FILTER (WHERE n <> 10000) AS n_min, max(n) FILTER (WHERE n <> 10000) AS n_max,
            count(*) FILTER (WHERE n IS NULL) AS no_parseable
        FROM fins GROUP BY 1 HAVING count(*) FILTER (WHERE n <> 10000) > 0 OR "ANY" IN ('2023','2024','2025')
        ORDER BY 1""")
    r = con.sql("""SELECT count(*), count(DISTINCT n), min(n), max(n) FROM fins
                   WHERE "ANY" = '2024' AND n <> 10000""").fetchone()
    print(f"2024: {r[0]:,} filas anómalas, {r[1]:,} valores distintos, N de {r[2]} a {r[3]} "
          f"(secuencia completa sin huecos: {r[3] - r[2] + 1 == r[1] == r[0]})")
    sub("4.2 Fila semilla 'Fins a 10000' de 2024 y extremos de la secuencia")
    sql(con, """SELECT linea, "ANY", "HÀBITAT", AREA_TERRITORIAL, NATURALESA FROM fins
        WHERE "ANY" = '2024' AND n IN (10000, 10001, 10002, 23356, 23357) ORDER BY n""")
    sub("4.3 ¿El valor N sigue el orden del fichero? (la secuencia se generó con otro orden de filas)")
    sql(con, """WITH a AS (SELECT linea, n, lag(n) OVER (ORDER BY linea) AS n_ant FROM fins WHERE "ANY" = '2024')
        SELECT count(*) FILTER (WHERE n > n_ant) AS sube, count(*) FILTER (WHERE n < n_ant) AS baja,
               round(corr(linea, n), 4) AS correlacion_linea_n FROM a""")
    sub("4.4 ¿Se concentran en algún área/naturaleza? % de filas 'Fins a' por área y año (2022-2025)")
    sql(con, """PIVOT (SELECT coalesce(AREA_TERRITORIAL, '<NULO>') AS area, "ANY",
                          ("HÀBITAT" LIKE 'Fins a %')::INT AS es_fins FROM d WHERE "ANY" >= '2022')
        ON "ANY" USING round(100.0 * avg(es_fins), 1) ORDER BY area""")
    sql(con, f"""SELECT "ANY", {NAT_SQL} AS naturaleza,
            count(*) FILTER (WHERE "HÀBITAT" LIKE 'Fins a %') AS filas_fins,
            count(*) FILTER (WHERE "HÀBITAT" LIKE 'Fins a %' AND "HÀBITAT" <> 'Fins a 10000') AS anomalas,
            count(*) AS total, round(100.0 * filas_fins / total, 1) AS pct_fins
        FROM d WHERE "ANY" >= '2022' GROUP BY ALL ORDER BY 2, 1""")
    print("% de las filas 'Fins a' de 2024 que son anómalas:",
          con.sql("""SELECT round(100.0 * count(*) FILTER (WHERE n <> 10000) / count(*), 3)
                     FROM fins WHERE "ANY" = '2024'""").fetchone()[0])
    sub("4.5 Propuesta de mapeo a 3 categorías y verificación de cobertura")
    sql(con, f"""SELECT {hab3_sql()} AS habitat_cod, count(*) AS filas, count(DISTINCT "HÀBITAT") AS valores_brutos,
            min("HÀBITAT") AS ejemplo_min, max("HÀBITAT") AS ejemplo_max
        FROM d GROUP BY 1 ORDER BY 1""")
    sql(con, f"""PIVOT (SELECT "ANY", {hab3_sql()} AS habitat_cod FROM d) ON habitat_cod
        USING count(*) ORDER BY "ANY" """, "habitat3_por_anio.csv")
    sub("4.6 Coherencia área x hábitat: combinaciones presentes en <= 2 convocatorias")
    sql(con, f"""WITH c AS (SELECT AREA_TERRITORIAL AS area, {hab3_sql()} AS hab, "ANY", count(*) AS n
                 FROM d WHERE AREA_TERRITORIAL IS NOT NULL GROUP BY ALL)
        SELECT area, hab, count(*) AS n_convocatorias, string_agg("ANY" || ':' || n::VARCHAR, ', ' ORDER BY "ANY") AS detalle
        FROM c GROUP BY ALL HAVING count(*) <= 2 ORDER BY 1, 2""")
    combos = " OR ".join(f"(AREA_TERRITORIAL = '{a.replace(chr(39), chr(39) * 2)}' AND {hab3_sql()} = {h})"
                         for a, h in sorted(COMBOS_HABITAT_INCOHERENTES))
    sql(con, f"""SELECT "ANY", count(*) FILTER (WHERE {combos}) AS filas_incoherentes, count(*) AS filas,
            round(100.0 * filas_incoherentes / filas, 2) AS pct
        FROM d GROUP BY 1 HAVING filas_incoherentes > 0 ORDER BY 1""")
    sub("4.7 Hábitat por área y año (1=Fins 10000, 2=10001-100000, 3=Més de 100000) - áreas con anomalías")
    sql(con, f"""PIVOT (SELECT AREA_TERRITORIAL AS area, {hab3_sql()} AS hab, "ANY" FROM d
                  WHERE AREA_TERRITORIAL IN ('Consorci d''Educació de Barcelona', 'Catalunya Central',
                        'Terres de l''Ebre', 'Baix Llobregat', 'Girona', 'Maresme - Vallès Oriental'))
        ON "ANY" USING count(*) GROUP BY area, hab ORDER BY area, hab""", "habitat_area_anio.csv")
    sub("4.8 2010: ¿hábitat y naturaleza mantienen su relación habitual? (área x naturaleza x hábitat, 2010 vs 2011)")
    for anio in ("2010", "2011"):
        print(f"Año {anio}")
        sql(con, f"""PIVOT (SELECT AREA_TERRITORIAL AS area, {NAT_SQL} AS naturaleza, {hab3_sql()} AS hab
                      FROM d WHERE "ANY" = '{anio}') ON hab USING count(*) ORDER BY 1, 2""")

    # ------------------------------------------------------------------------------------------
    titulo("5. FECHA DE NACIMIENTO Y EDAD EN LA PRUEBA")
    sub("5.1 Rangos, vacíos y valores no válidos por año")
    sql(con, """SELECT "ANY",
            count(*) FILTER (WHERE MES_NAIXEMENT IS NULL) AS mes_nulo,
            count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL) AS anio_nulo,
            count(*) FILTER (WHERE MES_NAIXEMENT IS NULL AND ANY_NAIXEMENT IS NULL) AS ambos_nulos,
            count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL AND MES_NAIXEMENT IS NOT NULL) AS solo_anio_nulo,
            count(*) FILTER (WHERE MES_NAIXEMENT IS NOT NULL AND NOT regexp_full_match(MES_NAIXEMENT, '\\d{1,2}')) AS mes_no_numerico,
            count(*) FILTER (WHERE TRY_CAST(MES_NAIXEMENT AS INT) NOT BETWEEN 1 AND 12) AS mes_fuera_1_12,
            count(*) FILTER (WHERE ANY_NAIXEMENT IS NOT NULL AND NOT regexp_full_match(ANY_NAIXEMENT, '\\d{4}')) AS anio_no_4dig,
            min(TRY_CAST(MES_NAIXEMENT AS INT)) AS mes_min, max(TRY_CAST(MES_NAIXEMENT AS INT)) AS mes_max,
            min(TRY_CAST(ANY_NAIXEMENT AS INT)) AS anio_nac_min, max(TRY_CAST(ANY_NAIXEMENT AS INT)) AS anio_nac_max
        FROM d GROUP BY 1 ORDER BY 1""", "fechas_nacimiento_por_anio.csv")
    sql(con, """SELECT count(*) FILTER (WHERE MES_NAIXEMENT IS NULL) AS mes_nulo_total,
            count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL) AS anio_nulo_total,
            min(TRY_CAST(ANY_NAIXEMENT AS INT)) AS anio_nac_min, max(TRY_CAST(ANY_NAIXEMENT AS INT)) AS anio_nac_max
        FROM d""")
    sub("5.2 Distribución de EDAD = ANY - ANY_NAIXEMENT por año (columnas = edad; NaN = nacimiento vacío)")
    con.execute("""CREATE TEMP TABLE e AS SELECT "ANY", "ANY"::INT - TRY_CAST(ANY_NAIXEMENT AS INT) AS edad FROM d""")
    edades = con.sql("""SELECT "ANY", coalesce(edad::VARCHAR, 'nulo') AS edad, count(*) AS n FROM e GROUP BY ALL""").df()
    orden = sorted([x for x in edades["edad"].unique() if x != "nulo"], key=int) + ["nulo"]
    tabla_edad = edades.pivot_table(index="ANY", columns="edad", values="n", fill_value=0)[orden].astype(int).reset_index()
    mostrar(tabla_edad, "edad_por_anio.csv")
    sql(con, """SELECT edad, count(*) AS filas FROM e GROUP BY 1 ORDER BY 1 NULLS LAST""")
    sub("5.3 Moda de la edad por año y % mayor/menor de la edad teórica (12) por año, género y naturaleza")
    sql(con, f"""WITH x AS (SELECT "ANY", {GEN_SQL} AS g, {NAT_SQL} AS nat,
                       "ANY"::INT - TRY_CAST(ANY_NAIXEMENT AS INT) AS edad FROM d)
        SELECT "ANY", count(edad) AS con_edad, mode(edad) AS moda,
            round(100.0 * count(*) FILTER (WHERE edad = 12) / count(edad), 2) AS pct_12,
            round(100.0 * count(*) FILTER (WHERE edad > 12) / count(edad), 2) AS pct_mayor,
            round(100.0 * count(*) FILTER (WHERE edad < 12) / count(edad), 2) AS pct_menor,
            round(100.0 * count(*) FILTER (WHERE edad > 12 AND g = 'H') / count(edad) FILTER (WHERE g = 'H'), 2) AS pct_mayor_ninos,
            round(100.0 * count(*) FILTER (WHERE edad > 12 AND g = 'D') / count(edad) FILTER (WHERE g = 'D'), 2) AS pct_mayor_ninas,
            round(100.0 * count(*) FILTER (WHERE edad > 12 AND nat = 'Pública') / count(edad) FILTER (WHERE nat = 'Pública'), 2) AS pct_mayor_publica,
            round(100.0 * count(*) FILTER (WHERE edad > 12 AND nat = 'Privada') / count(edad) FILTER (WHERE nat = 'Privada'), 2) AS pct_mayor_privada
        FROM x GROUP BY 1 ORDER BY 1""", "pct_mayor_edad_teorica.csv")
    sub(f"5.4 Edades fuera del rango plausible [{EDAD_MIN_VALIDA}, {EDAD_MAX_VALIDA}] por año")
    sql(con, f"""SELECT "ANY", count(*) FILTER (WHERE edad < {EDAD_MIN_VALIDA}) AS menores_de_{EDAD_MIN_VALIDA},
            count(*) FILTER (WHERE edad > {EDAD_MAX_VALIDA}) AS mayores_de_{EDAD_MAX_VALIDA},
            count(*) FILTER (WHERE edad IS NULL) AS sin_edad
        FROM e GROUP BY 1 ORDER BY 1""")
    sub("5.5 Marcador de posición en 2016: nacidos en 2001 (edad 15) por mes")
    sql(con, """SELECT "ANY", ANY_NAIXEMENT, MES_NAIXEMENT, count(*) AS filas, count(CODI_ALUMNE) AS con_codigo
        FROM d WHERE "ANY" = '2016' AND ANY_NAIXEMENT = '2001' GROUP BY ALL""")
    sql(con, """SELECT "ANY", count(*) AS filas_sin_codigo,
            count(*) FILTER (WHERE MES_NAIXEMENT = '1') AS con_mes_1
        FROM d WHERE CODI_ALUMNE IS NULL AND "ANY" IN ('2016', '2018') GROUP BY 1""")
    sub("5.6 Exceso de nacidos en enero: enero vs media de los meses de 31 días (mar, may, jul, ago, oct, dic)")
    sql(con, """WITH c AS (SELECT "ANY", TRY_CAST(MES_NAIXEMENT AS INT) AS mes, count(*) AS n
                 FROM d WHERE MES_NAIXEMENT IS NOT NULL GROUP BY ALL)
        SELECT "ANY", max(n) FILTER (WHERE mes = 1) AS enero,
            round(avg(n) FILTER (WHERE mes IN (3,5,7,8,10,12)), 0) AS media_meses_31d,
            round(max(n) FILTER (WHERE mes = 1) - avg(n) FILTER (WHERE mes IN (3,5,7,8,10,12)), 0) AS exceso,
            round(100.0 * max(n) FILTER (WHERE mes = 1) / avg(n) FILTER (WHERE mes IN (3,5,7,8,10,12)) - 100, 1) AS pct_exceso
        FROM c GROUP BY 1 ORDER BY 1""", "exceso_enero.csv")
    sub("5.7 Prueba de alineación atributo-puntuación por año (diferencias de medias, puntos sobre 100)")
    print("edad12-13: PMAT(edad 12) - PMAT(edad 13); T1-T4: PMAT nacidos ene-mar - oct-dic (solo edad 12);")
    print("D-H: PCAT/PCAST niñas - niños; H-D: PMAT niños - niñas; Priv-Pub: PMAT privada - pública")
    sql(con, f"""WITH x AS (SELECT "ANY", {GEN_SQL} AS g, {NAT_SQL} AS nat,
                    "ANY"::INT - TRY_CAST(ANY_NAIXEMENT AS INT) AS edad, TRY_CAST(MES_NAIXEMENT AS INT) AS mes,
                    {num_sql('PMAT')} AS pmat, {num_sql('PCAT')} AS pcat, {num_sql('PCAST')} AS pcast FROM d)
        SELECT "ANY",
            round(avg(pmat) FILTER (WHERE edad = 12) - avg(pmat) FILTER (WHERE edad = 13), 2) AS mat_edad12_13,
            round(avg(pcat) FILTER (WHERE edad = 12) - avg(pcat) FILTER (WHERE edad = 13), 2) AS cat_edad12_13,
            round(avg(pmat) FILTER (WHERE edad = 12 AND mes <= 3) - avg(pmat) FILTER (WHERE edad = 12 AND mes >= 10), 2) AS mat_T1_T4,
            round(avg(pcat) FILTER (WHERE g = 'D') - avg(pcat) FILTER (WHERE g = 'H'), 2) AS cat_D_H,
            round(avg(pcast) FILTER (WHERE g = 'D') - avg(pcast) FILTER (WHERE g = 'H'), 2) AS cast_D_H,
            round(avg(pmat) FILTER (WHERE g = 'H') - avg(pmat) FILTER (WHERE g = 'D'), 2) AS mat_H_D,
            round(avg(pmat) FILTER (WHERE nat = 'Privada') - avg(pmat) FILTER (WHERE nat = 'Pública'), 2) AS mat_Priv_Pub
        FROM x GROUP BY 1 ORDER BY 1""", "alineacion_atributo_puntuacion.csv")
    sub("5.8 2009-2011 por área: % mayor de edad teórica y diferencia de PMAT/PCAT edad 12 vs 13")
    sql(con, f"""WITH x AS (SELECT "ANY", AREA_TERRITORIAL AS area, "ANY"::INT - TRY_CAST(ANY_NAIXEMENT AS INT) AS edad,
                    {num_sql('PMAT')} AS pmat, {num_sql('PCAT')} AS pcat FROM d WHERE "ANY" IN ('2009','2010','2011'))
        SELECT area, "ANY", round(100.0 * count(*) FILTER (WHERE edad > 12) / count(edad), 2) AS pct_mayor,
            round(avg(pmat) FILTER (WHERE edad = 12) - avg(pmat) FILTER (WHERE edad = 13), 2) AS mat_12_13,
            round(avg(pcat) FILTER (WHERE edad = 12) - avg(pcat) FILTER (WHERE edad = 13), 2) AS cat_12_13
        FROM x GROUP BY ALL ORDER BY 1, 2""")

    # ------------------------------------------------------------------------------------------
    titulo("6. RUPTURA TERRITORIAL 2024-2025")
    cnt = con.sql("""SELECT coalesce(AREA_TERRITORIAL, '<NULO>') AS area, "ANY"::INT AS anio, count(*) AS n
                     FROM d GROUP BY ALL""").df()
    pv = cnt.pivot_table(index="area", columns="anio", values="n", fill_value=0).astype(int)
    afect = ["Barcelona Comarques", "Barcelonès", "Penedès", "Tarragona", "Catalunya Central",
             "Lleida", "Alt Pirineu i Aran"]
    sub("6.1 Conteos 2019-2025 de las áreas afectadas y del conjunto de áreas estables")
    t = pv.loc[afect, [2019, 2021, 2022, 2023, 2024, 2025]].copy()
    t.loc["(Suma áreas estables)"] = pv.loc[AREAS_ESTABLES, [2019, 2021, 2022, 2023, 2024, 2025]].sum()
    t.loc["(Total Cataluña)"] = pv[[2019, 2021, 2022, 2023, 2024, 2025]].sum()
    mostrar(t.reset_index(), "ruptura_conteos.csv")
    est = pv.loc[AREAS_ESTABLES].sum()
    g24, g25 = est[2024] / est[2023], est[2025] / est[2024]
    tot = pv.sum()
    print(f"Áreas estables (sin cambio de nombre 2009-2025): {AREAS_ESTABLES}")
    print(f"Factor 2024/2023 áreas estables: {g24:.4f}; total Cataluña: {tot[2024] / tot[2023]:.4f}")
    print(f"Factor 2025/2024 áreas estables: {g25:.4f}; total Cataluña: {tot[2025] / tot[2024]:.4f}")

    sub("6.2 Balance Lleida 2023 vs Lleida 2024 + Alt Pirineu i Aran 2024")
    ll23, ll24, apa24 = pv.loc["Lleida", 2023], pv.loc["Lleida", 2024], pv.loc["Alt Pirineu i Aran", 2024]
    print(f"Lleida 2023 = {ll23}; Lleida 2024 = {ll24}; Alt Pirineu i Aran 2024 = {apa24}; suma 2024 = {ll24 + apa24}")
    print(f"Ratio (Lleida+APA 2024)/Lleida 2023 = {(ll24 + apa24) / ll23:.4f} (áreas estables {g24:.4f})")
    print(f"Déficit de Lleida 2024 respecto a lo esperado con el factor estable: {ll23 * g24 - ll24:.0f} "
          f"vs Alt Pirineu i Aran 2024 = {apa24}")

    sub("6.3 Balance Penedès 2024 vs déficit de Barcelona Comarques, Tarragona y Catalunya Central")
    filas = []
    for a in ["Barcelona Comarques", "Tarragona", "Catalunya Central", "Lleida"] + AREAS_ESTABLES:
        esperado = pv.loc[a, 2023] * g24
        filas.append({"area": a, "n_2023": pv.loc[a, 2023], "n_2024": pv.loc[a, 2024],
                      "ratio_24_23": round(pv.loc[a, 2024] / pv.loc[a, 2023], 4),
                      "esperado_2024": round(esperado), "deficit_vs_esperado": round(esperado - pv.loc[a, 2024])})
    bal = pd.DataFrame(filas)
    mostrar(bal, "ruptura_deficits.csv")
    tres = ["Barcelona Comarques", "Tarragona", "Catalunya Central"]
    suma_def = bal.loc[bal["area"].isin(tres), "deficit_vs_esperado"].sum()
    print(f"Suma de déficits BC + Tarragona + Cat. Central = {suma_def}; Penedès 2024 = {pv.loc['Penedès', 2024]}")
    bruto = sum(pv.loc[a, 2023] - pv.loc[a, 2024] for a in tres)
    print(f"Pérdida bruta (sin ajustar tendencia) de esas tres áreas 2023->2024 = {bruto}")
    print(f"BC 2023 = {pv.loc['Barcelona Comarques', 2023]} vs BC 2024 + Penedès 2024 = "
          f"{pv.loc['Barcelona Comarques', 2024] + pv.loc['Penedès', 2024]} (no cuadra solo con BC)")

    sub("6.4 Mismo balance por naturaleza (factor estable calculado por naturaleza)")
    cn = con.sql(f"""SELECT AREA_TERRITORIAL AS area, {NAT_SQL} AS nat, "ANY"::INT AS anio, count(*) AS n
                     FROM d WHERE "ANY" >= '2023' AND AREA_TERRITORIAL IS NOT NULL GROUP BY ALL""").df()
    pn = cn.pivot_table(index=["nat", "area"], columns="anio", values="n", fill_value=0).astype(int)
    filas = []
    for nat in ["Pública", "Privada"]:
        g = pn.loc[nat].loc[AREAS_ESTABLES, 2024].sum() / pn.loc[nat].loc[AREAS_ESTABLES, 2023].sum()
        deficit_pen = sum(pn.loc[nat].loc[a, 2023] * g - pn.loc[nat].loc[a, 2024] for a in tres)
        deficit_ll = pn.loc[nat].loc["Lleida", 2023] * g - pn.loc[nat].loc["Lleida", 2024]
        filas.append({"naturaleza": nat, "factor_estable": round(g, 4),
                      "deficit_BC_Tarr_CC": round(deficit_pen), "Penedes_2024": pn.loc[nat].loc["Penedès", 2024],
                      "deficit_Lleida": round(deficit_ll), "AltPirineu_2024": pn.loc[nat].loc["Alt Pirineu i Aran", 2024]})
    mostrar(pd.DataFrame(filas), "ruptura_por_naturaleza.csv")

    sub("6.5 Barcelona Comarques 2024 vs Barcelonès 2025: volumen y composición naturaleza x hábitat")
    sql(con, f"""PIVOT (SELECT AREA_TERRITORIAL || ' ' || "ANY" AS area_anio, {NAT_SQL} || '_' || ({hab3_sql()})::VARCHAR AS estrato
                  FROM d WHERE (AREA_TERRITORIAL = 'Barcelona Comarques' AND "ANY" IN ('2023', '2024'))
                     OR (AREA_TERRITORIAL = 'Barcelonès' AND "ANY" = '2025')
                     OR (AREA_TERRITORIAL = 'Penedès' AND "ANY" IN ('2024', '2025')))
        ON estrato USING count(*) ORDER BY 1""")
    print(f"Ratio Barcelonès 2025 / BC 2024 = {pv.loc['Barcelonès', 2025] / pv.loc['Barcelona Comarques', 2024]:.4f} "
          f"(áreas estables 2025/2024 = {g25:.4f})")

    sub("6.6 Transiciones de área de los códigos repetidos entre convocatorias (2023->2024 y 2024->2025)")
    sql(con, """WITH x AS (SELECT CODI_ALUMNE, "ANY", AREA_TERRITORIAL FROM d WHERE CODI_ALUMNE IN (SELECT * FROM rep))
        SELECT a."ANY" AS anio_1, b."ANY" AS anio_2, a.AREA_TERRITORIAL AS area_1, b.AREA_TERRITORIAL AS area_2,
               count(*) AS codigos
        FROM x a JOIN x b ON a.CODI_ALUMNE = b.CODI_ALUMNE AND a."ANY" < b."ANY"
        WHERE a."ANY" >= '2023' GROUP BY ALL ORDER BY 1, 3, 4""")

    sub("6.7 Serie de los grupos comparables propuestos (AreaSerieComparable)")
    con.execute(f"""CREATE TEMP TABLE serie AS SELECT "ANY",
            CASE WHEN AREA_TERRITORIAL IN ('Lleida', 'Alt Pirineu i Aran') THEN '{NOMBRE_GRUPO_LLEIDA}'
                 WHEN AREA_TERRITORIAL IN ('Barcelona Comarques', 'Barcelonès', 'Penedès', 'Tarragona', 'Catalunya Central')
                      THEN 'Grupo BC/Barcelonès+Penedès+Tarragona+Cat.Central'
                 WHEN AREA_TERRITORIAL IS NULL THEN 'Desconocida'
                 ELSE 'Áreas estables (6)' END AS grupo FROM d""")
    sql(con, """PIVOT serie ON "ANY" IN ('2016','2017','2018','2019','2021','2022','2023','2024','2025')
        USING count(*) ORDER BY grupo""")
    sql(con, """WITH c AS (SELECT grupo, "ANY", count(*) AS n FROM serie GROUP BY ALL)
        SELECT grupo, "ANY", n, round(n / lag(n) OVER (PARTITION BY grupo ORDER BY "ANY"), 4) AS ratio_vs_anterior
        FROM c WHERE "ANY" >= '2021' AND grupo <> 'Desconocida' ORDER BY 1, 2""")

    # ------------------------------------------------------------------------------------------
    titulo("7. OTRAS ANOMALÍAS")
    sub("7.1 Fila con AREA_TERRITORIAL vacía")
    sql(con, """SELECT linea, "ANY", CODI_ALUMNE, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT, NATURALESA, "HÀBITAT"
        FROM d WHERE AREA_TERRITORIAL IS NULL""")
    print("Apariciones de ese CODI_ALUMNE en otros años:",
          con.sql("""SELECT count(*) FROM d WHERE CODI_ALUMNE IN (SELECT CODI_ALUMNE FROM d WHERE AREA_TERRITORIAL IS NULL)
                     AND AREA_TERRITORIAL IS NOT NULL""").fetchone()[0])
    sub("7.2 Filas sin ninguna puntuación (afecta a FactEvaluacion)")
    sql(con, f"""SELECT "ANY", count(*) FILTER (WHERE coalesce({', '.join(PUNT)}) IS NULL) AS sin_puntuacion
        FROM d GROUP BY 1 HAVING sin_puntuacion > 0 ORDER BY 1""")
    print("Total filas sin ninguna puntuación:",
          con.sql(f"SELECT count(*) FROM d WHERE coalesce({', '.join(PUNT)}) IS NULL").fetchone()[0])
    sub("7.3 Orden del fichero: bloques por año (líneas)")
    sql(con, """SELECT "ANY", min(linea) AS linea_ini, max(linea) AS linea_fin, count(*) AS filas,
            (max(linea) - min(linea) + 1 = count(*)) AS bloque_contiguo FROM d GROUP BY 1 ORDER BY 2""")

    # ------------------------------------------------------------------------------------------
    titulo("8. APLICACIÓN Y VERIFICACIÓN DE LAS REGLAS DE LIMPIEZA (pandas: limpiar_categoricas)")
    df = pd.read_csv(CSV, dtype=str, keep_default_na=False, usecols=CATEG + ["PMAT"], encoding="utf-8")
    lim = limpiar_categoricas(df)
    print(f"Filas limpiadas: {len(lim):,}; EvaluacionID único: {lim['EvaluacionID'].is_unique}")
    for c in ["Genero", "Naturaleza", "Habitat", "SituacionEdad"]:
        sub(f"8.x {c} x Anio")
        mostrar(pd.crosstab(lim["Anio"], lim[c]).reset_index(), f"limpio_{c.lower()}_por_anio.csv")
    sub("8.x AreaSerieComparable x Anio")
    mostrar(pd.crosstab(lim["AreaSerieComparable"], lim["Anio"]).reset_index())
    sub("8.x AreaPerimetro2025 x Anio (2022-2025)")
    x = lim[lim["Anio"] >= 2022]
    mostrar(pd.crosstab(x["AreaPerimetro2025"], x["Anio"]).reset_index())
    sub("8.x Marcas (flags) por año")
    flags = ["TieneCodigo", "FlagCodigoDuplicadoAnio", "CodigoEnConvocatoriaAnterior", "RepeticionProbable",
             "FlagHabitatTextoAnomalo", "FlagHabitatIncoherenteArea", "HabitatFiable", "AreaConRupturaSerie",
             "FlagEdadFueraRango"]
    mostrar(lim.groupby("Anio")[flags].sum().astype(int).reset_index(), "limpio_flags_por_anio.csv")
    print("\nTotales de flags:")
    print(lim[flags].sum().astype(int).to_string())
    print("\nValores distintos tras limpieza:")
    for c in ["GeneroCod", "Genero", "Naturaleza", "HabitatCod", "Habitat", "AreaTerritorial", "SituacionEdad"]:
        print(f"  {c}: {sorted(lim[c].dropna().astype(str).unique().tolist())}")
    print("\nEdadPrueba (tras regla) - distribución:")
    print(lim["EdadPrueba"].value_counts(dropna=False).sort_index().to_string())

    # ------------------------------------------------------------------------------------------
    titulo("9. CIFRAS DERIVADAS CITADAS EN EL INFORME")
    sql(con, """SELECT count(*) AS filas, count(*) - count(CODI_ALUMNE) AS codi_vacios,
            round(100.0 * (count(*) - count(CODI_ALUMNE)) / count(*), 2) AS pct_codi_vacios,
            count(*) FILTER (WHERE "ANY" <= '2015') AS filas_2009_2015
        FROM d""")
    sub("9.1 % de cada categoría de hábitat por año")
    sql(con, f"""WITH c AS (SELECT "ANY", {hab3_sql()} AS hab, count(*) AS n FROM d GROUP BY ALL)
        SELECT "ANY", round(100.0 * sum(n) FILTER (WHERE hab = 1) / sum(n), 2) AS pct_hasta_10k,
               round(100.0 * sum(n) FILTER (WHERE hab = 2) / sum(n), 2) AS pct_10k_100k,
               round(100.0 * sum(n) FILTER (WHERE hab = 3) / sum(n), 2) AS pct_mas_100k
        FROM c GROUP BY 1 ORDER BY 1""", "habitat3_pct_por_anio.csv")
    sub("9.2 % de CODI_ALUMNE con 11 dígitos por año")
    sql(con, """SELECT "ANY", round(100.0 * count(*) FILTER (WHERE length(CODI_ALUMNE) = 11) / count(CODI_ALUMNE), 2) AS pct_11_digitos
        FROM d WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1 ORDER BY 1""")
    sub("9.3 Filas de las áreas con ruptura de serie")
    sql(con, """SELECT count(*) FILTER (WHERE "ANY" >= '2024') AS filas_2024_2025, count(*) AS filas_todos_los_anios
        FROM d WHERE AREA_TERRITORIAL IN ('Lleida', 'Alt Pirineu i Aran', 'Barcelona Comarques', 'Barcelonès',
                                          'Penedès', 'Tarragona', 'Catalunya Central')""")
    sql(con, """SELECT count(*) AS filas_girona_maresme_2024_2025 FROM d
        WHERE "ANY" >= '2024' AND AREA_TERRITORIAL IN ('Girona', 'Maresme - Vallès Oriental')""")
    sql(con, """SELECT count(*) FILTER (WHERE "ANY" IN ('2024', '2025')) AS filas_nat_nueva_etiqueta,
            count(*) FILTER (WHERE "HÀBITAT" = 'Més de 100001') AS filas_mes_de_100001,
            count(*) FILTER (WHERE "ANY" = '2021') AS filas_2021_home_dona FROM d""")


if __name__ == "__main__":
    log = open(os.path.join(SALIDA, "perfil_categoricas_salida.txt"), "w", encoding="utf-8")
    sys.stdout = Tee(sys.__stdout__, log)
    try:
        main()
    finally:
        sys.stdout = sys.__stdout__
        log.close()
