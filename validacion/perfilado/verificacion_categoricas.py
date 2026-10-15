#!/usr/bin/env python
"""Verificación independiente del perfilado de variables categóricas de Datos.csv.

Script escrito desde cero (no reutiliza perfil_categoricas.py). Carga el CSV con
pyarrow (parser distinto del de DuckDB), numera las filas con su número de línea
real del fichero y ejecuta las consultas con DuckDB. Cada bloque corresponde a un
hallazgo del perfilado (ANY-01, COD-01, ...). Al final hay comprobaciones extra
(EXTRA-*) de problemas que el perfilado podría no haber detectado.

Uso:
    .venv/bin/python validacion/perfilado/verificacion_categoricas.py            # todo
    .venv/bin/python validacion/perfilado/verificacion_categoricas.py HAB FEC    # solo bloques cuyo id empiece así
No modifica Datos.csv.
"""
import csv
import re
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pacsv

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "Datos.csv"

PUNT = [
    "PCAT", "PCAT_CL", "PCAT_EE", "PCAST", "PCAST_CL", "PCAST_EE", "PMAT", "PMAT_NC",
    "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE", "PFRAN", "PFRAN_CO", "PFRAN_CE",
    "PANG_EE", "PFRAN_EE", "PCAT_CO", "PCAST_CO", "PMED", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3",
]
CATEG = ["ANY", "CODI_ALUMNE", "GENERE", "MES_NAIXEMENT", "ANY_NAIXEMENT",
         "AREA_TERRITORIAL", "NATURALESA", "HABITAT"]

con = duckdb.connect()
con.execute("SET threads TO 8")


def titulo(t):
    print("\n" + "=" * 110 + "\n" + t + "\n" + "=" * 110, flush=True)


def q(sql, max_rows=300):
    print("\n-- SQL:\n" + sql.strip())
    df = con.execute(sql).df()
    with pd.option_context("display.max_rows", max_rows, "display.max_columns", 80,
                           "display.width", 260, "display.max_colwidth", 90):
        print(df.head(max_rows).to_string() if len(df) else "(sin filas)")
    print(flush=True)
    return df


def cargar():
    with open(CSV, encoding="utf-8", newline="") as f:
        cab = next(csv.reader(f))
    tipos = {c: pa.string() for c in cab}
    conv = pacsv.ConvertOptions(column_types=tipos, strings_can_be_null=True,
                                null_values=[""], quoted_strings_can_be_null=False)
    t = pacsv.read_csv(CSV, read_options=pacsv.ReadOptions(block_size=64 << 20),
                       parse_options=pacsv.ParseOptions(delimiter=",", quote_char='"'),
                       convert_options=conv)
    t = t.rename_columns(["HABITAT" if c == "HÀBITAT" else c for c in t.column_names])
    t = t.append_column("linea", pa.array(np.arange(2, t.num_rows + 2, dtype=np.int64)))
    con.register("t_arrow", t)
    con.execute("CREATE TABLE d AS SELECT * FROM t_arrow")
    con.unregister("t_arrow")
    num = ",\n".join(f"TRY_CAST(replace({c}, ',', '.') AS DOUBLE) AS n_{c}" for c in PUNT)
    con.execute(f"""
    CREATE TABLE v AS SELECT d.*,
      CAST("ANY" AS INTEGER) AS anio,
      TRY_CAST(ANY_NAIXEMENT AS INTEGER) AS anio_nac,
      TRY_CAST(MES_NAIXEMENT AS INTEGER) AS mes,
      CAST("ANY" AS INTEGER) - TRY_CAST(ANY_NAIXEMENT AS INTEGER) AS edad,
      CASE WHEN GENERE IN ('H','Home') THEN 'H' WHEN GENERE IN ('D','Dona') THEN 'D' END AS gen,
      CASE WHEN NATURALESA IN ('Públic','Pública') THEN 'Pública'
           WHEN NATURALESA IN ('Privat','Privada') THEN 'Privada' END AS nat,
      CASE WHEN HABITAT LIKE 'Fins a %' THEN 1 WHEN HABITAT = 'De 10001 a 100000' THEN 2
           WHEN HABITAT LIKE 'Més de %' THEN 3 END AS hab,
      {num}
    FROM d""")
    print("Filas cargadas con pyarrow:", con.execute("SELECT count(*) FROM d").fetchone()[0])


# --------------------------------------------------------------------------------------------
def b_OTR01_estructura():
    titulo("OTR-01 / estructura en bruto del fichero (lectura línea a línea, sin DuckDB)")
    raw = CSV.read_bytes()
    print("bytes:", len(raw), "| BOM UTF-8:", raw[:3] == b"\xef\xbb\xbf",
          "| saltos \\n:", raw.count(b"\n"), "| \\r:", raw.count(b"\r"),
          "| termina en \\n:", raw.endswith(b"\n"))
    texto = raw.decode("utf-8")
    del raw
    lineas = texto.split("\n")
    if lineas[-1] == "":
        lineas.pop()
    print("líneas (incluida cabecera):", len(lineas))
    distintos32 = 0
    con_comillas_vacias = 0
    no_entrecomillados = 0
    vacios_sin_comillas = 0
    entrecomillado = re.compile(r'"[^"]*"')
    for ln in lineas:
        if '""' in ln:
            con_comillas_vacias += 1
        toks = entrecomillado.sub("Q", ln).split(",")
        no_entrecomillados += sum(1 for tk in toks if tk not in ("Q", ""))
        vacios_sin_comillas += sum(1 for tk in toks if tk == "")
    for campos in csv.reader(lineas):
        if len(campos) != 32:
            distintos32 += 1
    print("líneas con nº de campos != 32:", distintos32)
    print("líneas que contienen \"\" (comillas vacías o escapadas):", con_comillas_vacias)
    print("campos no vacíos sin comillas:", no_entrecomillados)
    print("campos vacíos sin comillas:", vacios_sin_comillas)
    del texto, lineas
    q("""SELECT count(*) AS filas FROM read_csv('%s', all_varchar=true, header=true)""" % CSV)
    q("""
    SELECT "ANY", min(linea) AS primera, max(linea) AS ultima, count(*) AS filas,
           max(linea)-min(linea)+1 = count(*) AS contiguo
    FROM d GROUP BY 1 ORDER BY primera""")
    blancos = " + ".join(
        f"""count(*) FILTER (WHERE "{c}" <> trim("{c}") OR "{c}" LIKE '%  %'
             OR regexp_matches("{c}", '[\\x00-\\x1F\\x7F\\x{{80}}-\\x{{A0}}\\x{{FEFF}}\\x{{200B}}]'))"""
        for c in CATEG)
    q(f"SELECT {blancos} AS valores_con_espacios_o_no_imprimibles FROM d")
    todas_nulas = " AND ".join(f"{c} IS NULL" for c in PUNT)
    q(f"SELECT count(*) AS filas_sin_ninguna_puntuacion FROM d WHERE {todas_nulas}")
    q(f"""SELECT count(*) AS valores_puntuacion_no_numericos FROM v WHERE
       {' OR '.join(f'({c} IS NOT NULL AND n_{c} IS NULL)' for c in PUNT)}""")


