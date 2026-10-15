"""Verificación (3): claves deterministas del M frente a las dimensiones estáticas y al parquet.

1. Extrae del M (vía validar_m.py) los literales de las dimensiones estáticas y reconstruye
   las dimensiones tal como las genera el M; las compara con validacion/salida/*.parquet.
2. Enumera TODAS las combinaciones posibles de staging según las reglas del M y comprueba que
   ContextoKey / PerfilKey / AnioKey / CompetenciaKey / NivelKey / CalidadKey caen en filas de
   las dimensiones (0 huérfanas).
3. Comprueba las claves de los hechos del parquet contra las dimensiones del M.
"""
import ast
import re
import sys
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "trabajo_en_curso/herramientas"))
import validar_m  # noqa: E402

DEF = RAIZ / "PowerBI/CMI_Educacion_Primaria.SemanticModel/definition"
SAL = RAIZ / "validacion/salida"
M = {}
for f in DEF.rglob("*.tmdl"):
    for ident, code in validar_m.extraer(f):
        M[ident] = code

fallos = []


def check(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        fallos.append(msg)


def literal(code, nombre):
    """Convierte el literal M `nombre = {...}` o `[...]` en objeto Python."""
    i = code.index(nombre + " = ")
    j = i + len(nombre) + 3
    apertura = code[j]
    cierre = {"{": "}", "[": "]"}[apertura]
    prof, k, en_txt = 0, j, False
    while True:
        c = code[k]
        if c == '"':
            en_txt = not en_txt
        elif not en_txt:
            if c == apertura:
                prof += 1
            elif c == cierre:
                prof -= 1
                if prof == 0:
                    break
        k += 1
    txt = code[j:k + 1]
    txt = re.sub(r"//[^\n]*", "", txt)
    if apertura == "[":  # registro M -> dict
        pares = re.findall(r'(#"[^"]*"|\w+)\s*=\s*([^,\]\n]+)', txt)
        return {(k[2:-1] if k.startswith("#") else k): ast.literal_eval(v.strip()) for k, v in pares}
    py = txt.replace("{", "[").replace("}", "]")
    py = re.sub(r"\btrue\b", "True", py)
    py = re.sub(r"\bfalse\b", "False", py)
    py = re.sub(r"\bnull\b", "None", py)
    return ast.literal_eval(py)


stg = M["expression_stg_Evaluaciones"]
con = duckdb.connect()
pq = {t: con.execute(f"select * from '{SAL}/{t}.parquet'").fetchall() for t in
      ["DimAnio", "DimContextoCentro", "DimPerfilAlumno", "DimCompetencia", "DimNivelLogro", "DimCalidadDato"]}

# ---- Fórmulas de clave idénticas en staging y dimensiones
check("[AreaCodigo] * 100 + [NaturalezaCodigo] * 10 + [HabitatCodigo]" in stg, "fórmula ContextoKey en stg")
check("area{0} * 100 + naturaleza{0} * 10 + habitat{0}" in M["partition_DimContextoCentro"], "fórmula ContextoKey en DimContextoCentro")
check("[GeneroCodigo] * 100000 + [SituacionEdadCodigo] * 10000" in stg and "* 100 + [MesNacimiento]" in stg, "fórmula PerfilKey en stg")
check("genero{0} * 100000 + combinacion{1} * 10000 + combinacion{0} * 100 + mes" in M["partition_DimPerfilAlumno"], "fórmula PerfilKey en DimPerfilAlumno")

# ---- DimContextoCentro reconstruida desde el M
cc = M["partition_DimContextoCentro"]
areas, nats, habs = literal(cc, "Areas"), literal(cc, "Naturalezas"), literal(cc, "Habitats")
dim_ctx = [(a[0] * 100 + n[0] * 10 + h[0], a[0], a[1], a[2], a[3], a[4], a[5], n[1], n[0], h[1], h[0], 3 if a[0] == 4 else a[0])
           for a in areas for n in nats for h in habs]
check(sorted(dim_ctx) == sorted(pq["DimContextoCentro"]), f"DimContextoCentro M == parquet ({len(dim_ctx)} filas)")
claves_ctx = {r[0] for r in dim_ctx}

# ---- DimPerfilAlumno
pa_ = M["partition_DimPerfilAlumno"]
gens, sits, combs = literal(pa_, "Generos"), literal(pa_, "Situaciones"), literal(pa_, "Combinaciones")
dim_perf = []
for g in gens:
    for c in combs:
        s = next(x for x in sits if x[0] == c[1])
        for mes in range(13):
            dim_perf.append((g[0] * 100000 + c[1] * 10000 + c[0] * 100 + mes, g[1], g[0], c[0] or None, s[1], s[0], s[2],
                             mes or None, "No informado" if mes == 0 else f"T{(mes - 1) // 3 + 1}"))
check(sorted(dim_perf) == sorted(pq["DimPerfilAlumno"]), f"DimPerfilAlumno M == parquet ({len(dim_perf)} filas)")
claves_perf = {r[0] for r in dim_perf}

# ---- DimCompetencia y registro ClaveCompetencia
dc = M["partition_DimCompetencia"]
i = dc.index("],\n") + 3
filas_comp = literal("X = " + dc[i:].strip(), "X")
check([tuple(r) for r in filas_comp] == [tuple(r) for r in pq["DimCompetencia"]], f"DimCompetencia M == parquet ({len(filas_comp)} filas)")
clave_comp = literal(M["partition_FactPuntuacion"], "ClaveCompetencia")
check(clave_comp == {r[1]: r[0] for r in filas_comp}, "ClaveCompetencia (FactPuntuacion) == DimCompetencia[CampoOrigen -> Key]")
check(set(literal(stg, "CamposPuntuacion")) == set(clave_comp), "CamposPuntuacion (stg) == campos de ClaveCompetencia")
check(set(literal(M["partition_FactPuntuacion"], "CamposGlobales")) == {r[1] for r in filas_comp if r[7]}, "CamposGlobales == EsGlobal")

# ---- DimNivelLogro
dn = M["partition_DimNivelLogro"]
i = dn.index("],\n") + 3
filas_niv = literal("X = " + dn[i:].strip(), "X")
check([tuple(r) for r in filas_niv] == [tuple(r) for r in pq["DimNivelLogro"]], "DimNivelLogro M == parquet")

# ---- DimCalidadDato
bits = literal(M["partition_DimCalidadDato"], "Bits")
dim_cal = [(k, *[bool(k & b) for b, _ in bits], "Válido" if k == 0 else "; ".join(t for b, t in bits if k & b)) for k in range(16)]
check(dim_cal == [tuple(r) for r in pq["DimCalidadDato"]], "DimCalidadDato M == parquet")
reglas = literal(M["partition_FactPuntuacion"], "ReglasCalidad")
mapa = {}
for bit, campos, anios in reglas:
    for c in campos:
        for a in anios:
            mapa[f"{c}|{a}"] = mapa.get(f"{c}|{a}", 0) | bit
obs = con.execute(f"""select c.CampoOrigen, f.AnioKey, f.CalidadKey from '{SAL}/FactPuntuacion.parquet' f
    join '{SAL}/DimCompetencia.parquet' c using (CompetenciaKey) group by all""").fetchall()
check(all(mapa.get(f"{c}|{a}", 0) == k for c, a, k in obs), f"CalidadKey del M == parquet en las {len(obs)} parejas (campo, año)")

# ---- DimAnio (lógica del M sobre los años del parquet)
anios = sorted(r[0] for r in con.execute(f"select distinct AnioKey from '{SAL}/FactEvaluacion.parquet'").fetchall())
notas = literal(M["partition_DimAnio"], "Notas")
dim_anio = [(a, a, f"{a-1}-{a}", a in anios, anios.index(a) + 1 if a in anios else None, a == max(anios), notas.get(str(a), ""))
            for a in range(2009, max(anios) + 1)]
check(dim_anio == [tuple(r) for r in pq["DimAnio"]], f"DimAnio (lógica M) == parquet ({len(dim_anio)} filas)")
claves_anio = {r[0] for r in dim_anio}

# ---- Enumeración del dominio de staging según las reglas del M
codigos_area = literal(stg, "CodigosArea")
huerfanas = []
for anio in anios:
    area_cods = {99, *codigos_area.values()} | ({4} if anio == 2024 else {3} if anio <= 2023 else set())
    for area in area_cods:
        for nat in (1, 2):
            for hab_map in (1, 2, 3):
                for override in (False, True):
                    hab = 0 if (anio == 2010 or override) else hab_map
                    if area * 100 + nat * 10 + hab not in claves_ctx:
                        huerfanas.append(("ctx", anio, area, nat, hab))
    for gen in (1, 2):
        for edad in (None, 10, 11, 12, 13, 14):
            e = None if anio == 2010 else edad
            sit = 8 if anio == 2010 else 9 if e is None else 4 if e < 12 else 1 if e == 12 else 2 if e == 13 else 3
            for mes in range(13):
                if gen * 100000 + sit * 10000 + (e or 0) * 100 + mes not in claves_perf:
                    huerfanas.append(("perf", anio, gen, e, sit, mes))
    if anio not in claves_anio:
        huerfanas.append(("anio", anio))
check(not huerfanas, f"dominio de staging: 0 combinaciones huérfanas (encontradas {len(huerfanas)}) {huerfanas[:5]}")

# ---- Claves de los hechos del parquet frente a las dimensiones del M
for fact, col, claves in [("FactEvaluacion", "ContextoKey", claves_ctx), ("FactEvaluacion", "PerfilKey", claves_perf),
                          ("FactEvaluacion", "AnioKey", claves_anio), ("FactPuntuacion", "ContextoKey", claves_ctx),
                          ("FactPuntuacion", "PerfilKey", claves_perf), ("FactPuntuacion", "AnioKey", claves_anio),
                          ("FactPuntuacion", "CompetenciaKey", set(clave_comp.values())),
                          ("FactPuntuacion", "NivelKey", {r[0] for r in filas_niv}),
                          ("FactPuntuacion", "CalidadKey", set(range(16)))]:
    vals = {r[0] for r in con.execute(f"select distinct {col} from '{SAL}/{fact}.parquet'").fetchall()}
    check(vals <= claves, f"{fact}[{col}]: {len(vals)} valores distintos, huérfanos: {sorted(vals - claves)[:5]}")

print("\nRESULTADO:", "0 fallos" if not fallos else f"{len(fallos)} FALLOS")
sys.exit(1 if fallos else 0)
