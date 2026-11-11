"""Genera el diagrama de arquitectura general del sistema para el capítulo de especificación de la memoria.

Muestra el recorrido de los datos desde el Portal de Datos Abiertos hasta los paneles de cada perfil.
Uso: python3 trabajo_en_curso/generadores/gen_arquitectura.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "Documentation/Docu_Final/Memoria/Latex_Memoria/imagenes/especificacion"

E = 2
ANCHO, ALTO = 1280, 730
# Lato: carpeta de Linux (paquete fonts-lato) o de Windows; se usa la primera que exista
FUENTES = next((c for c in ("/usr/share/fonts/truetype/lato/", "C:/Windows/Fonts/",
                            str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts") + "/")
                if (Path(c) / "Lato-Regular.ttf").exists()), "/usr/share/fonts/truetype/lato/")
TINTA = (40, 40, 40)
GRIS = (110, 110, 110)
CABECERA = (232, 232, 232)
FONDO_PBI = (247, 247, 247)

img = Image.new("RGB", (ANCHO * E, ALTO * E), "white")
d = ImageDraw.Draw(img)


def fuente(tam, peso="Regular"):
    return ImageFont.truetype(f"{FUENTES}Lato-{peso}.ttf", tam * E)


def r(*v):
    return [x * E for x in v]


def texto(x, y, t, tam=14, peso="Regular", color=TINTA, anchor="mm", align="center"):
    d.multiline_text(r(x, y), t, font=fuente(tam, peso), fill=color, anchor=anchor, align=align, spacing=3 * E)


def bloque(x, y, w, h, titulo, subtitulo, elementos):
    """Caja con cabecera; cada elemento es una viñeta y sus saltos de línea continúan sin viñeta nueva."""
    d.rounded_rectangle(r(x, y, x + w, y + h), radius=8 * E, fill="white", outline=TINTA, width=2 * E)
    d.rounded_rectangle(r(x, y, x + w, y + 58), radius=8 * E, fill=CABECERA, outline=TINTA, width=2 * E)
    d.rectangle(r(x + 2, y + 40, x + w - 2, y + 56), fill=CABECERA)
    d.line(r(x, y + 58, x + w, y + 58), fill=TINTA, width=2 * E)
    texto(x + w / 2, y + 20, titulo, 16, "Bold")
    texto(x + w / 2, y + 42, subtitulo, 13, "Italic", GRIS)
    fila = 0
    for elemento in elementos:
        d.text(r(x + 14, y + 72 + fila * 23), "•", font=fuente(14), fill=GRIS)
        for linea in elemento.split("\n"):
            d.text(r(x + 28, y + 72 + fila * 23), linea, font=fuente(14), fill=TINTA)
            fila += 1
        fila += 0.3


def segmento(x0, y0, x1, y1, discontinua=False):
    if not discontinua:
        d.line(r(x0, y0, x1, y1), fill=TINTA, width=2 * E)
        return
    largo = math.hypot(x1 - x0, y1 - y0)
    pasos = max(int(largo // 8), 1)
    for i in range(0, pasos, 2):
        a, b = i / pasos, min((i + 1) / pasos, 1)
        d.line(r(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=TINTA,
               width=2 * E)


def flecha(*puntos, discontinua=False):
    """Polilínea con punta en el último punto."""
    for (x0, y0), (x1, y1) in zip(puntos, puntos[1:]):
        segmento(x0, y0, x1, y1, discontinua)
    (x0, y0), (x1, y1) = puntos[-2], puntos[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    d.polygon(r(x1, y1, x1 - 12 * math.cos(ang - 0.4), y1 - 12 * math.sin(ang - 0.4),
                x1 - 12 * math.cos(ang + 0.4), y1 - 12 * math.sin(ang + 0.4)), fill=TINTA)


def actor(x, y, nombre):
    d.ellipse(r(x - 9, y - 38, x + 9, y - 20), outline=TINTA, width=2 * E)
    d.line(r(x, y - 20, x, y + 6), fill=TINTA, width=2 * E)
    d.line(r(x - 16, y - 11, x + 16, y - 11), fill=TINTA, width=2 * E)
    d.line(r(x, y + 6, x - 12, y + 24), fill=TINTA, width=2 * E)
    d.line(r(x, y + 6, x + 12, y + 24), fill=TINTA, width=2 * E)
    texto(x, y + 38, nombre, 13, "Bold")


# Marco de Power BI Desktop, que contiene la ETL, el modelo, la lógica y los paneles
Y, H, W = 90, 270, 230
PX0, PY0, PX1, PY1 = 250, 40, 1250, Y + H + 30
d.rounded_rectangle(r(PX0, PY0, PX1, PY1), radius=12 * E, fill=FONDO_PBI, outline=GRIS, width=2 * E)
texto(PX0 + 16, PY0 + 16, "Proyecto de Power BI Desktop (.pbip)", 15, "Bold", GRIS, anchor="lm")

X = [20, 270, 520, 770, 1010]
bloque(X[0], Y, 210, H, "Fuente", "Portal de Datos Abiertos",
       ["Fichero CSV", "32 columnas", "1,1 millones de filas", "16 convocatorias\n(2009–2025)"])
bloque(X[1], Y, W, H, "ETL", "Power Query (M)",
       ["Lectura y comprobación", "Unificación de códigos", "Corrección de errores", "Marcas de calidad",
        "Despivotado de las\n24 puntuaciones"])
bloque(X[2], Y, W, H, "Modelo dimensional", "Motor VertiPaq",
       ["2 tablas de hechos:\nevaluaciones y\npuntuaciones", "6 dimensiones: año,\ncontexto, perfil,\ncompetencia, nivel\ny calidad del dato"])
bloque(X[3], Y, 220, H, "Lógica analítica", "Medidas DAX",
       ["12 KPIs", "Semáforos", "Regla de las\n30 puntuaciones", "Comparación con\nCataluña"])
bloque(X[4], Y, 220, H, "Interfaz", "Informe de Power BI",
       ["Panel estratégico", "Panel táctico", "Panel operativo", "Filtros sincronizados", "Aviso de\nlimitaciones"])

YF = Y + H / 2
flecha((X[0] + 210, YF), (X[1], YF))
flecha((X[1] + W, YF), (X[2], YF))
flecha((X[2] + W, YF), (X[3], YF))
flecha((X[3] + 220, YF), (X[4], YF))

YA = PY1 + 110
cx = X[4] + 110
for nombre, dx in (("E", -60), ("T", 0), ("O", 60)):
    actor(cx + dx, YA, nombre)
flecha((cx, YA - 48), (cx, PY1 + 2))
texto(cx + 10, PY1 + 30, "CU02–CU10", 12, "Italic", GRIS, anchor="lm")

dx_ = X[1] + W / 2
actor(dx_, YA, "Desarrolladora")
flecha((dx_, YA - 48), (dx_, PY1 + 2))
texto(dx_ + 10, PY1 + 30, "CU01", 12, "Italic", GRIS, anchor="lm")

# Validación independiente, fuera de Power BI
VX0, VY0, VX1, VY1 = 360, YA + 90, 820, YA + 190
d.rounded_rectangle(r(VX0, VY0, VX1, VY1), radius=8 * E, fill="white", outline=TINTA, width=2 * E)
texto((VX0 + VX1) / 2, VY0 + 24, "Validación independiente (Python y DuckDB)", 15, "Bold")
texto((VX0 + VX1) / 2, VY0 + 64, "Réplica de la ETL y de los KPIs fuera de Power BI\ny contraste con los informes oficiales",
      13, color=GRIS)
ym = (VY0 + VY1) / 2
flecha((VX0, ym), (X[0] + 105, ym), (X[0] + 105, Y + H + 2), discontinua=True)
texto(X[0] + 115, ym - 12, "lee el mismo fichero", 12, "Italic", GRIS, anchor="lm")
xl = X[3] + 110
flecha((VX1, ym), (xl, ym), (xl, PY1 - 28 - 2), discontinua=True)
texto(xl + 10, ym - 40, "compara los resultados", 12, "Italic", GRIS, anchor="lm")

SALIDA.mkdir(parents=True, exist_ok=True)
img.save(SALIDA / "arquitectura.png", optimize=True)
print(f"Diagrama creado: {SALIDA / 'arquitectura.png'}")