def b_ANY01():
    titulo("ANY-01 años")
    q("""SELECT "ANY", count(*) AS filas FROM d GROUP BY 1 ORDER BY 1""")
    q("""SELECT count(*) FILTER (WHERE "ANY" IS NULL) AS nulos,
               count(*) FILTER (WHERE NOT regexp_matches("ANY", '^[0-9]{4}$')) AS no_4_digitos,
               count(DISTINCT "ANY") AS anios
        FROM d""")
    q("""SELECT y AS anio_sin_datos FROM range(2009, 2026) r(y)
        WHERE y NOT IN (SELECT DISTINCT anio FROM v)""")
    q("""
    WITH c AS (SELECT DISTINCT CODI_ALUMNE, anio FROM v WHERE CODI_ALUMNE IS NOT NULL)
    SELECT a.anio AS anio1, b.anio AS anio2, count(*) AS codigos
    FROM c a JOIN c b ON a.CODI_ALUMNE = b.CODI_ALUMNE AND a.anio < b.anio
    GROUP BY ALL ORDER BY ALL""")


def b_COD01():
    titulo("COD-01 CODI_ALUMNE vacío")
    q("""
    SELECT "ANY", count(*) AS filas, count(*) FILTER (WHERE CODI_ALUMNE IS NULL) AS nulos,
           count(*) FILTER (WHERE CODI_ALUMNE = '') AS cadena_vacia,
           round(100.0*count(*) FILTER (WHERE CODI_ALUMNE IS NULL)/count(*), 2) AS pct
    FROM d GROUP BY 1 ORDER BY 1""")
    q("""SELECT count(*) FILTER (WHERE CODI_ALUMNE IS NULL) AS nulos_total,
               round(100.0*count(*) FILTER (WHERE CODI_ALUMNE IS NULL)/count(*), 2) AS pct,
               count(*) FILTER (WHERE CODI_ALUMNE IS NULL AND anio BETWEEN 2009 AND 2015) AS nulos_09_15
        FROM v""")
    q("""SELECT count(*) - count(CODI_ALUMNE) AS nulos_segun_duckdb_read_csv
        FROM read_csv('%s', all_varchar=true, header=true)""" % CSV)
    q("""SELECT "ANY", MES_NAIXEMENT, ANY_NAIXEMENT, GENERE, count(*) AS filas
        FROM d WHERE CODI_ALUMNE IS NULL AND "ANY" IN ('2016','2017','2018','2019')
        GROUP BY ALL ORDER BY ALL""")
    q("SELECT count(DISTINCT linea) = count(*) AS linea_unica FROM d")


def b_COD02():
    titulo("COD-02 duplicados de código dentro de un año")
    q("""SELECT "ANY", coalesce(CODI_ALUMNE, '') AS cod, count(*) AS filas
        FROM d WHERE anio >= 2016 GROUP BY ALL HAVING count(*) > 1 ORDER BY ALL""".replace(
        "FROM d", "FROM v"))
    q("""SELECT "ANY", count(CODI_ALUMNE) AS con_codigo, count(DISTINCT CODI_ALUMNE) AS distintos
        FROM d WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1 ORDER BY 1""")
    df = q("""SELECT * EXCLUDE (anio, anio_nac, mes, edad, gen, nat, hab)
             FROM v WHERE CODI_ALUMNE = '2483875190' ORDER BY linea""")
    cols = [c for c in df.columns if not c.startswith("n_") and c != "linea"]
    dif = [c for c in cols if not (df[c].iloc[0] == df[c].iloc[1]
                                   or (pd.isna(df[c].iloc[0]) and pd.isna(df[c].iloc[1])))]
    print("columnas que difieren:", len(dif), dif)
    print("de ellas puntuaciones:", len([c for c in dif if c in PUNT]))
    q("""SELECT "ANY", count(*) FROM d WHERE CODI_ALUMNE = '2483875190' GROUP BY 1""")


