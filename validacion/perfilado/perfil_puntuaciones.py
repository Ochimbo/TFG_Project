"""Perfilado exhaustivo de las 24 columnas de puntuación de Datos.csv.

TFG: Cuadro de Mando Integral (Power BI) - Avaluació de sisè d'educació primària.
Fuente: Portal de Dades Obertes de la Generalitat (dataset rk5x-gny6).

Uso:
    .venv/bin/python validacion/perfilado/perfil_puntuaciones.py

Lee Datos.csv en solo lectura (no lo modifica), imprime todas las cifras por
secciones y guarda las tablas intermedias en
validacion/perfilado/salidas_puntuaciones/*.csv
"""

import os

import duckdb
import numpy as np
import pandas as pd

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV = os.path.join(RAIZ, "Datos.csv")
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salidas_puntuaciones")
os.makedirs(SALIDA, exist_ok=True)

pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_rows", 2000)

PUNT = [
    "PCAT", "PCAT_CL", "PCAT_EE", "PCAST", "PCAST_CL", "PCAST_EE",
    "PMAT", "PMAT_NC", "PMAT_EFM", "PMAT_CR", "PANG", "PANG_CO", "PANG_CE",
    "PFRAN", "PFRAN_CO", "PFRAN_CE", "PANG_EE", "PFRAN_EE", "PCAT_CO",
    "PCAST_CO", "PMED", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3",
]
MATERIAS = {
    "PCAT": ["PCAT_CL", "PCAT_EE", "PCAT_CO"],
    "PCAST": ["PCAST_CL", "PCAST_EE", "PCAST_CO"],
    "PMAT": ["PMAT_NC", "PMAT_EFM", "PMAT_CR"],
    "PANG": ["PANG_CO", "PANG_CE", "PANG_EE"],
    "PFRAN": ["PFRAN_CO", "PFRAN_CE", "PFRAN_EE"],
    "PMED": ["PMED_COMP1", "PMED_COMP2", "PMED_COMP3"],
}
GLOBALES = list(MATERIAS)
TOL = 0.065
TOL_1DEC = 0.115
UMBRALES = [50, 70, 85]
NIVELES = ["Bajo", "Medio-bajo", "Medio-alto", "Alto"]


def q(c):
    return '"' + c + '"'


def titulo(txt):
    print("\n" + "=" * 110)
    print(txt)
    print("=" * 110)


def guardar(df, nombre):
    df.to_csv(os.path.join(SALIDA, nombre), index=False)


con = duckdb.connect()
con.execute(f"""
    CREATE TABLE raw AS
    SELECT row_number() OVER () AS rid, *
    FROM read_csv('{CSV}', all_varchar=true, header=true)
""")
sel = ", ".join(f"TRY_CAST(replace({q(c)}, ',', '.') AS DOUBLE) AS {q(c)}" for c in PUNT)
con.execute(f'CREATE TABLE t AS SELECT rid, CAST("ANY" AS INTEGER) AS anio, CODI_ALUMNE, {sel} FROM raw')
ANIOS = [r[0] for r in con.execute("SELECT DISTINCT anio FROM t ORDER BY 1").fetchall()]

# Tabla corregida: rotaciones de columnas detectadas en la sección 4.
# PCAST 2017: PCAST->CL real, PCAST_CL->EE real, PCAST_EE->global real.
# PFRAN 2016: PFRAN->CO real, PFRAN_CO->CE real, PFRAN_CE->EE real, PFRAN_EE->global real.
cols_corr = []
for c in PUNT:
    expr = q(c)
    if c == "PCAST":
        expr = 'CASE WHEN anio=2017 THEN "PCAST_EE" ELSE "PCAST" END'
    elif c == "PCAST_CL":
        expr = 'CASE WHEN anio=2017 THEN "PCAST" ELSE "PCAST_CL" END'
    elif c == "PCAST_EE":
        expr = 'CASE WHEN anio=2017 THEN "PCAST_CL" ELSE "PCAST_EE" END'
    elif c == "PFRAN":
        expr = 'CASE WHEN anio=2016 THEN "PFRAN_EE" ELSE "PFRAN" END'
    elif c == "PFRAN_CO":
        expr = 'CASE WHEN anio=2016 THEN "PFRAN" ELSE "PFRAN_CO" END'
    elif c == "PFRAN_CE":
        expr = 'CASE WHEN anio=2016 THEN "PFRAN_CO" ELSE "PFRAN_CE" END'
    elif c == "PFRAN_EE":
        expr = 'CASE WHEN anio=2016 THEN "PFRAN_CE" ELSE "PFRAN_EE" END'
    cols_corr.append(f"{expr} AS {q(c)}")
con.execute(f"CREATE TABLE tc AS SELECT rid, anio, CODI_ALUMNE, {', '.join(cols_corr)} FROM t")

