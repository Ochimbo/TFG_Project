"""Verificación independiente de los hallazgos PUN-01..PUN-23 (perfilado de puntuaciones).

Escrito desde cero (no reutiliza perfil_puntuaciones.py). Lee Datos.csv en modo solo
lectura con DuckDB y no modifica Datos.csv ni Datos.zip.

Convenciones:
- raw: el CSV tal cual (todo VARCHAR).
- t:   puntuaciones convertidas a CENTÉSIMAS ENTERAS ("87,70" -> 8770) para comparar sin
       errores de coma flotante.
- tc:  t con las rotaciones propuestas deshechas (PCAST 2017 y PFRAN 2016).

Uso:  .venv/bin/python validacion/perfilado/verificacion_puntuaciones.py [PUN-02 PUN-05 ...]
"""

import csv
import itertools
import subprocess
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

pd.set_option("display.width", 320)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_rows", 200)

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / "Datos.csv"

S = ["PCAT", "PCAT_CL", "PCAT_EE", "PCAT_CO", "PCAST", "PCAST_CL", "PCAST_EE", "PCAST_CO",
     "PMAT", "PMAT_NC", "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE", "PANG_EE",
     "PFRAN", "PFRAN_CO", "PFRAN_CE", "PFRAN_EE", "PMED", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3"]
G = ["PCAT", "PCAST", "PMAT", "PANG", "PFRAN", "PMED"]
M = {"PCAT": ["PCAT_CL", "PCAT_EE", "PCAT_CO"], "PCAST": ["PCAST_CL", "PCAST_EE", "PCAST_CO"],
     "PMAT": ["PMAT_NC", "PMAT_EFM", "PMAT_CR"], "PANG": ["PANG_CO", "PANG_CE", "PANG_EE"],
     "PFRAN": ["PFRAN_CO", "PFRAN_CE", "PFRAN_EE"], "PMED": ["PMED_COMP1", "PMED_COMP2", "PMED_COMP3"]}
TODAS = ["ANY", "CODI_ALUMNE", "PCAT", "PCAT_CL", "PCAT_EE", "PCAST", "PCAST_CL", "PCAST_EE", "PMAT",
         "PMAT_NC", "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE", "PFRAN", "PFRAN_CO",
         "PFRAN_CE", "PANG_EE", "PFRAN_EE", "PCAT_CO", "PCAST_CO", "PMED", "PMED_COMP1",
         "PMED_COMP2", "PMED_COMP3", "GENERE", "MES_NAIXEMENT", "ANY_NAIXEMENT",
         "AREA_TERRITORIAL", "NATURALESA", "HÀBITAT"]

con = duckdb.connect()


def df(sql):
    return con.execute(sql).df()


def val(sql):
    return con.execute(sql).fetchall()


def titulo(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def cargar():
    con.execute(f"""CREATE TABLE raw AS SELECT row_number() OVER () AS rid, *
                    FROM read_csv('{CSV}', all_varchar=true, header=true)""")
    cols = ", ".join(f"CAST(replace({c}, ',', '') AS INTEGER) AS {c}" for c in S)
    con.execute(f'CREATE TABLE t AS SELECT rid, CAST("ANY" AS INTEGER) anio, CODI_ALUMNE codi, {cols} FROM raw')
    con.execute("""CREATE TABLE tc AS SELECT * REPLACE (
        CASE WHEN anio=2017 THEN PCAST_EE ELSE PCAST    END AS PCAST,
        CASE WHEN anio=2017 THEN PCAST    ELSE PCAST_CL END AS PCAST_CL,
        CASE WHEN anio=2017 THEN PCAST_CL ELSE PCAST_EE END AS PCAST_EE,
        CASE WHEN anio=2016 THEN PFRAN_EE ELSE PFRAN    END AS PFRAN,
        CASE WHEN anio=2016 THEN PFRAN    ELSE PFRAN_CO END AS PFRAN_CO,
        CASE WHEN anio=2016 THEN PFRAN_CO ELSE PFRAN_CE END AS PFRAN_CE,
        CASE WHEN anio=2016 THEN PFRAN_CE ELSE PFRAN_EE END AS PFRAN_EE) FROM t""")


def sub_global(tabla, g, subs, anio):
    """Filas con global y todas las subcompetencias informadas, en puntos (double)."""
    filtro = " AND ".join(f"{c} IS NOT NULL" for c in subs)
    return df(f"SELECT {g} g, {', '.join(subs)} FROM {tabla} WHERE anio={anio} AND {g} IS NOT NULL AND {filtro}").astype(float) / 100


def residuo(tabla, g, subs, pesos, anio):
    d = sub_global(tabla, g, subs, anio)
    return d, d.g - d[subs].values @ np.array(pesos, dtype=float)


def subs_existentes():
    cov = df("SELECT anio, " + ", ".join(f"count({c}) {c}" for v in M.values() for c in v) + " FROM tc GROUP BY 1 ORDER BY 1").set_index("anio")
    return {(g, y): [c for c in subs if cov.loc[y, c] > 0] for g, subs in M.items() for y in cov.index
            if any(cov.loc[y, c] > 0 for c in subs)}


# ------------------------------------------------------------------------------------------
def pun01():
    titulo("PUN-01 formato numérico")
    with open(CSV, newline="", encoding="utf-8") as f:
        ncampos = {}
        for r in csv.reader(f):
            ncampos[len(r)] = ncampos.get(len(r), 0) + 1
    print("campos por registro (csv.reader):", ncampos)
    print('líneas con "" en el fichero bruto:', subprocess.run(["grep", "-c", '""', str(CSV)], capture_output=True, text=True).stdout.strip())
    partes = []
    for c in S:
        partes.append(f"""SELECT '{c}' col, count({c}) nn,
          count(*) FILTER (WHERE regexp_full_match({c}, '[0-9]{{1,3}},[0-9]{{2}}')) ok_patron,
          count(*) FILTER (WHERE {c} LIKE '%.%') con_punto,
          count(*) FILTER (WHERE {c} IS NOT NULL AND TRY_CAST(replace({c}, ',', '.') AS DOUBLE) IS NULL) no_parse,
          count(*) FILTER (WHERE TRY_CAST(replace({c}, ',', '.') AS DOUBLE) < 0) negativos,
          count(*) FILTER (WHERE TRY_CAST(replace({c}, ',', '.') AS DOUBLE) > 100) mayor100,
          min(TRY_CAST(replace({c}, ',', '.') AS DOUBLE)) minimo, max(TRY_CAST(replace({c}, ',', '.') AS DOUBLE)) maximo
          FROM raw""")
    d = df(" UNION ALL ".join(partes))
    print(d.to_string())
    print(d[["nn", "ok_patron", "con_punto", "no_parse", "negativos", "mayor100"]].sum().to_dict())


def pun02():
    titulo("PUN-02 rotación castellano 2017")
    for y in (2016, 2017, 2018):
        d = sub_global("t", "PCAST", ["PCAST_CL", "PCAST_EE"], y)
        w, *_ = np.linalg.lstsq(d[["PCAST_CL", "PCAST_EE"]].values, d.g.values, rcond=None)
        r_rot = d.PCAST_EE - (0.6 * d.g + 0.4 * d.PCAST_CL)
        print(y, "n", len(d), "distintos G/CL/EE", d.g.nunique(), d.PCAST_CL.nunique(), d.PCAST_EE.nunique(),
              "OLS G~CL+EE", w.round(4), "| EE=0,6G+0,4CL cuadra", int((r_rot.abs() <= 0.065).sum()),
              f"({(r_rot.abs() <= 0.065).mean() * 100:.2f} %)")
    print(df("""SELECT count(*) filas, count(PCAST) g, count(PCAST_CL) cl, count(PCAST_EE) ee,
                count(*) FILTER (WHERE (PCAST IS NULL)<>(PCAST_CL IS NULL) OR (PCAST IS NULL)<>(PCAST_EE IS NULL)) desalineados
                FROM t WHERE anio=2017"""))
    print("tras corregir 2017 (tc):", df("""SELECT round(avg(PCAST)/100,2) media_g, round(stddev_samp(PCAST)/100,2) sd_g,
            round(avg(PCAST_CL)/100,2) media_cl, round(avg(PCAST_EE)/100,2) media_ee FROM tc WHERE anio=2017""").to_dict("records"))
    print("original 2017 (t):", df("SELECT round(avg(PCAST)/100,2) media_g, round(stddev_samp(PCAST)/100,2) sd_g FROM t WHERE anio=2017").to_dict("records"))
    print("residuos fuera de tolerancia tras corregir (centésimas):",
          df("""SELECT PCAST_CL, PCAST_EE, PCAST, PCAST*100 - (60*PCAST_CL + 40*PCAST_EE) res_x100, count(*) n
                FROM tc WHERE anio=2017 AND abs(PCAST*100 - (60*PCAST_CL + 40*PCAST_EE)) > 650 GROUP BY ALL""").to_dict("records"))
    print("comprobación independiente de qué columna es CL (correlación con catalán):")
    for y in (2016, 2017, 2018):
        print(" ", y, df(f"""SELECT round(corr(PCAST,PCAT_CL),3) pcast_catcl, round(corr(PCAST,PCAT_EE),3) pcast_catee,
                 round(corr(PCAST_CL,PCAT_CL),3) cl_catcl, round(corr(PCAST_CL,PCAT_EE),3) cl_catee,
                 round(corr(PCAST_EE,PCAT_CL),3) ee_catcl, round(corr(PCAST_EE,PCAT_EE),3) ee_catee FROM t WHERE anio={y}""").to_dict("records"))


def pun03():
    titulo("PUN-03 rotación francés 2016")
    for y in (2015, 2016, 2017):
        d = sub_global("t", "PFRAN", ["PFRAN_CO", "PFRAN_CE", "PFRAN_EE"], y)
        X = d[["PFRAN_CO", "PFRAN_CE", "PFRAN_EE"]].values
        w, *_ = np.linalg.lstsq(X, d.g.values, rcond=None)
        r = d.PFRAN_EE - (0.35 * d.g + 0.5 * d.PFRAN_CO + 0.15 * d.PFRAN_CE)
        print(y, "n", len(d), "distintos G/CO/CE/EE", [d[c].nunique() for c in d], "OLS", w.round(4),
              "| EE=0,35G+0,5CO+0,15CE cuadra", int((r.abs() <= 0.065).sum()))
    print("medias tras corregir 2016:", df("""SELECT round(avg(PFRAN)/100,2) g, round(avg(PFRAN_CO)/100,2) co,
             round(avg(PFRAN_CE)/100,2) ce, round(avg(PFRAN_EE)/100,2) ee FROM tc WHERE anio=2016""").to_dict("records"))


def tabla_pesos():
    filas = []
    for (g, y), ex in subs_existentes().items():
        d = sub_global("tc", g, ex, y)
        X, yv = d[ex].values, d.g.values
        w, *_ = np.linalg.lstsq(X, yv, rcond=None)
        for _ in range(3):  # ajuste recortado: reajusta sin |residuo| >= 0,5
            keep = np.abs(yv - X @ w) < 0.5
            if keep.sum() < len(ex) + 5:
                break
            w, *_ = np.linalg.lstsq(X[keep], yv[keep], rcond=None)
        r = yv - X @ w
        rs = yv - X.mean(axis=1)
        filas.append(dict(materia=g, anio=y, n=len(d), subs="/".join(c.split("_")[1] for c in ex),
                          pesos="/".join(f"{x:.4f}" for x in w), ajuste_065=round((np.abs(r) <= 0.065).mean() * 100, 2),
                          fuera_065=int((np.abs(r) > 0.065).sum()), fuera_115=int((np.abs(r) > 0.115).sum()),
                          res_max=round(np.abs(r).max(), 3), err_medio_media_simple=round(np.abs(rs).mean(), 3),
                          err_max_media_simple=round(np.abs(rs).max(), 2)))
    return pd.DataFrame(filas)


def pun04():
    titulo("PUN-04 pesos de la global (datos corregidos, mínimos cuadrados recortados)")
    print(tabla_pesos().to_string())


def pun05():
    titulo("PUN-05 PANG y PCAST 2022")
    d, r = residuo("tc", "PANG", ["PANG_CO", "PANG_CE", "PANG_EE"], [.35, .5, .15], 2022)
    fuera = r.abs() > 0.115
    print("PANG 2022: fuera", int(fuera.sum()), "de", len(d), f"({fuera.mean() * 100:.2f} %)", "err medio", round(r[fuera].abs().mean(), 3),
          "residuo medio global", round(r.mean(), 3), "| residuos", r[fuera].round(1).value_counts().to_dict())
    for k in (-1, 1):
        r2 = d.g - (.35 * d.PANG_CO + .5 * (d.PANG_CE + k * 100 / 24) + .15 * d.PANG_EE)
        print("   CE", k, "ítem explica", int((fuera & (r2.abs() <= 0.115)).sum()))
    print("   descuadres con CE=100:", int((fuera & (d.PANG_CE == 100)).sum()), "| distintos CE:", d.PANG_CE.nunique())
    d, r = residuo("tc", "PCAST", ["PCAST_CL", "PCAST_EE", "PCAST_CO"], [.5, .35, .15], 2022)
    fuera = r.abs() > 0.115
    print("PCAST 2022: fuera", int(fuera.sum()), "de", len(d), f"({fuera.mean() * 100:.2f} %)", "err medio", round(r[fuera].abs().mean(), 3),
          "residuo medio global", round(r.mean(), 4), "| residuos", r[fuera].round(1).value_counts().to_dict())
    for k in (-1, 1):
        r2 = d.g - (.5 * d.PCAST_CL + .35 * (d.PCAST_EE + k * 100 / 18) + .15 * d.PCAST_CO)
        print("   EE", k, "ítem explica", int((fuera & (r2.abs() <= 0.115)).sum()))
    print("   distintos EE:", d.PCAST_EE.nunique())


def pun06():
    titulo("PUN-06 PANG_EE 2015")
    print(df("""SELECT anio, PANG_EE/100.0 v, count(*) n FROM tc WHERE anio BETWEEN 2013 AND 2017 AND PANG_EE IS NOT NULL
               GROUP BY 1,2 ORDER BY 1,2""").pivot(index="v", columns="anio", values="n").fillna(0).astype(int).to_string())
    d = sub_global("tc", "PANG", ["PANG_CO", "PANG_CE", "PANG_EE"], 2015)
    d["ee_impl"] = 3 * d.g - d.PANG_CO - d.PANG_CE
    for tol in (0.065, 0.115):
        d[f"ok{tol}"] = (d.g - (d.PANG_CO + d.PANG_CE + d.PANG_EE) / 3).abs() <= tol
        print(f"pesos 1/3 exactos, tol {tol}: ajuste {d[f'ok{tol}'].mean() * 100:.2f} %, fuera {int((~d[f'ok{tol}']).sum())}")
    print(d.groupby("PANG_EE").agg(n=("g", "size"), pct_cuadra=("ok0.065", lambda s: round(s.mean() * 100, 1)),
                                   impl_min=("ee_impl", "min"), impl_mediana=("ee_impl", "median"), impl_max=("ee_impl", "max")).round(2).to_string())


def pun07():
    titulo("PUN-07 PFRAN 2022")
    d, r = residuo("tc", "PFRAN", ["PFRAN_CO", "PFRAN_CE", "PFRAN_EE"], [.35, .5, .15], 2022)
    fuera = r.abs() > 0.115
    print("fuera", int(fuera.sum()), "de", len(d), f"({fuera.mean() * 100:.1f} %)", "err medio", round(r[fuera].abs().mean(), 3), "max", round(r.abs().max(), 3),
          "| media publicada", round(d.g.mean(), 3), "media recalculada", round((d.g - r).mean(), 3))
    cols = ["g", "PFRAN_CO", "PFRAN_CE", "PFRAN_EE"]
    mejor = sorted(((int(((d[p[0]] - (.35 * d[p[1]] + .5 * d[p[2]] + .15 * d[p[3]])).abs() <= 0.115).sum()), p)
                    for p in itertools.permutations(cols)), reverse=True)[:3]
    print("mejores permutaciones de columnas (filas que cuadran):", mejor)
    pond = (d.g - r).round(1)
    print("corr(global, ponderada) en filas que no cuadran:", round(np.corrcoef(d.g[fuera], pond[fuera])[0, 1], 3))
    pares = set(pond[fuera])
    print("globales malas que coinciden con la ponderada de otra fila mala:", sum(x in pares for x in d.g[fuera].round(1)), "de", int(fuera.sum()))
    print("mínimo PFRAN 2022 y n<50:", val("SELECT min(PFRAN)/100.0, count(*) FILTER (WHERE PFRAN<5000) FROM tc WHERE anio=2022"))


def pun08():
    titulo("PUN-08 PCAT_EE 2018")
    print(df("SELECT PCAT_EE/100.0 v, count(*) n FROM tc WHERE anio=2018 AND PCAT_EE IS NOT NULL GROUP BY 1 ORDER BY 1").T.to_string())
    print(df("""SELECT anio, count(PCAT_EE) nn, min(PCAT_EE)/100.0 minimo, quantile_disc(PCAT_EE,0.10)/100.0 p10,
                count(*) FILTER (WHERE PCAT_EE=0) n_cero, count(*) FILTER (WHERE PCAT_EE<=5000) le50
                FROM tc WHERE anio BETWEEN 2016 AND 2025 GROUP BY 1 ORDER BY 1""").to_string())
    print(df("""SELECT anio, min(PCAT)/100.0 minimo, round(100.0*count(*) FILTER (WHERE PCAT<3000)/count(PCAT),2) pct_lt30,
                round(100.0*count(*) FILTER (WHERE PCAT<5000)/count(PCAT),2) pct_lt50, round(stddev_samp(PCAT)/100,2) sd
                FROM tc GROUP BY 1 ORDER BY 1""").to_string())


def pun09():
    titulo("PUN-09 PMAT 2015 y 2019")
    print(df("""SELECT anio, min(PMAT)/100.0 minimo, round(100.0*count(*) FILTER (WHERE PMAT<3000)/count(PMAT),2) lt30,
                round(100.0*count(*) FILTER (WHERE PMAT<5000)/count(PMAT),2) lt50, round(100.0*count(*) FILTER (WHERE PMAT>=9500)/count(PMAT),2) ge95,
                round(avg(PMAT)/100,2) media, round(stddev_samp(PMAT)/100,2) sd,
                min(PMAT_NC)/100.0 min_nc, min(PMAT_EFM)/100.0 min_efm, min(PMAT_CR)/100.0 min_cr,
                min(PMAT_NC) FILTER (WHERE PMAT_NC>0)/100.0 minpos_nc, min(PMAT_EFM) FILTER (WHERE PMAT_EFM>0)/100.0 minpos_efm,
                min(PMAT_CR) FILTER (WHERE PMAT_CR>0)/100.0 minpos_cr, count(DISTINCT PMAT_NC) dist_nc
                FROM tc GROUP BY 1 ORDER BY 1""").to_string())
    for c in ("PMAT_NC", "PMAT_EFM", "PMAT_CR"):
        print(c, "2019 valores más bajos:", val(f"SELECT {c}/100.0, count(*) FROM tc WHERE anio=2019 AND {c} IS NOT NULL GROUP BY 1 ORDER BY 1 LIMIT 4"))


def pun10():
    titulo("PUN-10 techo 2011")
    print("PANG_CO 2011 = 99,73:", val("SELECT count(*) FILTER (WHERE PANG_CO=9973), count(PANG_CO), max(PANG_CO)/100.0 FROM tc WHERE anio=2011"))
    print("media PANG_CO 2010-2012:", val("SELECT anio, round(avg(PANG_CO)/100,2) FROM tc WHERE anio BETWEEN 2010 AND 2012 GROUP BY 1 ORDER BY 1"))
    print("PCAT_CL 2011 = 99,73 y máximo:", val("SELECT count(*) FILTER (WHERE PCAT_CL=9973), max(PCAT_CL)/100.0 FROM tc WHERE anio=2011"))
    print("máximos globales 2011 PCAT/PCAST/PMAT/PANG:", val("SELECT max(PCAT)/100.0, max(PCAST)/100.0, max(PMAT)/100.0, max(PANG)/100.0 FROM tc WHERE anio=2011"))
    print("media PANG 2010-2012:", val("SELECT anio, round(avg(PANG)/100,2) FROM tc WHERE anio BETWEEN 2010 AND 2012 GROUP BY 1 ORDER BY 1"))
    d, r = residuo("tc", "PANG", ["PANG_CO", "PANG_CE"], [.5, .5], 2011)
    print("PANG 2011 - media simple CO/CE: filas con residuo en [0,065; 0,075]:", int(((r >= 0.0649) & (r <= 0.0751)).sum()), "de", len(d),
          "| distribución:", r.round(3).value_counts().to_dict(), "| >0,065:", int((r.abs() > 0.065).sum()))


def cobertura():
    return df("SELECT anio, count(*) n_filas, " + ", ".join(f"count({c}) {c}" for c in S) + " FROM tc GROUP BY 1 ORDER BY 1").set_index("anio")


def pun11():
    titulo("PUN-11 rupturas de diseño")
    print(cobertura().T.to_string())
    for nombre, agg in (("valores distintos", "count(DISTINCT {c})"), ("máximo", "max({c})/100.0"), ("mínimo positivo", "min({c}) FILTER (WHERE {c}>0)/100.0")):
        print("\n" + nombre)
        print(df("SELECT anio, " + ", ".join(agg.format(c=c) + f" {c}" for c in S) + " FROM tc GROUP BY 1 ORDER BY 1").set_index("anio").T.to_string())


def saltos(tabla):
    un = " UNION ALL ".join(f"SELECT '{c}' col, anio, avg({c})/100.0 media FROM {tabla} WHERE {c} IS NOT NULL GROUP BY anio" for c in S)
    return df(f"""WITH m AS ({un}) SELECT col, lag(anio) OVER w anio0, anio anio1, round(media - lag(media) OVER w, 2) delta
                  FROM m WINDOW w AS (PARTITION BY col ORDER BY anio)""").dropna()


def pun12():
    titulo("PUN-12 saltos interanuales >= 8 puntos")
    s = saltos("tc")
    grandes = s[s.delta.abs() >= 8].sort_values("delta")
    print("pares:", len(grandes), "| de ellos francés:", int(grandes.col.str.startswith("PFRAN").sum()), "| con datos sin corregir:", int((saltos("t").delta.abs() >= 8).sum()))
    print(grandes.to_string())
    print("media PMAT por año:", val("SELECT anio, round(avg(PMAT)/100,2) FROM tc GROUP BY 1 ORDER BY 1"))
    print("% <50 por materia y año:")
    print(df("SELECT anio, " + ", ".join(f"round(100.0*count(*) FILTER (WHERE {g}<5000)/nullif(count({g}),0),1) {g}" for g in G) + " FROM tc GROUP BY 1 ORDER BY 1").to_string())


def pun13():
    titulo("PUN-13 globales con 1 decimal")
    d = df("SELECT anio, " + ", ".join(f"round(100.0*count(*) FILTER (WHERE {c}%10=0)/nullif(count({c}),0),1) {c}" for c in G) + " FROM tc GROUP BY 1 ORDER BY 1").set_index("anio")
    print(d.to_string())
    pares = [(g, y) for g in G for y in d.index if d.loc[y, g] == 100.0]
    print("materia-año con 100 % de segundo decimal 0:", pares)
    total = sum(val(f"SELECT count({g}) FROM tc WHERE anio={y}")[0][0] for g, y in pares)
    print("filas afectadas (suma):", total)


def pun14():
    titulo("PUN-14 coherencia de nulos global/subcompetencias (datos corregidos)")
    casos = []
    combos = subs_existentes()
    for (g, y), ex in combos.items():
        a, b = val(f"""SELECT count(*) FILTER (WHERE {g} IS NOT NULL AND ({' OR '.join(f'{c} IS NULL' for c in ex)})),
                              count(*) FILTER (WHERE {g} IS NULL AND ({' OR '.join(f'{c} IS NOT NULL' for c in ex)}))
                       FROM tc WHERE anio={y}""")[0]
        if a or b:
            casos.append((g, y, a, b))
    print("combinaciones materia-año:", len(combos), "| con incoherencias (global sí/sub no, global no/sub sí):", casos)


def pun15():
    titulo("PUN-15 filas sin puntuaciones y cobertura")
    print("filas con las 24 columnas nulas:", val("SELECT count(*) FROM tc WHERE " + " AND ".join(f"{c} IS NULL" for c in S)))
    print("filas sin ninguna global:", val("SELECT count(*) FROM tc WHERE " + " AND ".join(f"{c} IS NULL" for c in G)))
    cov = cobertura()
    pct = cov[G].div(cov.n_filas, axis=0) * 100
    print(pct.round(2).to_string())
    print("francés por año, con inglés:", val("SELECT anio, count(PFRAN), count(*) FILTER (WHERE PFRAN IS NOT NULL AND PANG IS NOT NULL) FROM tc GROUP BY 1 ORDER BY 1"))


def pun16():
    titulo("PUN-16 PCAST 2024 y PMAT 2017 sin nulos")
    print(df("""SELECT anio, count(*) filas, count(PCAST) pcast, count(PMAT) pmat,
                round(100.0*count(PCAT)/count(*),2) cob_pcat, round(100.0*count(PMAT)/count(*),2) cob_pmat,
                count(*) FILTER (WHERE PCAT IS NULL) sin_pcat, round(avg(PCAST) FILTER (WHERE PCAT IS NULL)/100,2) pcast_de_sin_pcat,
                count(*) FILTER (WHERE PCAST=0) pcast0, count(*) FILTER (WHERE PCAST_EE=0) pcast_ee0
                FROM tc WHERE anio>=2014 GROUP BY 1 ORDER BY 1""").to_string())


def pun17():
    titulo("PUN-17 tamaño FactPuntuacion")
    con.execute(f"CREATE OR REPLACE TEMP VIEW u AS SELECT rid, anio, competencia, puntuacion FROM (UNPIVOT tc ON {', '.join(S)} INTO NAME competencia VALUE puntuacion)")
    gl = ", ".join(f"'{g}'" for g in G)
    print("total / globales / subcompetencias:", val(f"SELECT count(*), count(*) FILTER (WHERE competencia IN ({gl})), count(*) FILTER (WHERE competencia NOT IN ({gl})) FROM u"))
    d = df("SELECT u.anio, count(*) n, any_value(f.filas) filas FROM u JOIN (SELECT anio, count(*) filas FROM tc GROUP BY 1) f USING (anio) GROUP BY 1 ORDER BY 1")
    d["por_alumno"] = (d.n / d.filas).round(2)
    print(d.to_string())
    print("media por alumno:", round(d.n.sum() / d.filas.sum(), 2), "| sin PANG_EE 2015:", val("SELECT count(*) FROM u WHERE NOT (anio=2015 AND competencia='PANG_EE')"))


def pun18():
    titulo("PUN-18 niveles de logro 50/70/85 sobre globales corregidas")
    gl = ", ".join(f"'{g}'" for g in G)
    con.execute(f"CREATE OR REPLACE TEMP VIEW u AS SELECT rid, anio, competencia, puntuacion FROM (UNPIVOT tc ON {', '.join(S)} INTO NAME competencia VALUE puntuacion)")
    g = df(f"SELECT anio, competencia, puntuacion/100.0 p FROM u WHERE competencia IN ({gl})")
    g["nivel"] = pd.cut(g.p, [-1, 49.995, 69.995, 84.995, 101], labels=["Bajo", "Medio-bajo", "Medio-alto", "Alto"])
    t = pd.crosstab(g.competencia, g.nivel, normalize="index").mul(100).round(1)
    t.loc["TOTAL"] = (g.nivel.value_counts(normalize=True) * 100).round(1)
    print(t.to_string())
    print("acumulado <50/<70/<85:", [round((g.p < x).mean() * 100, 1) for x in (50, 70, 85)])
    print(g.groupby("competencia").p.quantile([.1, .5]).unstack().round(2).to_string())
    print("% en [95,100]:", g.assign(a=g.p >= 95).groupby("competencia").a.mean().mul(100).round(1).to_dict())
    print("efecto de los suelos sobre el umbral 50:")
    print("  PANG 2015 = 48,79:", val("SELECT count(*) FILTER (WHERE PANG=4879), count(*) FILTER (WHERE PANG<5000), count(PANG) FROM tc WHERE anio=2015"))
    print("  PANG_CO 2015 = 53,19 / PANG_CE 2015 = 45,00:", val("SELECT count(*) FILTER (WHERE PANG_CO=5319), count(*) FILTER (WHERE PANG_CE=4500) FROM tc WHERE anio=2015"))
    print("  PANG_CO 2016 en [51,70; 55,80]:", val("SELECT count(*) FROM tc WHERE anio=2016 AND PANG_CO BETWEEN 5170 AND 5580"),
          "| PANG_CE 2016 en {53; 53,67; 54,5; 54,8}:", val("SELECT count(*) FROM tc WHERE anio=2016 AND PANG_CE IN (5300,5367,5450,5480)"))


def pun19():
    titulo("PUN-19 francés")
    print(val("SELECT anio, count(PFRAN), round(100.0*count(PFRAN)/count(*),2), count(*) FILTER (WHERE PFRAN IS NOT NULL AND PANG IS NOT NULL) FROM tc GROUP BY 1 ORDER BY 1"))
    print("total filas PFRAN:", val("SELECT count(PFRAN) FROM tc"))
    s = saltos("tc")
    print(s[(s.col == "PFRAN_EE") & (s.anio1 == 2014)].to_dict("records"), s[(s.col == "PFRAN_CO") & (s.anio1 == 2025)].to_dict("records"))


def pun20():
    titulo("PUN-20 duplicados")
    print("CODI nulos por año:", val("SELECT anio, count(*) FILTER (WHERE codi IS NULL) FROM t GROUP BY 1 ORDER BY 1"))
    print("CODI repetidos dentro de un año:", val("SELECT anio, count(*), sum(n) FROM (SELECT anio, codi, count(*) n FROM t WHERE codi IS NOT NULL GROUP BY 1,2 HAVING count(*)>1) GROUP BY 1"))
    print("CODI en más de un año (n_años, n):", val("SELECT k, count(*) FROM (SELECT codi, count(DISTINCT anio) k FROM t WHERE codi IS NOT NULL GROUP BY 1 HAVING count(DISTINCT anio)>1) GROUP BY 1"))
    cols = ", ".join(f'"{c}"' for c in TODAS)
    print("copias sobrantes idénticas en 32 columnas:", val(f'SELECT "ANY", sum(n-1) FROM (SELECT {cols}, count(*) n FROM raw GROUP BY ALL HAVING count(*)>1) GROUP BY 1 ORDER BY 1'))
    print(df(f'SELECT "ANY", PCAT, PCAST, PMAT, PMAT_NC, PMAT_EFM, PMAT_CR, PANG, n FROM (SELECT {cols}, count(*) n FROM raw GROUP BY ALL HAVING count(*)>1) ORDER BY 1').to_string())


def pun21():
    titulo("PUN-21 escala PANG_EE")
    print(df("""SELECT anio, count(DISTINCT PANG_EE) distintos, count(*) FILTER (WHERE PANG_EE=0) ceros, count(PANG_EE) nn,
                round(avg(PANG_EE)/100,2) media, list(DISTINCT PANG_EE/100.0 ORDER BY PANG_EE/100.0) valores
                FROM tc WHERE PANG_EE IS NOT NULL GROUP BY 1 ORDER BY 1""").to_string())


def pun22():
    titulo("PUN-22 granularidad 2023-2025")
    print(df("SELECT anio, " + ", ".join(f"count(DISTINCT {c}) {c}" for c in ["PCAT_EE", "PCAST_EE", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3"]) +
             " FROM tc WHERE anio BETWEEN 2023 AND 2025 GROUP BY 1 ORDER BY 1").to_string())
    print("PMED_COMP2 2024 más frecuentes:", val("SELECT PMED_COMP2/100.0, count(*) FROM tc WHERE anio=2024 AND PMED_COMP2 IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 6"))
    print("PMED 2024 = media simple (±0,065):", val("SELECT count(*) FILTER (WHERE abs(PMED - (PMED_COMP1+PMED_COMP2+PMED_COMP3)/3.0) <= 6.5), count(PMED) FROM tc WHERE anio=2024"))


def pun23():
    titulo("PUN-23 descuadres residuales")
    p = tabla_pesos()
    print(p[p.fuera_065 > 0].to_string())
    print("PMAT 2016: globales de las filas que no cuadran:",
          val("SELECT PMAT/100.0, count(*) FROM tc WHERE anio=2016 AND abs(PMAT*100 - (35*PMAT_NC+35*PMAT_EFM+30*PMAT_CR)) > 650 GROUP BY 1"),
          "| filas con PMAT=59,20:", val("SELECT count(*), min((35*PMAT_NC+35*PMAT_EFM+30*PMAT_CR)/10000.0), max((35*PMAT_NC+35*PMAT_EFM+30*PMAT_CR)/10000.0) FROM tc WHERE anio=2016 AND PMAT=5920"),
          "| frecuencia de valores vecinos:", val("SELECT PMAT/100.0, count(*) FROM tc WHERE anio=2016 AND PMAT IN (5918,5919,5920,5921,5922) GROUP BY 1 ORDER BY 1"))
    for g, a, b, y in (("PCAT", "PCAT_CL", "PCAT_EE", 2009), ("PCAST", "PCAST_CL", "PCAST_EE", 2009), ("PCAST", "PCAST_CL", "PCAST_EE", 2010)):
        k = val(f"SELECT count(*) FILTER (WHERE k>1), count(*) FROM (SELECT {a}, {b}, count(DISTINCT {g}) k FROM tc WHERE anio={y} AND {g} IS NOT NULL GROUP BY 1,2)")
        print(f"{g} {y}: combinaciones (CL,EE) con más de una global distinta / total:", k)


SECCIONES = {f"PUN-{i:02d}": f for i, f in enumerate([pun01, pun02, pun03, pun04, pun05, pun06, pun07, pun08, pun09, pun10, pun11, pun12,
                                                      pun13, pun14, pun15, pun16, pun17, pun18, pun19, pun20, pun21, pun22, pun23], start=1)}

if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(SECCIONES)
    cargar()
    print("filas cargadas:", val("SELECT count(*) FROM raw"), "| años:", val("SELECT list(DISTINCT anio ORDER BY anio) FROM t"))
    for s in pedidas:
        SECCIONES[s]()
