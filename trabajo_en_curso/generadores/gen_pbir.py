"""Genera el informe PBIR CMI_Educacion_Primaria.Report (contrato §8)."""
import json
import shutil
import sys
from pathlib import Path

TRABAJO = Path(__file__).resolve().parents[1]
REPORT = TRABAJO.parent / "PowerBI/CMI_Educacion_Primaria.Report"
THEME_SRC = TRABAJO / "referencias_pbir/ejemplos/pbipdemo/r01/StaticResources/SharedResources/BaseThemes/CY24SU10.json"
REFS_OUT = TRABAJO / "generadores/pbir_referencias.json"

BASE = "https://developer.microsoft.com/json-schemas/fabric/item/report"
SCH_PBIR = f"{BASE}/definitionProperties/2.0.0/schema.json"
SCH_VERSION = f"{BASE}/definition/versionMetadata/1.0.0/schema.json"
SCH_REPORT = f"{BASE}/definition/report/3.0.0/schema.json"
SCH_PAGES = f"{BASE}/definition/pagesMetadata/1.0.0/schema.json"
SCH_PAGE = f"{BASE}/definition/page/2.0.0/schema.json"
SCH_VISUAL = f"{BASE}/definition/visualContainer/2.4.0/schema.json"

M = "_Medidas"
REFS = set()


def lit(value):
    return {"expr": {"Literal": {"Value": value}}}


def txt(value):
    return "'" + value.replace("'", "''") + "'"


def color(hex_value):
    return {"solid": {"color": lit(txt(hex_value))}}


def col(entity, prop):
    REFS.add((entity, prop, "Column"))
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def meas(prop, entity=M):
    REFS.add((entity, prop, "Measure"))
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def field_ids(field):
    kind = next(iter(field))
    return field[kind]["Expression"]["SourceRef"]["Entity"], field[kind]["Property"]


def proj(field, display=None, active=None):
    entity, prop = field_ids(field)
    p = {"field": field, "queryRef": f"{entity}.{prop}", "nativeQueryRef": display or prop}
    if display:
        p["displayName"] = display
    if active is not None:
        p["active"] = active
    return p


def container_objects(title, subtitle=None, alt=None):
    vco = {"title": [{"properties": {"show": lit("true"), "text": lit(txt(title))}}]}
    if subtitle:
        vco["subTitle"] = [{"properties": {"show": lit("true"), "text": lit(txt(subtitle))}}]
    vco["general"] = [{"properties": {"altText": lit(txt(alt or title))}}]
    return vco


def visual(name, pos, vis, filters=None):
    v = {"$schema": SCH_VISUAL, "name": name, "position": pos, "visual": vis}
    if filters:
        v["filterConfig"] = {"filters": filters}
    return v


class Layout:
    def __init__(self):
        self.n = 0

    def pos(self, x, y, w, h):
        self.n += 1
        return {"x": x, "y": y, "z": self.n * 1000, "height": h, "width": w, "tabOrder": self.n * 1000}


def slicer(name, pos, field, display, sync_group, single=False, default_in=None):
    objects = {
        "data": [{"properties": {"mode": lit("'Dropdown'")}}],
        "header": [{"properties": {"show": lit("false")}}],
    }
    if single:
        objects["selection"] = [{"properties": {"singleSelect": lit("true")}}]
    if default_in is not None:
        entity, prop = field_ids(field)
        objects["general"] = [{"properties": {"filter": {"filter": {
            "Version": 2,
            "From": [{"Name": "s", "Entity": entity, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "s"}}, "Property": prop}}],
                "Values": [[{"Literal": {"Value": v}}] for v in default_in],
            }}}],
        }}}}]
    vis = {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [proj(field, display, active=True)]}}},
        "objects": objects,
        "visualContainerObjects": container_objects(display, alt=f"Segmentador de {display.lower()}"),
        "syncGroup": {"groupName": sync_group, "fieldChanges": True, "filterChanges": True},
        "drillFilterOtherVisuals": True,
    }
    return visual(name, pos, vis)