# ---------------------------------------------------------------------------
titulo("0. VOLUMEN")
print(con.execute('SELECT anio, count(*) AS filas FROM t GROUP BY 1 ORDER BY 1').df().to_string(index=False))
print("Total filas:", con.execute("SELECT count(*) FROM t").fetchone()[0])

# ---------------------------------------------------------------------------
titulo("1. FORMATO DE LAS 24 COLUMNAS DE PUNTUACIÓN")
with open(CSV, "rb") as fh:
    n_comillas_vacias = 0
    prev = b""
    while True:
        bloque = fh.read(1 << 24)
        if not bloque:
            break
        n_comillas_vacias += (prev + bloque).count(b'""') - prev.count(b'""')
        prev = bloque[-1:]
print('Apariciones de "" (cadena vacía entre comillas) en el fichero:', n_comillas_vacias)
filas = []
for c in PUNT:
    r = con.execute(f"""
        SELECT '{c}',
          count(r.{q(c)}) AS no_nulos,
          count(*) FILTER (WHERE r.{q(c)} = '') AS cadenas_vacias,
          count(*) FILTER (WHERE regexp_full_match(r.{q(c)}, '[0-9]{{1,3}},[0-9]{{2}}')) AS formato_coma_2dec,
          count(*) FILTER (WHERE r.{q(c)} LIKE '%.%') AS con_punto,
          count(*) FILTER (WHERE r.{q(c)} IS NOT NULL AND t.{q(c)} IS NULL) AS no_parseables,
          count(*) FILTER (WHERE t.{q(c)} < 0) AS negativos,
          count(*) FILTER (WHERE t.{q(c)} > 100) AS mayores_100,
          min(t.{q(c)}) AS minimo, max(t.{q(c)}) AS maximo,
          count(DISTINCT t.{q(c)}) AS valores_distintos
        FROM raw r JOIN t USING (rid)""").fetchone()
    filas.append(r)
fmt = pd.DataFrame(filas, columns=["columna", "no_nulos", "cadenas_vacias", "formato_coma_2dec", "con_punto",
                                   "no_parseables", "negativos", "mayores_100", "minimo", "maximo", "valores_distintos"])
print(fmt.to_string(index=False))
guardar(fmt, "01_formato.csv")
print("\nTotal valores no nulos en las 24 columnas:", int(fmt.no_nulos.sum()),
      "| con formato 'ddd,dd':", int(fmt.formato_coma_2dec.sum()),
      "| no parseables:", int(fmt.no_parseables.sum()))

print("\n% de valores cuyo 2º decimal es 0 (100 % => la columna-año está redondeada a 1 decimal):")
sel = ", ".join(f"round(100.0*count(*) FILTER (WHERE right({q(c)},1)='0')/nullif(count({q(c)}),0),1) AS {q(c)}" for c in PUNT)
dec = con.execute(f'SELECT CAST("ANY" AS INTEGER) AS anio, {sel} FROM raw GROUP BY 1 ORDER BY 1').df().set_index("anio").T
print(dec.to_string())
guardar(dec.reset_index().rename(columns={"index": "columna"}), "01_pct_segundo_decimal_cero.csv")
print("\nColumnas GLOBALES redondeadas a 1 decimal (100 % con 2º decimal 0):")
for g in GLOBALES:
    anios = [a for a in dec.columns if dec.loc[g, a] == 100.0]
    print(f"  {g}: {anios}")

# ---------------------------------------------------------------------------
titulo("2. MATRIZ DE COBERTURA (% NO NULOS POR COLUMNA Y AÑO) - datos originales")
sel = ", ".join(f"round(100.0*count({q(c)})/count(*),1) AS {q(c)}" for c in PUNT)
cob = con.execute(f"SELECT anio, {sel} FROM t GROUP BY 1 ORDER BY 1").df().set_index("anio").T
print(cob.to_string())
guardar(cob.reset_index().rename(columns={"index": "columna"}), "02_cobertura_pct.csv")
sel = ", ".join(f"count({q(c)}) AS {q(c)}" for c in PUNT)
cobn = con.execute(f"SELECT anio, count(*) AS filas, {sel} FROM t GROUP BY 1 ORDER BY 1").df().set_index("anio").T
print("\nConteo de no nulos:")
print(cobn.to_string())
guardar(cobn.reset_index().rename(columns={"index": "columna"}), "02_cobertura_n.csv")
print("\nAños en que existe cada columna (algún no nulo):")
for c in PUNT:
    anios = [a for a in ANIOS if cobn.loc[c, a] > 0]
    print(f"  {c:11s} {anios[0]}-{anios[-1]}  ({len(anios)} convocatorias)")
