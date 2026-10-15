"""Validador del informe PBIR del CMI (sin Power BI Desktop).

Comprueba:
  1. Esquemas: cada JSON con "$schema" se valida contra el esquema oficial local (clon de
     github.com/microsoft/json-schemas), resolviendo los $ref con referencing.Registry.
  2. Estructura: definition.pbir, version.json, report.json, pages.json frente a carpetas, nombres de
     carpeta, tema base en StaticResources y resourcePackages, posiciones dentro del lienzo y sin solapes.
  3. Referencias al modelo: cada (Entity, Property) usada existe como columna o medida, con el tipo
     correcto y el nombre exacto. Columnas: TMDL de las tablas si existe; si no, el contrato §3.
     Medidas: _Medidas.tmdl.
  4. Consultas: roles de proyección válidos por tipo de visual, cardinalidad, queryRef, campos de
     ordenación presentes en la consulta y alias de filtros (Source) declarados en From.

Uso:
  python validar_pbir.py [--report RUTA.Report] [--model RUTA.SemanticModel] [--schemas RUTA/fabric]
Esquemas: clon disperso de github.com/microsoft/json-schemas (carpeta fabric). Se toma de --schemas,
de la variable de entorno PBIR_SCHEMAS o, por defecto, de la copia del scratchpad de /tmp:
  git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/json-schemas ~/json-schemas
  git -C ~/json-schemas sparse-checkout set fabric/item/report fabric/item/semanticModel fabric/pbip
  PBIR_SCHEMAS=~/json-schemas/fabric python validar_pbir.py
Sale con código 1 si hay errores. Los avisos no cambian el código de salida.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

from jsonschema import validators
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

RAIZ = Path(__file__).resolve().parents[2]
REPORT_DEF = RAIZ / "PowerBI/CMI_Educacion_Primaria.Report"
MODEL_DEF = RAIZ / "PowerBI/CMI_Educacion_Primaria.SemanticModel"
SCHEMAS_DEF = Path(os.environ.get("PBIR_SCHEMAS") or "/tmp/claude-1000/-home-kiara-rodriguez-uribe-Uni-TFG-Project/"
                   "e4d67534-2cda-46c9-9607-3737fe5b6260/scratchpad/json-schemas/fabric")
PREFIJO = "https://developer.microsoft.com/json-schemas/fabric/"
DATASET_PATH = "../CMI_Educacion_Primaria.SemanticModel"

COLUMNAS_CONTRATO = {
    "DimAnio": ["AnioKey", "Anio", "Curso", "TieneConvocatoria", "IndiceConvocatoria",
                "EsUltimaConvocatoria", "NotaConvocatoria"],
    "DimContextoCentro": ["ContextoKey", "AreaCodigo", "AreaTerritorial", "AreaPerimetro2025",
                          "AreaSerieComparable", "AreaConRupturaSerie", "RupturaHabitat2024", "Naturaleza",
                          "NaturalezaCodigo", "Habitat", "HabitatCodigo", "AreaOrden"],
    "DimPerfilAlumno": ["PerfilKey", "Genero", "GeneroCodigo", "EdadAnioNatural", "SituacionEdad",
                        "SituacionEdadCodigo", "SituacionEdadOrden", "MesNacimiento", "TrimestreNacimiento"],
    "DimCompetencia": ["CompetenciaKey", "CampoOrigen", "CodigoMateria", "Materia", "MateriaOrden",
                       "Subcompetencia", "SubcompetenciaOrden", "EsGlobal", "AnioInicio", "AnioFin",
                       "PeriodoDisenoInicio", "EsInformativa"],
    "DimNivelLogro": ["NivelKey", "Nivel", "LimiteInferior", "LimiteSuperior", "NivelOrden"],
    "DimCalidadDato": ["CalidadKey", "NoValida", "Censurada", "NoComparableSerie", "NivelNoComparable",
                       "DescripcionCalidad"],
    "FactEvaluacion": ["EvaluacionID", "AnioKey", "ContextoKey", "PerfilKey", "TieneCodigoAlumno",
                       "CompetenciasEvaluadas"],
    "FactPuntuacion": ["AnioKey", "ContextoKey", "PerfilKey", "CompetenciaKey", "NivelKey", "CalidadKey",
                       "Puntuacion"],
}

ROLES = {
    "slicer": {"Values"},
    "card": {"Values"},
    "textbox": set(),
    "tableEx": {"Values"},
    "pivotTable": {"Rows", "Columns", "Values"},
    "lineChart": {"Category", "Y", "Series", "Y2", "Tooltips"},
    "barChart": {"Category", "Y", "Series", "Tooltips"},
    "clusteredBarChart": {"Category", "Y", "Series", "Tooltips"},
    "hundredPercentStackedBarChart": {"Category", "Y", "Series", "Tooltips"},
    "columnChart": {"Category", "Y", "Series", "Tooltips"},
    "clusteredColumnChart": {"Category", "Y", "Series", "Tooltips"},
}
ROLES_REQUERIDOS = {
    "slicer": {"Values"}, "card": {"Values"}, "tableEx": {"Values"}, "pivotTable": {"Values"},
    "lineChart": {"Category", "Y"}, "barChart": {"Category", "Y"}, "clusteredBarChart": {"Category", "Y"},
    "hundredPercentStackedBarChart": {"Category", "Y"},
}
ROLES_MEDIDA = {"Y", "Y2", "Tooltips"}
ROLES_COLUMNA = {"Category", "Series", "Rows", "Columns"}
NOMBRE_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_-]*$")


class Informe:
    def __init__(self):
        self.errores = []
        self.avisos = []
        self.ok = []

    def error(self, msg):
        self.errores.append(msg)

    def aviso(self, msg):
        self.avisos.append(msg)


def registro(schemas):
    def recuperar(uri):
        if not uri.startswith(PREFIJO):
            raise NoSuchResource(ref=uri)
        ruta = schemas / uri[len(PREFIJO):]
        if not ruta.exists():
            raise NoSuchResource(ref=uri)
        return Resource.from_contents(json.loads(ruta.read_text(encoding="utf-8")))
    return Registry(retrieve=recuperar)


def validar_esquemas(report, schemas, inf):
    reg = registro(schemas)
    cache = {}
    n = 0
    for f in sorted(report.rglob("*.json")) + sorted(report.glob("*.pbir")):
        rel = f.relative_to(report)
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            inf.error(f"[json] {rel}: no es JSON válido: {exc}")
            continue
        url = doc.get("$schema") if isinstance(doc, dict) else None
        if not url:
            if rel.parts[0] == "StaticResources":
                continue
            inf.error(f"[esquema] {rel}: falta $schema")
            continue
        if not url.startswith(PREFIJO):
            inf.error(f"[esquema] {rel}: $schema fuera de {PREFIJO}: {url}")
            continue
        local = schemas / url[len(PREFIJO):]
        if not local.exists():
            inf.error(f"[esquema] {rel}: esquema no encontrado localmente: {url}")
            continue
        if url not in cache:
            sch = json.loads(local.read_text(encoding="utf-8"))
            cls = validators.validator_for(sch)
            cls.check_schema(sch)
            cache[url] = cls(sch, registry=reg)
        errs = sorted(cache[url].iter_errors(doc), key=lambda e: list(e.absolute_path))
        for e in errs:
            ruta = "/".join(str(p) for p in e.absolute_path)
            inf.error(f"[esquema] {rel} @ /{ruta}: {e.message[:300]}")
        n += 1
    inf.ok.append(f"esquemas: {n} ficheros validados, {len(cache)} esquemas distintos")


def cargar(f):
    return json.loads(f.read_text(encoding="utf-8"))


def validar_estructura(report, inf):
    pbir = report / "definition.pbir"
    if not pbir.exists():
        inf.error("[estructura] falta definition.pbir")
    else:
        d = cargar(pbir)
        ruta = d.get("datasetReference", {}).get("byPath", {}).get("path")
        if ruta != DATASET_PATH:
            inf.error(f"[estructura] definition.pbir datasetReference.byPath.path = {ruta!r}, se espera {DATASET_PATH!r}")
        if not (report.parent / Path(ruta or "x").name).is_dir():
            inf.aviso(f"[estructura] la carpeta del modelo {ruta} no existe todavía junto al informe")
    defn = report / "definition"
    for req in ("version.json", "report.json", "pages/pages.json"):
        if not (defn / req).exists():
            inf.error(f"[estructura] falta definition/{req}")
    rep = cargar(defn / "report.json")
    base = rep.get("themeCollection", {}).get("baseTheme")
    if base:
        tipo = base.get("type")
        paquetes = {p["name"]: p for p in rep.get("resourcePackages", [])}
        pk = paquetes.get(tipo)
        if not pk:
            inf.error(f"[tema] baseTheme de tipo {tipo} sin resourcePackage {tipo} en report.json")
        else:
            item = next((i for i in pk.get("items", []) if i.get("name") == base.get("name")), None)
            if not item:
                inf.error(f"[tema] resourcePackage {tipo} no declara el item {base.get('name')}")
            else:
                fich = report / "StaticResources" / tipo / item["path"]
                if not fich.exists():
                    inf.error(f"[tema] no existe {fich.relative_to(report)}")
                else:
                    tema = cargar(fich)
                    if tema.get("name") is None or "dataColors" not in tema:
                        inf.error(f"[tema] {fich.relative_to(report)} no parece un tema de Power BI")
    pages_dir = defn / "pages"
    meta = cargar(pages_dir / "pages.json")
    carpetas = sorted(p.name for p in pages_dir.iterdir() if p.is_dir())
    orden = meta.get("pageOrder", [])
    if sorted(orden) != carpetas:
        inf.error(f"[páginas] pageOrder {orden} no coincide con las carpetas {carpetas}")
    if len(set(orden)) != len(orden):
        inf.error("[páginas] pageOrder con duplicados")
    if meta.get("activePageName") not in orden:
        inf.error(f"[páginas] activePageName {meta.get('activePageName')!r} no está en pageOrder")
    visuales = {}
    for pc in carpetas:
        if not NOMBRE_RE.match(pc):
            inf.error(f"[nombres] carpeta de página no válida: {pc!r}")
        pj = pages_dir / pc / "page.json"
        if not pj.exists():
            inf.error(f"[estructura] falta {pc}/page.json")
            continue
        pg = cargar(pj)
        if pg.get("name") != pc:
            inf.error(f"[nombres] page.json name {pg.get('name')!r} != carpeta {pc!r}")
        W, H = pg.get("width", 1280), pg.get("height", 720)
        vdir = pages_dir / pc / "visuals"
        vis = []
        for vc in sorted(p.name for p in vdir.iterdir() if p.is_dir()) if vdir.exists() else []:
            if not NOMBRE_RE.match(vc):
                inf.error(f"[nombres] carpeta de visual no válida: {pc}/{vc!r}")
            vf = vdir / vc / "visual.json"
            if not vf.exists():
                inf.error(f"[estructura] falta {pc}/{vc}/visual.json")
                continue
            v = cargar(vf)
            if v.get("name") != vc:
                inf.error(f"[nombres] visual.json name {v.get('name')!r} != carpeta {pc}/{vc}")
            p = v.get("position", {})
            x, y, w, h = p.get("x", 0), p.get("y", 0), p.get("width", 0), p.get("height", 0)
            if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > W + 1e-6 or y + h > H + 1e-6:
                inf.error(f"[posición] {pc}/{vc} fuera del lienzo {W}x{H}: x={x} y={y} w={w} h={h}")
            vis.append((vc, x, y, w, h, v))
        for i in range(len(vis)):
            for j in range(i + 1, len(vis)):
                a, b = vis[i], vis[j]
                if a[1] < b[1] + b[3] - 1e-6 and b[1] < a[1] + a[3] - 1e-6 and a[2] < b[2] + b[4] - 1e-6 and b[2] < a[2] + a[4] - 1e-6:
                    inf.error(f"[posición] solape en {pc}: {a[0]} y {b[0]}")
        nombres = {x[0] for x in vis}
        for it in pg.get("visualInteractions", []):
            for k in ("source", "target"):
                if it.get(k) not in nombres:
                    inf.error(f"[páginas] {pc}: visualInteractions.{k} {it.get(k)!r} no es un visual de la página")
        visuales[pc] = vis
    inf.ok.append(f"estructura: {len(carpetas)} páginas, {sum(len(v) for v in visuales.values())} visuales")
    return visuales


def nombre_tmdl(raw):
    raw = raw.strip()
    if raw.startswith("'"):
        return raw[1:raw.index("'", 1)] if raw.count("'") >= 2 else raw[1:]
    return raw.split()[0]


def objeto_tmdl(linea, clave):
    rest = linea.strip()[len(clave) + 1:]
    if rest.startswith("'"):
        m = re.match(r"'((?:[^']|'')*)'", rest)
        return m.group(1).replace("''", "'")
    return re.split(r"\s|=", rest, maxsplit=1)[0]


def cargar_modelo(model, inf):
    tablas = model / "definition/tables"
    columnas, medidas, fuente = {}, {}, {}
    for t in sorted(tablas.glob("*.tmdl")) if tablas.exists() else []:
        tabla = None
        for linea in t.read_text(encoding="utf-8").splitlines():
            s = linea.strip()
            if linea.startswith("table "):
                tabla = objeto_tmdl(linea, "table")
                columnas.setdefault(tabla, set())
                medidas.setdefault(tabla, set())
                fuente[tabla] = "TMDL"
            elif tabla and linea.startswith("\t") and not linea.startswith("\t\t"):
                if s.startswith("column "):
                    columnas[tabla].add(objeto_tmdl(s, "column"))
                elif s.startswith("measure "):
                    medidas[tabla].add(objeto_tmdl(s, "measure"))
    for tabla, cols in COLUMNAS_CONTRATO.items():
        if tabla not in fuente:
            columnas[tabla] = set(cols)
            medidas.setdefault(tabla, set())
            fuente[tabla] = "contrato"
        else:
            faltan = set(cols) - columnas[tabla]
            if faltan:
                inf.aviso(f"[modelo] {tabla}.tmdl no tiene columnas del contrato: {sorted(faltan)}")
    inf.ok.append("modelo: " + ", ".join(f"{t}({fuente[t]})" for t in sorted(fuente)))
    if not any(medidas.values()):
        inf.error("[modelo] no se ha encontrado ninguna medida (¿falta _Medidas.tmdl?)")
    return columnas, medidas


def recoger_campos(nodo, ruta, salida, alias=None):
    alias = dict(alias or {})
    if isinstance(nodo, dict):
        if isinstance(nodo.get("From"), list):
            alias.update({f.get("Name"): f.get("Entity") for f in nodo["From"]})
        for tipo in ("Column", "Measure"):
            val = nodo.get(tipo)
            if isinstance(val, dict) and "Property" in val:
                sr = val.get("Expression", {}).get("SourceRef", {})
                ent = sr.get("Entity")
                if ent is None and "Source" in sr:
                    ent = alias.get(sr["Source"], KeyError)
                salida.append((tipo, ent, sr.get("Source"), val["Property"], ruta))
        for k, v in nodo.items():
            recoger_campos(v, f"{ruta}/{k}", salida, alias)
    elif isinstance(nodo, list):
        for i, v in enumerate(nodo):
            recoger_campos(v, f"{ruta}/{i}", salida, alias)


def clave(campo):
    tipo = next(iter(campo))
    return tipo, campo[tipo]["Expression"]["SourceRef"].get("Entity"), campo[tipo]["Property"]


def validar_referencias(visuales, columnas, medidas, report, inf):
    usadas = set()
    pages_dir = report / "definition/pages"
    docs = [(f"{pc}/page.json", cargar(pages_dir / pc / "page.json")) for pc in visuales]
    docs += [(f"{pc}/{vc}", v) for pc, vis in visuales.items() for vc, *_r, v in vis]
    for etiqueta, doc in docs:
        campos = []
        recoger_campos(doc, "", campos)
        for tipo, ent, src, prop, ruta in campos:
            if ent is KeyError or ent is None:
                inf.error(f"[filtro] {etiqueta}{ruta}: Source {src!r} no declarado en From")
                continue
            usadas.add((ent, prop, tipo))
            if ent not in columnas and ent not in medidas:
                inf.error(f"[campo] {etiqueta}{ruta}: tabla inexistente {ent!r}")
            elif tipo == "Column" and prop not in columnas.get(ent, set()):
                extra = " (es una medida)" if prop in medidas.get(ent, set()) else ""
                inf.error(f"[campo] {etiqueta}{ruta}: columna inexistente {ent}[{prop}]{extra}")
            elif tipo == "Measure" and prop not in medidas.get(ent, set()):
                extra = " (es una columna)" if prop in columnas.get(ent, set()) else ""
                inf.error(f"[campo] {etiqueta}{ruta}: medida inexistente {ent}[{prop}]{extra}")
    inf.ok.append(f"referencias: {len(usadas)} campos distintos ("
                  f"{sum(1 for u in usadas if u[2] == 'Column')} columnas, "
                  f"{sum(1 for u in usadas if u[2] == 'Measure')} medidas)")
    return usadas


def validar_consultas(visuales, inf):
    for pc, vis in visuales.items():
        for vc, *_r, v in vis:
            et = f"{pc}/{vc}"
            cuerpo = v.get("visual", {})
            tipo = cuerpo.get("visualType")
            if tipo not in ROLES:
                inf.aviso(f"[visual] {et}: tipo {tipo!r} no comprobado por este validador")
                continue
            query = cuerpo.get("query", {})
            qs = query.get("queryState", {})
            if tipo == "textbox":
                if qs:
                    inf.error(f"[consulta] {et}: un textbox no debe tener queryState")
                if not cuerpo.get("objects", {}).get("general"):
                    inf.error(f"[consulta] {et}: textbox sin objects.general.paragraphs")
                continue
            roles = set(qs)
            for r in roles - ROLES[tipo]:
                inf.error(f"[consulta] {et}: rol {r!r} no válido para {tipo} (válidos: {sorted(ROLES[tipo])})")
            for r in ROLES_REQUERIDOS.get(tipo, set()) - roles:
                inf.error(f"[consulta] {et}: falta el rol {r!r} para {tipo}: el visual quedaría vacío")
            claves_q = set()
            for r, cont in qs.items():
                proys = cont.get("projections", [])
                if not proys:
                    inf.error(f"[consulta] {et}: rol {r} sin proyecciones")
                for p in proys:
                    k = clave(p["field"])
                    claves_q.add(k)
                    esperado = f"{k[1]}.{k[2]}"
                    if p.get("queryRef") != esperado:
                        inf.error(f"[consulta] {et}: queryRef {p.get('queryRef')!r} != {esperado!r}")
                    if r in ROLES_MEDIDA and k[0] != "Measure":
                        inf.error(f"[consulta] {et}: rol {r} con columna {esperado} (se espera medida)")
                    if r in ROLES_COLUMNA and k[0] != "Column":
                        inf.error(f"[consulta] {et}: rol {r} con medida {esperado} (se espera columna)")
                    if tipo in ("slicer",) and k[0] != "Column":
                        inf.error(f"[consulta] {et}: segmentador con medida {esperado}")
            if tipo == "card" and len(qs.get("Values", {}).get("projections", [])) != 1:
                inf.error(f"[consulta] {et}: una tarjeta (card) admite exactamente una medida")
            if tipo in ("lineChart", "clusteredBarChart", "barChart", "hundredPercentStackedBarChart"):
                if len(qs.get("Series", {}).get("projections", [])) > 1:
                    inf.error(f"[consulta] {et}: Series admite un solo campo")
                if qs.get("Series") and len(qs.get("Y", {}).get("projections", [])) > 1:
                    inf.error(f"[consulta] {et}: con leyenda (Series) solo se admite una medida en Y")
            if tipo == "hundredPercentStackedBarChart" and not qs.get("Series"):
                inf.aviso(f"[consulta] {et}: barras 100% sin Series: todas las barras serían 100%")
            for s in query.get("sortDefinition", {}).get("sort", []):
                k = clave(s["field"])
                if k not in claves_q:
                    inf.error(f"[orden] {et}: ordena por {k[1]}.{k[2]}, que no está en la consulta")
                if s.get("direction") not in ("Ascending", "Descending"):
                    inf.error(f"[orden] {et}: dirección no válida {s.get('direction')!r}")


LITERAL_RE = re.compile(r"^(?:'(?:[^']|'')*'|true|false|null|-?\d+L|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?[DM]|datetime'[^']*')$")


def validar_expresiones(report, schemas, inf):
    """Las propiedades de objects solo están tipadas de forma laxa en los esquemas: se comprueba aquí
    que cada "expr" use un tipo de expresión del esquema semanticQuery y que los literales sean válidos."""
    sq = sorted((schemas / "item/report/definition/semanticQuery").glob("*/schema.json"))
    if not sq:
        inf.aviso("[expr] no se encuentra el esquema semanticQuery; se omite la comprobación de expresiones")
        return
    tipos = set(json.loads(sq[-1].read_text(encoding="utf-8"))["definitions"]["QueryExpressionContainer"]["properties"])
    n = 0

    def visitar(nodo, ruta, rel):
        nonlocal n
        if isinstance(nodo, dict):
            for k, v in nodo.items():
                if k == "expr" and isinstance(v, dict):
                    n += 1
                    for t in set(v) - tipos:
                        inf.error(f"[expr] {rel}{ruta}/expr: tipo de expresión desconocido {t!r}")
                if k == "Literal" and isinstance(v, dict):
                    val = v.get("Value")
                    if not isinstance(val, str) or not LITERAL_RE.match(val):
                        inf.error(f"[expr] {rel}{ruta}/Literal: valor literal mal formado {val!r}")
                visitar(v, f"{ruta}/{k}", rel)
        elif isinstance(nodo, list):
            for i, v in enumerate(nodo):
                visitar(v, f"{ruta}/{i}", rel)

    for f in sorted((report / "definition").rglob("*.json")):
        visitar(json.loads(f.read_text(encoding="utf-8")), "", str(f.relative_to(report)))
    inf.ok.append(f"expresiones: {n} expr de formato revisadas")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", type=Path, default=REPORT_DEF)
    ap.add_argument("--model", type=Path, default=MODEL_DEF)
    ap.add_argument("--schemas", type=Path, default=SCHEMAS_DEF)
    ap.add_argument("--referencias", type=Path, default=RAIZ / "trabajo_en_curso/generadores/pbir_referencias.json",
                    help="JSON de referencias del generador (Entity, Property, tipo) para contrastar")
    a = ap.parse_args()
    inf = Informe()
    if not a.schemas.exists():
        inf.error(f"[esquema] no existe la carpeta de esquemas {a.schemas}: clona microsoft/json-schemas "
                  f"y pásala con --schemas o PBIR_SCHEMAS (ver la cabecera de este script)")
    else:
        validar_esquemas(a.report, a.schemas, inf)
        validar_expresiones(a.report, a.schemas, inf)
    visuales = validar_estructura(a.report, inf)
    columnas, medidas = cargar_modelo(a.model, inf)
    usadas = validar_referencias(visuales, columnas, medidas, a.report, inf)
    validar_consultas(visuales, inf)
    if a.referencias and a.referencias.exists():
        gen = {(r["Entity"], r["Property"], r["tipo"]) for r in cargar(a.referencias)}
        if gen != usadas:
            inf.error(f"[referencias] el JSON del generador difiere del informe: "
                      f"solo generador={sorted(gen - usadas)} solo informe={sorted(usadas - gen)}")
        else:
            inf.ok.append(f"referencias: coinciden con {a.referencias.name}")
    for m in inf.ok:
        print(f"OK     {m}")
    for m in inf.avisos:
        print(f"AVISO  {m}")
    for m in inf.errores:
        print(f"ERROR  {m}")
    print(f"RESULTADO: {len(inf.errores)} errores, {len(inf.avisos)} avisos")
    return 1 if inf.errores else 0


if __name__ == "__main__":
    sys.exit(main())