def card(name, pos, measure, title, subtitle=None, alt=None):
    vis = {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [proj(meas(measure))]}}},
        "objects": {
            "labels": [{"properties": {"fontSize": lit("22D"), "labelDisplayUnits": lit("1D")}}],
            "categoryLabels": [{"properties": {"show": lit("false")}}],
        },
        "visualContainerObjects": container_objects(title, subtitle, alt or f"Tarjeta: {title}"),
        "drillFilterOtherVisuals": True,
    }
    return visual(name, pos, vis)


def textbox(name, pos, paragraphs, alt):
    vis = {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
        "visualContainerObjects": {
            "title": [{"properties": {"show": lit("false")}}],
            "general": [{"properties": {"altText": lit(txt(alt))}}],
        },
        "drillFilterOtherVisuals": True,
    }
    return visual(name, pos, vis)


def run(text, size, bold=False, colour="#252423"):
    style = {"fontFamily": "Segoe UI", "fontSize": f"{size}pt", "color": colour}
    if bold:
        style["fontWeight"] = "bold"
    return {"value": text, "textStyle": style}


def header(name, pos, title, subtitle):
    return textbox(name, pos, [
        {"textRuns": [run(title, 16, bold=True)]},
        {"textRuns": [run(subtitle, 10, colour="#605E5C")]},
    ], alt=f"{title}. {subtitle}")


def line_chart(name, pos, category, ys, title, series=None, subtitle=None, alt=None):
    qs = {"Category": {"projections": [proj(category[0], category[1], active=True)]}}
    if series:
        qs["Series"] = {"projections": [proj(series[0], series[1])]}
    qs["Y"] = {"projections": [proj(meas(m), d) for m, d in ys]}
    vis = {
        "visualType": "lineChart",
        "query": {
            "queryState": qs,
            "sortDefinition": {"sort": [{"field": category[0], "direction": "Ascending"}]},
        },
        "objects": {
            "categoryAxis": [{"properties": {"axisType": lit("'Categorical'")}}],
            "legend": [{"properties": {"show": lit("true"), "position": lit("'Top'")}}],
        },
        "visualContainerObjects": container_objects(title, subtitle, alt),
        "drillFilterOtherVisuals": True,
    }
    return visual(name, pos, vis)


def bar_chart(name, pos, category, y, title, series=None, tooltips=None, subtitle=None, alt=None, sort_by_measure=True):
    qs = {"Category": {"projections": [proj(category[0], category[1], active=True)]}}
    if series:
        qs["Series"] = {"projections": [proj(series[0], series[1])]}
    qs["Y"] = {"projections": [proj(meas(y[0]), y[1])]}
    if tooltips:
        qs["Tooltips"] = {"projections": [proj(meas(m), d) for m, d in tooltips]}
    query = {"queryState": qs}
    if sort_by_measure:
        query["sortDefinition"] = {"sort": [{"field": meas(y[0]), "direction": "Descending"}]}
    vis = {
        "visualType": "clusteredBarChart",
        "query": query,
        "objects": {"labels": [{"properties": {"show": lit("true")}}]},
        "visualContainerObjects": container_objects(title, subtitle, alt),
        "drillFilterOtherVisuals": True,
    }
    if series:
        vis["objects"]["legend"] = [{"properties": {"show": lit("true"), "position": lit("'Top'")}}]
    return visual(name, pos, vis)


def categorical_filter(name, field, values, negate=False):
    entity, prop = field_ids(field)
    cond = {"In": {
        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": prop}}],
        "Values": [[{"Literal": {"Value": v}}] for v in values],
    }}
    if negate:
        cond = {"Not": {"Expression": cond}}
    flt = {
        "name": name,
        "field": field,
        "type": "Categorical",
        "filter": {"Version": 2, "From": [{"Name": "f", "Entity": entity, "Type": 0}], "Where": [{"Condition": cond}]},
        "howCreated": "User",
    }
    if negate:
        flt["objects"] = {"general": [{"properties": {"isInvertedSelectionMode": lit("true")}}]}
    return flt


