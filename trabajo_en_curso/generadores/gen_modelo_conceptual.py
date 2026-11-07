"""Genera el modelo conceptual (diagrama de clases UML) del capítulo de especificación de la memoria.

Describe los conceptos del dominio con independencia de Power BI; el diseño lo traduce a un modelo en estrella.
Uso: python3 trabajo_en_curso/generadores/gen_modelo_conceptual.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "Documentation/Docu_Final/Memoria/Latex_Memoria/imagenes/especificacion"

E = 2
ANCHO, ALTO = 1280, 900
FUENTES = "/usr/share/fonts/truetype/lato/"
TINTA = (40, 40, 40)
GRIS = (110, 110, 110)
CABECERA = (232, 232, 232)
LINEA_ATRIB = 22

img = Image.new("RGB", (ANCHO * E, ALTO * E), "white")
d = ImageDraw.Draw(img)


def fuente(tam, peso="Regular"):
    return ImageFont.truetype(f"{FUENTES}Lato-{peso}.ttf", tam * E)


def r(*v):
    return [x * E for x in v]


class Clase:
    def __init__(self, x, y, w, nombre, atributos, abstracta=False):
        self.x, self.y, self.w = x, y, w
        self.h = 40 + 12 + LINEA_ATRIB * len(atributos)
        d.rectangle(r(x, y, x + w, y + self.h), fill="white", outline=TINTA, width=2 * E)
        d.rectangle(r(x, y, x + w, y + 40), fill=CABECERA, outline=TINTA, width=2 * E)
        d.text(r(x + w / 2, y + 20), nombre, font=fuente(17, "BoldItalic" if abstracta else "Bold"), fill=TINTA,
               anchor="mm")
        for i, a in enumerate(atributos):
            d.text(r(x + 12, y + 48 + i * LINEA_ATRIB), a, font=fuente(14), fill=TINTA)

    @property
    def arriba(self):
        return self.x + self.w / 2, self.y

    @property
    def abajo(self):
        return self.x + self.w / 2, self.y + self.h

    def izq(self, dy=20):
        return self.x, self.y + dy

    def der(self, dy=20):
        return self.x + self.w, self.y + dy


def texto(x, y, t, tam=14, peso="Regular", color=TINTA, anchor="mm"):
    d.text(r(x, y), t, font=fuente(tam, peso), fill=color, anchor=anchor)


def asociacion(p0, p1, m0, m1, nombre=None, desp=(0, -14), lado=1):
    """Línea entre p0 y p1 con la multiplicidad m0 junto a p0 y m1 junto a p1."""
    d.line(r(*p0, *p1), fill=TINTA, width=2 * E)
    horizontal = abs(p1[0] - p0[0]) > abs(p1[1] - p0[1])
    for (x, y), m, otro in ((p0, m0, p1), (p1, m1, p0)):
        if horizontal:
            sx = 1 if otro[0] > x else -1
            texto(x + sx * 18, y - 14, m, 16, anchor="mm")
        else:
            sy = 1 if otro[1] > y else -1
            texto(x + 14 * lado, y + sy * 17, m, 16, anchor="lm" if lado > 0 else "rm")
    if nombre:
        texto((p0[0] + p1[0]) / 2 + desp[0], (p0[1] + p1[1]) / 2 + desp[1], nombre, 13, "Italic", GRIS)


def discontinua(p0, p1):
    x0, y0 = p0
    x1, y1 = p1
    largo = max(abs(x1 - x0), abs(y1 - y0))
    pasos = int(largo // 8)
    for i in range(0, pasos, 2):
        a, b = i / pasos, (i + 1) / pasos
        d.line(r(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=TINTA,
               width=2 * E)


convocatoria = Clase(40, 40, 270, "Convocatoria", ["año: Entero", "curso: Texto", "hayPrueba: Booleano",
                                                     "nota: Texto"])
evaluacion = Clase(480, 40, 300, "Evaluación", ["género: {niña, niño}", "edad: Entero [0..1]",
                                                 "situaciónEdad: Texto", "mesNacimiento: Entero [0..1]"])
contexto = Clase(950, 40, 290, "ContextoDeCentro", ["titularidad: {pública, privada}", "hábitat: Texto"])
area = Clase(950, 270, 290, "ÁreaTerritorial", ["nombre: Texto", "serieComparable: Texto",
                                                "conRupturaDeSerie: Booleano"])
puntuacion = Clase(40, 300, 270, "Puntuación", ["valor: Real [0..100]", "noVálida: Booleano", "censurada: Booleano",
                                                 "noComparable: Booleano"])
nivel = Clase(40, 600, 270, "NivelDeLogro", ["nombre: Texto", "límiteInferior: Real", "límiteSuperior: Real"])
elemento = Clase(480, 430, 300, "ElementoEvaluado", ["nombre: Texto", "añoInicio: Entero",
                                                     "añoFin: Entero [0..1]"], abstracta=True)
competencia = Clase(370, 720, 210, "Competencia", ["esInformativa: Booleano"])
subcompetencia = Clase(700, 720, 210, "Subcompetencia", [])
indicador = Clase(950, 500, 290, "Indicador", ["código: Texto", "nombre: Texto", "sentidoFavorable: Texto",
                                               "referencia: Texto"])
perspectiva = Clase(950, 780, 290, "Perspectiva", ["nombre: Texto", "objetivo: Texto"])

asociacion(convocatoria.der(60), evaluacion.izq(60), "1", "*", "pertenece a", (0, 14))
asociacion(evaluacion.der(60), contexto.izq(60), "*", "1", "se realiza en", (0, 14))
asociacion(contexto.abajo, area.arriba, "*", "1", "está en", (-40, 0))
x_ev = evaluacion.abajo[0]
asociacion(evaluacion.abajo, elemento.arriba, "*", "*", "es puntuada en", (60, 30))
medio = (x_ev, (evaluacion.abajo[1] + elemento.arriba[1]) / 2)
discontinua(puntuacion.der(60), medio)
asociacion(puntuacion.abajo, nivel.arriba, "*", "0..1", "se clasifica en", (-62, 0))
asociacion(competencia.der(26), subcompetencia.izq(26), "1", "1..*", "se desglosa en", (0, 16))
asociacion(indicador.abajo, perspectiva.arriba, "*", "1", "pertenece a", (-50, 0))

# Generalización: Competencia y Subcompetencia son elementos evaluados
punta_y = elemento.abajo[1]
base_y = punta_y + 16
cx = elemento.abajo[0]
d.polygon(r(cx, punta_y, cx - 11, base_y, cx + 11, base_y), outline=TINTA, fill="white", width=2 * E)
union_y = base_y + 50
d.line(r(cx, base_y, cx, union_y), fill=TINTA, width=2 * E)
d.line(r(competencia.arriba[0], union_y, subcompetencia.arriba[0], union_y), fill=TINTA, width=2 * E)
for c in (competencia, subcompetencia):
    d.line(r(c.arriba[0], union_y, *c.arriba), fill=TINTA, width=2 * E)
texto(cx + 14, base_y + 22, "{disjunta, completa}", 13, "Italic", GRIS, anchor="lm")

SALIDA.mkdir(parents=True, exist_ok=True)
img.save(SALIDA / "modelo_conceptual.png", optimize=True)
print(f"Diagrama creado: {SALIDA / 'modelo_conceptual.png'}")
