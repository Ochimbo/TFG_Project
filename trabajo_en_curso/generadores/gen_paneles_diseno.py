"""Genera la disposición final de los tres paneles (capítulo de diseño de la memoria).

Lee la posición, el tipo, el título y los campos de cada visual de los ficheros visual.json del informe (PowerBI/,
formato PBIR) y los dibuja como un esquema de cajas a escala sobre el lienzo de 1280 x 720. No inventa nada: si
cambia el informe, se vuelve a ejecutar. Mismo estilo que gen_modelo_conceptual.py.
Uso: python3 trabajo_en_curso/generadores/gen_paneles_diseno.py
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
PAGINAS = RAIZ / "PowerBI/CMI_Educacion_Primaria.Report/definition/pages"
SALIDA = RAIZ / "Documentation/Docu_Final/Memoria/Latex_Memoria/imagenes/diseno"

E = 2
MARGEN = 12
ANCHO, ALTO = 1280, 720
# Lato: carpeta de Linux (paquete fonts-lato) o de Windows; se usa la primera que exista
FUENTES = next((c for c in ("/usr/share/fonts/truetype/lato/", "C:/Windows/Fonts/",
                            str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts") + "/")
                if (Path(c) / "Lato-Regular.ttf").exists()), "/usr/share/fonts/truetype/lato/")
TINTA = (40, 40, 40)
GRIS = (110, 110, 110)
CABECERA = (232, 232, 232)
FONDO_VISUAL = (248, 248, 248)
AVISO = (164, 38, 44)  # color del «Aviso:» del informe (#A4262C)

TIPOS = {
    "card": "Tarjeta",
    "slicer": "Segmentador",
    "lineChart": "Gráfico de líneas",
    "clusteredBarChart": "Barras agrupadas",
    "hundredPercentStackedBarChart": "Barras apiladas al 100 %",
    "tableEx": "Tabla",
    "pivotTable": "Matriz",
}
PAGINAS_SALIDA = {
    "Estrategico_Departamento": "panel_estrategico.png",
    "Tactico_Inspeccion": "panel_tactico.png",
    "Operativo_Direccion_Centro": "panel_operativo.png",
}


def fuente(tam, peso="Regular"):
    return ImageFont.truetype(f"{FUENTES}Lato-{peso}.ttf", int(tam * E))


def r(*v):
    return [(x + MARGEN) * E for x in v]


def literal(objetos, nombre, prop):
    """Valor literal de una propiedad de formato (por ejemplo, el texto del título) o None."""
    for o in objetos.get(nombre, []):
        valor = o.get("properties", {}).get(prop, {}).get("expr", {}).get("Literal", {}).get("Value")
        if valor is not None:
            return valor.strip("'")
    return None


def campos(visual):
    """Nombres visibles de los campos del visual: el alias si existe, si no la columna o la medida."""
    nombres = []
    for rol in visual.get("query", {}).get("queryState", {}).values():
        for p in rol.get("projections", []):
            campo = p.get("field", {})
            prop = (campo.get("Measure") or campo.get("Column") or {}).get("Property")
            nombre = p.get("displayName") or prop
            if nombre and nombre not in nombres:
                nombres.append(nombre)
    return nombres


def partir(texto, f, ancho):
    """Divide el texto en líneas que caben en el ancho (en píxeles de la imagen)."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if f.getlength(prueba) <= ancho * E or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def escribir(d, x, y, ancho, texto, tam, peso="Regular", color=TINTA, interlinea=1.25, max_lineas=None):
    f = fuente(tam, peso)
    lineas = partir(texto, f, ancho)
    if max_lineas and len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        lineas[-1] = lineas[-1].rstrip(".,;") + "…"
    for i, linea in enumerate(lineas):
        d.text(r(x, y + i * tam * interlinea), linea, font=f, fill=color)
    return y + len(lineas) * tam * interlinea


