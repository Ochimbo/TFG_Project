"""Genera el esquema en estrella del modelo dimensional (capítulo de diseño de la memoria).

Dibuja las 8 tablas del modelo semántico (2 de hechos y 6 dimensiones) con sus claves y las 9 relaciones
muchos a uno de relationships.tmdl. Mismo estilo que gen_modelo_conceptual.py.
Uso: python3 trabajo_en_curso/generadores/gen_esquema_estrella.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "Documentation/Docu_Final/Memoria/Latex_Memoria/imagenes/diseno"

E = 2
ANCHO, ALTO = 1280, 820
# Lato: carpeta de Linux (paquete fonts-lato) o de Windows; se usa la primera que exista
FUENTES = next((c for c in ("/usr/share/fonts/truetype/lato/", "C:/Windows/Fonts/",
                            str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts") + "/")
                if (Path(c) / "Lato-Regular.ttf").exists()), "/usr/share/fonts/truetype/lato/")
TINTA = (40, 40, 40)
GRIS = (110, 110, 110)
CABECERA = (232, 232, 232)
CABECERA_HECHOS = (200, 200, 200)
LINEA_ATRIB = 22
ALTO_CAB = 52

img = Image.new("RGB", (ANCHO * E, ALTO * E), "white")
d = ImageDraw.Draw(img)


def fuente(tam, peso="Regular"):
    return ImageFont.truetype(f"{FUENTES}Lato-{peso}.ttf", tam * E)


def r(*v):
    return [x * E for x in v]


def texto(x, y, t, tam=14, peso="Regular", color=TINTA, anchor="mm"):
    d.text(r(x, y), t, font=fuente(tam, peso), fill=color, anchor=anchor)


class Tabla:
    """Caja con el nombre, el tipo y las filas, y una línea por columna («PK»/«FK» a la izquierda)."""

    def __init__(self, x, y, w, nombre, subtitulo, columnas, hechos=False):
        self.x, self.y, self.w = x, y, w
        self.h = ALTO_CAB + 12 + LINEA_ATRIB * len(columnas)
        self.filas = {}
        d.rectangle(r(x, y, x + w, y + self.h), fill="white", outline=TINTA, width=2 * E)
        d.rectangle(r(x, y, x + w, y + ALTO_CAB), fill=CABECERA_HECHOS if hechos else CABECERA, outline=TINTA,
                    width=2 * E)
        texto(x + w / 2, y + 19, nombre, 17, "Bold")
        texto(x + w / 2, y + 39, subtitulo, 12, "Italic", GRIS)
        for i, (marca, col) in enumerate(columnas):
            cy = y + ALTO_CAB + 6 + i * LINEA_ATRIB + LINEA_ATRIB / 2
            self.filas[col] = cy
            if marca:
                texto(x + 12, cy, marca, 12, "Bold", GRIS, anchor="lm")
            texto(x + 44, cy, col, 14, "Bold" if marca == "PK" else "Regular", anchor="lm")

    def izq(self, col):
        return self.x, self.filas[col]

    def der(self, col):
        return self.x + self.w, self.filas[col]


def relacion(p_muchos, p_uno):
    """Línea entre la FK (lado muchos, «*») y la PK (lado uno, «1»)."""
    d.line(r(*p_muchos, *p_uno), fill=TINTA, width=2 * E)
    for (x, y), m, otro in ((p_muchos, "*", p_uno), (p_uno, "1", p_muchos)):
        sx = 1 if otro[0] > x else -1
        texto(x + sx * 14, y - 12, m, 16)


# Columnas: dimensiones solo de FactPuntuacion | FactPuntuacion | dimensiones conformadas | FactEvaluacion
X1, W1 = 24, 262
X2, W2 = 368, 250
X3, W3 = 700, 262
X4, W4 = 1044, 214

competencia = Tabla(X1, 40, W1, "DimCompetencia", "dimensión · 24 filas",
                    [("PK", "CompetenciaKey"), ("", "Materia"), ("", "Subcompetencia"), ("", "EsGlobal"),
                     ("", "PeriodoDisenoInicio")])
nivel = Tabla(X1, 300, W1, "DimNivelLogro", "dimensión · 5 filas",
              [("PK", "NivelKey"), ("", "Nivel"), ("", "LimiteInferior"), ("", "LimiteSuperior")])
calidad = Tabla(X1, 540, W1, "DimCalidadDato", "dimensión · 16 filas",
                [("PK", "CalidadKey"), ("", "NoValida"), ("", "Censurada"), ("", "NoComparableSerie"),
                 ("", "NivelNoComparable")])

anio = Tabla(X3, 40, W3, "DimAnio", "dimensión · 17 filas",
             [("PK", "AnioKey"), ("", "Anio"), ("", "TieneConvocatoria"), ("", "IndiceConvocatoria")])
contexto = Tabla(X3, 290, W3, "DimContextoCentro", "dimensión · 120 filas",
                 [("PK", "ContextoKey"), ("", "AreaTerritorial"), ("", "AreaSerieComparable"),
                  ("", "Naturaleza"), ("", "Habitat")])
perfil = Tabla(X3, 560, W3, "DimPerfilAlumno", "dimensión · 182 filas",
               [("PK", "PerfilKey"), ("", "Genero"), ("", "EdadAnioNatural"), ("", "SituacionEdad"),
                ("", "MesNacimiento")])

puntuacion = Tabla(X2, 270, W2, "FactPuntuacion", "hechos · 17.728.085 filas",
                   [("FK", "AnioKey"), ("FK", "ContextoKey"), ("FK", "PerfilKey"), ("FK", "CompetenciaKey"),
                    ("FK", "NivelKey"), ("FK", "CalidadKey"), ("", "Puntuacion")])
evaluacion = Tabla(X4, 300, W4, "FactEvaluacion", "hechos · 1.102.324 filas",
                   [("", "EvaluacionID"), ("FK", "AnioKey"), ("FK", "ContextoKey"), ("FK", "PerfilKey"),
                    ("", "TieneCodigoAlumno"), ("", "CompetenciasEvaluadas")])

# 6 relaciones de FactPuntuacion y 3 de FactEvaluacion (muchos a uno, filtro de la dimensión a los hechos)
relacion(puntuacion.izq("CompetenciaKey"), competencia.der("CompetenciaKey"))
relacion(puntuacion.izq("NivelKey"), nivel.der("NivelKey"))
relacion(puntuacion.izq("CalidadKey"), calidad.der("CalidadKey"))
for dim, col in ((anio, "AnioKey"), (contexto, "ContextoKey"), (perfil, "PerfilKey")):
    relacion(puntuacion.der(col), dim.izq(col))
    relacion(evaluacion.izq(col), dim.der(col))

# Leyenda
texto(ANCHO / 2, ALTO - 22, "PK: clave primaria   ·   FK: clave externa   ·   * muchos, 1 uno   ·   "
      "las relaciones filtran en un solo sentido, de la dimensión a los hechos", 13, "Italic", GRIS)

SALIDA.mkdir(parents=True, exist_ok=True)
img.save(SALIDA / "esquema_estrella.png", optimize=True)
print(f"Diagrama creado: {SALIDA / 'esquema_estrella.png'}")