def page(name, display, visuals, interactions):
    return {
        "$schema": SCH_PAGE,
        "name": name,
        "displayName": display,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
        "visualInteractions": [{"source": s, "target": t, "type": "NoFilter"} for s, t in interactions],
    }


ANIO = ("DimAnio", "Anio")
AVISO = "Puntuaciones no equiparadas entre convocatorias; 2020 sin prueba (COVID-19)"
ANIO_DEFECTO = ["2025L"]


def f_anio():
    return col(*ANIO)


def f_materia():
    return col("DimCompetencia", "Materia")


def f_area():
    return col("DimContextoCentro", "AreaTerritorial")


def page1():
    L = Layout()
    pid = "Estrategico_Departamento"
    v = []
    v.append(header("p1_cabecera", L.pos(16, 8, 860, 60),
                    "Cuadro de Mando Integral - Educación primaria de Cataluña",
                    "Visión estratégica (Departamento de Educación): resultados de la convocatoria seleccionada y evolución"))
    v.append(slicer("p1_seg_anio", L.pos(884, 8, 186, 60), f_anio(), "Año", "Anio", single=True, default_in=ANIO_DEFECTO))
    v.append(slicer("p1_seg_materia", L.pos(1078, 8, 186, 60), f_materia(), "Materia", "Materia"))
    cards = [
        ("p1_tarjeta_k01", "K01 Puntuación media competencia", "Puntuación media (K01)", "Competencias globales"),
        ("p1_tarjeta_k03", "K03 % alumnado nivel bajo", "% alumnado en nivel bajo (K03)", "Puntuación global < 55"),
        ("p1_tarjeta_k06", "K06 Dispersión de resultados", "Dispersión de resultados (K06)", "Desviación típica"),
        ("p1_tarjeta_k10", "K10 Variación interanual", "Variación interanual (K10)", "Frente a la convocatoria anterior"),
        ("p1_tarjeta_k12", "K12 % competencias que mejoran", "% competencias que mejoran (K12)", "Mejora de 1 punto o más"),
        ("p1_tarjeta_alumnos", "Alumnos evaluados", "Alumnos evaluados", "Registros de evaluación"),
    ]
    x = 16.0
    for name, m, title, sub in cards:
        v.append(card(name, L.pos(round(x, 1), 76, 200, 100), m, title, sub))
        x += 209.6
    v.append(line_chart("p1_linea_k01_materia", L.pos(16, 188, 724, 462),
                        (f_anio(), "Año"), [("K01 Puntuación media competencia", "Puntuación media (K01)")],
                        "Evolución de la puntuación media (K01) por materia",
                        series=(f_materia(), "Materia"),
                        subtitle="Todas las convocatorias; no se filtra por el segmentador de año",
                        alt="Gráfico de líneas con la puntuación media global por año para cada materia"))
    tabla_vals = [
        proj(f_materia(), "Materia"),
        proj(meas("K01 Puntuación media competencia"), "K01 Puntuación media"),
        proj(meas("K10 Variación interanual"), "K10 Variación interanual"),
        proj(meas("K11 Tendencia 5 convocatorias"), "K11 Tendencia (5 conv.)"),
        proj(meas("K03 % alumnado nivel bajo"), "K03 % nivel bajo"),
    ]
    v.append(visual("p1_tabla_materia", L.pos(748, 188, 516, 462), {
        "visualType": "tableEx",
        "query": {
            "queryState": {"Values": {"projections": tabla_vals}},
            "sortDefinition": {"sort": [{"field": f_materia(), "direction": "Ascending"}]},
        },
        "visualContainerObjects": container_objects(
            "Resumen por materia", "Convocatoria seleccionada",
            "Tabla por materia con puntuación media, variación interanual, tendencia y porcentaje en nivel bajo"),
        "drillFilterOtherVisuals": True,
    }))
    v.append(textbox("p1_aviso", L.pos(16, 658, 1248, 50), [
        {"textRuns": [run("Aviso: ", 10, bold=True, colour="#A4262C"), run(AVISO, 10, bold=True)]},
        {"textRuns": [run("Umbrales de nivel de logro provisionales e internos del TFG (no oficiales). "
                          "Se oculta un valor si se basa en menos de 30 puntuaciones.", 9, colour="#605E5C")]},
    ], alt=AVISO))
    inter = [("p1_seg_anio", "p1_linea_k01_materia")]
    return pid, page(pid, "Estratégico - Departamento", v, inter), v