def b_COD03():
    titulo("COD-03 códigos en más de una convocatoria")
    q("""
    WITH c AS (SELECT CODI_ALUMNE, count(DISTINCT anio) AS n_anios, count(*) AS n_filas,
                      max(anio) - min(anio) AS salto, min(anio) a1, max(anio) a2
               FROM v WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1 HAVING count(DISTINCT anio) > 1)
    SELECT n_anios, n_filas, salto, count(*) AS codigos FROM c GROUP BY ALL ORDER BY ALL""")
    q("""
    WITH c AS (SELECT CODI_ALUMNE, min(anio) a1, max(anio) a2
               FROM v WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1 HAVING count(DISTINCT anio) > 1)
    SELECT a1, a2, count(*) AS codigos FROM c GROUP BY ALL ORDER BY ALL""")
    con.execute("""
    CREATE OR REPLACE TABLE pares AS
    WITH c AS (SELECT CODI_ALUMNE FROM v WHERE CODI_ALUMNE IS NOT NULL
               GROUP BY 1 HAVING count(DISTINCT anio) > 1)
    SELECT a.CODI_ALUMNE, a.anio a1, b.anio a2, a.gen g1, b.gen g2, a.GENERE graw1, b.GENERE graw2,
           a.anio_nac an1, b.anio_nac an2, a.mes m1, b.mes m2, a.edad e1, b.edad e2,
           a.AREA_TERRITORIAL ar1, b.AREA_TERRITORIAL ar2, a.nat n1, b.nat n2,
           a.linea l1, b.linea l2
    FROM v a JOIN v b USING (CODI_ALUMNE) JOIN c USING (CODI_ALUMNE)
    WHERE a.anio < b.anio""")
    q("""SELECT count(*) AS pares, count(DISTINCT CODI_ALUMNE) AS codigos,
           count(*) FILTER (WHERE g1 = g2) AS mismo_genero,
           count(*) FILTER (WHERE an1 = an2 AND m1 = m2) AS misma_fecha,
           count(*) FILTER (WHERE g1 = g2 AND an1 = an2 AND m1 = m2) AS genero_y_fecha,
           count(*) FILTER (WHERE ar1 = ar2) AS misma_area,
           count(*) FILTER (WHERE n1 = n2) AS misma_naturaleza,
           count(*) FILTER (WHERE graw1 = graw2) AS mismo_genero_sin_normalizar
        FROM pares""")
    q("SELECT e1, e2, count(*) FROM pares GROUP BY ALL ORDER BY ALL")
    q("""SELECT * FROM pares WHERE NOT (g1 = g2 AND an1 = an2 AND m1 = m2) ORDER BY a1""")
    q("""SELECT (g1 = g2 AND an1 = an2 AND m1 = m2) AS coherente, e1, e2, count(*)
        FROM pares GROUP BY ALL ORDER BY ALL""")
    titulo("COD-03 simulación de la regla propuesta (merge con ANY-1) en pandas")
    coded = con.execute("""SELECT linea, CODI_ALUMNE AS CodiAlumne, anio AS Anio, gen AS GeneroCod,
                                  anio_nac AS AnioNacimiento, mes AS MesNacimiento
                           FROM v WHERE CODI_ALUMNE IS NOT NULL""").df()
    prev = coded[["CodiAlumne", "Anio", "GeneroCod", "AnioNacimiento", "MesNacimiento"]].copy()
    prev["Anio"] += 1
    m = coded.merge(prev, on=["CodiAlumne", "Anio"], how="left", suffixes=("", "Ant"),
                    indicator=True)
    print("filas con código:", len(coded), "| filas tras merge:", len(m),
          "| filas duplicadas por el merge:", len(m) - len(coded))
    m["CodigoEnConvocatoriaAnterior"] = m["_merge"].eq("both")
    rep = (m.CodigoEnConvocatoriaAnterior & m.GeneroCod.eq(m.GeneroCodAnt)
           & m.AnioNacimiento.eq(m.AnioNacimientoAnt) & m.MesNacimiento.eq(m.MesNacimientoAnt))
    print("CodigoEnConvocatoriaAnterior:", int(m.CodigoEnConvocatoriaAnterior.sum()),
          "| RepeticionProbable:", int(rep.sum()))
    dup_prev = prev.duplicated(["CodiAlumne", "Anio"], keep=False).sum()
    print("claves (código, ANY+1) duplicadas en 'prev':", int(dup_prev))


def b_COD04():
    titulo("COD-04 formato de CODI_ALUMNE")
    q("""SELECT count(*) FILTER (WHERE NOT regexp_matches(CODI_ALUMNE, '^[0-9]+$')) AS no_digitos,
               min(length(CODI_ALUMNE)) AS lmin, max(length(CODI_ALUMNE)) AS lmax,
               count(*) FILTER (WHERE CODI_ALUMNE LIKE '0%') AS empieza_por_0,
               count(DISTINCT CODI_ALUMNE) AS distintos_texto,
               count(DISTINCT TRY_CAST(CODI_ALUMNE AS BIGINT)) AS distintos_bigint
        FROM d WHERE CODI_ALUMNE IS NOT NULL""")
    q("""SELECT "ANY", count(*) AS con_codigo,
               round(100.0*count(*) FILTER (WHERE length(CODI_ALUMNE)=11)/count(*), 2) AS pct_11,
               round(100.0*count(*) FILTER (WHERE length(CODI_ALUMNE)=10)/count(*), 2) AS pct_10,
               round(100.0*count(*) FILTER (WHERE length(CODI_ALUMNE)<=9)/count(*), 2) AS pct_le9,
               min(TRY_CAST(CODI_ALUMNE AS BIGINT)) AS minimo, max(TRY_CAST(CODI_ALUMNE AS BIGINT)) AS maximo
        FROM d WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1 ORDER BY 1""")
    q("""SELECT count(*) AS codigos_2024_2025,
               count(*) FILTER (WHERE g1=g2 AND an1=an2 AND m1=m2) AS coinciden,
               list(DISTINCT length(CODI_ALUMNE)) AS longitudes
        FROM pares WHERE a1 = 2024 AND a2 = 2025""")
    q("""SELECT count(*) AS filas_2025 FROM d WHERE "ANY" = '2025'""")


def b_GEN01():
    titulo("GEN-01 GENERE")
    q("""PIVOT (SELECT "ANY", coalesce(GENERE, '<NULL>') AS g FROM d) ON g USING count(*)
        GROUP BY "ANY" ORDER BY "ANY" """)
    q("""SELECT count(DISTINCT GENERE) AS distintos_bruto,
               count(*) FILTER (WHERE GENERE IS NULL) AS nulos,
               count(*) FILTER (WHERE gen IS NULL) AS sin_mapear,
               count(DISTINCT gen) AS distintos_tras_regla FROM v""")


def b_NAT01():
    titulo("NAT-01 NATURALESA")
    q("""PIVOT (SELECT "ANY", coalesce(NATURALESA, '<NULL>') AS n FROM d) ON n USING count(*)
        GROUP BY "ANY" ORDER BY "ANY" """)
    q("""SELECT count(*) FILTER (WHERE nat IS NULL) AS sin_mapear,
               count(*) FILTER (WHERE NATURALESA IN ('Pública','Privada')) AS etiqueta_nueva
        FROM v""")


