#!/usr/bin/env python3
"""Réplica de referencia de la ETL del CMI, independiente de Power BI.

Propósito (método de validación del TFG, GEP §4.3)
--------------------------------------------------
La ETL del cuadro de mando está escrita en Power Query (M) y solo se puede ejecutar
dentro de Power BI Desktop. Este script reproduce, con Python y DuckDB (SQL), las MISMAS
reglas de limpieza y el MISMO modelo en estrella que fija el contrato de diseño
(§2 reglas, §3 tablas, §5 tablas de códigos). Así se obtiene una «verdad de referencia»
con la que contrastar el modelo de Power BI: recuentos, claves y valores de los KPIs.

Uso
---
    python validacion/etl_referencia.py [--datos RUTA_CSV] [--salida CARPETA]

Entrada: Datos.csv (raíz del repositorio; se abre solo en lectura).
Salida : validacion/salida/<Tabla>.parquet para DimAnio, DimContextoCentro,
         DimPerfilAlumno, DimCompetencia, DimNivelLogro, DimCalidadDato,
         FactEvaluacion y FactPuntuacion (mismos nombres de columna que el modelo).

Correspondencia con la ETL de Power Query (contrato §2)
-------------------------------------------------------
  Paso M (stg_Evaluaciones)                    Función de este script
  1. R01  índice 1..N antes de filtrar          leer_csv()
  2. R05  Text.Trim y "" -> null                construir_staging(), paso 1
  3. R02  Number.FromText(texto, "es-ES")       construir_staging(), paso 2
  4. R03/R04 rotaciones (asignación simultánea)  construir_staging(), paso 3
  5-10.   Año, género, naturaleza, hábitat,     construir_staging(), pasos 4-6
          área, edad
  11.     claves deterministas                  construir_staging(), paso 7
  12.     TieneCodigoAlumno                     construir_staging(), paso 7
  Tablas §3                                     construir_dimensiones(), construir_hechos()

Las reglas que en M terminan en «error» (la actualización falla) aquí lanzan ValueError
con un mensaje que indica la columna y los valores que no se han podido mapear.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.csv as pacsv

RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "Datos.csv"
CARPETA_SALIDA = Path(__file__).resolve().parent / "salida"

# ---------------------------------------------------------------------------------------
# Estructura del fichero de origen (32 columnas, en este orden)
# ---------------------------------------------------------------------------------------
COLUMNAS_CSV = [
    "ANY", "CODI_ALUMNE", "PCAT", "PCAT_CL", "PCAT_EE", "PCAST", "PCAST_CL", "PCAST_EE",
    "PMAT", "PMAT_NC", "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE", "PFRAN",
    "PFRAN_CO", "PFRAN_CE", "PANG_EE", "PFRAN_EE", "PCAT_CO", "PCAST_CO", "PMED",
    "PMED_COMP1", "PMED_COMP2", "PMED_COMP3", "GENERE", "MES_NAIXEMENT", "ANY_NAIXEMENT",
    "AREA_TERRITORIAL", "NATURALESA", "HÀBITAT",
]

# ---------------------------------------------------------------------------------------
# §5.2 DimCompetencia (24 filas). Es también el «registro M estático» CampoOrigen -> clave.
# (CompetenciaKey, CampoOrigen, CodigoMateria, Materia, MateriaOrden, Subcompetencia,
#  SubcompetenciaOrden (único por texto, sortByColumn de Subcompetencia), EsGlobal, AnioInicio, AnioFin, PeriodoDisenoInicio, EsInformativa)
# ---------------------------------------------------------------------------------------
COMPETENCIAS = [
    (1, "PCAT", "PCAT", "Lengua catalana", 1, "Global", 0, True, 2009, None, 2018, False),
    (2, "PCAT_CL", "PCAT", "Lengua catalana", 1, "Comprensión lectora", 1, False, 2009, None, 2018, False),
    (3, "PCAT_EE", "PCAT", "Lengua catalana", 1, "Expresión escrita", 3, False, 2009, None, 2018, False),
    (4, "PCAT_CO", "PCAT", "Lengua catalana", 1, "Comprensión oral", 2, False, 2018, None, 2018, False),
    (5, "PCAST", "PCAST", "Lengua castellana", 2, "Global", 0, True, 2009, None, 2018, False),
    (6, "PCAST_CL", "PCAST", "Lengua castellana", 2, "Comprensión lectora", 1, False, 2009, None, 2018, False),
    (7, "PCAST_EE", "PCAST", "Lengua castellana", 2, "Expresión escrita", 3, False, 2009, None, 2018, False),
    (8, "PCAST_CO", "PCAST", "Lengua castellana", 2, "Comprensión oral", 2, False, 2018, None, 2018, False),
    (9, "PMAT", "PMAT", "Matemáticas", 3, "Global", 0, True, 2009, None, 2017, False),
    (10, "PMAT_NC", "PMAT", "Matemáticas", 3, "Numeración y cálculo", 4, False, 2009, None, 2017, False),
    (11, "PMAT_EFM", "PMAT", "Matemáticas", 3, "Espacio, medida y datos", 5, False, 2009, None, 2017, False),
    (12, "PMAT_CR", "PMAT", "Matemáticas", 3, "Relaciones y cambio", 6, False, 2009, None, 2017, False),
    (13, "PANG", "PANG", "Lengua inglesa", 4, "Global", 0, True, 2010, None, 2016, False),
    (14, "PANG_CO", "PANG", "Lengua inglesa", 4, "Comprensión oral", 2, False, 2010, None, 2017, False),
    (15, "PANG_CE", "PANG", "Lengua inglesa", 4, "Comprensión lectora", 1, False, 2010, None, 2017, False),
    (16, "PANG_EE", "PANG", "Lengua inglesa", 4, "Expresión escrita", 3, False, 2013, None, 2017, False),
    (17, "PFRAN", "PFRAN", "Lengua francesa", 5, "Global", 0, True, 2010, None, 2016, True),
    (18, "PFRAN_CO", "PFRAN", "Lengua francesa", 5, "Comprensión oral", 2, False, 2010, None, 2017, True),
    (19, "PFRAN_CE", "PFRAN", "Lengua francesa", 5, "Comprensión lectora", 1, False, 2010, None, 2017, True),
    (20, "PFRAN_EE", "PFRAN", "Lengua francesa", 5, "Expresión escrita", 3, False, 2013, None, 2017, True),
    (21, "PMED", "PMED", "Ciencias", 6, "Global", 0, True, 2018, None, 2018, False),
    (22, "PMED_COMP1", "PMED", "Ciencias", 6, "Explicar fenómenos naturales y tecnológicos", 7, False, 2018, None, 2018, False),
    (23, "PMED_COMP2", "PMED", "Ciencias", 6, "Reconocer la investigación científica", 8, False, 2018, None, 2018, False),
    (24, "PMED_COMP3", "PMED", "Ciencias", 6, "Interpretar datos y pruebas científicas", 9, False, 2018, None, 2018, False),
]
CAMPOS_PUNTUACION = [c[1] for c in COMPETENCIAS]          # las 24 columnas de puntuación
CAMPOS_GLOBALES = [c[1] for c in COMPETENCIAS if c[7]]    # PCAT, PCAST, PMAT, PANG, PFRAN, PMED
CLAVE_COMPETENCIA = {c[1]: c[0] for c in COMPETENCIAS}    # CampoOrigen -> CompetenciaKey

# ---------------------------------------------------------------------------------------
# §5.1 Áreas: (AreaCodigo, AreaTerritorial, AreaPerimetro2025, AreaSerieComparable,
#              AreaConRupturaSerie, RupturaHabitat2024)
# ---------------------------------------------------------------------------------------
GRUPO_BCN = "Barcelonès-Penedès y áreas afectadas"
GRUPO_LLEIDA = "Lleida + Alt Pirineu i Aran"
AREAS = [
    (1, "Alt Pirineu i Aran", "Alt Pirineu i Aran", GRUPO_LLEIDA, True, False),
    (2, "Baix Llobregat", "Baix Llobregat", "Baix Llobregat", False, False),
    (3, "Barcelona Comarques", "Barcelona Comarques (perímetro hasta 2023)", GRUPO_BCN, True, False),
    (4, "Barcelona Comarques", "Barcelonès", GRUPO_BCN, True, False),
    (5, "Barcelonès", "Barcelonès", GRUPO_BCN, True, False),
    (6, "Catalunya Central", "Catalunya Central", GRUPO_BCN, True, False),
    (7, "Consorci d'Educació de Barcelona", "Consorci d'Educació de Barcelona",
     "Consorci d'Educació de Barcelona", False, False),
    (8, "Girona", "Girona", "Girona", False, True),
    (9, "Lleida", "Lleida", GRUPO_LLEIDA, True, False),
    (10, "Maresme - Vallès Oriental", "Maresme - Vallès Oriental", "Maresme - Vallès Oriental", False, True),
    (11, "Penedès", "Penedès", GRUPO_BCN, True, False),
    (12, "Tarragona", "Tarragona", GRUPO_BCN, True, False),
    (13, "Terres de l'Ebre", "Terres de l'Ebre", "Terres de l'Ebre", False, False),
    (14, "Vallès Occidental", "Vallès Occidental", "Vallès Occidental", False, False),
    (99, "Desconocida", "Desconocida", "Desconocida", False, False),
]
# Texto de AREA_TERRITORIAL en el CSV -> AreaCodigo. «Barcelona Comarques» depende del año
# (3 hasta 2023, 4 en 2024) y se trata aparte en _sql_area(); el nulo va a 99 (R13).
CODIGO_AREA_POR_TEXTO = {
    "Alt Pirineu i Aran": 1, "Baix Llobregat": 2, "Barcelonès": 5, "Catalunya Central": 6,
    "Consorci d'Educació de Barcelona": 7, "Girona": 8, "Lleida": 9,
    "Maresme - Vallès Oriental": 10, "Penedès": 11, "Tarragona": 12, "Terres de l'Ebre": 13,
    "Vallès Occidental": 14,
}

NATURALEZAS = [(1, "Pública"), (2, "Privada")]
HABITATS = [(0, "No fiable"), (1, "Hasta 10.000 hab."), (2, "De 10.001 a 100.000 hab."),
            (3, "Más de 100.000 hab.")]

# ---------------------------------------------------------------------------------------
# §3 DimPerfilAlumno
# ---------------------------------------------------------------------------------------
GENEROS = [(1, "Niña"), (2, "Niño")]
# SituacionEdadCodigo -> (texto, orden de presentación 4,1,2,3,8,9)
SITUACIONES_EDAD = {
    4: ("Adelantado", 1),
    1: ("Edad teórica (12 años)", 2),
    2: ("Retraso de 1 año", 3),
    3: ("Retraso de 2 años", 4),
    8: ("No fiable (2010)", 5),
    9: ("Desconocida", 6),
}
# Combinaciones válidas (EdadAnioNatural ?? 0, SituacionEdadCodigo): 7 combinaciones.
COMBINACIONES_EDAD = [(10, 4), (11, 4), (12, 1), (13, 2), (14, 3), (0, 8), (0, 9)]

# ---------------------------------------------------------------------------------------
# §3 DimNivelLogro (umbrales R29: internos del TFG, NO oficiales)
# ---------------------------------------------------------------------------------------
NIVELES = [  # (NivelKey, Nivel, LimiteInferior, LimiteSuperior, NivelOrden)
    (0, "No aplica (subcompetencia)", None, None, 0),
    (1, "Bajo", 0.0, 55.0, 1),
    (2, "Medio-bajo", 55.0, 70.0, 2),
    (3, "Medio-alto", 70.0, 85.0, 3),
    (4, "Alto", 85.0, 100.0, 4),
]

# ---------------------------------------------------------------------------------------
# §3 DimCalidadDato: máscara de bits y reglas de asignación por (CampoOrigen, Anio)
# ---------------------------------------------------------------------------------------
BITS_CALIDAD = [  # (bit, columna de DimCalidadDato, texto para DescripcionCalidad)
    (1, "NoValida", "No válida"),
    (2, "Censurada", "Censurada"),
    (4, "NoComparableSerie", "No comparable en la serie"),
    (8, "NivelNoComparable", "Nivel no comparable"),
]
REGLAS_CALIDAD = [  # (bit, campos afectados, años afectados, regla del informe)
    (1, ["PANG_EE"], [2015], "R25 escala anómala"),
    (2, ["PCAT_EE"], [2018], "R26 suelo artificial"),
    (2, ["PANG", "PANG_CO", "PANG_CE"], [2015], "R26 suelo artificial"),
    (4, ["PANG_CO", "PCAT_CL"], [2011], "R27 techo 99,73"),
    (4, ["PANG_EE"], [2013, 2014, 2015, 2016], "R27 escala no estándar"),
    (4, ["PANG_CO", "PANG_CE"], [2015, 2016], "R27 escalas comprimidas"),
    (4, ["PMAT_NC", "PMAT_EFM", "PMAT_CR"], [2015], "R27 otra escala"),
    (8, ["PANG"], [2015, 2016], "R28 % por nivel no comparable"),
    (8, ["PMAT"], [2015, 2019], "R28 % por nivel no comparable"),
    (8, ["PCAT"], [2018], "R28 % por nivel no comparable"),
    (8, ["PFRAN"], [2022], "R28 % por nivel no comparable"),
]

NOTAS_CONVOCATORIA = {
    2020: "Sin prueba por la COVID-19",
    2021: "Primera convocatoria tras la COVID-19 (se compara con 2019)",
}

TABLAS_MODELO = ["DimAnio", "DimContextoCentro", "DimPerfilAlumno", "DimCompetencia",
                 "DimNivelLogro", "DimCalidadDato", "FactEvaluacion", "FactPuntuacion"]


def _texto_sql(valor: str) -> str:
    """Literal de texto SQL (duplica la comilla simple, p. ej. «Consorci d'Educació»)."""
    return "'" + valor.replace("'", "''") + "'"


def _lista_sql(valores) -> str:
    return ", ".join(_texto_sql(v) if isinstance(v, str) else str(v) for v in valores)


# =======================================================================================
# Paso R01: lectura del CSV
# =======================================================================================
def leer_csv(ruta: Path = RUTA_DATOS) -> pa.Table:
    """Lee el CSV con TODAS las columnas como texto y añade EvaluacionID (R01).

    Equivale a Csv.Document(..., [Delimiter=",", Columns=32, Encoding=65001,
    QuoteStyle=QuoteStyle.Csv]) + Table.PromoteHeaders + Table.AddIndexColumn(1, 1).
    pyarrow conserva el orden de las filas del fichero, de modo que EvaluacionID = 1..N
    es la posición del registro (número de línea del CSV menos 1, por la cabecera).
    Un campo vacío sin comillas se lee como nulo; R05 trata además la cadena vacía.
    """
    tabla = pacsv.read_csv(
        ruta,
        read_options=pacsv.ReadOptions(encoding="utf8"),
        parse_options=pacsv.ParseOptions(delimiter=",", quote_char='"'),
        convert_options=pacsv.ConvertOptions(
            column_types={c: pa.string() for c in COLUMNAS_CSV},
            strings_can_be_null=True, null_values=[""], quoted_strings_can_be_null=False),
    )
    if tabla.column_names != COLUMNAS_CSV:
        raise ValueError(f"Cabecera inesperada: {tabla.column_names}")
    ids = pa.array(np.arange(1, tabla.num_rows + 1, dtype=np.int64))
    return tabla.add_column(0, "EvaluacionID", ids)


# =======================================================================================
# stg_Evaluaciones: tabla ancha con una fila por registro y las reglas R02-R21 aplicadas
# =======================================================================================
def _error_si_hay(con: duckdb.DuckDBPyConnection, sql: str, mensaje: str) -> None:
    """Ejecuta una consulta de comprobación; si devuelve filas, la «actualización» falla."""
    filas = con.execute(sql).fetchall()
    if filas:
        raise ValueError(f"{mensaje}: {filas[:10]}")


def _sql_area() -> str:
    """R13 + R14 + §5.1: texto del área (y año) -> AreaCodigo; NULL si no se reconoce."""
    ramas = [f"WHEN AREA_TERRITORIAL = {_texto_sql(t)} THEN {c}"
             for t, c in CODIGO_AREA_POR_TEXTO.items()]
    return ("CASE WHEN AREA_TERRITORIAL IS NULL THEN 99 "
            "WHEN AREA_TERRITORIAL = 'Barcelona Comarques' AND Anio = 2024 THEN 4 "
            "WHEN AREA_TERRITORIAL = 'Barcelona Comarques' AND Anio <= 2023 THEN 3 "
            + " ".join(ramas) + " END")


def construir_staging(con: duckdb.DuckDBPyConnection, crudo: pa.Table) -> None:
    """Crea en `con` la tabla `stg_evaluaciones` (equivalente a la expresión M stg_Evaluaciones).

    También deja la tabla `crudo` (texto original + EvaluacionID), que los tests usan
    como control negativo de las rotaciones.
    """
    con.register("crudo_arrow", crudo)
    con.execute("CREATE OR REPLACE TABLE crudo AS SELECT * FROM crudo_arrow")
    con.unregister("crudo_arrow")

    # Paso 1 (R05): Text.Trim en todas las columnas y cadena vacía -> null.
    recorte = ", ".join(f'NULLIF(trim("{c}"), \'\') AS "{c}"' for c in COLUMNAS_CSV)
    con.execute(f"CREATE OR REPLACE TEMP TABLE t_texto AS SELECT EvaluacionID, {recorte} FROM crudo")

    # Paso 2 (R02): las 24 puntuaciones se convierten desde el texto ORIGINAL.
    # En M se usa Number.FromText(texto, "es-ES"). Aquí se exige además el patrón estricto
    # del informe (^\d{1,3},\d{2}$): con él, la coma es siempre el separador decimal y no
    # puede haber separador de miles, así que sustituirla por un punto y convertir es
    # exactamente lo mismo que leer con cultura es-ES. Cualquier valor que no cumpla el
    # patrón o quede fuera de [0, 100] hace fallar la carga.
    _error_si_hay(con, " UNION ALL ".join(
        f"""SELECT '{c}' AS campo, "ANY" AS anio, "{c}" AS valor, EvaluacionID FROM t_texto
            WHERE "{c}" IS NOT NULL AND (NOT regexp_full_match("{c}", '\\d{{1,3}},\\d{{2}}')
                  OR TRY_CAST(replace("{c}", ',', '.') AS DECIMAL(5,2)) > 100)"""
        for c in CAMPOS_PUNTUACION), "R02: puntuación no convertible o fuera de [0,100]")
    _error_si_hay(con, """SELECT "ANY", count(*) FROM t_texto
                          WHERE TRY_CAST("ANY" AS BIGINT) IS NULL GROUP BY 1""",
                  "Año (ANY) vacío o no numérico")
    num = ", ".join(f"""CAST(replace("{c}", ',', '.') AS DECIMAL(5,2)) AS "{c}" """
                    for c in CAMPOS_PUNTUACION)
    con.execute(f"""CREATE OR REPLACE TEMP TABLE t_num AS
        SELECT EvaluacionID, CAST("ANY" AS BIGINT) AS Anio, CODI_ALUMNE, GENERE,
               MES_NAIXEMENT, ANY_NAIXEMENT, AREA_TERRITORIAL, NATURALESA, "HÀBITAT", {num}
        FROM t_texto""")

    # Paso 3 (R03, R04): rotaciones. En SQL todas las expresiones de un SELECT leen la fila
    # de ENTRADA, así que la asignación es simultánea y siempre desde las columnas originales
    # (nunca se lee una columna ya sobrescrita).
    con.execute("""CREATE OR REPLACE TEMP TABLE t_rot AS SELECT * REPLACE (
        -- R03 castellano 2017: global real = PCAST_EE, CL real = PCAST, EE real = PCAST_CL
        CASE WHEN Anio = 2017 THEN PCAST_EE ELSE PCAST    END AS PCAST,
        CASE WHEN Anio = 2017 THEN PCAST    ELSE PCAST_CL END AS PCAST_CL,
        CASE WHEN Anio = 2017 THEN PCAST_CL ELSE PCAST_EE END AS PCAST_EE,
        -- R04 francés 2016: global = PFRAN_EE, CO = PFRAN, CE = PFRAN_CO, EE = PFRAN_CE
        CASE WHEN Anio = 2016 THEN PFRAN_EE ELSE PFRAN    END AS PFRAN,
        CASE WHEN Anio = 2016 THEN PFRAN    ELSE PFRAN_CO END AS PFRAN_CO,
        CASE WHEN Anio = 2016 THEN PFRAN_CO ELSE PFRAN_CE END AS PFRAN_CE,
        CASE WHEN Anio = 2016 THEN PFRAN_CE ELSE PFRAN_EE END AS PFRAN_EE
    ) FROM t_num""")

    # Pasos 4-6: códigos de género (R09), naturaleza (R10), hábitat (R11) y área (R13-R14).
    # Un valor no previsto da NULL aquí y la comprobación posterior hace fallar la carga.
    con.execute(f"""CREATE OR REPLACE TEMP TABLE t_cod AS SELECT *,
        CASE WHEN GENERE IN ('H', 'Home') THEN 2 WHEN GENERE IN ('D', 'Dona') THEN 1 END
            AS GeneroCodigo,
        CASE WHEN NATURALESA IN ('Públic', 'Pública') THEN 1
             WHEN NATURALESA IN ('Privat', 'Privada') THEN 2 END AS NaturalezaCodigo,
        CASE WHEN starts_with("HÀBITAT", 'Fins a') THEN 1
             WHEN "HÀBITAT" = 'De 10001 a 100000' THEN 2
             WHEN starts_with("HÀBITAT", 'Més de') THEN 3 END AS HabitatMapeado,
        {_sql_area()} AS AreaCodigo
        FROM t_rot""")
    for col, origen, regla in [("GeneroCodigo", "GENERE", "R09"),
                               ("NaturalezaCodigo", "NATURALESA", "R10"),
                               ("HabitatMapeado", '"HÀBITAT"', "R11"),
                               ("AreaCodigo", "AREA_TERRITORIAL", "R13/R14")]:
        _error_si_hay(con, f"""SELECT Anio, {origen}, count(*) FROM t_cod WHERE {col} IS NULL
                               GROUP BY ALL ORDER BY ALL""",
                      f"{regla}: valores de {origen} sin mapear (Anio, valor, filas)")

    # Paso 8 (R12): el hábitat se sobrescribe DESPUÉS de mapearlo (si el texto fuera
    # desconocido, la carga ya habría fallado). 2010 -> 0 «No fiable»; bloque incoherente
    # de 2014 en Baix Llobregat con «Més de 100000» -> 0.
    # Paso 10 (R16-R19, R21): edad en el año natural y situación de edad.
    con.execute("""CREATE OR REPLACE TEMP TABLE t_perfil AS
        WITH base AS (
            SELECT *,
                CASE WHEN Anio = 2010 THEN 0
                     WHEN Anio = 2014 AND AREA_TERRITORIAL = 'Baix Llobregat'
                          AND "HÀBITAT" = 'Més de 100000' THEN 0
                     ELSE HabitatMapeado END AS HabitatCodigo,
                TRY_CAST(ANY_NAIXEMENT AS BIGINT) AS AnioNac,
                TRY_CAST(MES_NAIXEMENT AS BIGINT) AS MesNac
            FROM t_cod),
        fechas AS (
            SELECT *,
                -- R19: fecha de nacimiento de relleno
                coalesce((CODI_ALUMNE IS NULL AND Anio IN (2016, 2018))
                         OR (Anio = 2016 AND AnioNac = 2001 AND MesNac = 1), FALSE)
                    AS FechaNacimientoDudosa,
                Anio - AnioNac AS EdadBruta        -- R16: NULL si falta el año de nacimiento
            FROM base),
        edad AS (
            SELECT *,
                CASE WHEN Anio = 2010 THEN NULL                       -- R18
                     WHEN FechaNacimientoDudosa THEN NULL             -- R19
                     WHEN EdadBruta BETWEEN 10 AND 14 THEN EdadBruta  -- R17 (fuera -> NULL)
                END AS EdadAnioNatural,
                CASE WHEN MesNac BETWEEN 1 AND 12 THEN MesNac ELSE 0 END AS MesNacimiento
            FROM fechas)
        SELECT *,
            CASE WHEN Anio = 2010 THEN 8                  -- R21, en este orden
                 WHEN EdadAnioNatural IS NULL THEN 9
                 WHEN EdadAnioNatural < 12 THEN 4
                 WHEN EdadAnioNatural = 12 THEN 1
                 WHEN EdadAnioNatural = 13 THEN 2
                 WHEN EdadAnioNatural = 14 THEN 3 END AS SituacionEdadCodigo
        FROM edad""")

    # Pasos 11-12: claves deterministas (sin merges) y TieneCodigoAlumno.
    # CODI_ALUMNE no pasa al modelo (privacidad y memoria); solo se usa aquí.
    puntuaciones = ", ".join(f'"{c}"' for c in CAMPOS_PUNTUACION)
    con.execute(f"""CREATE OR REPLACE TABLE stg_evaluaciones AS SELECT
        EvaluacionID, Anio,
        Anio AS AnioKey,
        CAST(AreaCodigo * 100 + NaturalezaCodigo * 10 + HabitatCodigo AS BIGINT) AS ContextoKey,
        CAST(GeneroCodigo * 100000 + SituacionEdadCodigo * 10000
             + coalesce(EdadAnioNatural, 0) * 100 + MesNacimiento AS BIGINT) AS PerfilKey,
        CODI_ALUMNE IS NOT NULL AS TieneCodigoAlumno,
        CAST(GeneroCodigo AS BIGINT) AS GeneroCodigo,
        CAST(NaturalezaCodigo AS BIGINT) AS NaturalezaCodigo,
        CAST(HabitatCodigo AS BIGINT) AS HabitatCodigo,
        CAST(AreaCodigo AS BIGINT) AS AreaCodigo,
        CAST(EdadAnioNatural AS BIGINT) AS EdadAnioNatural,
        CAST(SituacionEdadCodigo AS BIGINT) AS SituacionEdadCodigo,
        CAST(MesNacimiento AS BIGINT) AS MesNacimiento,
        FechaNacimientoDudosa,
        {puntuaciones}
        FROM t_perfil ORDER BY EvaluacionID""")
    for t in ("t_texto", "t_num", "t_rot", "t_cod", "t_perfil"):
        con.execute(f"DROP TABLE {t}")


# =======================================================================================
# Dimensiones (§3)
# =======================================================================================
def _crear_tabla(con, nombre: str, filas: list[tuple], esquema: pa.Schema) -> None:
    """Crea una tabla DuckDB a partir de filas Python con tipos explícitos (int64, bool...)."""
    columnas = list(zip(*filas))
    tabla = pa.table([pa.array(list(col), type=campo.type)
                      for col, campo in zip(columnas, esquema)], schema=esquema)
    con.register("tmp_arrow", tabla)
    con.execute(f"CREATE OR REPLACE TABLE {nombre} AS SELECT * FROM tmp_arrow")
    con.unregister("tmp_arrow")


def construir_dimensiones(con: duckdb.DuckDBPyConnection) -> None:
    i64, txt, bln, dbl = pa.int64(), pa.string(), pa.bool_(), pa.float64()

    # DimAnio: de 2009 al último año con datos, 2020 incluido (sin datos).
    anios_datos = [r[0] for r in con.execute(
        "SELECT DISTINCT Anio FROM stg_evaluaciones ORDER BY 1").fetchall()]
    ultimo = max(anios_datos)
    indice = {a: i for i, a in enumerate(anios_datos, start=1)}   # 1..N solo con datos
    filas = [(a, a, f"{a - 1}-{a}", a in indice, indice.get(a), a == ultimo,
              NOTAS_CONVOCATORIA.get(a, "")) for a in range(2009, ultimo + 1)]
    _crear_tabla(con, "DimAnio", filas, pa.schema([
        ("AnioKey", i64), ("Anio", i64), ("Curso", txt), ("TieneConvocatoria", bln),
        ("IndiceConvocatoria", i64), ("EsUltimaConvocatoria", bln), ("NotaConvocatoria", txt)]))

    # DimContextoCentro: producto cartesiano áreas (15) x naturaleza (2) x hábitat (4) = 120.
    filas = []
    for area_cod, area, perimetro, serie, ruptura, ruptura_hab in AREAS:
        for nat_cod, nat in NATURALEZAS:
            for hab_cod, hab in HABITATS:
                filas.append((area_cod * 100 + nat_cod * 10 + hab_cod, area_cod, area,
                              perimetro, serie, ruptura, ruptura_hab, nat, nat_cod, hab,
                              hab_cod, 3 if area_cod == 4 else area_cod))   # AreaOrden (contrato §5.1)
    _crear_tabla(con, "DimContextoCentro", filas, pa.schema([
        ("ContextoKey", i64), ("AreaCodigo", i64), ("AreaTerritorial", txt),
        ("AreaPerimetro2025", txt), ("AreaSerieComparable", txt), ("AreaConRupturaSerie", bln),
        ("RupturaHabitat2024", bln), ("Naturaleza", txt), ("NaturalezaCodigo", i64),
        ("Habitat", txt), ("HabitatCodigo", i64), ("AreaOrden", i64)]))

    # DimPerfilAlumno: género (2) x combinaciones edad/situación (7) x mes 0..12 (13) = 182.
    filas = []
    for gen_cod, gen in GENEROS:
        for edad, sit in COMBINACIONES_EDAD:
            for mes in range(13):
                trimestre = f"T{(mes - 1) // 3 + 1}" if mes else "No informado"
                filas.append((gen_cod * 100000 + sit * 10000 + edad * 100 + mes, gen, gen_cod,
                              edad or None, SITUACIONES_EDAD[sit][0], sit,
                              SITUACIONES_EDAD[sit][1], mes or None, trimestre))
    _crear_tabla(con, "DimPerfilAlumno", filas, pa.schema([
        ("PerfilKey", i64), ("Genero", txt), ("GeneroCodigo", i64), ("EdadAnioNatural", i64),
        ("SituacionEdad", txt), ("SituacionEdadCodigo", i64), ("SituacionEdadOrden", i64),
        ("MesNacimiento", i64), ("TrimestreNacimiento", txt)]))

    # DimCompetencia (§5.2).
    _crear_tabla(con, "DimCompetencia", COMPETENCIAS, pa.schema([
        ("CompetenciaKey", i64), ("CampoOrigen", txt), ("CodigoMateria", txt), ("Materia", txt),
        ("MateriaOrden", i64), ("Subcompetencia", txt), ("SubcompetenciaOrden", i64),
        ("EsGlobal", bln), ("AnioInicio", i64), ("AnioFin", i64),
        ("PeriodoDisenoInicio", i64), ("EsInformativa", bln)]))

    # DimNivelLogro (R29).
    _crear_tabla(con, "DimNivelLogro", NIVELES, pa.schema([
        ("NivelKey", i64), ("Nivel", txt), ("LimiteInferior", dbl), ("LimiteSuperior", dbl),
        ("NivelOrden", i64)]))

    # DimCalidadDato: las 16 combinaciones de la máscara de 4 bits.
    filas = []
    for clave in range(16):
        problemas = [texto for bit, _, texto in BITS_CALIDAD if clave & bit]
        filas.append((clave, *[bool(clave & bit) for bit, _, _ in BITS_CALIDAD],
                      "Válido" if clave == 0 else "; ".join(problemas)))
    _crear_tabla(con, "DimCalidadDato", filas, pa.schema(
        [("CalidadKey", i64)] + [(col, bln) for _, col, _ in BITS_CALIDAD]
        + [("DescripcionCalidad", txt)]))


# =======================================================================================
# Hechos (§3)
# =======================================================================================
def _sql_calidad() -> str:
    """CalidadKey = suma de los bits de las reglas R25-R28 que cumple (CampoOrigen, Anio)."""
    terminos = []
    for bit, _, _ in BITS_CALIDAD:
        condiciones = [f"(CampoOrigen IN ({_lista_sql(campos)}) AND Anio IN ({_lista_sql(anios)}))"
                       for b, campos, anios, _ in REGLAS_CALIDAD if b == bit]
        terminos.append(f"CASE WHEN {' OR '.join(condiciones)} THEN {bit} ELSE 0 END")
    return "\n            + ".join(terminos)


def construir_hechos(con: duckdb.DuckDBPyConnection) -> None:
    # FactEvaluacion: una fila por registro. CompetenciasEvaluadas = nº de globales no nulas.
    n_globales = " + ".join(f'CAST("{c}" IS NOT NULL AS BIGINT)' for c in CAMPOS_GLOBALES)
    con.execute(f"""CREATE OR REPLACE TABLE FactEvaluacion AS SELECT
        EvaluacionID, AnioKey, ContextoKey, PerfilKey, TieneCodigoAlumno,
        {n_globales} AS CompetenciasEvaluadas
        FROM stg_evaluaciones ORDER BY EvaluacionID""")

    # FactPuntuacion: despivotado de las 24 columnas (R33). UNPIVOT descarta los nulos,
    # igual que Table.UnpivotOtherColumns en M. La clave de competencia se obtiene por
    # búsqueda en el registro estático CampoOrigen -> CompetenciaKey (sin merge).
    busqueda = " ".join(f"WHEN '{campo}' THEN {clave}" for campo, clave in CLAVE_COMPETENCIA.items())
    globales = _lista_sql(CAMPOS_GLOBALES)
    columnas = ", ".join(f'"{c}"' for c in CAMPOS_PUNTUACION)
    con.execute(f"""CREATE OR REPLACE TABLE FactPuntuacion AS
        WITH largo AS (
            UNPIVOT (SELECT EvaluacionID, Anio, AnioKey, ContextoKey, PerfilKey, {columnas}
                     FROM stg_evaluaciones)
            ON {columnas} INTO NAME CampoOrigen VALUE Puntuacion)
        SELECT
            AnioKey, ContextoKey, PerfilKey,
            CAST(CASE CampoOrigen {busqueda} END AS BIGINT) AS CompetenciaKey,
            -- R29: nivel de logro solo para globales; subcompetencias -> 0 «No aplica»
            CAST(CASE WHEN CampoOrigen NOT IN ({globales}) THEN 0
                      WHEN Puntuacion < 55 THEN 1
                      WHEN Puntuacion < 70 THEN 2
                      WHEN Puntuacion < 85 THEN 3
                      ELSE 4 END AS BIGINT) AS NivelKey,
            CAST({_sql_calidad()} AS BIGINT) AS CalidadKey,
            CAST(Puntuacion AS DECIMAL(5,2)) AS Puntuacion
        FROM largo
        ORDER BY EvaluacionID, CompetenciaKey""")


def escribir_parquet(con: duckdb.DuckDBPyConnection, carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    for tabla in TABLAS_MODELO:
        destino = carpeta / f"{tabla}.parquet"
        con.execute(f"COPY {tabla} TO '{destino}' (FORMAT parquet, COMPRESSION zstd)")


def ejecutar(ruta_datos: Path = RUTA_DATOS, carpeta_salida: Path | None = CARPETA_SALIDA,
             con: duckdb.DuckDBPyConnection | None = None) -> duckdb.DuckDBPyConnection:
    """Ejecuta la ETL completa. Devuelve la conexión con todas las tablas en memoria."""
    con = con or duckdb.connect()
    t0 = time.time()
    construir_staging(con, leer_csv(ruta_datos))
    construir_dimensiones(con)
    construir_hechos(con)
    if carpeta_salida is not None:
        escribir_parquet(con, carpeta_salida)
    print(f"ETL de referencia completada en {time.time() - t0:.1f} s")
    for tabla in TABLAS_MODELO:
        n = con.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0]
        print(f"  {tabla:<18} {n:>12,} filas".replace(",", "."))
    return con


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--datos", type=Path, default=RUTA_DATOS, help="ruta de Datos.csv")
    parser.add_argument("--salida", type=Path, default=CARPETA_SALIDA,
                        help="carpeta de los .parquet (por defecto validacion/salida)")
    args = parser.parse_args(argv)
    ejecutar(args.datos, args.salida)
    print(f"Ficheros escritos en {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