def page2():
    L = Layout()
    pid = "Tactico_Inspeccion"
    v = []
    v.append(header("p2_cabecera", L.pos(16, 8, 660, 60),
                    "Visión táctica - Inspección educativa",
                    "Comparación territorial y equidad. " + AVISO))
    v.append(slicer("p2_seg_anio", L.pos(684, 8, 188, 60), f_anio(), "Año", "Anio", single=True, default_in=ANIO_DEFECTO))
    v.append(slicer("p2_seg_materia", L.pos(880, 8, 188, 60), f_materia(), "Materia", "Materia"))
    v.append(slicer("p2_seg_area", L.pos(1076, 8, 188, 60), f_area(), "Área territorial", "AreaTerritorial"))
    cards = [
        ("p2_tarjeta_k04", "K04 Brecha de género (Niños - Niñas)", "Brecha de género: niños - niñas (K04)", "Puntos de diferencia"),
        ("p2_tarjeta_k05", "K05 Brecha pública - privada", "Brecha pública - privada (K05)", "Puntos de diferencia"),
        ("p2_tarjeta_k08", "K08 Diferencia urbano - rural", "Diferencia urbano - rural (K08)", "Más de 100.000 hab. frente a hasta 10.000"),
        ("p2_tarjeta_k09", "K09 Posición del área", "Posición del área (K09)", "Requiere una sola área en contexto"),
    ]
    x = 16
    for name, m, title, sub in cards:
        v.append(card(name, L.pos(x, 76, 306, 100), m, title, sub))
        x += 314
    v.append(bar_chart("p2_barras_k07_area", L.pos(16, 188, 410, 520),
                       (f_area(), "Área territorial"),
                       ("K07 Desviación respecto a Cataluña", "Desviación respecto a Cataluña (K07)"),
                       "Desviación de cada área respecto a Cataluña (K07)",
                       tooltips=[("K01 Puntuación media competencia", "Puntuación media (K01)"),
                                 ("K09 Posición del área", "Posición del área (K09)")],
                       subtitle="Puntos de diferencia sobre la media de Cataluña",
                       alt="Gráfico de barras con la desviación de la puntuación media de cada área respecto a Cataluña"))
    v.append(visual("p2_matriz_area_naturaleza", L.pos(434, 188, 410, 520), {
        "visualType": "pivotTable",
        "query": {"queryState": {
            "Rows": {"projections": [proj(f_area(), "Área territorial", active=True)]},
            "Columns": {"projections": [proj(col("DimContextoCentro", "Naturaleza"), "Naturaleza", active=True)]},
            "Values": {"projections": [proj(meas("K01 Puntuación media competencia"), "Puntuación media (K01)")]},
        }},
        "visualContainerObjects": container_objects(
            "Puntuación media (K01) por área y naturaleza", "Centros públicos y privados",
            "Matriz con la puntuación media por área territorial y naturaleza del centro"),
        "drillFilterOtherVisuals": True,
    }))
    v.append(line_chart("p2_linea_k01_serie", L.pos(852, 188, 412, 520),
                        (f_anio(), "Año"), [("K01 Puntuación media competencia", "Puntuación media (K01)")],
                        "Evolución de K01 por serie territorial comparable",
                        series=(col("DimContextoCentro", "AreaSerieComparable"), "Serie territorial comparable"),
                        subtitle="Todas las convocatorias",
                        alt="Gráfico de líneas con la puntuación media por año para cada serie territorial comparable"))
    inter = [("p2_seg_anio", "p2_linea_k01_serie"), ("p2_seg_area", "p2_barras_k07_area")]
    return pid, page(pid, "Táctico - Inspección", v, inter), v