def b_HAB():
    titulo("HAB-01/02 valores de HÀBITAT")
    q("""SELECT count(DISTINCT HABITAT) AS distintos_bruto, count(*) FILTER (WHERE HABITAT IS NULL) AS nulos,
               count(*) FILTER (WHERE hab IS NULL) AS sin_mapear FROM v""")
    q("""SELECT CASE WHEN regexp_matches(HABITAT, '^Fins a [0-9]+$') AND HABITAT <> 'Fins a 10000'
                    THEN 'Fins a N (N<>10000)' ELSE HABITAT END AS valor,
               "ANY", count(*) AS filas
        FROM d GROUP BY ALL ORDER BY valor, "ANY" """)
    con.execute("""CREATE OR REPLACE TABLE fins AS
        SELECT linea, anio, AREA_TERRITORIAL, nat, CODI_ALUMNE,
               TRY_CAST(regexp_extract(HABITAT, '^Fins a ([0-9]+)$', 1) AS BIGINT) AS n
        FROM v WHERE HABITAT LIKE 'Fins a%'""")
    q("""SELECT anio, count(*) AS filas_fins, count(*) FILTER (WHERE n = 10000) AS n10000,
               count(*) FILTER (WHERE n <> 10000) AS n_otro, min(n) FILTER (WHERE n<>10000) AS nmin,
               max(n) AS nmax, count(DISTINCT n) FILTER (WHERE n<>10000) AS n_distintos,
               count(*) FILTER (WHERE n IS NULL) AS n_no_numerico
        FROM fins GROUP BY 1 ORDER BY 1""")
    q("""SELECT linea, anio, AREA_TERRITORIAL, nat FROM fins WHERE anio = 2024 AND n = 10000""")
    q("""WITH s AS (SELECT n FROM fins WHERE anio = 2024 AND n > 10000)
        SELECT count(*) AS filas, count(DISTINCT n) AS distintos, max(n) - min(n) + 1 AS rango,
               (max(n) - min(n) + 1) - count(DISTINCT n) AS huecos FROM s""")
    q("""WITH s AS (SELECT linea, n, n - lag(n) OVER (ORDER BY linea) AS dn
                   FROM fins WHERE anio = 2024 AND n > 10000)
        SELECT round(corr(linea, n), 3) AS corr_linea_n,
               count(*) FILTER (WHERE dn > 0) AS subidas, count(*) FILTER (WHERE dn < 0) AS bajadas
        FROM s""")
    q("""WITH s AS (SELECT n - lag(n) OVER (ORDER BY linea) AS dn FROM fins WHERE anio = 2024)
        SELECT count(*) FILTER (WHERE dn > 0) AS subidas_incl_10000,
               count(*) FILTER (WHERE dn < 0) AS bajadas_incl_10000 FROM s""")
    q("""SELECT nat, count(*) FROM fins WHERE anio = 2024 AND n > 10000 GROUP BY 1 ORDER BY 1""")
    q("""SELECT round(corr(f.n, TRY_CAST(v.CODI_ALUMNE AS DOUBLE)), 3) AS corr_n_codigo,
               round(corr(f.n, v.n_PCAT), 3) AS corr_n_pcat, round(corr(f.n, v.n_PMAT), 3) AS corr_n_pmat,
               round(corr(f.n, v.anio_nac * 12 + v.mes), 3) AS corr_n_fecha_nac
        FROM fins f JOIN v USING (linea) WHERE f.anio = 2024 AND f.n > 10000""")
    q("""SELECT round(100.0 * count(*) FILTER (WHERE n > 10000) / count(*), 3) AS pct_afectado_2024
        FROM fins WHERE anio = 2024""")
    titulo("HAB-01 extra: ¿el orden de N agrupa por área/naturaleza? (indicaría orden de la hoja al arrastrar)")
    q("""WITH s AS (SELECT n, AREA_TERRITORIAL a, nat, CODI_ALUMNE c,
                          lag(AREA_TERRITORIAL) OVER (ORDER BY n) a_prev,
                          lag(nat) OVER (ORDER BY n) nat_prev FROM fins WHERE anio = 2024)
        SELECT count(*) FILTER (WHERE a <> a_prev) AS cambios_area_en_orden_n,
               count(*) FILTER (WHERE nat <> nat_prev) AS cambios_nat_en_orden_n FROM s""")
    q("""SELECT AREA_TERRITORIAL, nat, min(n) AS nmin, max(n) AS nmax, count(*) AS filas,
               max(n)-min(n)+1 = count(*) AS bloque_contiguo
        FROM fins WHERE anio = 2024 GROUP BY ALL ORDER BY nmin""")
    titulo("HAB-01 % 'Fins a' por área y peso en Cataluña")
    q("""PIVOT (SELECT anio, coalesce(AREA_TERRITORIAL,'<NULL>') AS area, (hab = 1)::INT AS es1
               FROM v WHERE anio >= 2021)
        ON anio USING round(100.0 * avg(es1), 1)
        GROUP BY area ORDER BY area""")
    q("""SELECT anio, count(*) AS filas,
               count(*) FILTER (WHERE hab=1) AS h1, count(*) FILTER (WHERE hab=2) AS h2,
               count(*) FILTER (WHERE hab=3) AS h3,
               round(100.0*count(*) FILTER (WHERE hab=1)/count(*), 2) AS pct1,
               round(100.0*count(*) FILTER (WHERE hab=2)/count(*), 2) AS pct2,
               round(100.0*count(*) FILTER (WHERE hab=3)/count(*), 2) AS pct3
        FROM v GROUP BY 1 ORDER BY 1""")
    q("""SELECT "ANY", count(*) FROM d WHERE HABITAT = 'Més de 100001' GROUP BY 1 ORDER BY 1""")
    titulo("HAB-03 combinaciones área x hábitat raras")
    q("""WITH c AS (SELECT AREA_TERRITORIAL, hab, anio, count(*) AS filas FROM v
                   WHERE AREA_TERRITORIAL IS NOT NULL GROUP BY ALL),
             r AS (SELECT AREA_TERRITORIAL, hab, count(DISTINCT anio) AS n_anios,
                          string_agg(anio || ':' || filas, ', ' ORDER BY anio) AS detalle
                   FROM c GROUP BY ALL)
        SELECT * FROM r WHERE n_anios <= 4 ORDER BY AREA_TERRITORIAL, hab""")
    q("""SELECT AREA_TERRITORIAL, hab, string_agg(anio || ':' || filas, ', ' ORDER BY anio) AS por_anio
        FROM (SELECT AREA_TERRITORIAL, hab, anio, count(*) filas FROM v GROUP BY ALL)
        GROUP BY ALL ORDER BY ALL""")
    q("""SELECT anio, AREA_TERRITORIAL, nat,
               count(*) FILTER (WHERE hab=1) h1, count(*) FILTER (WHERE hab=2) h2,
               count(*) FILTER (WHERE hab=3) h3
        FROM v WHERE anio IN (2009, 2010, 2011)
          AND AREA_TERRITORIAL IN ('Consorci d''Educació de Barcelona','Catalunya Central',
                                   'Terres de l''Ebre','Baix Llobregat')
        GROUP BY ALL ORDER BY AREA_TERRITORIAL, nat, anio""")
    q("""WITH f AS (SELECT *, (AREA_TERRITORIAL = 'Consorci d''Educació de Barcelona' AND hab IN (1,2))
                            OR (AREA_TERRITORIAL IN ('Catalunya Central','Terres de l''Ebre','Baix Llobregat')
                                AND hab = 3) AS incoh FROM v)
        SELECT anio, count(*) AS filas, count(*) FILTER (WHERE incoh) AS incoherentes,
               round(100.0*count(*) FILTER (WHERE incoh)/count(*), 2) AS pct
        FROM f GROUP BY 1 HAVING count(*) FILTER (WHERE incoh) > 0 ORDER BY 1""")
    titulo("HAB-03 extra: naturaleza x hábitat y relación hábitat-puntuación por año")
    q("""SELECT anio,
               round(100.0*count(*) FILTER (WHERE nat='Privada' AND hab=3)/count(*) FILTER (WHERE hab=3),1) AS pct_priv_en_h3,
               round(100.0*count(*) FILTER (WHERE nat='Privada' AND hab=1)/count(*) FILTER (WHERE hab=1),1) AS pct_priv_en_h1,
               round(avg(n_PMAT) FILTER (WHERE hab=3) - avg(n_PMAT) FILTER (WHERE hab=1), 2) AS pmat_h3_menos_h1,
               round(avg(n_PCAT) FILTER (WHERE hab=1) - avg(n_PCAT) FILTER (WHERE hab=3), 2) AS pcat_h1_menos_h3,
               round(avg(n_PCAST) FILTER (WHERE hab=3) - avg(n_PCAST) FILTER (WHERE hab=1), 2) AS pcast_h3_menos_h1
        FROM v GROUP BY 1 ORDER BY 1""")
    titulo("HAB-03 extra: alcance real en 2010 (cota inferior por distancia de variación total)")
    q("""WITH c AS (SELECT anio, AREA_TERRITORIAL a, hab, count(*) n FROM v WHERE anio IN (2009,2010,2011) GROUP BY ALL),
             t AS (SELECT anio, a, sum(n) na FROM c GROUP BY ALL),
             p AS (SELECT c.a, c.hab, avg(c.n / t.na) AS p FROM c JOIN t USING (anio, a)
                   WHERE anio IN (2009, 2011) GROUP BY ALL),
             e AS (SELECT t.a, p.hab, t.na * p.p AS esperado FROM t JOIN p USING (a) WHERE t.anio = 2010),
             o AS (SELECT a, hab, n FROM c WHERE anio = 2010)
        SELECT round(0.5 * sum(abs(coalesce(o.n,0) - coalesce(e.esperado,0)))) AS filas_minimas_mal_asignadas,
               round(100.0 * 0.5 * sum(abs(coalesce(o.n,0) - coalesce(e.esperado,0))) / 59329, 1) AS pct_2010
        FROM e FULL JOIN o USING (a, hab)""")
    q("""WITH s AS (SELECT anio,
            AREA_TERRITORIAL <> lag(AREA_TERRITORIAL) OVER w AS c_area,
            NATURALESA <> lag(NATURALESA) OVER w AS c_nat,
            HABITAT <> lag(HABITAT) OVER w AS c_hab,
            ANY_NAIXEMENT IS DISTINCT FROM lag(ANY_NAIXEMENT) OVER w AS c_anac
          FROM v WINDOW w AS (PARTITION BY anio ORDER BY linea))
        SELECT anio, count(*) FILTER (WHERE c_area) AS cambios_area, count(*) FILTER (WHERE c_nat) AS cambios_nat,
               count(*) FILTER (WHERE c_hab) AS cambios_hab, count(*) FILTER (WHERE c_anac) AS cambios_anio_nac
        FROM s WHERE anio <= 2012 GROUP BY 1 ORDER BY 1""")
    q("""WITH t AS (SELECT ntile(10) OVER (ORDER BY linea) AS decil, * FROM v WHERE anio = 2010)
        SELECT decil, min(linea) AS desde, max(linea) AS hasta,
          round(100.0*count(*) FILTER (WHERE AREA_TERRITORIAL='Consorci d''Educació de Barcelona' AND hab<>3)/
                nullif(count(*) FILTER (WHERE AREA_TERRITORIAL='Consorci d''Educació de Barcelona'),0),1) AS pct_consorci_no_mas_de,
          round(100.0*count(*) FILTER (WHERE AREA_TERRITORIAL IN ('Baix Llobregat','Catalunya Central','Terres de l''Ebre') AND hab=3)/
                nullif(count(*) FILTER (WHERE AREA_TERRITORIAL IN ('Baix Llobregat','Catalunya Central','Terres de l''Ebre')),0),1) AS pct_bll_cc_te_mas_de,
          round(avg(n_PMAT) FILTER (WHERE edad=12) - avg(n_PMAT) FILTER (WHERE edad=13),2) AS pmat_12_menos_13
        FROM t GROUP BY 1 ORDER BY 1""")
    titulo("HAB-04 reclasificación de hábitat en 2024 por área")
    q("""SELECT AREA_TERRITORIAL, anio, count(*) filas, count(*) FILTER (WHERE hab=1) h1,
               count(*) FILTER (WHERE hab=2) h2, count(*) FILTER (WHERE hab=3) h3,
               round(100.0*count(*) FILTER (WHERE hab=1)/count(*),1) p1,
               round(100.0*count(*) FILTER (WHERE hab=2)/count(*),1) p2,
               round(100.0*count(*) FILTER (WHERE hab=3)/count(*),1) p3
        FROM v WHERE anio >= 2021 GROUP BY ALL ORDER BY AREA_TERRITORIAL, anio""")
    q("""SELECT count(*) AS filas_girona_maresme_2024_2025 FROM d
        WHERE AREA_TERRITORIAL IN ('Girona','Maresme - Vallès Oriental') AND "ANY" IN ('2024','2025')""")
    q("""SELECT count(*) AS filas_girona_maresme_todos FROM d
        WHERE AREA_TERRITORIAL IN ('Girona','Maresme - Vallès Oriental')""")


