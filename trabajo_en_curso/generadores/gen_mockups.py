"""Genera los mockups (wireframes) de los tres paneles del CMI para la memoria.

Son bocetos de propuesta de diseño: cajas grises, datos ficticios y llamadas numeradas que se explican en el texto.
Uso: python3 trabajo_en_curso/generadores/gen_mockups.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "Documentation/Docu_Final/Memoria/Latex_Memoria/imagenes"

E = 2  # escala: lienzo lógico 1280 x 720 (el de Power BI), imagen a 2560 x 1440
ANCHO, ALTO = 1280, 720
FUENTES = "/usr/share/fonts/truetype/lato/"

TINTA = (60, 60, 60)
GRIS = (150, 150, 150)
BORDE = (120, 120, 120)
FONDO_CAJA = (246, 246, 246)
RELLENO = (205, 205, 205)
ACENTO = (228, 87, 46)
TONOS = [(90, 90, 90), (130, 130, 130), (170, 170, 170), (205, 205, 205), (110, 110, 110), (190, 190, 190)]


def fuente(tam, peso="Regular"):
    return ImageFont.truetype(f"{FUENTES}Lato-{peso}.ttf", tam * E)


def r(*v):
    return [x * E for x in v]


class Lienzo:
    def __init__(self, titulo):
        self.img = Image.new("RGB", (ANCHO * E, ALTO * E), "white")
        self.d = ImageDraw.Draw(self.img)
        self.d.rectangle(r(0, 0, ANCHO, 52), fill=(232, 232, 232))
        self.d.text(r(20, 14), titulo, font=fuente(20, "Bold"), fill=TINTA)
        etiqueta = "Mockup · propuesta de diseño"
        self.d.rounded_rectangle(r(1040, 14, 1262, 40), radius=6 * E, outline=ACENTO, width=2 * E)
        self.d.text(r(1151, 27), etiqueta, font=fuente(13, "Bold"), fill=ACENTO, anchor="mm")

    def caja(self, x, y, w, h, titulo=None):
        self.d.rounded_rectangle(r(x, y, x + w, y + h), radius=6 * E, fill=FONDO_CAJA, outline=BORDE, width=E)
        if titulo:
            self.d.text(r(x + 12, y + 10), titulo, font=fuente(14, "Bold"), fill=TINTA)

    def segmentador(self, x, y, w, etiqueta):
        self.d.text(r(x, y), etiqueta, font=fuente(11), fill=GRIS)
        self.d.rounded_rectangle(r(x, y + 16, x + w, y + 40), radius=4 * E, fill="white", outline=BORDE, width=E)
        self.d.text(r(x + 8, y + 28), "Seleccionar", font=fuente(12), fill=GRIS, anchor="lm")
        cx, cy = x + w - 14, y + 28
        self.d.polygon(r(cx - 5, cy - 3, cx + 5, cy - 3, cx, cy + 4), fill=TINTA)

    def tarjeta(self, x, y, w, h, etiqueta, semaforo=False):
        self.caja(x, y, w, h)
        self.d.text(r(x + 12, y + 30), "00,0", font=fuente(28, "Bold"), fill=TINTA)
        self.d.multiline_text(r(x + 12, y + 68), etiqueta, font=fuente(11), fill=GRIS, spacing=2 * E)
        if semaforo:
            for i in range(3):
                cx = x + w - 52 + i * 16
                relleno = RELLENO if i == 1 else None
                self.d.ellipse(r(cx, y + 14, cx + 10, y + 24), outline=BORDE, fill=relleno, width=E)

    def ejes(self, x, y, w, h):
        x0, y0, x1, y1 = x + 40, y + 40, x + w - 16, y + h - 30
        self.d.line(r(x0, y0, x0, y1, x1, y1), fill=BORDE, width=E)
        return x0, y0, x1, y1

    def lineas(self, x, y, w, h, titulo, series, hueco=None, discontinua=None, leyenda=None):
        self.caja(x, y, w, h, titulo)
        if leyenda:
            lx = x + w - 16
            for s in reversed(range(len(leyenda))):
                ancho_txt = self.d.textlength(leyenda[s], font=fuente(10)) / E
                lx -= ancho_txt + 30
                yy = y + 18
                if discontinua is not None and s == discontinua:
                    for k in range(3):
                        self.d.line(r(lx + k * 7, yy, lx + k * 7 + 4, yy), fill=TONOS[s % 6], width=2 * E)
                else:
                    self.d.line(r(lx, yy, lx + 18, yy), fill=TONOS[s % 6], width=2 * E)
                self.d.text(r(lx + 22, yy), leyenda[s], font=fuente(10), fill=GRIS, anchor="lm")
        x0, y0, x1, y1 = self.ejes(x, y, w, h)
        n = 16
        for s in range(series):
            pts = []
            for i in range(n):
                v = 0.5 + 0.18 * math.sin(i * 0.6 + s * 1.3) + 0.08 * (s - series / 2) / series
                pts.append((x0 + 10 + i * (x1 - x0 - 20) / (n - 1), y1 - v * (y1 - y0)))
            tramos = [pts] if hueco is None else [pts[: hueco + 1], pts[hueco + 1 :]]
            for tramo in tramos:
                if discontinua is not None and s == discontinua:
                    for a, b in zip(tramo, tramo[1:]):
                        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                        self.d.line(r(*a, *m), fill=TONOS[s % 6], width=2 * E)
                else:
                    self.d.line([c * E for p in tramo for c in p], fill=TONOS[s % 6], width=2 * E)
        if hueco is not None:
            hx = x0 + 10 + (hueco + 0.5) * (x1 - x0 - 20) / (n - 1)
            self.d.line(r(hx, y0, hx, y1), fill=GRIS, width=E)
            self.d.text(r(hx + 4, y0), "sin prueba", font=fuente(10), fill=GRIS)

    def barras_divergentes(self, x, y, w, h, titulo, n):
        self.caja(x, y, w, h, titulo)
        cx = x + w / 2 + 40
        top, alto = y + 44, (h - 70) / n
        for i in range(n):
            v = math.sin(i * 1.7 + 0.4) * (w / 2 - 70)
            yy = top + i * alto
            self.d.text(r(x + 14, yy + alto / 2), f"Área {chr(65 + i)}", font=fuente(11), fill=GRIS, anchor="lm")
            self.d.rectangle(r(min(cx, cx + v), yy + 3, max(cx, cx + v), yy + alto - 3), fill=RELLENO, outline=BORDE)
        self.d.line(r(cx, top - 6, cx, top + n * alto), fill=TINTA, width=E)
        self.d.text(r(cx, y + h - 20), "Cataluña", font=fuente(11, "Bold"), fill=TINTA, anchor="mm")

    def barras(self, x, y, w, h, titulo, grupos, por_grupo):
        self.caja(x, y, w, h, titulo)
        x0, y0, x1, y1 = self.ejes(x, y, w, h)
        total = grupos * por_grupo + grupos - 1
        ancho = (x1 - x0 - 20) / total
        k = 0
        for g in range(grupos):
            for b in range(por_grupo):
                v = 0.45 + 0.3 * abs(math.sin(k * 0.9 + g))
                bx = x0 + 10 + (k + g) * ancho
                self.d.rectangle(r(bx, y1 - v * (y1 - y0), bx + ancho * 0.85, y1), fill=TONOS[g % 6])
                k += 1

    def apiladas(self, x, y, w, h, titulo, filas, leyenda):
        self.caja(x, y, w, h, titulo)
        x0, x1, top = x + 100, x + w - 16, y + 38
        alto = (h - 70) / len(filas)
        for i, fila in enumerate(filas):
            yy = top + i * alto
            self.d.text(r(x + 14, yy + alto / 2), fila, font=fuente(11), fill=GRIS, anchor="lm")
            partes = [0.15 + 0.05 * math.sin(i), 0.3, 0.35, 0.2 - 0.05 * math.sin(i)]
            acc = x0
            for j, p in enumerate(partes):
                fin = acc + p * (x1 - x0)
                self.d.rectangle(r(acc, yy + 3, fin, yy + alto - 3), fill=TONOS[j])
                acc = fin
        lx = x0
        for j, nombre in enumerate(leyenda):
            self.d.rectangle(r(lx, y + h - 22, lx + 10, y + h - 12), fill=TONOS[j])
            self.d.text(r(lx + 14, y + h - 17), nombre, font=fuente(10), fill=GRIS, anchor="lm")
            lx += 100

    def tabla(self, x, y, w, h, titulo, columnas, filas):
        self.caja(x, y, w, h, titulo)
        top = y + 42
        alto = (h - 54) / (len(filas) + 1)
        ancho = (w - 24) / len(columnas)
        for c, nombre in enumerate(columnas):
            self.d.text(r(x + 12 + c * ancho, top + alto / 2), nombre, font=fuente(12, "Bold"), fill=TINTA, anchor="lm")
        for f, fila in enumerate(filas, 1):
            yy = top + f * alto
            self.d.line(r(x + 12, yy, x + w - 12, yy), fill=RELLENO, width=E)
            for c in range(len(columnas)):
                texto = fila if c == 0 else "00,0"
                self.d.text(r(x + 12 + c * ancho, yy + alto / 2), texto, font=fuente(12), fill=GRIS, anchor="lm")

    def aviso(self, texto):
        self.d.rounded_rectangle(r(20, 640, 1260, 674), radius=4 * E, outline=GRIS, width=E)
        self.d.text(r(32, 657), texto, font=fuente(12, "Italic"), fill=GRIS, anchor="lm")

    def pestanas(self, activa):
        for i, nombre in enumerate(["Estratégico", "Táctico", "Operativo"]):
            x = 20 + i * 150
            relleno = RELLENO if i == activa else "white"
            self.d.rectangle(r(x, 684, x + 140, 712), fill=relleno, outline=BORDE, width=E)
            self.d.text(r(x + 70, 698), nombre, font=fuente(12, "Bold" if i == activa else "Regular"), fill=TINTA, anchor="mm")

    def llamada(self, n, x, y):
        self.d.ellipse(r(x - 13, y - 13, x + 13, y + 13), fill=ACENTO)
        self.d.text(r(x, y), str(n), font=fuente(14, "Bold"), fill="white", anchor="mm")

    def guardar(self, nombre):
        self.img.save(SALIDA / nombre, optimize=True)


AVISO = "Las puntuaciones no están equiparadas entre convocatorias · 2020 sin prueba · umbrales de nivel provisionales · en blanco si n < 30"
COMPETENCIAS = ["Catalán", "Castellano", "Matemáticas", "Inglés", "Ciencias"]


def fila_tarjetas(lz, etiquetas, semaforos=()):
    n = len(etiquetas)
    w = (1240 - (n - 1) * 12) / n
    for i, et in enumerate(etiquetas):
        lz.tarjeta(20 + i * (w + 12), 112, w, 100, et, semaforo=i in semaforos)


def estrategico():
    lz = Lienzo("Panel estratégico · Departamento de Educación")
    lz.segmentador(20, 58, 180, "Año")
    lz.segmentador(214, 58, 220, "Competencia")
    fila_tarjetas(lz, ["K01 Puntuación\nmedia", "K03 % alumnado\nen nivel bajo", "K06 Dispersión", "K10 Variación\ninteranual",
                       "K12 % competencias\nque mejoran", "Alumnado\nevaluado"], semaforos=(0, 1, 3))
    lz.lineas(20, 226, 740, 404, "Evolución de K01 por competencia", 5, hueco=10, leyenda=COMPETENCIAS)
    lz.tabla(776, 226, 484, 404, "Resumen por competencia del año seleccionado", ["Competencia", "K01", "K10", "K11", "K03"], COMPETENCIAS)
    lz.aviso(AVISO)
    lz.pestanas(0)
    for n, (x, y) in enumerate([(448, 86), (20, 112), (20, 226), (776, 226), (20, 640), (480, 698)], 1):
        lz.llamada(n, x, y)
    lz.guardar("mockup_estrategico.png")


def tactico():
    lz = Lienzo("Panel táctico · Inspección y coordinación territorial")
    lz.segmentador(20, 58, 180, "Año")
    lz.segmentador(214, 58, 220, "Competencia")
    lz.segmentador(448, 58, 260, "Área territorial")
    fila_tarjetas(lz, ["K04 Brecha de género\n(niños − niñas)", "K05 Brecha pública\n− privada", "K08 Diferencia\nurbano − rural",
                       "K09 Posición del área\n(1 = mejor)"])
    lz.barras_divergentes(20, 226, 600, 404, "K07 Desviación de cada área respecto a Cataluña", 12)
    lz.tabla(636, 226, 624, 196, "K01 por área y titularidad", ["Área", "Pública", "Privada", "Total"], ["Área A", "Área B", "Área C"])
    lz.lineas(636, 434, 624, 196, "K01 por serie territorial comparable", 3, leyenda=["Serie 1", "Serie 2", "Serie 3"])
    lz.aviso(AVISO)
    lz.pestanas(1)
    for n, (x, y) in enumerate([(722, 86), (20, 112), (20, 226), (636, 226), (636, 434)], 1):
        lz.llamada(n, x, y)
    lz.guardar("mockup_tactico.png")


def operativo():
    lz = Lienzo("Panel operativo · Dirección de centro")
    for i, et in enumerate(["Área territorial", "Titularidad", "Hábitat", "Año", "Competencia"]):
        lz.segmentador(20 + i * 196, 58, 182, et)
    fila_tarjetas(lz, ["K01 Puntuación media\ndel contexto", "K07 Desviación\nrespecto a Cataluña", "Puntuación media\nde Cataluña",
                       "Estado respecto\na la referencia"], semaforos=(3,))
    lz.barras(20, 226, 600, 404, "K02 Puntuación media por subcompetencia", 5, 3)
    lz.apiladas(636, 226, 624, 196, "Distribución por nivel de logro", COMPETENCIAS[:4], ["Bajo", "Medio-bajo", "Medio-alto", "Alto"])
    lz.lineas(636, 434, 624, 196, "K01 del contexto frente a Cataluña", 2, discontinua=1, leyenda=["Contexto", "Cataluña"])
    lz.aviso(AVISO)
    lz.pestanas(2)
    for n, (x, y) in enumerate([(1008, 86), (20, 112), (20, 226), (636, 226), (636, 434)], 1):
        lz.llamada(n, x, y)
    lz.guardar("mockup_operativo.png")


if __name__ == "__main__":
    estrategico()
    tactico()
    operativo()
    print(f"Mockups generados en {SALIDA}")
