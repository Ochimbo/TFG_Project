"""Cifras complementarias para el informe de calidad de datos (T7).

Calcula lo que el perfilado y la verificación no dejaron cerrado:
  A. Pesos reales de PMED (media simple frente a los pesos oficiales 42/25/33 del Quadern 68).
  B. Comparación de umbrales fijos de nivel de logro con los % oficiales por nivel 2018-2025.
  C. % por nivel con los umbrales propuestos (2009-2025, rotaciones corregidas).
  D. Recuento del flag de incoherencia global-subcompetencias con tolerancia única 0,115 (2011-2025).
  E. Recuentos de flags de calidad propuestos (fechas de relleno, suelos, escalas).
  F. Cardinalidad estimada de las dimensiones tras la limpieza.

Lee Datos.csv en modo solo lectura con DuckDB. No modifica Datos.csv ni Datos.zip.
Uso: .venv/bin/python validacion/perfilado/complemento_informe_calidad.py
Salida: se imprime y se copia en validacion/perfilado/salidas_complemento/complemento_informe_calidad.log
"""

import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 300)

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "Datos.csv"
SALIDA = Path(__file__).resolve().parent / "salidas_complemento"
SALIDA.mkdir(exist_ok=True)


class Tee:
    def __init__(self, *f):
        self.f = f

    def write(self, s):
        for x in self.f:
            x.write(s)

    def flush(self):
        for x in self.f:
            x.flush()


LOG = open(SALIDA / "complemento_informe_calidad.log", "w", encoding="utf-8")
sys.stdout = Tee(sys.__stdout__, LOG)