def b_ARE():
    titulo("ARE-01 área vacía")
    q("""SELECT linea, "ANY", CODI_ALUMNE, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT, NATURALESA, HABITAT
        FROM d WHERE AREA_TERRITORIAL IS NULL OR trim(AREA_TERRITORIAL) = ''""")
    q("""SELECT "ANY", AREA_TERRITORIAL FROM d WHERE CODI_ALUMNE =
           (SELECT CODI_ALUMNE FROM d WHERE AREA_TERRITORIAL IS NULL)""")
    titulo("ARE-02 áreas por año")
    q("""PIVOT (SELECT anio, coalesce(AREA_TERRITORIAL,'<NULL>') AS area FROM v WHERE anio >= 2019)
        ON anio USING count(*) GROUP BY area ORDER BY area""")
    q("""SELECT AREA_TERRITORIAL, min(anio) AS desde, max(anio) AS hasta, count(DISTINCT anio) AS n_anios
        FROM v GROUP BY 1 ORDER BY 1""")
    estables = ("'Baix Llobregat','Consorci d''Educació de Barcelona','Girona',"
                "'Maresme - Vallès Oriental','Terres de l''Ebre','Vallès Occidental'")
    con.execute(f"""CREATE OR REPLACE TABLE ar AS
        SELECT anio,
          count(*) AS cat,
          count(*) FILTER (WHERE AREA_TERRITORIAL IN ({estables})) AS est,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Lleida') AS lle,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Alt Pirineu i Aran') AS apa,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Barcelona Comarques') AS bc,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Barcelonès') AS bcs,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Penedès') AS pen,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Tarragona') AS tar,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Catalunya Central') AS cc,
          count(*) FILTER (WHERE AREA_TERRITORIAL = 'Consorci d''Educació de Barcelona') AS cons
        FROM v WHERE anio >= 2023 GROUP BY 1""")
    q("SELECT * FROM ar ORDER BY anio")
    q("""SELECT a.anio, round(a.est / b.est, 4) AS factor_estables, round(a.cat / b.cat, 4) AS factor_cat,
               a.lle + a.apa AS lle_apa, round((a.lle + a.apa) / b.lle, 4) AS ratio_lle_apa,
               round(b.lle * a.est / b.est - a.lle) AS faltan_lle,
               round(b.bc * a.est / b.est - a.bc) AS faltan_bc,
               round(b.tar * a.est / b.est - a.tar) AS faltan_tar,
               round(b.cc * a.est / b.est - a.cc) AS faltan_cc,
               round(b.cons * a.est / b.est - a.cons) AS faltan_cons,
               a.bc + a.pen AS bc_mas_pen,
               (a.bc + a.bcs + a.pen + a.tar + a.cc) AS grupo, round((a.bc + a.bcs + a.pen + a.tar + a.cc) /
                   (b.bc + b.bcs + b.pen + b.tar + b.cc), 4) AS ratio_grupo,
               round(a.bcs / b.bc, 4) AS ratio_bcs_bc
        FROM ar a JOIN ar b ON a.anio = b.anio + 1 ORDER BY 1""")
    q(f"""WITH x AS (SELECT anio, nat, count(*) FILTER (WHERE AREA_TERRITORIAL IN ({estables})) est,
                           count(*) FILTER (WHERE AREA_TERRITORIAL IN ('Barcelona Comarques','Tarragona','Catalunya Central')) grp,
                           count(*) FILTER (WHERE AREA_TERRITORIAL = 'Penedès') pen
                    FROM v WHERE anio IN (2023, 2024) GROUP BY ALL)
         SELECT a.nat, round(b.grp * a.est / b.est - a.grp) AS faltan, a.pen
         FROM x a JOIN x b ON a.nat = b.nat AND a.anio = 2024 AND b.anio = 2023""")
    q("""SELECT AREA_TERRITORIAL, anio, nat, hab, count(*) FROM v
        WHERE (AREA_TERRITORIAL = 'Barcelona Comarques' AND anio = 2024)
           OR (AREA_TERRITORIAL = 'Barcelonès' AND anio = 2025)
        GROUP BY ALL ORDER BY nat, hab, anio""")
    q("""SELECT count(*) FILTER (WHERE hab = 3) AS penedes_mes_de FROM v WHERE AREA_TERRITORIAL = 'Penedès'""")
    q("""WITH c AS (SELECT CODI_ALUMNE, anio, AREA_TERRITORIAL a FROM v WHERE CODI_ALUMNE IS NOT NULL AND anio >= 2023)
        SELECT x.anio a1, x.a area1, y.anio a2, y.a area2, count(*) AS codigos
        FROM c x JOIN c y ON x.CODI_ALUMNE = y.CODI_ALUMNE AND y.anio = x.anio + 1
        WHERE x.a IS DISTINCT FROM y.a GROUP BY ALL ORDER BY ALL""")
    q("""SELECT count(*) AS filas_bc_bcs_pen_tar_cc_lle_apa_todos_anios FROM d
        WHERE AREA_TERRITORIAL IN ('Barcelona Comarques','Barcelonès','Penedès','Tarragona',
                                   'Catalunya Central','Lleida','Alt Pirineu i Aran')""")
    q("""SELECT count(*) AS filas_grupo_2023_2025 FROM v WHERE anio >= 2023 AND AREA_TERRITORIAL IN
           ('Barcelona Comarques','Barcelonès','Penedès','Tarragona','Catalunya Central','Lleida','Alt Pirineu i Aran')""")
    q("""SELECT count(*) AS filas_grupo_2024_2025 FROM v WHERE anio >= 2024 AND AREA_TERRITORIAL IN
           ('Barcelona Comarques','Barcelonès','Penedès','Tarragona','Catalunya Central','Lleida','Alt Pirineu i Aran')""")