print("\nFrancés (PFRAN) y solapamiento con inglés (PANG):")
print(con.execute("""
    SELECT anio,
      count(*) FILTER (WHERE PFRAN IS NOT NULL OR PFRAN_CO IS NOT NULL) AS alumnos_frances,
      count(*) FILTER (WHERE (PFRAN IS NOT NULL OR PFRAN_CO IS NOT NULL) AND PANG IS NOT NULL) AS frances_y_ingles,
      round(100.0*count(*) FILTER (WHERE PFRAN IS NOT NULL OR PFRAN_CO IS NOT NULL)/count(*),2) AS pct_frances
    FROM t GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
print("\nFilas con PCAST informada y sin PCAT, PMAT, PANG ni PMED (solo castellano), por año:")
print(con.execute("""
    SELECT anio,
      count(*) FILTER (WHERE PCAT IS NULL AND PMAT IS NULL AND PANG IS NULL AND PMED IS NULL AND PCAST IS NOT NULL) AS solo_pcast,
      count(*) FILTER (WHERE PCAST IS NULL) AS pcast_nulo,
      count(*) FILTER (WHERE PCAT IS NULL) AS pcat_nulo,
      count(*) FILTER (WHERE PMAT IS NULL) AS pmat_nulo
    FROM t GROUP BY 1 ORDER BY 1""").df().to_string(index=False))

# ---------------------------------------------------------------------------
titulo("3. ESTADÍSTICOS POR COLUMNA Y AÑO (datos originales, sin corregir)")
partes = []
for c in PUNT:
    partes.append(con.execute(f"""
        SELECT '{c}' AS columna, anio, count({q(c)}) AS n,
          round(avg({q(c)}),2) AS media, round(stddev_samp({q(c)}),2) AS sd,
          min({q(c)}) AS min, max({q(c)}) AS max,
          round(quantile_cont({q(c)},0.10),2) AS p10, round(quantile_cont({q(c)},0.25),2) AS p25,
          round(quantile_cont({q(c)},0.50),2) AS p50, round(quantile_cont({q(c)},0.75),2) AS p75,
          round(quantile_cont({q(c)},0.90),2) AS p90,
          count(*) FILTER (WHERE {q(c)} = 0) AS n_cero, count(*) FILTER (WHERE {q(c)} = 100) AS n_100,
          count(DISTINCT {q(c)}) AS n_distintos
        FROM t WHERE {q(c)} IS NOT NULL GROUP BY anio ORDER BY anio""").df())
est = pd.concat(partes, ignore_index=True)
print(est.to_string(index=False))
guardar(est, "03_estadisticos_columna_anio.csv")

print("\nSaltos bruscos entre convocatorias consecutivas (|Δmedia| >= 5 o |Δsd| >= 5 o n_distintos x3 / ÷3):")
saltos = []
for c in PUNT:
    e = est[est.columna == c].sort_values("anio").reset_index(drop=True)
    for i in range(1, len(e)):
        a, b = e.iloc[i - 1], e.iloc[i]
        dm, ds = b.media - a.media, b.sd - a.sd
        rd = b.n_distintos / a.n_distintos
        if abs(dm) >= 5 or abs(ds) >= 5 or rd >= 3 or rd <= 1 / 3:
            saltos.append(dict(columna=c, de=int(a.anio), a=int(b.anio), media_de=a.media, media_a=b.media,
                               delta_media=round(dm, 2), sd_de=a.sd, sd_a=b.sd, distintos_de=int(a.n_distintos),
                               distintos_a=int(b.n_distintos)))
saltos = pd.DataFrame(saltos)
print(saltos.to_string(index=False))
guardar(saltos, "03_saltos.csv")

print("\nMedia (sd) de la puntuación GLOBAL por materia y año, datos CORREGIDOS (rotaciones PCAST 2017 y PFRAN 2016):")
sel = ", ".join(f"round(avg({q(g)}),2) AS {q(g)}" for g in GLOBALES)
medias = con.execute(f"SELECT anio, {sel} FROM tc GROUP BY 1 ORDER BY 1").df().set_index("anio").T
print(medias.to_string())
sel = ", ".join(f"round(stddev_samp({q(g)}),2) AS {q(g)}" for g in GLOBALES)
print(con.execute(f"SELECT anio, {sel} FROM tc GROUP BY 1 ORDER BY 1").df().set_index("anio").T.to_string())
guardar(medias.reset_index().rename(columns={"index": "materia"}), "03_media_global_corregida.csv")

print("\nColumna-año con máximo < 100 (n >= 1000): techo de escala distinto de 100")
print(est[(est["max"] < 100) & (est.n >= 1000)][["columna", "anio", "n", "max", "p90", "n_distintos"]].to_string(index=False))

# ---------------------------------------------------------------------------
titulo("4. RELACIÓN GLOBAL vs SUBCOMPETENCIAS")


def ajuste_robusto(X, y, tol=TOL, iters=20):
    mask = np.ones(len(y), bool)
    w = None
    for _ in range(iters):
        w, *_ = np.linalg.lstsq(X[mask], y[mask], rcond=None)
        e = np.abs(y - X @ w)
        nuevo = e <= max(tol, np.quantile(e[mask], 0.5))
        if (nuevo == mask).all():
            break
        mask = nuevo
    return w


def tolerancia(g, anio):
    return TOL_1DEC if dec.loc[g, anio] == 100.0 else TOL


def analisis_relacion(tabla):
    filas = []
    for g, subs in MATERIAS.items():
        df = con.execute(f"SELECT anio, {q(g)}, {', '.join(q(s) for s in subs)} FROM {tabla} WHERE {q(g)} IS NOT NULL").df()
        for anio, d in df.groupby("anio"):
            tol = tolerancia(g, anio)
            presentes = [s for s in subs if d[s].notna().any()]
            dd = d.dropna(subset=presentes)
            X, y = dd[presentes].to_numpy(), dd[g].to_numpy()
            e_simple = y - X.mean(axis=1)
            w_ols, *_ = np.linalg.lstsq(X, y, rcond=None)
            e_ols = y - X @ w_ols
            w_rob = ajuste_robusto(X, y, tol)
            e_rob = y - X @ w_rob
            fit_simple = (np.abs(e_simple) <= tol).mean()
            fit_rob = (np.abs(e_rob) <= tol).mean()
            if (w_rob < -0.001).any():
                tipo = "pesos negativos (rotación)"
            elif fit_simple >= 0.95:
                tipo = "media simple"
            elif fit_rob >= 0.95:
                tipo = "media ponderada"
            else:
                tipo = "inconsistente/mixta"
            filas.append(dict(
                materia=g, anio=int(anio), subcompetencias="+".join(s.split("_", 1)[1] for s in presentes), n=len(dd), tol=tol,
                simple_err_medio=round(np.abs(e_simple).mean(), 3), simple_err_max=round(np.abs(e_simple).max(), 2),
                simple_pct_ok=round(100 * fit_simple, 1),
                pesos_ols=" / ".join(f"{x:.4f}" for x in w_ols), ols_err_medio=round(np.abs(e_ols).mean(), 3),
                ols_err_max=round(np.abs(e_ols).max(), 2),
                pesos_robustos=" / ".join(f"{x:.4f}" for x in w_rob), suma_pesos=round(w_rob.sum(), 4),
                rob_err_medio=round(np.abs(e_rob).mean(), 3), rob_err_max=round(np.abs(e_rob).max(), 2),
                rob_pct_ok=round(100 * fit_rob, 1), filas_fuera_tol=int((np.abs(e_rob) > tol).sum()), tipo=tipo,
            ))
    return pd.DataFrame(filas)


print(f"Tolerancia de ajuste: |global - predicción| <= {TOL} puntos ({TOL_1DEC} si la global del año está redondeada a 1 decimal).")
print("'pct_ok' = % filas dentro de tolerancia.")
print("Pesos OLS = regresión lineal sin intercepto sobre todas las filas completas; pesos robustos = OLS")
print("iterativo descartando residuos grandes (resistente a filas erróneas).")
print("\n4.a Datos ORIGINALES:")
rel_orig = analisis_relacion("t")
print(rel_orig.to_string(index=False))
guardar(rel_orig, "04_relacion_global_subcompetencias_original.csv")

print("\n4.b Búsqueda de rotaciones de columnas (otra columna de la materia actúa como global con pesos >= 0):")
rot = []
for g, subs in MATERIAS.items():
    df = con.execute(f"SELECT anio, {q(g)}, {', '.join(q(s) for s in subs)} FROM t").df()
    for anio, d in df.groupby("anio"):
        cols = [c for c in [g] + subs if d[c].notna().any()]
        if len(cols) < 3:
            continue
        dd = d.dropna(subset=cols)
        for tgt in cols:
            otras = [c for c in cols if c != tgt]
            X, y = dd[otras].to_numpy(), dd[tgt].to_numpy()
            w, *_ = np.linalg.lstsq(X, y, rcond=None)
            ok = (np.abs(y - X @ w) <= tolerancia(g, anio)).mean()
            if tgt != g and (w >= -0.001).all() and ok >= 0.9:
                rot.append(dict(materia=g, anio=int(anio), columna_que_contiene_la_global=tgt,
                                predictores=" + ".join(f"{x:.3f}*{c}" for x, c in zip(w, otras)), pct_ok=round(100 * ok, 1), n=len(dd)))
rot = pd.DataFrame(rot)
print(rot.to_string(index=False))
guardar(rot, "04_rotaciones.csv")
print("\nValores distintos de las columnas afectadas (original):")
print(est[((est.columna.str.startswith("PCAST")) & (est.anio.isin([2016, 2017, 2018]))) |
          ((est.columna.str.startswith("PFRAN")) & (est.anio.isin([2015, 2016, 2017])))]
      [["columna", "anio", "n", "media", "sd", "n_distintos"]].to_string(index=False))

print("\nEstadísticos de las columnas rotadas tras la corrección:")
partes = []
for c in ["PCAST", "PCAST_CL", "PCAST_EE", "PFRAN", "PFRAN_CO", "PFRAN_CE", "PFRAN_EE"]:
    partes.append(con.execute(f"""SELECT '{c}' AS columna, anio, count({q(c)}) n, round(avg({q(c)}),2) media,
        round(stddev_samp({q(c)}),2) sd, count(DISTINCT {q(c)}) n_distintos
        FROM tc WHERE {q(c)} IS NOT NULL AND anio IN (2016, 2017) GROUP BY anio ORDER BY anio""").df())
print(pd.concat(partes).to_string(index=False))

print("\n4.c Datos CORREGIDOS (rotaciones PCAST 2017 y PFRAN 2016 deshechas):")
rel_corr = analisis_relacion("tc")
print(rel_corr.to_string(index=False))
guardar(rel_corr, "04_relacion_global_subcompetencias_corregida.csv")

print("\n4.d Resumen de pesos por materia y periodo (pesos robustos, datos corregidos):")
rel_corr["pesos_red"] = rel_corr.pesos_robustos.apply(lambda s: " / ".join(f"{float(x):.2f}" for x in s.split(" / ")))
for g in GLOBALES:
    r = rel_corr[rel_corr.materia == g]
    print(f"  {g}:")
    for (subs, pesos, tipo), grp in r.groupby(["subcompetencias", "pesos_red", "tipo"], sort=False):
        print(f"     {subs:18s} pesos {pesos:20s} {tipo:20s} años {list(grp.anio)}")

print("\n4.e Detalle de discrepancias en años 'inconsistente/mixta' o con filas fuera de tolerancia:")
print("PANG_EE 2015: valores y valor implícito de EE si la global fuese la media simple (EE_impl = 3*PANG - CO - CE):")
d = con.execute("SELECT PANG, PANG_CO, PANG_CE, PANG_EE FROM t WHERE anio=2015 AND PANG IS NOT NULL").df()
d["ee_impl"] = (3 * d.PANG - d.PANG_CO - d.PANG_CE).round(0)
d["ok_media_simple"] = (d.PANG - d[["PANG_CO", "PANG_CE", "PANG_EE"]].mean(axis=1)).abs() <= TOL
print(d.groupby("PANG_EE").agg(n=("ok_media_simple", "size"), pct_ok_media_simple=("ok_media_simple", "mean"),
                               ee_impl_min=("ee_impl", "min"), ee_impl_mediana=("ee_impl", "median"),
                               ee_impl_max=("ee_impl", "max")).round(3).to_string())
print("Distribución de PANG_EE por año (valores distintos):")
for a in [2013, 2014, 2015, 2016, 2017]:
    print(f"  {a}:", con.execute(f"SELECT PANG_EE, count(*) FROM t WHERE anio={a} AND PANG_EE IS NOT NULL GROUP BY 1 ORDER BY 1").fetchall())
for g, w, anio in [("PCAST", [0.6, 0.4], 2017), ("PANG", [0.35, 0.5, 0.15], 2022), ("PCAST", [0.5, 0.35, 0.15], 2022),
                   ("PFRAN", [0.35, 0.5, 0.15], 2022), ("PCAT", [0.5, 0.35, 0.15], 2022),
                   ("PMAT", [0.35, 0.35, 0.30], 2016), ("PANG", [0.5, 0.5], 2011)]:
    subs = MATERIAS[g][:len(w)]
    d = con.execute(f"SELECT {q(g)} g, {', '.join(q(s) for s in subs)} FROM tc WHERE anio={anio} AND {q(g)} IS NOT NULL").df().dropna()
    e = d.g - d[subs].to_numpy() @ np.array(w)
    fuera = e[e.abs() > tolerancia(g, anio)]
    print(f"\n{g} {anio} con pesos {w}: n={len(d)}, fuera de tolerancia={len(fuera)} ({100*len(fuera)/len(d):.1f} %), "
          f"error medio fuera={fuera.abs().mean() if len(fuera) else 0:.3f}")
    print("   residuo redondeado a 0,1 (top 8):", e.round(1).value_counts().head(8).to_dict())

print("\n2011 - techo 99,73:")
print(con.execute("""SELECT 'PANG_CO' c, count(*) FILTER (WHERE PANG_CO=99.73) n_9973, count(PANG_CO) n FROM t WHERE anio=2011
                     UNION ALL SELECT 'PCAT_CL', count(*) FILTER (WHERE PCAT_CL=99.73), count(PCAT_CL) FROM t WHERE anio=2011
                     UNION ALL SELECT 'PCAST_CL', count(*) FILTER (WHERE PCAST_CL=99.73), count(PCAST_CL) FROM t WHERE anio=2011""").df().to_string(index=False))

# ---------------------------------------------------------------------------
titulo("5. COHERENCIA DE NULOS GLOBAL vs SUBCOMPETENCIAS (datos corregidos)")
coh = []
for g, subs in MATERIAS.items():
    for anio in ANIOS:
        presentes = [s for s in subs if con.execute(f"SELECT count({q(s)}) FROM tc WHERE anio={anio}").fetchone()[0] > 0]
        if not presentes and con.execute(f"SELECT count({q(g)}) FROM tc WHERE anio={anio}").fetchone()[0] == 0:
            continue
        alguna_nula = " OR ".join(f"{q(s)} IS NULL" for s in presentes)
        alguna_no_nula = " OR ".join(f"{q(s)} IS NOT NULL" for s in presentes)
        todas_nulas = " AND ".join(f"{q(s)} IS NULL" for s in presentes)
        r = con.execute(f"""SELECT count({q(g)}),
             count(*) FILTER (WHERE {q(g)} IS NOT NULL AND ({alguna_nula})),
             count(*) FILTER (WHERE {q(g)} IS NOT NULL AND ({todas_nulas})),
             count(*) FILTER (WHERE {q(g)} IS NULL AND ({alguna_no_nula})),
             {', '.join(f"count(*) FILTER (WHERE {q(g)} IS NOT NULL AND {q(s)} IS NULL)" for s in presentes)},
             {', '.join(f"count(*) FILTER (WHERE {q(g)} IS NULL AND {q(s)} IS NOT NULL)" for s in presentes)}
             FROM tc WHERE anio={anio}""").fetchone()
        k = len(presentes)
        coh.append(dict(materia=g, anio=anio, subcompetencias="+".join(s.split("_", 1)[1] for s in presentes),
                        global_no_nula=r[0], global_si_alguna_sub_nula=r[1], global_si_todas_sub_nulas=r[2],
                        global_nula_alguna_sub_si=r[3],
                        detalle_global_si_sub_no=dict(zip([s for s in presentes], r[4:4 + k])),
                        detalle_global_no_sub_si=dict(zip([s for s in presentes], r[4 + k:4 + 2 * k]))))
coh = pd.DataFrame(coh)
print(coh[["materia", "anio", "subcompetencias", "global_no_nula", "global_si_alguna_sub_nula",
           "global_si_todas_sub_nulas", "global_nula_alguna_sub_si"]].to_string(index=False))
print("\nCasos no nulos en detalle:")
print(coh[(coh.global_si_alguna_sub_nula > 0) | (coh.global_nula_alguna_sub_si > 0)].to_string(index=False))
guardar(coh, "05_coherencia_nulos.csv")
print("\nTotales: global informada con alguna subcompetencia nula =", int(coh.global_si_alguna_sub_nula.sum()),
      "| global nula con alguna subcompetencia informada =", int(coh.global_nula_alguna_sub_si.sum()))

# ---------------------------------------------------------------------------
titulo("6. FILAS SIN NINGUNA PUNTUACIÓN (las 24 columnas nulas)")
todas_nulas = " AND ".join(f"{q(c)} IS NULL" for c in PUNT)
globales_nulas = " AND ".join(f"{q(c)} IS NULL" for c in GLOBALES)
sinp = con.execute(f"""SELECT anio, count(*) AS filas,
        count(*) FILTER (WHERE {todas_nulas}) AS sin_ninguna_puntuacion,
        round(100.0*count(*) FILTER (WHERE {todas_nulas})/count(*),2) AS pct,
        count(*) FILTER (WHERE {globales_nulas}) AS sin_ninguna_global
      FROM tc GROUP BY 1 ORDER BY 1""").df()
print(sinp.to_string(index=False))
print("Total sin ninguna puntuación:", int(sinp.sin_ninguna_puntuacion.sum()),
      "| total sin ninguna global:", int(sinp.sin_ninguna_global.sum()))
guardar(sinp, "06_filas_sin_puntuacion.csv")

# ---------------------------------------------------------------------------
titulo("7. TAMAÑO DE FactPuntuacion (UNPIVOT de las 24 columnas descartando nulos)")
unp = con.execute(f"""
    SELECT anio, count(*) AS filas_fact_puntuacion
    FROM (UNPIVOT tc ON {', '.join(q(c) for c in PUNT)} INTO NAME competencia VALUE puntuacion)
    WHERE puntuacion IS NOT NULL GROUP BY 1 ORDER BY 1""").df()
glob = con.execute(f"""
    SELECT anio, count(*) AS filas_solo_globales
    FROM (UNPIVOT tc ON {', '.join(q(c) for c in GLOBALES)} INTO NAME competencia VALUE puntuacion)
    WHERE puntuacion IS NOT NULL GROUP BY 1 ORDER BY 1""").df()
fe = con.execute(f"""SELECT anio, count(*) AS filas_fact_evaluacion,
        count(*) FILTER (WHERE NOT ({todas_nulas})) AS fact_evaluacion_con_alguna_puntuacion
      FROM tc GROUP BY 1 ORDER BY 1""").df()
unp = unp.merge(glob, on="anio").merge(fe, on="anio")
unp["subcompetencias"] = unp.filas_fact_puntuacion - unp.filas_solo_globales
unp["media_puntuaciones_por_alumno"] = (unp.filas_fact_puntuacion / unp.fact_evaluacion_con_alguna_puntuacion).round(2)
print(unp.to_string(index=False))
print("TOTAL FactPuntuacion:", int(unp.filas_fact_puntuacion.sum()), "| de ellas globales:", int(unp.filas_solo_globales.sum()),
      "| subcompetencias:", int(unp.subcompetencias.sum()))
print("TOTAL FactEvaluacion (todas las filas):", int(unp.filas_fact_evaluacion.sum()),
      "| con alguna puntuación:", int(unp.fact_evaluacion_con_alguna_puntuacion.sum()))
guardar(unp, "07_tamano_fact_puntuacion.csv")

# ---------------------------------------------------------------------------
titulo("8. DISTRIBUCIÓN DE PUNTUACIONES GLOBALES Y PROPUESTA DE NIVELES DE LOGRO (datos corregidos)")
glob_long = con.execute(f"""
    SELECT anio, competencia AS materia, puntuacion
    FROM (UNPIVOT tc ON {', '.join(q(c) for c in GLOBALES)} INTO NAME competencia VALUE puntuacion)
    WHERE puntuacion IS NOT NULL""").df()
glob_long["tramo"] = (np.minimum(np.floor(glob_long.puntuacion / 5) * 5, 95)).astype(int)
glob_long["tramo"] = glob_long.tramo.map(lambda x: f"[{x:02d},{x + 5})" if x < 95 else "[95,100]")
hist = pd.crosstab(glob_long.tramo, glob_long.materia)
hist["TODAS"] = hist.sum(axis=1)
hist_pct = (100 * hist / hist.sum()).round(2)
print("Histograma en tramos de 5 puntos - recuento:")
print(hist.to_string())
print("\nHistograma en tramos de 5 puntos - % por materia:")
print(hist_pct.to_string())
guardar(hist.reset_index(), "08_histograma_n.csv")
guardar(hist_pct.reset_index(), "08_histograma_pct.csv")

print("\nPercentiles de la puntuación global por materia (todas las convocatorias):")
pct = glob_long.groupby("materia").puntuacion.describe(percentiles=[.05, .1, .2, .25, .5, .75, .8, .9]).round(2)
print(pct.to_string())

print("\n% acumulado por debajo de cortes candidatos:")
cortes = [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
acum = pd.DataFrame({f"<{c}": glob_long.groupby("materia").puntuacion.apply(lambda s, c=c: round(100 * (s < c).mean(), 1)) for c in cortes})
acum.loc["TODAS"] = [round(100 * (glob_long.puntuacion < c).mean(), 1) for c in cortes]
print(acum.to_string())


def nivel(v):
    return pd.cut(v, bins=[-0.001] + UMBRALES + [100.001], right=False, labels=NIVELES)


glob_long["nivel"] = nivel(glob_long.puntuacion)
print(f"\nPropuesta de niveles: Bajo [0,{UMBRALES[0]}), Medio-bajo [{UMBRALES[0]},{UMBRALES[1]}), "
      f"Medio-alto [{UMBRALES[1]},{UMBRALES[2]}), Alto [{UMBRALES[2]},100]")
niv = (100 * pd.crosstab(glob_long.materia, glob_long.nivel, normalize="index")).round(1)
niv.loc["TODAS"] = (100 * glob_long.nivel.value_counts(normalize=True)).reindex(NIVELES).round(1).values
print(niv.to_string())
guardar(niv.reset_index(), "08_niveles_por_materia.csv")
print("\n% en nivel Bajo por materia y año:")
bajo = (100 * glob_long.assign(b=glob_long.nivel == "Bajo").pivot_table(index="materia", columns="anio", values="b", aggfunc="mean")).round(1)
print(bajo.to_string())
print("\n% en nivel Alto por materia y año:")
alto = (100 * glob_long.assign(b=glob_long.nivel == "Alto").pivot_table(index="materia", columns="anio", values="b", aggfunc="mean")).round(1)
print(alto.to_string())
guardar(bajo.reset_index(), "08_pct_bajo_materia_anio.csv")
guardar(alto.reset_index(), "08_pct_alto_materia_anio.csv")
print("\nAlternativa relativa (percentiles 10/40/75 por materia y año): rango de cortes observados")
rel = glob_long.groupby(["materia", "anio"]).puntuacion.quantile([0.10, 0.40, 0.75]).unstack().round(1)
print(rel.groupby("materia").agg(["min", "max"]).to_string())

# ---------------------------------------------------------------------------
titulo("9. OTRAS ANOMALÍAS")
print("9.a PCAT_EE 2018 - suelo artificial en 49,40 (valores distintos y recuento):")
print(con.execute("SELECT PCAT_EE, count(*) FROM t WHERE anio=2018 AND PCAT_EE IS NOT NULL GROUP BY 1 ORDER BY 1").fetchall())
print("   Comparación 2019:", con.execute("SELECT count(*) FILTER (WHERE PCAT_EE<=50), count(PCAT_EE) FROM t WHERE anio=2019").fetchone(),
      "(<=50, n)")
print("   PCAT 2018 global <30 / <50 (%):", con.execute(
    "SELECT round(100.0*count(*) FILTER (WHERE PCAT<30)/count(PCAT),2), round(100.0*count(*) FILTER (WHERE PCAT<50)/count(PCAT),2) FROM t WHERE anio=2018").fetchone())

print("\n9.b PMAT 2019 - cola inferior ausente (% por debajo de 30/40/50 en 2017-2021):")
for c in ["PMAT", "PMAT_NC", "PMAT_EFM", "PMAT_CR"]:
    print(f"   {c}:", con.execute(f"""SELECT anio, min({q(c)}), round(100.0*count(*) FILTER (WHERE {q(c)}<30)/count({q(c)}),2),
        round(100.0*count(*) FILTER (WHERE {q(c)}<50)/count({q(c)}),2) FROM t WHERE anio BETWEEN 2017 AND 2021 GROUP BY 1 ORDER BY 1""").fetchall())

print("\n9.c Cobertura de PCAST 2024 (100 %) frente a otras materias y años:")
print(con.execute("""SELECT anio, count(*) filas, count(PCAST) pcast, count(PCAT) pcat, count(PMAT) pmat, count(PANG) pang,
     count(*) FILTER (WHERE PCAT IS NULL AND PCAST IS NOT NULL) pcast_sin_pcat,
     round(avg(PCAST) FILTER (WHERE PCAT IS NULL),2) media_pcast_sin_pcat,
     round(avg(PCAST) FILTER (WHERE PCAT IS NOT NULL),2) media_pcast_con_pcat,
     count(*) FILTER (WHERE PCAST=0) pcast_cero, count(*) FILTER (WHERE PCAST_EE=0) pcast_ee_cero
     FROM t WHERE anio BETWEEN 2021 AND 2025 GROUP BY 1 ORDER BY 1""").df().to_string(index=False))

print("\n9.d Filas exactamente duplicadas (las 32 columnas) por año:")
todas = ", ".join(q(c) for c in con.execute("SELECT * FROM raw LIMIT 0").df().columns if c != "rid")
print(con.execute(f"""SELECT "ANY", sum(n-1) AS copias_sobrantes, count(*) AS grupos
     FROM (SELECT {todas}, count(*) n FROM raw GROUP BY ALL HAVING count(*)>1) GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
print("CODI_ALUMNE repetido dentro del mismo año: grupos con puntuaciones idénticas vs distintas")
punt_raw = ", ".join(q(c) for c in PUNT)
print(con.execute(f"""
    WITH d AS (SELECT "ANY", CODI_ALUMNE, count(*) n, count(DISTINCT ({punt_raw})) n_dist_punt
               FROM raw WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1,2 HAVING count(*)>1)
    SELECT "ANY", count(*) grupos, sum(n) filas, count(*) FILTER (WHERE n_dist_punt=1) grupos_punt_identicas,
           count(*) FILTER (WHERE n_dist_punt>1) grupos_punt_distintas
    FROM d GROUP BY 1 ORDER BY 1""").df().to_string(index=False))

print("CODI_ALUMNE nulo por año y códigos repetidos entre años:")
print(con.execute("""SELECT anio, count(*) filas, count(*) - count(CODI_ALUMNE) codi_nulo, count(DISTINCT CODI_ALUMNE) codi_distintos
     FROM t GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
print("CODI_ALUMNE presentes en más de un año:", con.execute(
    "SELECT count(*) FROM (SELECT CODI_ALUMNE FROM t WHERE CODI_ALUMNE IS NOT NULL GROUP BY 1 HAVING count(DISTINCT anio) > 1)").fetchone()[0])

print("\n9.e Granularidad (nº de valores distintos) de las subcompetencias en 2024 frente a 2023 y 2025:")
print(est[(est.anio.isin([2023, 2024, 2025])) & (est.columna.isin(["PCAT_EE", "PCAST_EE", "PCAT_CL", "PMED_COMP1", "PMED_COMP2", "PMED_COMP3"]))]
      [["columna", "anio", "n_distintos"]].pivot(index="columna", columns="anio", values="n_distintos").to_string())
print("PMED_COMP2 2024, valores más frecuentes:",
      con.execute("SELECT PMED_COMP2, count(*) FROM t WHERE anio=2024 AND PMED_COMP2 IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 12").fetchall())

print("\nSalidas CSV en:", SALIDA)
