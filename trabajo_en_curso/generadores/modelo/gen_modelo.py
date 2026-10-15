"""Genera el modelo semántico TMDL (salvo _Medidas.tmdl) y el andamiaje PBIP del CMI.

Uso: python gen_modelo.py <carpeta PowerBI>
(p. ej. python trabajo_en_curso/generadores/modelo/gen_modelo.py PowerBI; _Medidas.tmdl lo genera gen_medidas.py)
Las consultas M están en los ficheros m_*.m junto a este script.
"""
import json
import sys
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = Path(sys.argv[1])
SM = RAIZ / "CMI_Educacion_Primaria.SemanticModel"
DEF = SM / "definition"
TAB = DEF / "tables"

NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://tfg.fib.upc/CMI_Educacion_Primaria")


def guid(*partes):
    return str(uuid.uuid5(NS, "/".join(partes)))


def m(nombre):
    return (AQUI / f"m_{nombre}.m").read_text(encoding="utf-8").rstrip("\n").split("\n")


FMT = {"int64": "0", "decimal": "0.00", "double": "0.00"}

# (columna, tipo, oculta, sortByColumn, descripción)
TABLAS = {
    "DimAnio": ("Dimensiones", "Convocatorias de la prueba de sexto de primaria, de 2009 al último año con datos. 2020 se incluye sin datos (sin prueba por la COVID-19).", [
        ("AnioKey", "int64", True, None, "Clave del año (igual a Anio)."),
        ("Anio", "int64", False, None, "Año natural de la convocatoria (columna ANY del origen)."),
        ("Curso", "string", False, "Anio", "Curso escolar de la convocatoria, p. ej. 2016-2017."),
        ("TieneConvocatoria", "boolean", False, None, "VERDADERO si ese año hubo prueba y hay datos (FALSO en 2020)."),
        ("IndiceConvocatoria", "int64", True, None, "Número de orden 1..N de las convocatorias con datos (vacío en 2020). Las comparaciones temporales usan este índice, no Anio - 1."),
        ("EsUltimaConvocatoria", "boolean", False, None, "VERDADERO en el último año con datos."),
        ("NotaConvocatoria", "string", False, None, "Advertencia sobre la convocatoria (2020 sin prueba; 2021 se compara con 2019)."),
    ]),
    "DimContextoCentro": ("Dimensiones", "Contexto del centro: área territorial x naturaleza x hábitat (15 x 2 x 4 = 120 filas). Clave = AreaCodigo * 100 + NaturalezaCodigo * 10 + HabitatCodigo.", [
        ("ContextoKey", "int64", True, None, "Clave determinista: AreaCodigo * 100 + NaturalezaCodigo * 10 + HabitatCodigo."),
        ("AreaCodigo", "int64", True, None, "Código del área (contrato §5.1). 3 = Barcelona Comarques hasta 2023; 4 = Barcelona Comarques en 2024 (perímetro del Barcelonès); 99 = desconocida (R13, R14)."),
        ("AreaTerritorial", "string", False, "AreaOrden", "Área territorial tal como la publica el Departament (los códigos 3 y 4 comparten el nombre Barcelona Comarques)."),
        ("AreaPerimetro2025", "string", False, None, "Área expresada con el perímetro territorial vigente en 2025 (R14)."),
        ("AreaSerieComparable", "string", False, None, "Agrupación de áreas con serie temporal comparable a pesar de los cambios de perímetro de 2024-2025."),
        ("AreaConRupturaSerie", "boolean", False, None, "VERDADERO si el área cambió de perímetro y su serie no es comparable sin agrupar."),
        ("RupturaHabitat2024", "boolean", False, None, "VERDADERO en Girona y Maresme - Vallès Oriental, cuya clasificación de hábitat cambió en 2024."),
        ("Naturaleza", "string", False, "NaturalezaCodigo", "Titularidad del centro: Pública o Privada (incluye la concertada) (R10)."),
        ("NaturalezaCodigo", "int64", True, None, "1 = Pública, 2 = Privada."),
        ("Habitat", "string", False, "HabitatCodigo", "Tamaño del municipio del centro (R11). No fiable: 2010 y bloque incoherente de 2014 (R12)."),
        ("HabitatCodigo", "int64", True, None, "0 = No fiable, 1 = hasta 10.000 hab., 2 = de 10.001 a 100.000 hab., 3 = más de 100.000 hab."),
        ("AreaOrden", "int64", True, None, "Orden de presentación de las áreas (= AreaCodigo, salvo el código 4, que toma el 3 para que Barcelona Comarques tenga un único orden)."),
    ]),
    "DimPerfilAlumno": ("Dimensiones", "Perfil del alumno: género x situación de edad x mes de nacimiento (2 x 7 x 13 = 182 filas). Clave = GeneroCodigo * 100000 + SituacionEdadCodigo * 10000 + EdadAnioNatural * 100 + MesNacimiento.", [
        ("PerfilKey", "int64", True, None, "Clave determinista: GeneroCodigo * 100000 + SituacionEdadCodigo * 10000 + (EdadAnioNatural o 0) * 100 + MesNacimiento (0 si no informado)."),
        ("Genero", "string", False, "GeneroCodigo", "Género del alumno: Niña o Niño (R09)."),
        ("GeneroCodigo", "int64", True, None, "1 = Niña, 2 = Niño."),
        ("EdadAnioNatural", "int64", False, None, "Edad cumplida en el año natural de la prueba (Anio - año de nacimiento), entre 10 y 14. Vacía si falta, está fuera de rango, es 2010 o la fecha es de relleno (R16-R19)."),
        ("SituacionEdad", "string", False, "SituacionEdadOrden", "Situación respecto a la edad teórica de sexto (12 años): adelantado, edad teórica, retraso de 1 o 2 años, no fiable (2010) o desconocida (R21)."),
        ("SituacionEdadCodigo", "int64", True, None, "1 = edad teórica, 2 = retraso de 1 año, 3 = retraso de 2 años, 4 = adelantado, 8 = no fiable (2010), 9 = desconocida."),
        ("SituacionEdadOrden", "int64", True, None, "Orden de presentación de SituacionEdad (4, 1, 2, 3, 8, 9)."),
        ("MesNacimiento", "int64", False, None, "Mes de nacimiento 1-12; vacío si no está informado o es inválido."),
        ("TrimestreNacimiento", "string", False, None, "Trimestre de nacimiento T1-T4, o No informado."),
    ]),
    "DimCompetencia": ("Dimensiones", "Competencias evaluadas: las 24 columnas de puntuación del origen (contrato §5.2), con su materia y subcompetencia.", [
        ("CompetenciaKey", "int64", True, None, "Clave de la competencia (1-24)."),
        ("CampoOrigen", "string", False, None, "Nombre de la columna de puntuación en Datos.csv (p. ej. PCAT_CL)."),
        ("CodigoMateria", "string", False, None, "Código de la materia: columna de su puntuación global (PCAT, PCAST, PMAT, PANG, PFRAN, PMED)."),
        ("Materia", "string", False, "MateriaOrden", "Materia evaluada."),
        ("MateriaOrden", "int64", True, None, "Orden de presentación de las materias."),
        ("Subcompetencia", "string", False, "SubcompetenciaOrden", "Subcompetencia evaluada, o Global para la puntuación global de la materia."),
        ("SubcompetenciaOrden", "int64", True, None, "Orden de presentación de la subcompetencia, único por texto: 0 Global, 1 Comprensión lectora, 2 Comprensión oral, 3 Expresión escrita, 4-6 matemáticas, 7-9 ciencias."),
        ("EsGlobal", "boolean", False, None, "VERDADERO si es la puntuación global de la materia (base de K01, K03, K06 y K10-K12)."),
        ("AnioInicio", "int64", False, None, "Primer año con datos de la competencia."),
        ("AnioFin", "int64", False, None, "Último año de la competencia; vacío si sigue vigente."),
        ("PeriodoDisenoInicio", "int64", False, None, "Primer año del diseño actual de la prueba: las comparaciones temporales (K10, K11) solo usan años desde este."),
        ("EsInformativa", "boolean", False, None, "VERDADERO para el francés: muestra pequeña, solo informativo (no entra en K09 ni K12)."),
    ]),
    "DimNivelLogro": ("Dimensiones", "Niveles de logro de las puntuaciones globales (R29). Umbrales 55 / 70 / 85 provisionales e internos del TFG: NO son los niveles oficiales.", [
        ("NivelKey", "int64", True, None, "Clave del nivel: 0 = no aplica (subcompetencias), 1 = bajo ... 4 = alto."),
        ("Nivel", "string", False, "NivelOrden", "Nivel de logro (solo puntuaciones globales)."),
        ("LimiteInferior", "double", False, None, "Límite inferior del nivel (incluido)."),
        ("LimiteSuperior", "double", False, None, "Límite superior del nivel (excluido, salvo 100 en el nivel Alto)."),
        ("NivelOrden", "int64", True, None, "Orden de presentación de los niveles."),
    ]),
    "DimCalidadDato": ("Dimensiones", "Calidad de cada puntuación según su columna y año (R25-R28), codificada como máscara de 4 bits (16 filas).", [
        ("CalidadKey", "int64", True, None, "Máscara: 1 NoValida + 2 Censurada + 4 NoComparableSerie + 8 NivelNoComparable (0 = válido)."),
        ("NoValida", "boolean", False, None, "R25: puntuación no válida (expresión escrita de inglés 2015). K02 la excluye."),
        ("Censurada", "boolean", False, None, "R26: distribución censurada por un suelo artificial (catalán EE 2018; inglés global, CO y CE 2015). K03 y K06 la excluyen."),
        ("NoComparableSerie", "boolean", False, None, "R27: escala no comparable con el resto de la serie temporal."),
        ("NivelNoComparable", "boolean", False, None, "R28: el porcentaje por nivel de logro no es comparable (solo globales). K03 la excluye."),
        ("DescripcionCalidad", "string", False, "CalidadKey", "Válido o lista de problemas de calidad de la puntuación."),
    ]),
    "FactEvaluacion": ("Hechos", "Una fila por registro de Datos.csv (alumno evaluado en una convocatoria). Base de la medida Alumnos evaluados.", [
        ("EvaluacionID", "int64", True, None, "Posición del registro en Datos.csv (1..N), asignada antes de cualquier filtro (R01)."),
        ("AnioKey", "int64", True, None, "Año de la convocatoria (relación con DimAnio)."),
        ("ContextoKey", "int64", True, None, "Contexto del centro (relación con DimContextoCentro)."),
        ("PerfilKey", "int64", True, None, "Perfil del alumno (relación con DimPerfilAlumno)."),
        ("TieneCodigoAlumno", "boolean", True, None, "VERDADERO si el registro tiene CODI_ALUMNE (el código no se carga por privacidad)."),
        ("CompetenciasEvaluadas", "int64", True, None, "Número de puntuaciones globales informadas en el registro."),
    ]),
    "FactPuntuacion": ("Hechos", "Una fila por puntuación no nula (despivotado de las 24 columnas de puntuación, R33). Base de K01-K12.", [
        ("AnioKey", "int64", True, None, "Año de la convocatoria (relación con DimAnio)."),
        ("ContextoKey", "int64", True, None, "Contexto del centro (relación con DimContextoCentro)."),
        ("PerfilKey", "int64", True, None, "Perfil del alumno (relación con DimPerfilAlumno)."),
        ("CompetenciaKey", "int64", True, None, "Competencia evaluada (relación con DimCompetencia)."),
        ("NivelKey", "int64", True, None, "Nivel de logro (relación con DimNivelLogro); 0 en subcompetencias (R29)."),
        ("CalidadKey", "int64", True, None, "Calidad del dato (relación con DimCalidadDato), según columna y año (R25-R28)."),
        ("Puntuacion", "decimal", True, None, "Puntuación 0-100 con 2 decimales, convertida con cultura es-ES (R02) y con las rotaciones R03/R04 corregidas."),
    ]),
}