def b_FEC():
    titulo("FEC-01 nulos de fecha de nacimiento")
    q("""SELECT "ANY", count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL) AS anio_nulo,
               count(*) FILTER (WHERE MES_NAIXEMENT IS NULL) AS mes_nulo,
               count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL AND MES_NAIXEMENT IS NOT NULL) AS anio_nulo_mes_ok,
               count(*) FILTER (WHERE ANY_NAIXEMENT IS NOT NULL AND MES_NAIXEMENT IS NULL) AS mes_nulo_anio_ok
        FROM d GROUP BY 1 HAVING anio_nulo + mes_nulo > 0 ORDER BY 1""")
    q("""SELECT count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL) AS anio_nulo,
               count(*) FILTER (WHERE MES_NAIXEMENT IS NULL) AS mes_nulo,
               count(*) FILTER (WHERE ANY_NAIXEMENT IS NULL AND MES_NAIXEMENT IS NOT NULL) AS anio_nulo_mes_ok
        FROM d""")
    q("""SELECT list(DISTINCT MES_NAIXEMENT ORDER BY MES_NAIXEMENT) AS valores_mes,
               count(*) FILTER (WHERE ANY_NAIXEMENT IS NOT NULL AND NOT regexp_matches(ANY_NAIXEMENT, '^[0-9]{4}$')) AS anio_mal,
               min(ANY_NAIXEMENT) AS min_anio, max(ANY_NAIXEMENT) AS max_anio FROM d""")
    titulo("FEC-02 edades")
    q("SELECT edad, count(*) FROM v WHERE edad IS NOT NULL AND edad NOT BETWEEN 10 AND 14 GROUP BY 1 ORDER BY 1")
    q("""SELECT anio, count(*) AS fuera_rango, count(*) FILTER (WHERE edad < 10) AS menor10,
               count(*) FILTER (WHERE edad > 14) AS mayor14,
               count(*) FILTER (WHERE anio_nac = 2001 AND mes = 1) AS nac_1_2001,
               count(*) FILTER (WHERE anio_nac = 2001 AND mes = 1 AND CODI_ALUMNE IS NOT NULL) AS nac_1_2001_con_codigo
        FROM v WHERE edad NOT BETWEEN 10 AND 14 GROUP BY 1 ORDER BY 1""")
    q("""SELECT anio_nac, mes, CODI_ALUMNE IS NULL AS sin_codigo, count(*) FROM v WHERE anio = 2016 AND anio_nac <= 2002
        GROUP BY ALL ORDER BY ALL""")
    q("""SELECT anio_nac, mes, count(*) FROM v WHERE anio = 2016 AND CODI_ALUMNE IS NULL GROUP BY ALL ORDER BY ALL""")
    q("""SELECT anio_nac, mes, count(*) FROM v WHERE anio = 2018 AND CODI_ALUMNE IS NULL GROUP BY ALL ORDER BY ALL""")
    q("""SELECT anio, mode(edad) AS moda FROM v GROUP BY 1 HAVING mode(edad) <> 12 ORDER BY 1""")
    q("""WITH r AS (SELECT CASE WHEN anio = 2010 THEN NULL
                               WHEN edad BETWEEN 10 AND 14 THEN edad END AS edad_prueba FROM v)
        SELECT edad_prueba, count(*) FROM r GROUP BY 1 ORDER BY 1 NULLS LAST""")
    q("""SELECT count(*) FILTER (WHERE edad IS NULL) AS sin_edad,
               count(*) FILTER (WHERE edad NOT BETWEEN 10 AND 14) AS fuera_rango,
               count(*) FILTER (WHERE anio = 2010 AND edad BETWEEN 10 AND 14) AS validas_2010,
               count(*) FILTER (WHERE anio = 2010) AS filas_2010,
               count(*) FILTER (WHERE anio = 2010 AND edad NOT BETWEEN 10 AND 14) AS fuera_2010,
               count(*) FILTER (WHERE anio = 2010 AND edad IS NULL) AS nulas_2010
        FROM v""")
    titulo("FEC-03 2010: relación edad-rendimiento")
    q("""SELECT anio,
           round(avg(n_PMAT) FILTER (WHERE edad=12) - avg(n_PMAT) FILTER (WHERE edad=13), 2) AS pmat_12_13,
           round(avg(n_PCAT) FILTER (WHERE edad=12) - avg(n_PCAT) FILTER (WHERE edad=13), 2) AS pcat_12_13,
           round(100.0*count(*) FILTER (WHERE edad>12)/count(edad), 2) AS pct_mayor12_sobre_conedad,
           round(100.0*count(*) FILTER (WHERE edad>12)/count(*), 2) AS pct_mayor12_sobre_todas,
           round(100.0*count(*) FILTER (WHERE edad>12 AND gen='H')/count(edad) FILTER (WHERE gen='H'), 2) AS pct_h,
           round(100.0*count(*) FILTER (WHERE edad>12 AND gen='D')/count(edad) FILTER (WHERE gen='D'), 2) AS pct_d,
           round(100.0*count(*) FILTER (WHERE edad>12 AND nat='Pública')/count(edad) FILTER (WHERE nat='Pública'), 2) AS pct_pub,
           round(100.0*count(*) FILTER (WHERE edad>12 AND nat='Privada')/count(edad) FILTER (WHERE nat='Privada'), 2) AS pct_priv,
           round(avg(n_PMAT) FILTER (WHERE mes BETWEEN 1 AND 3) - avg(n_PMAT) FILTER (WHERE mes BETWEEN 10 AND 12), 2) AS pmat_t1_t4,
           round(avg(n_PMAT) FILTER (WHERE nat='Privada') - avg(n_PMAT) FILTER (WHERE nat='Pública'), 2) AS pmat_priv_pub
        FROM v GROUP BY 1 ORDER BY 1""")
    q("""SELECT anio, round(avg(n_PMAT) FILTER (WHERE mes BETWEEN 1 AND 3 AND edad = 12)
                            - avg(n_PMAT) FILTER (WHERE mes BETWEEN 10 AND 12 AND edad = 12), 2) AS pmat_t1_t4_edad12
        FROM v GROUP BY 1 ORDER BY 1""")
    q("""SELECT anio, min(d) AS min_dif_area, max(d) AS max_dif_area FROM (
           SELECT anio, AREA_TERRITORIAL,
                  round(avg(n_PMAT) FILTER (WHERE edad=12) - avg(n_PMAT) FILTER (WHERE edad=13), 2) AS d
           FROM v WHERE anio IN (2009, 2010, 2011) GROUP BY ALL) GROUP BY 1 ORDER BY 1""")
    titulo("FEC-04 exceso de nacidos en enero")
    q("""WITH m AS (SELECT anio, mes, count(*) AS n FROM v WHERE mes IS NOT NULL GROUP BY ALL),
             r AS (SELECT anio,
                     max(n) FILTER (WHERE mes = 1) AS enero,
                     avg(n) FILTER (WHERE mes IN (1,3,5,7,8,10,12)) AS media31_con_enero,
                     avg(n) FILTER (WHERE mes IN (3,5,7,8,10,12)) AS media31_sin_enero
                   FROM m GROUP BY 1)
        SELECT anio, enero, round(media31_sin_enero, 1) AS m31_sin_ene,
               round(100.0*(enero/media31_sin_enero - 1), 1) AS pct_exceso_sin,
               round(enero - media31_sin_enero) AS exceso_sin,
               round(100.0*(enero/media31_con_enero - 1), 1) AS pct_exceso_con,
               round(enero - media31_con_enero) AS exceso_con
        FROM r ORDER BY 1""")
    q("""SELECT count(*) AS filas_enero_en_2009_2012_2015 FROM v
        WHERE mes = 1 AND anio IN (2009, 2012, 2013, 2014, 2015)""")