S = ["PCAT", "PCAT_CL", "PCAT_EE", "PCAT_CO", "PCAST", "PCAST_CL", "PCAST_EE", "PCAST_CO",
     "PMAT", "PMAT_NC", "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE", "PANG_EE",
     "PFRAN", "PFRAN_CO", "PFRAN_CE", "PFRAN_EE", "PMED", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3"]
G = ["PCAT", "PCAST", "PMAT", "PANG", "PFRAN", "PMED"]

con = duckdb.connect()


def q(sql):
    print("\n-- SQL:\n" + sql.strip())
    d = con.execute(sql).df()
    print(d.to_string())
    return d


def titulo(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# Carga: puntuaciones en centésimas enteras ("87,70" -> 8770) y rotaciones PUN-02 / PUN-03 deshechas
con.execute(f"CREATE TABLE raw AS SELECT * FROM read_csv('{CSV}', all_varchar=true, header=true)")
cols = ", ".join(f"CAST(replace({c}, ',', '') AS INTEGER) AS {c}" for c in S)
con.execute(f"""CREATE TABLE t AS SELECT CAST("ANY" AS INTEGER) anio, CODI_ALUMNE codi, {cols},
    GENERE, TRY_CAST(MES_NAIXEMENT AS INTEGER) mes, TRY_CAST(ANY_NAIXEMENT AS INTEGER) anio_nac,
    AREA_TERRITORIAL area, NATURALESA, "HÀBITAT" habitat FROM raw""")
con.execute("""CREATE TABLE tc AS SELECT * REPLACE (
    CASE WHEN anio=2017 THEN PCAST_EE ELSE PCAST    END AS PCAST,
    CASE WHEN anio=2017 THEN PCAST    ELSE PCAST_CL END AS PCAST_CL,
    CASE WHEN anio=2017 THEN PCAST_CL ELSE PCAST_EE END AS PCAST_EE,
    CASE WHEN anio=2016 THEN PFRAN_EE ELSE PFRAN    END AS PFRAN,
    CASE WHEN anio=2016 THEN PFRAN    ELSE PFRAN_CO END AS PFRAN_CO,
    CASE WHEN anio=2016 THEN PFRAN_CO ELSE PFRAN_CE END AS PFRAN_CE,
    CASE WHEN anio=2016 THEN PFRAN_CE ELSE PFRAN_EE END AS PFRAN_EE) FROM t""")
print("filas cargadas:", con.execute("SELECT count(*) FROM tc").fetchone()[0])

# ------------------------------------------------------------------------------------------
titulo("A. PMED: ¿media simple o pesos oficiales 42/25/33 (Quadern 68, Taula 3)?")
q("""SELECT anio, count(*) n,
  count(*) FILTER (WHERE abs(PMED/100.0 - (PMED_COMP1+PMED_COMP2+PMED_COMP3)/300.0) <= 0.115) ok_simple,
  count(*) FILTER (WHERE abs(PMED/100.0 - (0.42*PMED_COMP1+0.25*PMED_COMP2+0.33*PMED_COMP3)/100.0) <= 0.115) ok_42_25_33,
  round(avg(abs(PMED/100.0 - (0.42*PMED_COMP1+0.25*PMED_COMP2+0.33*PMED_COMP3)/100.0)), 3) err_medio_oficial
FROM tc WHERE PMED IS NOT NULL AND PMED_COMP1 IS NOT NULL AND PMED_COMP2 IS NOT NULL AND PMED_COMP3 IS NOT NULL
GROUP BY 1 ORDER BY 1""")

# ------------------------------------------------------------------------------------------
titulo("B. Umbrales fijos frente a % oficiales por nivel (baix / mitjà-baix / mitjà-alt / alt)")
# Fuente: Quaderns d'avaluació 2018-2025 (handles en el informe). CTE = PMED en 2024-2025.
OFICIAL = {
    ("PCAT", 2018): (15.3, 21.8, 40.2, 22.7), ("PCAST", 2018): (13.9, 23.2, 38.6, 24.3),
    ("PANG", 2018): (15.9, 19.7, 31.5, 32.9), ("PMAT", 2018): (10.9, 21.7, 33.2, 34.2),
    ("PMED", 2018): (15.0, 24.7, 35.6, 24.7),
    ("PCAT", 2019): (12.8, 19.0, 35.3, 32.9), ("PCAST", 2019): (14.8, 22.0, 35.2, 28.0),
    ("PANG", 2019): (15.4, 19.1, 27.5, 38.0), ("PMAT", 2019): (13.0, 24.3, 40.4, 22.3),
    ("PMED", 2019): (15.7, 29.3, 36.3, 18.7),
    ("PCAT", 2021): (12.3, 16.1, 36.6, 35.0), ("PCAST", 2021): (15.0, 23.8, 36.2, 25.0),
    ("PANG", 2021): (18.7, 21.1, 28.4, 31.8), ("PMAT", 2021): (14.9, 20.1, 39.3, 25.8),
    ("PMED", 2021): (11.5, 23.6, 35.3, 29.6),
    ("PCAT", 2022): (16.6, 22.5, 36.3, 24.6), ("PCAST", 2022): (15.0, 22.4, 36.2, 26.4),
    ("PANG", 2022): (15.2, 20.9, 26.5, 37.3), ("PMAT", 2022): (16.5, 22.1, 40.2, 21.2),
    ("PMED", 2022): (13.2, 25.6, 33.5, 27.7),
    ("PCAT", 2023): (17.5, 20.1, 35.5, 26.9), ("PCAST", 2023): (17.2, 22.6, 37.0, 23.2),
    ("PANG", 2023): (13.8, 16.1, 38.5, 31.6), ("PMAT", 2023): (12.5, 24.1, 43.8, 19.6),
    ("PMED", 2023): (15.5, 25.7, 30.9, 27.9),
    ("PCAT", 2024): (14.2, 19.3, 36.2, 30.4), ("PCAST", 2024): (14.2, 20.3, 39.1, 26.4),
    ("PANG", 2024): (15.4, 22.0, 39.2, 23.4), ("PMAT", 2024): (12.2, 23.3, 43.1, 21.4),
    ("PMED", 2024): (14.0, 20.4, 35.9, 29.7),
    ("PCAT", 2025): (15.3, 20.6, 37.3, 26.8), ("PCAST", 2025): (10.5, 16.9, 40.6, 32.0),
    ("PANG", 2025): (13.6, 19.6, 34.8, 32.0), ("PMAT", 2025): (17.5, 26.5, 38.0, 18.0),
    ("PMED", 2025): (22.6, 28.5, 32.8, 16.1),
}
partes = [f"SELECT '{g}' materia, anio, {g} x FROM tc WHERE {g} IS NOT NULL" for g in G]
con.execute("CREATE TABLE globales AS " + " UNION ALL ".join(partes))
of = pd.DataFrame([(m, y, *v) for (m, y), v in OFICIAL.items()],
                  columns=["materia", "anio", "of_bajo", "of_mb", "of_ma", "of_alto"])

# cortes implícitos: percentil de la distribución del CSV en el % oficial acumulado
filas = []
for (m, y), v in OFICIAL.items():
    xs = np.sort(con.execute(f"SELECT x FROM globales WHERE materia='{m}' AND anio={y}").fetchnumpy()["x"]) / 100
    n = len(xs)
    c1 = xs[min(n - 1, int(np.ceil(v[0] / 100 * n)))]
    c2 = xs[min(n - 1, int(np.ceil((v[0] + v[1]) / 100 * n)))]
    c3 = xs[min(n - 1, int(np.ceil((v[0] + v[1] + v[2]) / 100 * n)))]
    filas.append((m, y, n, c1, c2, c3))
imp = pd.DataFrame(filas, columns=["materia", "anio", "n_csv", "corte_bajo", "corte_medio", "corte_alto"])
print("\nCortes implícitos en el CSV que reproducen los % oficiales (primer valor observado en cada corte):")
print(imp.to_string())
print("\nResumen de cortes implícitos:")
print(imp[["corte_bajo", "corte_medio", "corte_alto"]].describe().round(2).to_string())

CORTES = {"50/70/85": (50, 70, 85), "55/70/85": (55, 70, 85), "60/70/85": (60, 70, 85),
          "55/70/90": (55, 70, 90), "60/70/90": (60, 70, 90)}
res = []
for nombre, (a, b, c) in CORTES.items():
    d = con.execute(f"""SELECT materia, anio,
        100.0*count(*) FILTER (WHERE x <  {a*100})/count(*) bajo,
        100.0*count(*) FILTER (WHERE x >= {a*100} AND x < {b*100})/count(*) mb,
        100.0*count(*) FILTER (WHERE x >= {b*100} AND x < {c*100})/count(*) ma,
        100.0*count(*) FILTER (WHERE x >= {c*100})/count(*) alto
        FROM globales WHERE anio >= 2018 AND materia <> 'PFRAN' GROUP BY 1, 2""").df()
    d = d.merge(of, on=["materia", "anio"])
    res.append((nombre,
                round((d.bajo - d.of_bajo).abs().mean(), 2), round((d.bajo - d.of_bajo).mean(), 2),
                round((d.mb - d.of_mb).abs().mean(), 2), round((d.ma - d.of_ma).abs().mean(), 2),
                round((d.alto - d.of_alto).abs().mean(), 2), round((d.alto - d.of_alto).mean(), 2),
                round(d.bajo.min(), 1), round(d.bajo.max(), 1)))
    if nombre in ("50/70/85", "55/70/85"):
        d2 = d.copy()
        d2["dif_bajo"] = (d2.bajo - d2.of_bajo).round(1)
        print(f"\nDetalle {nombre} (CSV frente a oficial, 2018-2025):")
        print(d2.round(1).sort_values(["materia", "anio"]).to_string())
r = pd.DataFrame(res, columns=["cortes", "MAE_bajo", "sesgo_bajo", "MAE_mb", "MAE_ma", "MAE_alto", "sesgo_alto",
                               "bajo_min", "bajo_max"])
print("\nError absoluto medio (puntos porcentuales) frente a los % oficiales, 35 materia-año 2018-2025:")
print(r.to_string())

# ------------------------------------------------------------------------------------------
titulo("C. % por nivel con los umbrales propuestos 55/70/85 (2009-2025, globales corregidas)")
q("""SELECT materia, count(*) n,
  round(100.0*count(*) FILTER (WHERE x <  5500)/count(*), 1) bajo,
  round(100.0*count(*) FILTER (WHERE x >= 5500 AND x < 7000)/count(*), 1) medio_bajo,
  round(100.0*count(*) FILTER (WHERE x >= 7000 AND x < 8500)/count(*), 1) medio_alto,
  round(100.0*count(*) FILTER (WHERE x >= 8500)/count(*), 1) alto
FROM globales GROUP BY ROLLUP (materia) ORDER BY materia NULLS LAST""")
q("""PIVOT (SELECT materia, anio, round(100.0*count(*) FILTER (WHERE x < 5500)/count(*), 1) pct_bajo
        FROM globales GROUP BY 1, 2) ON anio USING first(pct_bajo) GROUP BY materia ORDER BY materia""")
q("""SELECT round(100.0*count(*) FILTER (WHERE x < 5500)/count(*), 1) pct_bajo_55,
  round(100.0*count(*) FILTER (WHERE x < 5000)/count(*), 1) pct_bajo_50 FROM globales""")
# Concentración en los suelos artificiales justo por debajo de 55
q("""SELECT 'PANG 2015 global = 48,79' caso, count(*) FILTER (WHERE x = 4879) n_suelo,
        count(*) FILTER (WHERE x < 5500) n_bajo_55, count(*) n FROM globales WHERE materia='PANG' AND anio=2015
UNION ALL SELECT 'PMAT 2016 global = 59,20', count(*) FILTER (WHERE x = 5920), count(*) FILTER (WHERE x < 5500), count(*)
        FROM globales WHERE materia='PMAT' AND anio=2016""")

# ------------------------------------------------------------------------------------------
titulo("D. FlagGlobalIncoherente con tolerancia única 0,115 en 2011-2025")
L3 = (0.50, 0.35, 0.15)
PESOS = {}
for y in range(2011, 2026):
    for g, cl, ee, co in (("PCAT", "PCAT_CL", "PCAT_EE", "PCAT_CO"), ("PCAST", "PCAST_CL", "PCAST_EE", "PCAST_CO")):
        if y in (2011, 2013, 2014, 2015):
            PESOS[(g, y)] = {cl: 0.5, ee: 0.5}
        elif y in (2012, 2016, 2017):
            PESOS[(g, y)] = {cl: 0.6, ee: 0.4}
        elif y >= 2018:
            PESOS[(g, y)] = {cl: 0.5, ee: 0.35, co: 0.15}
    for g in ("PANG", "PFRAN"):
        co, ce, ee = f"{g}_CO", f"{g}_CE", f"{g}_EE"
        if y in (2011, 2012):
            PESOS[(g, y)] = {co: 0.5, ce: 0.5}
        elif y in (2013, 2014, 2015):
            PESOS[(g, y)] = {co: 1 / 3, ce: 1 / 3, ee: 1 / 3}
        elif y >= 2016:
            PESOS[(g, y)] = {co: 0.35, ce: 0.5, ee: 0.15}
    if y in (2013, 2014, 2016):
        PESOS[("PMAT", y)] = {"PMAT_NC": 0.35, "PMAT_EFM": 0.35, "PMAT_CR": 0.30}
    elif y == 2015:
        PESOS[("PMAT", y)] = {"PMAT_NC": 0.40, "PMAT_EFM": 0.36, "PMAT_CR": 0.24}
    elif y >= 2017:
        PESOS[("PMAT", y)] = {"PMAT_NC": 0.30, "PMAT_EFM": 0.35, "PMAT_CR": 0.35}
    if y >= 2018:
        PESOS[("PMED", y)] = {"PMED_COMP1": 1 / 3, "PMED_COMP2": 1 / 3, "PMED_COMP3": 1 / 3}
# PMAT 2011 y 2012: pesos no redondos, estimados por mínimos cuadrados sin intercepto
for y in (2011, 2012):
    d = con.execute(f"""SELECT PMAT, PMAT_NC, PMAT_EFM, PMAT_CR FROM tc WHERE anio={y} AND PMAT IS NOT NULL
        AND PMAT_NC IS NOT NULL AND PMAT_EFM IS NOT NULL AND PMAT_CR IS NOT NULL""").df().astype(float) / 100
    w, *_ = np.linalg.lstsq(d[["PMAT_NC", "PMAT_EFM", "PMAT_CR"]].values, d.PMAT.values, rcond=None)
    PESOS[("PMAT", y)] = dict(zip(["PMAT_NC", "PMAT_EFM", "PMAT_CR"], w))
    print(f"pesos estimados PMAT {y}:", np.round(w, 4))
filas = []
for (g, y), w in sorted(PESOS.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    expr = " + ".join(f"{float(p)!r}::DOUBLE*{c}" for c, p in w.items())
    nn = " AND ".join(f"{c} IS NOT NULL" for c in w)
    n, fuera = con.execute(f"""SELECT count(*), count(*) FILTER (WHERE abs({g}::DOUBLE - ({expr}))/100.0 > 0.115)
        FROM tc WHERE anio={y} AND {g} IS NOT NULL AND {nn}""").fetchone()
    if n:
        filas.append((g, y, n, fuera))
fl = pd.DataFrame(filas, columns=["materia", "anio", "n_evaluable", "fuera_0115"])
print(fl[fl.fuera_0115 > 0].to_string())
print("total filas marcadas (2011-2025, tolerancia 0,115):", int(fl.fuera_0115.sum()))
print("total globales evaluables:", int(fl.n_evaluable.sum()))

# ------------------------------------------------------------------------------------------
titulo("E. Recuentos de flags de calidad propuestos")
q("""SELECT
  count(*) FILTER (WHERE (codi IS NULL AND anio IN (2016, 2018))
                      OR (anio = 2016 AND anio_nac = 2001 AND mes = 1)) fecha_nac_dudosa,
  count(*) FILTER (WHERE codi IS NULL AND anio IN (2016, 2018)) sin_codigo_2016_2018,
  count(*) FILTER (WHERE anio = 2016 AND anio_nac = 2001 AND mes = 1) relleno_1_2001,
  count(*) FILTER (WHERE anio = 2016 AND anio_nac = 2001 AND mes = 1 AND codi IS NOT NULL) relleno_con_codigo,
  count(*) FILTER (WHERE mes = 1 AND anio IN (2009, 2012, 2013, 2014, 2015)) mes_dudoso_enero,
  count(*) FILTER (WHERE anio = 2010) filas_2010,
  count(*) FILTER (WHERE anio = 2014 AND area = 'Baix Llobregat' AND habitat = 'Més de 100000') bll_2014
FROM tc""")
q("""SELECT
  count(PANG_EE) FILTER (WHERE anio = 2015) pang_ee_2015,
  count(PANG_CO) FILTER (WHERE anio = 2015) pang_co_2015,
  count(PANG_CE) FILTER (WHERE anio = 2015) pang_ce_2015,
  count(*) FILTER (WHERE anio = 2015 AND PANG = 4879) pang_2015_suelo,
  count(*) FILTER (WHERE anio = 2015 AND PANG_CO = 5319) pang_co_2015_suelo,
  count(*) FILTER (WHERE anio = 2015 AND PANG_CE = 4500) pang_ce_2015_suelo,
  count(PCAT_EE) FILTER (WHERE anio = 2018) pcat_ee_2018,
  count(*) FILTER (WHERE anio = 2018 AND PCAT_EE = 4940) pcat_ee_2018_suelo,
  count(PANG_CO) FILTER (WHERE anio = 2016) + count(PANG_CE) FILTER (WHERE anio = 2016)
    + count(PANG_EE) FILTER (WHERE anio = 2016) pang_subs_2016,
  count(PANG_EE) FILTER (WHERE anio = 2013) pang_ee_2013,
  count(PANG_EE) FILTER (WHERE anio = 2014) pang_ee_2014,
  count(PANG_CO) FILTER (WHERE anio = 2011) pang_co_2011,
  count(PCAT_CL) FILTER (WHERE anio = 2011) pcat_cl_2011,
  count(*) FILTER (WHERE anio = 2016 AND PMAT = 5920) pmat_2016_5920
FROM tc""")
# Celdas de FactPuntuacion afectadas por las marcas de no comparabilidad de subcompetencias
q("""SELECT
  count(PANG_EE) FILTER (WHERE anio = 2015) + count(PANG_CO) FILTER (WHERE anio = 2015)
  + count(PANG_CE) FILTER (WHERE anio = 2015) pang_subs_2015,
  count(PANG_EE) FILTER (WHERE anio BETWEEN 2013 AND 2016) pang_ee_2013_2016,
  count(PFRAN) + count(PFRAN_CO) + count(PFRAN_CE) + count(PFRAN_EE) celdas_frances
FROM tc""")

# ------------------------------------------------------------------------------------------
titulo("F. Cardinalidad estimada de las dimensiones tras la limpieza")
con.execute("""CREATE TABLE lim AS SELECT anio,
  CASE WHEN GENERE IN ('H','Home') THEN 'H' WHEN GENERE IN ('D','Dona') THEN 'D' END genero,
  CASE WHEN mes BETWEEN 1 AND 12 THEN mes END mes,
  CASE WHEN anio = 2010 THEN 'No fiable (2010)'
       WHEN (codi IS NULL AND anio IN (2016, 2018)) OR (anio = 2016 AND anio_nac = 2001 AND mes = 1) THEN 'Desconocida'
       WHEN anio_nac IS NULL THEN 'Desconocida'
       WHEN anio - anio_nac NOT BETWEEN 10 AND 14 THEN 'Desconocida'
       WHEN anio - anio_nac < 12 THEN 'Adelantado'
       WHEN anio - anio_nac = 12 THEN 'Edad teórica'
       WHEN anio - anio_nac = 13 THEN 'Retraso de 1 año'
       ELSE 'Retraso de 2 años' END situacion_edad,
  CASE WHEN anio <> 2010 AND anio - anio_nac BETWEEN 10 AND 14
        AND NOT ((codi IS NULL AND anio IN (2016, 2018)) OR (anio = 2016 AND anio_nac = 2001 AND mes = 1))
       THEN anio - anio_nac END edad,
  CASE WHEN area IS NULL THEN 'Desconocida'
       WHEN area = 'Barcelona Comarques' AND anio = 2024 THEN 'Barcelonès'
       WHEN area = 'Barcelona Comarques' THEN 'Barcelona Comarques (perímetro hasta 2023)'
       ELSE area END area_perimetro,
  coalesce(area, 'Desconocida') area_original,
  CASE WHEN NATURALESA IN ('Públic','Pública') THEN 'Pública' WHEN NATURALESA IN ('Privat','Privada') THEN 'Privada' END naturaleza,
  CASE WHEN anio = 2010 THEN 0
       WHEN habitat LIKE 'Fins a %' THEN 1 WHEN habitat = 'De 10001 a 100000' THEN 2
       WHEN habitat LIKE 'Més de %' THEN 3 END habitat_cod,
  (anio = 2014 AND area = 'Baix Llobregat' AND habitat = 'Més de 100000') habitat_incoherente_2014
FROM tc""")
q("""SELECT count(*) FILTER (WHERE genero IS NULL) genero_sin_mapear,
  count(*) FILTER (WHERE naturaleza IS NULL) naturaleza_sin_mapear,
  count(*) FILTER (WHERE habitat_cod IS NULL) habitat_sin_mapear FROM lim""")
q("""SELECT count(*) combinaciones_contexto FROM (SELECT DISTINCT area_original, area_perimetro, naturaleza,
  habitat_cod, habitat_incoherente_2014 FROM lim)""")
q("""SELECT count(*) combinaciones_perfil FROM (SELECT DISTINCT genero, mes, edad, situacion_edad FROM lim)""")
q("""SELECT situacion_edad, count(*) filas FROM lim GROUP BY 1 ORDER BY 2 DESC""")
q("""SELECT edad, count(*) filas FROM lim GROUP BY 1 ORDER BY 1 NULLS LAST""")

# ------------------------------------------------------------------------------------------
titulo("G. n y media de la global en el CSV (rotaciones corregidas) para contrastar con los Quaderns")
q("""PIVOT (SELECT materia, anio, printf('%d | %.2f', count(*), avg(x)/100.0) v FROM globales
        WHERE anio IN (2009, 2012, 2017, 2018, 2023, 2024, 2025) GROUP BY 1, 2)
   ON anio USING first(v) GROUP BY materia ORDER BY materia""")
q("""SELECT count(*) n_raw, round(avg(CAST(replace(PCAST, ',', '.') AS DOUBLE)), 2) media_sin_corregir
   FROM raw WHERE "ANY" = '2017' AND PCAST IS NOT NULL""")

# ------------------------------------------------------------------------------------------
titulo("H. RepeticionProbable: variantes de comparación de la fecha (COD-03 y su verificación)")
# Pares (convocatoria anterior, convocatoria actual) del mismo código en años consecutivos
pares = con.execute("""
WITH c AS (SELECT codi, anio, min(GENERE) g, min(anio_nac) an, min(mes) m, count(*) n
           FROM tc WHERE codi IS NOT NULL GROUP BY 1, 2 HAVING count(*) = 1)
SELECT a.codi, a.anio anio_ant, b.anio,
  CASE WHEN a.g IN ('H','Home') THEN 'H' ELSE 'D' END g_ant, CASE WHEN b.g IN ('H','Home') THEN 'H' ELSE 'D' END g,
  a.an an_ant, b.an, a.m m_ant, b.m
FROM c a JOIN c b ON a.codi = b.codi AND b.anio = a.anio + 1""").df()
print("pares en años consecutivos:", len(pares))
mismo_g = pares.g_ant.eq(pares.g)
mismo_a = pares.an_ant.eq(pares.an)
mismo_m = pares.m_ant.eq(pares.m)
# fecha de relleno: enero de 2016 en la aparición anterior (o 1/2001 de 2016)
relleno_mes = pares.anio_ant.eq(2016) & pares.m_ant.eq(1)
relleno_fecha = relleno_mes & pares.an_ant.eq(2001)
estricta = mismo_g & mismo_a & mismo_m
solo_anio = mismo_g & mismo_a
relajada = mismo_g & ((mismo_a & (mismo_m | relleno_mes)) | relleno_fecha)
print("estricta (género + año + mes):", int(estricta.sum()))
print("género + año de nacimiento:", int(solo_anio.sum()))
print("relajada (mes de enero de 2016 y 1/2001 como desconocidos):", int(relajada.sum()))
print(pares[~relajada].to_string())

print("\nFin. Log en", SALIDA / "complemento_informe_calidad.log")