RELACIONES = [
    ("FactPuntuacion", "AnioKey", "DimAnio", "AnioKey"),
    ("FactPuntuacion", "ContextoKey", "DimContextoCentro", "ContextoKey"),
    ("FactPuntuacion", "PerfilKey", "DimPerfilAlumno", "PerfilKey"),
    ("FactPuntuacion", "CompetenciaKey", "DimCompetencia", "CompetenciaKey"),
    ("FactPuntuacion", "NivelKey", "DimNivelLogro", "NivelKey"),
    ("FactPuntuacion", "CalidadKey", "DimCalidadDato", "CalidadKey"),
    ("FactEvaluacion", "AnioKey", "DimAnio", "AnioKey"),
    ("FactEvaluacion", "ContextoKey", "DimContextoCentro", "ContextoKey"),
    ("FactEvaluacion", "PerfilKey", "DimPerfilAlumno", "PerfilKey"),
]

GRUPOS = ["Parámetros", "Staging", "Dimensiones", "Hechos"]
ORDEN_CONSULTAS = ["RutaDatos", "stg_Evaluaciones"] + list(TABLAS) + ["_Medidas"]


def escribir(ruta, lineas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    texto = "\n".join(lineas).rstrip("\n") + "\n"
    ruta.write_text(texto, encoding="utf-8", newline="\n")


def quote(nombre):
    return f"'{nombre}'" if any(ch in nombre for ch in " .=:'") else nombre


# ---------------------------------------------------------------- PBIP y .gitignore
escribir(RAIZ / ".gitignore", ["**/.pbi/localSettings.json", "**/.pbi/cache.abf"])
escribir(RAIZ / "CMI_Educacion_Primaria.pbip", json.dumps({
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": "CMI_Educacion_Primaria.Report"}}],
    "settings": {"enableAutoRecovery": True},
}, indent=2, ensure_ascii=False).split("\n"))
escribir(SM / "definition.pbism", json.dumps({
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.2",
    "settings": {},
}, indent=2, ensure_ascii=False).split("\n"))

# ---------------------------------------------------------------- database / model
escribir(DEF / "database.tmdl", ["database", "\tcompatibilityLevel: 1567"])

modelo = [
    "model Model",
    "\tculture: es-ES",
    "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
    "\tdiscourageImplicitMeasures",
    "\tsourceQueryCulture: es-ES",
    "\tdataAccessOptions",
    "\t\tlegacyRedirects",
    "\t\treturnErrorValuesAsNull",
    "",
]
for i, g in enumerate(GRUPOS):
    modelo += [f"queryGroup {quote(g)}", "", f"\tannotation PBI_QueryGroupOrder = {i}", ""]
modelo += [
    "annotation PBI_QueryOrder = " + json.dumps(ORDEN_CONSULTAS, ensure_ascii=False, separators=(",", ":")),
    "",
    "annotation __PBI_TimeIntelligenceEnabled = 0",
    "",
    'annotation PBI_ProTooling = ["DevMode"]',
    "",
]
for t in list(TABLAS) + ["_Medidas"]:
    modelo.append(f"ref table {t}")
escribir(DEF / "model.tmdl", modelo)

# ---------------------------------------------------------------- expressions
expr = [
    "/// Ruta completa del fichero Datos.csv (Avaluació de sisè, 32 columnas). Ajustar antes de actualizar.",
    'expression RutaDatos = "C:\\TFG_Project\\Datos.csv" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]',
    f"\tlineageTag: {guid('expression', 'RutaDatos')}",
    "\tqueryGroup: Parámetros",
    "",
    "\tannotation PBI_ResultType = Text",
    "",
    "/// ETL compartida (no se carga): lee Datos.csv y aplica las reglas R01-R21 del informe de calidad. Una fila por registro con claves deterministas y las 24 puntuaciones corregidas.",
    "expression stg_Evaluaciones =",
]
expr += ["\t\t" + linea if linea else "" for linea in m("stg")]
expr += [
    f"\tlineageTag: {guid('expression', 'stg_Evaluaciones')}",
    "\tqueryGroup: Staging",
    "",
    "\tannotation PBI_ResultType = Table",
]
escribir(DEF / "expressions.tmdl", expr)

# ---------------------------------------------------------------- relationships
rel = []
for ft, fc, tt, tc in RELACIONES:
    rel += [f"relationship {guid('relationship', ft, fc, tt, tc)}",
            f"\tfromColumn: {ft}.{fc}", f"\ttoColumn: {tt}.{tc}", ""]
escribir(DEF / "relationships.tmdl", rel)

# ---------------------------------------------------------------- tablas
for tabla, (grupo, desc_tabla, columnas) in TABLAS.items():
    out = [f"/// {desc_tabla}", f"table {tabla}", f"\tlineageTag: {guid('table', tabla)}", ""]
    for col, tipo, oculta, orden, desc in columnas:
        out += [f"\t/// {desc}", f"\tcolumn {col}", f"\t\tdataType: {tipo}"]
        if oculta:
            out.append("\t\tisHidden")
        if tipo in FMT:
            out.append(f"\t\tformatString: {FMT[tipo]}")
        out += [f"\t\tlineageTag: {guid('column', tabla, col)}", "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {col}"]
        if orden:
            out.append(f"\t\tsortByColumn: {orden}")
        out += ["", "\t\tannotation SummarizationSetBy = User", ""]
    out += [f"\tpartition {tabla} = m", "\t\tmode: import", f"\t\tqueryGroup: {grupo}", "\t\tsource ="]
    out += ["\t\t\t\t" + linea if linea else "" for linea in m(tabla)]
    out += ["", "\tannotation PBI_ResultType = Table"]
    escribir(TAB / f"{tabla}.tmdl", out)

print("Modelo generado en", DEF)