def b_EXTRA():
    titulo("EXTRA-1 filas completamente idénticas (todas las columnas salvo la línea)")
    cols = ", ".join(f'"{c}"' for c in
                     ["ANY", "CODI_ALUMNE"] + PUNT + ["GENERE", "MES_NAIXEMENT", "ANY_NAIXEMENT",
                                                     "AREA_TERRITORIAL", "NATURALESA", "HABITAT"])
    q(f"""WITH g AS (SELECT {cols}, count(*) AS n FROM d GROUP BY ALL HAVING count(*) > 1)
         SELECT "ANY", CODI_ALUMNE IS NULL AS sin_codigo, count(*) AS grupos, sum(n) AS filas,
                sum(n) - count(*) AS filas_sobrantes
         FROM g GROUP BY ALL ORDER BY ALL""")
    q(f"""WITH g AS (SELECT {cols}, count(*) AS n FROM d GROUP BY ALL HAVING count(*) > 1)
         SELECT "ANY", n, (SELECT count(*) FROM (SELECT unnest([{', '.join(PUNT)}]) x) WHERE x IS NOT NULL) AS punt_informadas,
                count(*) AS grupos
         FROM g GROUP BY ALL ORDER BY "ANY", punt_informadas, n""")
    q(f"""WITH g AS (SELECT {cols}, count(*) AS n, list(linea ORDER BY linea) AS lineas FROM d GROUP BY ALL HAVING count(*) > 1)
         SELECT "ANY", lineas, PCAT, PCAST, PMAT, PANG, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT,
                AREA_TERRITORIAL, NATURALESA, HABITAT FROM g ORDER BY 1, 2""")
    titulo("EXTRA-2 relación GENERE-puntuación por año (¿2010 también desordenado?)")
    q("""SELECT anio,
           round(avg(n_PCAT) FILTER (WHERE gen='D') - avg(n_PCAT) FILTER (WHERE gen='H'), 2) AS pcat_d_menos_h,
           round(avg(n_PCAST) FILTER (WHERE gen='D') - avg(n_PCAST) FILTER (WHERE gen='H'), 2) AS pcast_d_menos_h,
           round(avg(n_PMAT) FILTER (WHERE gen='H') - avg(n_PMAT) FILTER (WHERE gen='D'), 2) AS pmat_h_menos_d,
           round(100.0*count(*) FILTER (WHERE gen='D')/count(*), 2) AS pct_d
        FROM v GROUP BY 1 ORDER BY 1""")
    titulo("EXTRA-3 relación ÁREA-puntuación en 2009-2011 (¿el área de 2010 es fiable?)")
    q("""PIVOT (SELECT anio, AREA_TERRITORIAL AS area, n_PMAT FROM v WHERE anio BETWEEN 2008 AND 2012)
        ON anio USING round(avg(n_PMAT), 2) GROUP BY area ORDER BY area""")
    q("""PIVOT (SELECT anio, AREA_TERRITORIAL AS area, (nat = 'Privada')::INT AS priv FROM v
               WHERE anio BETWEEN 2009 AND 2011)
        ON anio USING round(100.0 * avg(priv), 1) GROUP BY area ORDER BY area""")
    q("""PIVOT (SELECT anio, AREA_TERRITORIAL AS area FROM v WHERE anio BETWEEN 2009 AND 2012)
        ON anio USING count(*) GROUP BY area ORDER BY area""")
    titulo("EXTRA-4 edad 'calendario' vs edad a la fecha de la prueba")
    q("""SELECT anio, mes, count(*) FILTER (WHERE edad = 12) AS edad12 FROM v
        WHERE anio = 2023 GROUP BY ALL ORDER BY ALL""")
    titulo("EXTRA-5 valores de AREA_TERRITORIAL en bruto (variantes de escritura)")
    q("""SELECT AREA_TERRITORIAL, length(AREA_TERRITORIAL) AS len, count(*) AS filas,
               min(anio) desde, max(anio) hasta FROM v GROUP BY 1, 2 ORDER BY 1""")
    titulo("EXTRA-6 repetidores: fecha incoherente explicada por mes=1 en 2016")
    q("""SELECT a1, m1 = 1 AS mes1_en_primer_anio, an1 = an2 AS mismo_anio_nac, m1 = m2 AS mismo_mes, count(*)
        FROM pares WHERE g1 = g2 GROUP BY ALL ORDER BY ALL""")
    titulo("EXTRA-7 HAB-01: ¿los repetidores que siguen en la misma área conservan la categoría de hábitat?")
    q("""SELECT p.a1, p.a2, count(*) AS pares_misma_area_nat,
               count(*) FILTER (WHERE x.hab = y.hab) AS mismo_hab,
               round(100.0 * count(*) FILTER (WHERE x.hab = y.hab) / count(*), 1) AS pct
        FROM pares p JOIN v x ON x.linea = p.l1 JOIN v y ON y.linea = p.l2
        WHERE p.ar1 = p.ar2 AND p.n1 = p.n2 GROUP BY ALL ORDER BY ALL""")
    q("""SELECT y.HABITAT AS hab_2024, x.HABITAT AS hab_2023, count(*)
        FROM pares p JOIN v x ON x.linea = p.l1 JOIN v y ON y.linea = p.l2
        WHERE p.a2 = 2024 AND p.ar1 = p.ar2 GROUP BY ALL ORDER BY ALL""")
    titulo("EXTRA-8 2014: las 29 filas Baix Llobregat 'Més de 100000'")
    q("""SELECT nat, CODI_ALUMNE IS NULL AS sin_cod, min(linea), max(linea), count(*) FROM v
        WHERE anio = 2014 AND AREA_TERRITORIAL = 'Baix Llobregat' AND hab = 3 GROUP BY ALL""")
    titulo("EXTRA-9 2010: ¿qué columna está desordenada? área x naturaleza y área x puntuación")
    q("""WITH a AS (SELECT anio, AREA_TERRITORIAL area, avg(n_PMAT) m FROM v WHERE anio BETWEEN 2009 AND 2011 GROUP BY ALL)
        SELECT round(corr(x.m, y.m), 3) AS corr_area_pmat_2009_2010,
               round(corr(x.m, z.m), 3) AS corr_area_pmat_2009_2011,
               round(corr(y.m, z.m), 3) AS corr_area_pmat_2010_2011
        FROM a x JOIN a y ON x.area = y.area AND x.anio = 2009 AND y.anio = 2010
                 JOIN a z ON z.area = x.area AND z.anio = 2011""")


BLOQUES = [
    ("OTR", b_OTR01_estructura), ("ANY", b_ANY01), ("COD01", b_COD01), ("COD02", b_COD02),
    ("COD03", b_COD03), ("COD04", b_COD04), ("GEN", b_GEN01), ("NAT", b_NAT01),
    ("HAB", b_HAB), ("ARE", b_ARE), ("FEC", b_FEC), ("EXTRA", b_EXTRA),
]

if __name__ == "__main__":
    filtros = sys.argv[1:]
    cargar()
    necesita_pares = any(f.startswith(("COD04", "EXTRA")) for f in filtros) and not any(
        f.startswith("COD03") for f in filtros)
    for nombre, fn in BLOQUES:
        if not filtros or any(nombre.startswith(f) for f in filtros) or (
                necesita_pares and nombre == "COD03"):
            fn()
