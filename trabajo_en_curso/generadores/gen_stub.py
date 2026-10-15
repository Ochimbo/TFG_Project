import os
import sys

ROOT = sys.argv[1]
DEF = os.path.join(ROOT, "definition")
TAB = os.path.join(DEF, "tables")
os.makedirs(TAB, exist_ok=True)

M_TYPE = {
    "int64": "Int64.Type",
    "string": "text",
    "boolean": "logical",
    "double": "number",
    "decimal": "Currency.Type",
}

TABLES = {
    "DimAnio": [
        ("AnioKey", "int64"), ("Anio", "int64"), ("Curso", "string"),
        ("TieneConvocatoria", "boolean"), ("IndiceConvocatoria", "int64"),
        ("EsUltimaConvocatoria", "boolean"), ("NotaConvocatoria", "string"),
    ],
    "DimContextoCentro": [
        ("ContextoKey", "int64"), ("AreaCodigo", "int64"), ("AreaTerritorial", "string"),
        ("AreaPerimetro2025", "string"), ("AreaSerieComparable", "string"),
        ("AreaConRupturaSerie", "boolean"), ("RupturaHabitat2024", "boolean"),
        ("Naturaleza", "string"), ("NaturalezaCodigo", "int64"), ("Habitat", "string"),
        ("HabitatCodigo", "int64"), ("AreaOrden", "int64"),
    ],
    "DimPerfilAlumno": [
        ("PerfilKey", "int64"), ("Genero", "string"), ("GeneroCodigo", "int64"),
        ("EdadAnioNatural", "int64"), ("SituacionEdad", "string"), ("SituacionEdadCodigo", "int64"),
        ("SituacionEdadOrden", "int64"), ("MesNacimiento", "int64"), ("TrimestreNacimiento", "string"),
    ],
    "DimCompetencia": [
        ("CompetenciaKey", "int64"), ("CampoOrigen", "string"), ("CodigoMateria", "string"),
        ("Materia", "string"), ("MateriaOrden", "int64"), ("Subcompetencia", "string"),
        ("SubcompetenciaOrden", "int64"), ("EsGlobal", "boolean"), ("AnioInicio", "int64"),
        ("AnioFin", "int64"), ("PeriodoDisenoInicio", "int64"), ("EsInformativa", "boolean"),
    ],
    "DimNivelLogro": [
        ("NivelKey", "int64"), ("Nivel", "string"), ("LimiteInferior", "double"),
        ("LimiteSuperior", "double"), ("NivelOrden", "int64"),
    ],
    "DimCalidadDato": [
        ("CalidadKey", "int64"), ("NoValida", "boolean"), ("Censurada", "boolean"),
        ("NoComparableSerie", "boolean"), ("NivelNoComparable", "boolean"),
        ("DescripcionCalidad", "string"),
    ],
    "FactEvaluacion": [
        ("EvaluacionID", "int64"), ("AnioKey", "int64"), ("ContextoKey", "int64"),
        ("PerfilKey", "int64"), ("TieneCodigoAlumno", "boolean"), ("CompetenciasEvaluadas", "int64"),
    ],
    "FactPuntuacion": [
        ("AnioKey", "int64"), ("ContextoKey", "int64"), ("PerfilKey", "int64"),
        ("CompetenciaKey", "int64"), ("NivelKey", "int64"), ("CalidadKey", "int64"),
        ("Puntuacion", "decimal"),
    ],
}

RELS = [
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

with open(os.path.join(DEF, "database.tmdl"), "w", encoding="utf-8") as fh:
    fh.write("database\n\tcompatibilityLevel: 1567\n")

with open(os.path.join(DEF, "model.tmdl"), "w", encoding="utf-8") as fh:
    fh.write(
        "model Model\n\tculture: es-ES\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: es-ES\n\tdiscourageImplicitMeasures\n\n"
    )
    for t in list(TABLES) + ["_Medidas"]:
        fh.write(f"ref table {t}\n")

with open(os.path.join(DEF, "relationships.tmdl"), "w", encoding="utf-8") as fh:
    for i, (ft, fc, tt, tc) in enumerate(RELS, 1):
        fh.write(f"relationship r{i:02d}_{ft}_{fc}\n\tfromColumn: {ft}.{fc}\n\ttoColumn: {tt}.{tc}\n\n")

for t, cols in TABLES.items():
    out = [f"table {t}", ""]
    for c, dt in cols:
        out += [f"\tcolumn {c}", f"\t\tdataType: {dt}", "\t\tsummarizeBy: none", f"\t\tsourceColumn: {c}", ""]
    mt = ", ".join(f"{c} = {M_TYPE[dt]}" for c, dt in cols)
    out += [
        f"\tpartition {t} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        f"\t\t\t\t    Origen = #table(type table [{mt}], {{}})",
        "\t\t\t\tin",
        "\t\t\t\t    Origen",
        "",
    ]
    with open(os.path.join(TAB, f"{t}.tmdl"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
print("stub OK:", DEF)