def cuadro_texto(d, v, x, y, w, h):
    """Cuadro de texto (cabecera o aviso): se reproducen sus párrafos con el peso y el color del informe.
    El texto que no cabe en la altura del cuadro se corta con «…», como hace el informe."""
    yy = y + 4
    for par in v["visual"].get("objects", {}).get("general", [{}])[0].get("properties", {}).get("paragraphs", []):
        runs = par.get("textRuns", [])
        primero = runs[0] if runs else {}
        estilo = primero.get("textStyle", {})
        tam_pt = float(estilo.get("fontSize", "10pt").rstrip("pt"))
        tam = 26 if tam_pt >= 14 else 17
        caben = int((y + h - yy) // (tam * 1.25))
        if caben < 1:
            break
        if primero.get("value", "").startswith("Aviso"):
            d.text(r(x + 4, yy), "Aviso:", font=fuente(tam, "Bold"), fill=AVISO)
            resto = " ".join(t["value"].strip() for t in runs[1:])
            ancho_aviso = fuente(tam, "Bold").getlength("Aviso: ") / E
            yy = escribir(d, x + 4 + ancho_aviso, yy, w - 8 - ancho_aviso, resto, tam, "Bold", max_lineas=caben)
        else:
            texto = "".join(t["value"] for t in runs)
            peso = "Bold" if estilo.get("fontWeight") == "bold" else "Regular"
            yy = escribir(d, x + 4, yy, w - 8, texto, tam, peso, TINTA if peso == "Bold" else GRIS, max_lineas=caben)
        yy += 2


def visual(d, v):
    pos = v["position"]
    x, y, w, h = pos["x"], pos["y"], pos["width"], pos["height"]
    tipo = v["visual"]["visualType"]
    if tipo == "textbox":
        cuadro_texto(d, v, x, y, w, h)
        return
    contenedor = v["visual"].get("visualContainerObjects", {})
    titulo = literal(contenedor, "title", "text") or ""
    subtitulo = literal(contenedor, "subTitle", "text")
    d.rectangle(r(x + 2, y + 2, x + w - 2, y + h - 2), fill=FONDO_VISUAL, outline=TINTA, width=E + 1)
    if tipo == "slicer":
        escribir(d, x + 10, y + 6, w - 20, titulo, 19, "Bold", max_lineas=1)
        d.rectangle(r(x + 10, y + 34, x + w - 10, y + h - 8), fill="white", outline=GRIS, width=E)
        d.polygon(r(x + w - 30, y + 38, x + w - 18, y + 38, x + w - 24, y + 45), fill=GRIS)
        return
    yy = escribir(d, x + 10, y + 7, w - 20, titulo, 19, "Bold", max_lineas=3)
    if subtitulo:
        caben = max(1, min(2, int((y + h - 6 - (yy + 1)) // (16 * 1.25))))
        yy = escribir(d, x + 10, yy + 1, w - 20, subtitulo, 16, "Italic", GRIS, max_lineas=caben)
    if tipo == "card":
        return
    d.line(r(x + 10, yy + 6, x + w - 10, yy + 6), fill=GRIS, width=E)
    yy += 16
    yy = escribir(d, x + 10, yy, w - 20, TIPOS.get(tipo, tipo), 18, "Italic", GRIS)
    escribir(d, x + 10, yy + 4, w - 20, "Campos: " + "; ".join(campos(v["visual"])), 17, color=GRIS,
             max_lineas=6)


SALIDA.mkdir(parents=True, exist_ok=True)
for carpeta, nombre in PAGINAS_SALIDA.items():
    img = Image.new("RGB", ((ANCHO + 2 * MARGEN) * E, (ALTO + 2 * MARGEN) * E), "white")
    d = ImageDraw.Draw(img)
    d.rectangle(r(0, 0, ANCHO, ALTO), outline=TINTA, width=2 * E)
    # Los cuadros de texto van debajo: en el informe la cabecera ocupa todo el ancho y los segmentadores se le superponen
    visuales = [json.loads(f.read_text(encoding="utf-8"))
                for f in sorted((PAGINAS / carpeta / "visuals").glob("*/visual.json"))]
    for v in sorted(visuales, key=lambda v: v["visual"]["visualType"] != "textbox"):
        visual(d, v)
    img.save(SALIDA / nombre, optimize=True)
    print(f"Diagrama creado: {SALIDA / nombre}")