NIVELES = [("Bajo", "#B35806"), ("Medio-bajo", "#F1A340"), ("Medio-alto", "#998EC3"), ("Alto", "#542788")]


def page3():
    L = Layout()
    pid = "Operativo_Direccion_Centro"
    v = []
    v.append(header("p3_cabecera", L.pos(16, 8, 1248, 40),
                    "Visión operativa - Dirección de centro",
                    "Seleccione el contexto del centro (área, naturaleza, hábitat) para compararlo con Cataluña. " + AVISO))
    w = 243.2
    xs = [16 + i * (w + 8) for i in range(5)]
    v.append(slicer("p3_seg_area", L.pos(round(xs[0], 1), 52, w, 60), f_area(), "Área territorial", "AreaTerritorial"))
    v.append(slicer("p3_seg_naturaleza", L.pos(round(xs[1], 1), 52, w, 60), col("DimContextoCentro", "Naturaleza"), "Naturaleza", "Naturaleza"))
    v.append(slicer("p3_seg_habitat", L.pos(round(xs[2], 1), 52, w, 60), col("DimContextoCentro", "Habitat"), "Hábitat", "Habitat"))
    v.append(slicer("p3_seg_anio", L.pos(round(xs[3], 1), 52, w, 60), f_anio(), "Año", "Anio", single=True, default_in=ANIO_DEFECTO))
    v.append(slicer("p3_seg_materia", L.pos(round(xs[4], 1), 52, w, 60), f_materia(), "Materia", "Materia"))
    cards = [
        ("p3_tarjeta_k01", "K01 Puntuación media competencia", "Puntuación media del contexto (K01)", "Competencias globales"),
        ("p3_tarjeta_k07", "K07 Desviación respecto a Cataluña", "Desviación respecto a Cataluña (K07)", "Puntos de diferencia"),
        ("p3_tarjeta_cataluna", "Puntuación media Cataluña", "Puntuación media de Cataluña", "Referencia sin filtros de contexto"),
        ("p3_tarjeta_estado_k01", "Estado K01", "Estado de K01", "1 favorable, 0 neutro, -1 desfavorable"),
    ]
    x = 16
    for name, m, title, sub in cards:
        v.append(card(name, L.pos(x, 120, 306, 96), m, title, sub))
        x += 314
    v.append(bar_chart("p3_barras_k02_subcomp", L.pos(16, 228, 410, 480),
                       (col("DimCompetencia", "Subcompetencia"), "Subcompetencia"),
                       ("K02 Puntuación media subcompetencia", "Puntuación media (K02)"),
                       "Puntuación media por subcompetencia (K02)",
                       series=(f_materia(), "Materia"),
                       subtitle="Excluye datos no válidos",
                       alt="Gráfico de barras con la puntuación media de cada subcompetencia, coloreado por materia"))
    nivel = col("DimNivelLogro", "Nivel")
    data_point = [{
        "properties": {"fill": color(hexv)},
        "selector": {"data": [{"scopeId": {"Comparison": {
            "ComparisonKind": 0,
            "Left": nivel,
            "Right": {"Literal": {"Value": txt(nv)}},
        }}}]},
    } for nv, hexv in NIVELES]
    filtros = [
        categorical_filter("f_p3_nivel_sin_no_aplica", col("DimNivelLogro", "Nivel"), [txt("No aplica (subcompetencia)")], negate=True),
        categorical_filter("f_p3_calidad_no_censurada", col("DimCalidadDato", "Censurada"), ["false"]),
        categorical_filter("f_p3_calidad_nivel_comparable", col("DimCalidadDato", "NivelNoComparable"), ["false"]),
    ]
    v.append(visual("p3_barras100_nivel", L.pos(434, 228, 410, 480), {
        "visualType": "hundredPercentStackedBarChart",
        "query": {"queryState": {
            "Category": {"projections": [proj(f_materia(), "Materia", active=True)]},
            "Series": {"projections": [proj(col("DimNivelLogro", "Nivel"), "Nivel de logro")]},
            "Y": {"projections": [proj(meas("Puntuaciones globales"), "Puntuaciones globales")]},
        }},
        "objects": {
            "legend": [{"properties": {"show": lit("true"), "position": lit("'Top'")}}],
            "dataPoint": data_point,
        },
        "visualContainerObjects": container_objects(
            "Distribución por nivel de logro", "Puntuaciones globales; excluye datos censurados y niveles no comparables",
            "Barras apiladas al 100 % con la proporción de puntuaciones globales en cada nivel de logro por materia"),
        "drillFilterOtherVisuals": True,
    }, filters=filtros))
    v.append(line_chart("p3_linea_k01_cataluna", L.pos(852, 228, 412, 480),
                        (f_anio(), "Año"),
                        [("K01 Puntuación media competencia", "Contexto seleccionado (K01)"),
                         ("Puntuación media Cataluña", "Cataluña")],
                        "Evolución: contexto seleccionado frente a Cataluña",
                        subtitle="Todas las convocatorias",
                        alt="Gráfico de líneas con la puntuación media del contexto seleccionado y la de Cataluña por año"))
    inter = [("p3_seg_anio", "p3_linea_k01_cataluna")]
    return pid, page(pid, "Operativo - Dirección de centro", v, inter), v


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main():
    if REPORT.exists():
        shutil.rmtree(REPORT)
    d = REPORT / "definition"
    write(REPORT / "definition.pbir", {
        "$schema": SCH_PBIR,
        "version": "4.0",
        "datasetReference": {"byPath": {"path": "../CMI_Educacion_Primaria.SemanticModel"}},
    })
    write(d / "version.json", {"$schema": SCH_VERSION, "version": "2.0.0"})
    write(d / "report.json", {
        "$schema": SCH_REPORT,
        "themeCollection": {"baseTheme": {
            "name": "CY24SU10",
            "reportVersionAtImport": {"visual": "1.8.95", "report": "2.0.95", "page": "1.3.95"},
            "type": "SharedResources",
        }},
        "resourcePackages": [{
            "name": "SharedResources",
            "type": "SharedResources",
            "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}],
        }],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True,
        },
    })
    theme_dst = REPORT / "StaticResources/SharedResources/BaseThemes/CY24SU10.json"
    theme_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(THEME_SRC, theme_dst)
    order = []
    for builder in (page1, page2, page3):
        pid, pg, visuals = builder()
        order.append(pid)
        write(d / "pages" / pid / "page.json", pg)
        for vis in visuals:
            write(d / "pages" / pid / "visuals" / vis["name"] / "visual.json", vis)
    write(d / "pages" / "pages.json", {"$schema": SCH_PAGES, "pageOrder": order, "activePageName": order[0]})
    refs = [{"Entity": e, "Property": p, "tipo": t} for e, p, t in sorted(REFS, key=lambda r: (r[2], r[0], r[1]))]
    with open(REFS_OUT, "w", encoding="utf-8") as fh:
        json.dump(refs, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"pages={order} refs={len(refs)}")


if __name__ == "__main__":
    sys.exit(main())
