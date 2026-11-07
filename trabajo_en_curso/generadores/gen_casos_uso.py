"""Genera el diagrama de casos de uso (notación UML) del capítulo de especificación de la memoria.

Uso: python3 trabajo_en_curso/generadores/gen_casos_uso.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "Documentation/Docu_Final/Memoria/Latex_Memoria/imagenes/especificacion"

E = 2
ANCHO, ALTO = 1280, 950
FUENTES = "/usr/share/fonts/truetype/lato/"
TINTA = (40, 40, 40)
GRIS = (110, 110, 110)
FONDO_CU = (244, 244, 244)
CU_W, CU_H = 310, 80


def fuente(tam, peso="Regular"):
    return ImageFont.truetype(f"{FUENTES}Lato-{peso}.ttf", tam * E)


def r(*v):
    return [x * E for x in v]


img = Image.new("RGB", (ANCHO * E, ALTO * E), "white")
d = ImageDraw.Draw(img)


def actor(x, y, nombre):
    """Monigote UML con la cabeza centrada en (x, y - 34); devuelve el punto medio del cuerpo."""
    d.ellipse(r(x - 11, y - 45, x + 11, y - 23), outline=TINTA, width=2 * E)
    d.line(r(x, y - 23, x, y + 10), fill=TINTA, width=2 * E)
    d.line(r(x - 20, y - 12, x + 20, y - 12), fill=TINTA, width=2 * E)
    d.line(r(x, y + 10, x - 15, y + 32), fill=TINTA, width=2 * E)
    d.line(r(x, y + 10, x + 15, y + 32), fill=TINTA, width=2 * E)
    d.multiline_text(r(x, y + 40), nombre, font=fuente(17, "Bold"), fill=TINTA, anchor="ma", align="center",
                     spacing=2 * E)


def caso(x, y, ident, texto):
    d.ellipse(r(x - CU_W / 2, y - CU_H / 2, x + CU_W / 2, y + CU_H / 2), fill=FONDO_CU, outline=TINTA, width=2 * E)
    dos = "\n" in texto
    d.text(r(x, y - (24 if dos else 15)), ident, font=fuente(14, "Bold"), fill=GRIS, anchor="mm")
    d.multiline_text(r(x, y + (13 if dos else 10)), texto, font=fuente(17), fill=TINTA, anchor="mm", align="center", spacing=2 * E)


def borde_elipse(cx, cy, hacia_x, hacia_y):
    ang = math.atan2(hacia_y - cy, hacia_x - cx)
    a, b = CU_W / 2, CU_H / 2
    t = 1 / math.sqrt((math.cos(ang) / a) ** 2 + (math.sin(ang) / b) ** 2)
    return cx + t * math.cos(ang), cy + t * math.sin(ang)


def asociacion(x0, y0, cu):
    x1, y1 = borde_elipse(*cu, x0, y0)
    d.line(r(x0, y0, x1, y1), fill=TINTA, width=2 * E)


def punta_abierta(x0, y0, x1, y1):
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        d.line(r(x1, y1, x1 - 13 * math.cos(ang + s * 0.45), y1 - 13 * math.sin(ang + s * 0.45)), fill=TINTA,
               width=2 * E)


def include(origen, destino, etiqueta_dx=0, etiqueta_dy=-12):
    x0, y0 = borde_elipse(*origen, *destino)
    x1, y1 = borde_elipse(*destino, *origen)
    largo = math.hypot(x1 - x0, y1 - y0)
    pasos = int(largo // 9)
    for i in range(0, pasos, 2):
        a, b = i / pasos, min((i + 1) / pasos, 1)
        d.line(r(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=TINTA,
               width=2 * E)
    punta_abierta(x0, y0, x1, y1)
    mx, my = (x0 + x1) / 2 + etiqueta_dx, (y0 + y1) / 2 + etiqueta_dy
    d.text(r(mx, my), "«include»", font=fuente(15, "Italic"), fill=GRIS, anchor="mm")


# Límite del sistema
SX0, SY0, SX1, SY1 = 300, 20, 1100, 910
d.rectangle(r(SX0, SY0, SX1, SY1), outline=TINTA, width=2 * E)
d.text(r(SX0 + 16, SY0 + 12), "CMI de la evaluación de 6.º de primaria", font=fuente(19, "Bold"), fill=TINTA)

# Casos de uso
C1 = (660, 850)
C2, C3, C4 = (480, 410), (480, 545), (480, 680)
C5, C6, C10 = (480, 110), (480, 200), (480, 290)
C7, C8, C9 = (925, 575), (925, 670), (925, 765)
caso(*C1, "CU01", "Cargar y depurar\nlas convocatorias")
caso(*C2, "CU02", "Consultar el panel estratégico")
caso(*C3, "CU03", "Consultar el panel táctico")
caso(*C4, "CU04", "Consultar el panel operativo")
caso(*C5, "CU05", "Filtrar los resultados")
caso(*C6, "CU06", "Consultar la evolución temporal")
caso(*C10, "CU10", "Cambiar de panel")
caso(*C7, "CU07", "Comparar con Cataluña")
caso(*C8, "CU08", "Desglosar por subcompetencias")
caso(*C9, "CU09", "Consultar la distribución\npor nivel de logro")

# Actores principales y generalización hacia el usuario genérico
UX, UY = 75, 170
actor(UX, UY, "Usuario\ndel CMI")
perfiles = [(190, 410, "Departamento de\nEducación (E)"), (190, 545, "Inspección\nterritorial (T)"),
            (190, 680, "Dirección\nde centro (O)")]
for x, y, nombre in perfiles:
    actor(x, y, nombre)
tronco_y0 = UY + 112
d.polygon(r(UX, tronco_y0 - 16, UX - 10, tronco_y0, UX + 10, tronco_y0), outline=TINTA, fill="white", width=2 * E)
d.line(r(UX, tronco_y0, UX, perfiles[-1][1] - 12), fill=TINTA, width=2 * E)
for x, y, _ in perfiles:
    d.line(r(UX, y - 12, x - 20, y - 12), fill=TINTA, width=2 * E)

for cu in (C5, C6, C10):
    asociacion(UX + 20, UY - 12, cu)
for (x, y, _), cu in zip(perfiles, (C2, C3, C4)):
    asociacion(x + 20, y - 12, cu)

include(C3, C7, etiqueta_dx=10, etiqueta_dy=-14)
include(C4, C7, etiqueta_dx=-10, etiqueta_dy=-14)
include(C4, C8, etiqueta_dy=-13)
include(C4, C9, etiqueta_dx=-20, etiqueta_dy=8)

# Carga de datos: desarrolladora y sistema externo
actor(190, 850, "Desarrolladora")
asociacion(210, 838, C1)
PX, PY = 1195, 850
actor(PX, PY, "Portal de\nDatos Abiertos")
d.text(r(PX, PY - 66), "«sistema externo»", font=fuente(14, "Italic"), fill=GRIS, anchor="mm")
asociacion(PX - 20, PY - 12, C1)

SALIDA.mkdir(parents=True, exist_ok=True)
img.save(SALIDA / "casos_uso.png", optimize=True)
print(f"Diagrama creado: {SALIDA / 'casos_uso.png'}")
