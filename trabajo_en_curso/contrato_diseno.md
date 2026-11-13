# Contrato de diseño — CMI Educación Primaria (MVP v0.1)

Documento COMPARTIDO por todos los agentes de construcción. Nombres de carpetas, tablas, columnas, claves,
códigos y medidas son VINCULANTES. Si algo es imposible o erróneo, NO improvises otro nombre: dilo en tu respuesta.
Fuente de las reglas: `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md` (auditoría verificada,
reglas R01–R34). Léela si necesitas detalle; este contrato fija qué se implementa en el MVP.

## 0. Rutas (actualizado el 12/11/2026, D-18)

Raíz repo (Windows): `C:\Users\kiara\Desktop\Uni\TFG\Project\TFG_Project` (usar Git Bash para los scripts).
Python 3.12 global sin duckdb/pyarrow: instalarlos en una carpeta temporal (`pip install --target <tmp>/pylibs duckdb pyarrow numpy pandas jsonschema referencing`)
y ejecutar con `PYTHONPATH=<tmp>/pylibs PYTHONIOENCODING=utf-8 python ...`.
Datos: `Datos.csv` en la raíz del repositorio (NO modificar; no versionado). 1.102.324 filas. El parámetro `RutaDatos` del modelo
apunta a esa ruta (valor fijado desde Power BI Desktop y conservado por el generador, D-19).
Validador TMDL (`trabajo_en_curso/herramientas/tmdlcheck`, Microsoft TOM en .NET): hace falta el SDK de .NET 8 (en Windows,
`dotnet-install.ps1 -Channel 8.0 -InstallDir <tmp>/dotnet`); copiar la carpeta fuera del repo, `dotnet build -c Release -o out`
y `DOTNET_ROOT=<tmp>/dotnet out/tmdlcheck <carpeta definition>`. Deserializa la carpeta TMDL, lista tablas/columnas/medidas/relaciones
y ejecuta Model.Validate(). NO valida la semántica DAX.
Analizador sintáctico oficial de Power Query M (`trabajo_en_curso/herramientas/mparser`, @microsoft/powerquery-parser, Node 24):
copiar la carpeta a `<tmp>/mparser`, `npm ci` y `python trabajo_en_curso/herramientas/validar_m.py --mcheck <tmp>/mparser/mcheck.js`
(extrae cada expresión/partición del TMDL y da "OK" o "FAIL <motivo> <posición>" por bloque; detecta errores de sintaxis, no de tipos ni de ejecución).
Generadores (en el repo): modelo TMDL + M + PBIP -> `trabajo_en_curso/generadores/modelo/gen_modelo.py PowerBI`
(consultas en `modelo/m_*.m`); medidas -> `generadores/gen_medidas.py <_Medidas.tmdl>`; informe -> `generadores/gen_pbir.py`.
Los generadores conservan lo que Power BI Desktop añade al guardar (`.platform`, `.pbi/`, `cultures/`, `RutaDatos`; D-19).
Comprobación M frente a parquet: `trabajo_en_curso/herramientas/verificar_claves.py`.
Esquemas JSON oficiales de PBIR/PBIP: clon disperso de github.com/microsoft/json-schemas en `<tmp>/json-schemas`
(`sparse-checkout set fabric/item/report fabric/item/semanticModel fabric/pbip`) y
`PBIR_SCHEMAS=<tmp>/json-schemas/fabric python trabajo_en_curso/herramientas/validar_pbir.py`.
Decisiones posteriores a este contrato: `trabajo_en_curso/week2/DECISIONES.md` (D-01 a D-19); donde difieran, manda DECISIONES.md.

```
PowerBI/
  .gitignore                     (**/.pbi/localSettings.json, **/.pbi/cache.abf)
  CMI_Educacion_Primaria.pbip
  CMI_Educacion_Primaria.SemanticModel/
    definition.pbism
    definition/
      database.tmdl  model.tmdl  expressions.tmdl  relationships.tmdl
      tables/DimAnio.tmdl DimContextoCentro.tmdl DimPerfilAlumno.tmdl DimCompetencia.tmdl
             DimNivelLogro.tmdl DimCalidadDato.tmdl FactEvaluacion.tmdl FactPuntuacion.tmdl _Medidas.tmdl
  CMI_Educacion_Primaria.Report/
    definition.pbir
    definition/  (PBIR: version.json, report.json, pages/pages.json, pages/<id>/page.json, pages/<id>/visuals/<id>/visual.json)
validacion/
  requirements.txt
  perfilado/                     (YA EXISTE: scripts de auditoría; no tocar)
  etl_referencia.py              (réplica Python/DuckDB de la ETL -> validacion/salida/*.parquet)
  kpis_referencia.py             (12 KPIs en cortes concretos -> validacion/resultados/*.csv)
  test_modelo.py                 (tests de integridad, ejecutable con python test_modelo.py; sin pytest obligatorio)
  salida/                        (git-ignorado)
  resultados/                    (versionado; CSV pequeños)
Documentation/Docu_Final/Docu_Parcial/   (01 ya existe; 02_Modelo_y_diccionario.md, 03_Fichas_KPI.md, 04_Guia_de_uso.md en fase posterior)
```

## 1. Convenciones

- Castellano. Nombres de TABLAS y COLUMNAS sin tildes ni espacios (PascalCase): `DimAnio`, `AreaTerritorial`, `Puntuacion`.
  Medidas con nombres legibles con tildes y espacios (ver §7).
- `compatibilityLevel: 1606` (1567 en la primera versión; Power BI Desktop lo subió a 1606 al guardar y el generador lo respeta, D-19); `model Model` con `culture: es-ES`, `defaultPowerBIDataSourceVersion: powerBI_V3`,
  `sourceQueryCulture: es-ES`, `discourageImplicitMeasures` (true).
- Claves `int64`, `summarizeBy: none`. En hechos, todas las columnas ocultas (`isHidden`). Columnas *Codigo/*Orden
  de dimensiones ocultas y usadas como `sortByColumn` de su atributo de texto.
- Modo Import. Puntuacion con `dataType: decimal` (decimal fijo) y `formatString: 0.00`.

## 2. Origen y ETL (Power Query M) — el MVP implementa estas reglas

Parámetro `RutaDatos` (texto, `IsParameterQuery=true`, requerido). Defecto `C:\TFG_Project\Datos.csv`.
Lectura: `Csv.Document(File.Contents(RutaDatos), [Delimiter=",", Columns=32, Encoding=65001, QuoteStyle=QuoteStyle.Csv])`
+ `Table.PromoteHeaders(..., [PromoteAllScalars=true])`. Todo entra como texto.

Expresión compartida `stg_Evaluaciones` (no se carga; tabla ancha, una fila por registro) aplica en este orden:
1. R01: `EvaluacionID` = índice 1..N en el orden del fichero (Table.AddIndexColumn ANTES de cualquier filtro).
2. R05: Text.Trim en todas las columnas; "" -> null.
3. R02: 24 puntuaciones: `Number.FromText(texto, "es-ES")` sobre el texto ORIGINAL (no reemplazar comas). Si falla
   la conversión o el valor queda fuera de [0,100] -> error explícito con mensaje (la actualización debe fallar).
4. R03: si Anio = 2017: PCAST := PCAST_EE_orig; PCAST_CL := PCAST_orig; PCAST_EE := PCAST_CL_orig (simultáneo).
   R04: si Anio = 2016: PFRAN := PFRAN_EE_orig; PFRAN_CO := PFRAN_orig; PFRAN_CE := PFRAN_CO_orig; PFRAN_EE := PFRAN_CE_orig.
5. Anio = Int64 de ANY.
6. Género (R09): "H","Home" -> 2 "Niño"; "D","Dona" -> 1 "Niña"; otro -> error.
7. Naturaleza (R10): "Públic","Pública" -> 1 "Pública"; "Privat","Privada" -> 2 "Privada"; otro -> error.
8. Hábitat (R11, R12): prefijo "Fins a" -> 1; "De 10001 a 100000" -> 2; prefijo "Més de" -> 3; otro -> error.
   Después: si Anio = 2010 -> 0 ("No fiable"). Si Anio = 2014 y Área = "Baix Llobregat" y texto original "Més de 100000" -> 0.
9. Área (R13, R14): AreaCodigo según §5.1 (null -> 99 "Desconocida"; "Barcelona Comarques" con Anio = 2024 -> 4; con Anio <= 2023 -> 3).
   Área no reconocida -> error.
10. Edad (R16–R19, R21): EdadAnioNatural = Anio - ANY_NAIXEMENT (null si falta); si fuera de [10,14] -> null;
    si Anio = 2010 -> null; si FechaNacimientoDudosa (CODI_ALUMNE nulo y Anio en {2016,2018}, o Anio=2016 y
    ANY_NAIXEMENT=2001 y MES_NAIXEMENT=1) -> null.
    SituacionEdadCodigo: Anio=2010 -> 8; EdadAnioNatural null -> 9; <12 -> 4; 12 -> 1; 13 -> 2; 14 -> 3.
    MesNacimiento: 1..12 o 0 si falta / fuera de rango.
11. Claves deterministas (sin merges):
    ContextoKey = AreaCodigo*100 + NaturalezaCodigo*10 + HabitatCodigo
    PerfilKey   = GeneroCodigo*100000 + SituacionEdadCodigo*10000 + (EdadAnioNatural ?? 0)*100 + MesNacimiento
    AnioKey     = Anio
12. TieneCodigoAlumno = CODI_ALUMNE no nulo (lógico). CODI_ALUMNE NO se carga al modelo (privacidad/memoria).
FUERA del MVP (documentar como extensión): R07 flag duplicado, R08 repetición probable, R20 mes dudoso,
R23/R24 flags de global incoherente/recortada, comprobación de nº fijo de filas.

## 3. Tablas

### DimAnio (M: años 2009..max(Anio de los datos), 2020 incluido sin datos)
AnioKey int64 (=Anio) | Anio int64 | Curso string "(Anio-1)-Anio" | TieneConvocatoria boolean |
IndiceConvocatoria int64 (1..N solo en años con datos; null en 2020) | EsUltimaConvocatoria boolean |
NotaConvocatoria string ("Sin prueba por la COVID-19" en 2020; "Primera convocatoria tras la COVID-19 (se compara con 2019)" en 2021; "" resto)

### DimContextoCentro (M estática: producto cartesiano de §5.1 x naturaleza {1,2} x hábitat {0,1,2,3})
ContextoKey | AreaCodigo (oculta) | AreaTerritorial (nombre de los informes oficiales: código 3 -> "Barcelona Comarques"; códigos 4 y 5 -> "Barcelonès" (D-05); 99 -> "Desconocida") |
AreaPerimetro2025 | AreaSerieComparable | AreaConRupturaSerie boolean | RupturaHabitat2024 boolean (Girona, Maresme - Vallès Oriental) |
Naturaleza ("Pública"/"Privada") | NaturalezaCodigo (oculta, sort) | Habitat | HabitatCodigo (oculta, sort de Habitat) |
AreaOrden (oculta, sort de AreaTerritorial)

### DimPerfilAlumno (M estática: género {1,2} x combinaciones edad/situación válidas x mes {0..12})
Combinaciones edad/situación: (10,4) (11,4) (12,1) (13,2) (14,3) (0,8) (0,9)  -> 2 x 7 x 13 = 182 filas
PerfilKey | Genero ("Niña"/"Niño") | GeneroCodigo (oculta) | EdadAnioNatural (int64; null si 0) |
SituacionEdad | SituacionEdadCodigo (oculta, sort: orden 4,1,2,3,8,9 -> usar columna SituacionEdadOrden) | SituacionEdadOrden (oculta) |
MesNacimiento (int64; null si 0) | TrimestreNacimiento ("T1".."T4" / "No informado")
SituacionEdad textos: 1 "Edad teórica (12 años)", 2 "Retraso de 1 año", 3 "Retraso de 2 años", 4 "Adelantado",
8 "No fiable (2010)", 9 "Desconocida".

### DimCompetencia (M estática, §5.2, 24 filas)
CompetenciaKey | CampoOrigen | CodigoMateria | Materia | MateriaOrden (oculta, sort) | Subcompetencia |
SubcompetenciaOrden (oculta, sort de Subcompetencia; UN valor por texto, ver §5.2) | EsGlobal boolean | AnioInicio int64 | AnioFin int64 (null = vigente) |
PeriodoDisenoInicio int64 | EsInformativa boolean (francés)

### DimNivelLogro (M estática) — cortes fijos R29 55/70/85 (definitivos, D-08; internos del TFG, NO oficiales)
NivelKey | Nivel | LimiteInferior double | LimiteSuperior double | NivelOrden (oculta)
0 "No aplica (subcompetencia)" null null ; 1 "Bajo" 0 55 ; 2 "Medio-bajo" 55 70 ; 3 "Medio-alto" 70 85 ; 4 "Alto" 85 100.
Asignación (solo globales): <55 ->1; [55,70) ->2; [70,85) ->3; >=85 ->4. Subcompetencias -> 0.

### DimCalidadDato (M estática, 16 filas, máscara de bits)
CalidadKey (0..15) | NoValida bool (bit 1) | Censurada bool (bit 2) | NoComparableSerie bool (bit 4) |
NivelNoComparable bool (bit 8) | DescripcionCalidad string ("Válido" si 0; si no, lista de problemas)
Reglas de asignación por (CampoOrigen, Anio) en FactPuntuacion:
- bit 1 NoValida (R25): PANG_EE en 2015.
- bit 2 Censurada (R26): PCAT_EE en 2018; PANG, PANG_CO, PANG_CE en 2015 (toda la columna-año).
- bit 4 NoComparableSerie (R27): PANG_CO y PCAT_CL en 2011; PANG_EE en 2013-2016; PANG_CO y PANG_CE en 2015-2016;
  PMAT_NC, PMAT_EFM, PMAT_CR en 2015.
- bit 8 NivelNoComparable (R28, solo globales): PANG 2015, PMAT 2015, PMAT 2019, PCAT 2018, PANG 2016, PFRAN 2022.

### FactEvaluacion (una fila por registro; 1.102.324)
EvaluacionID | AnioKey | ContextoKey | PerfilKey | TieneCodigoAlumno (boolean) | CompetenciasEvaluadas (nº globales no nulas)  — todas ocultas

### FactPuntuacion (despivotado de las 24 columnas, sin nulos; 17.728.085 filas)
AnioKey | ContextoKey | PerfilKey | CompetenciaKey | NivelKey | CalidadKey | Puntuacion — todas ocultas.
CompetenciaKey por búsqueda en un registro M estático CampoOrigen -> clave (sin merge).

### _Medidas — solo medidas (§7)

## 4. Relaciones (muchos-a-uno, una dirección, activas)
FactPuntuacion[AnioKey]->DimAnio[AnioKey]; FactPuntuacion[ContextoKey]->DimContextoCentro[ContextoKey];
FactPuntuacion[PerfilKey]->DimPerfilAlumno[PerfilKey]; FactPuntuacion[CompetenciaKey]->DimCompetencia[CompetenciaKey];
FactPuntuacion[NivelKey]->DimNivelLogro[NivelKey]; FactPuntuacion[CalidadKey]->DimCalidadDato[CalidadKey];
FactEvaluacion[AnioKey]->DimAnio[AnioKey]; FactEvaluacion[ContextoKey]->DimContextoCentro[ContextoKey];
FactEvaluacion[PerfilKey]->DimPerfilAlumno[PerfilKey].

## 5. Tablas de códigos

### 5.1 Áreas (AreaCodigo | AreaTerritorial | AreaPerimetro2025 | AreaSerieComparable | AreaConRupturaSerie | RupturaHabitat2024)
| 1 | Alt Pirineu i Aran | Alt Pirineu i Aran | Lleida + Alt Pirineu i Aran | true | false |
| 2 | Baix Llobregat | Baix Llobregat | Baix Llobregat | false | false |
| 3 | Barcelona Comarques | Barcelona Comarques (perímetro hasta 2023) | Barcelonès-Penedès y áreas afectadas | true | false |
| 4 | Barcelonès (el CSV de 2024 la llama "Barcelona Comarques"; D-05) | Barcelonès | Barcelonès-Penedès y áreas afectadas | true | false |
| 5 | Barcelonès | Barcelonès | Barcelonès-Penedès y áreas afectadas | true | false |
| 6 | Catalunya Central | Catalunya Central | Barcelonès-Penedès y áreas afectadas | true | false |
| 7 | Consorci d'Educació de Barcelona | Consorci d'Educació de Barcelona | Consorci d'Educació de Barcelona | false | false |
| 8 | Girona | Girona | Girona | false | true |
| 9 | Lleida | Lleida | Lleida + Alt Pirineu i Aran | true | false |
| 10 | Maresme - Vallès Oriental | Maresme - Vallès Oriental | Maresme - Vallès Oriental | false | true |
| 11 | Penedès | Penedès | Barcelonès-Penedès y áreas afectadas | true | false |
| 12 | Tarragona | Tarragona | Barcelonès-Penedès y áreas afectadas | true | false |
| 13 | Terres de l'Ebre | Terres de l'Ebre | Terres de l'Ebre | false | false |
| 14 | Vallès Occidental | Vallès Occidental | Vallès Occidental | false | false |
| 99 | Desconocida | Desconocida | Desconocida | false | false |
AreaOrden = AreaCodigo, salvo el código 4, que toma AreaOrden = 5 (sortByColumn exige un único valor de orden por texto de
AreaTerritorial, y los códigos 4 y 5 comparten «Barcelonès»; D-05). El texto "Barcelona Comarques" del CSV se codifica 3 hasta 2023
y 4 en 2024 (m_stg.m); el código 4 tiene el perímetro del Barcelonès (5.386 alumnos en 2024 frente a 5.408 en 2025, misma composición)
y el Quadern 62 ya lo publica como Barcelonès. ("Barcelonès-Penedès y áreas afectadas" = Barcelona Comarques/Barcelonès + Penedès + Tarragona + Catalunya Central.)
Girona se mantiene como serie propia aunque pierda la Cerdanya en 2024 (en torno al 1 % de su alumnado; D-06).
Naturaleza: 1 "Pública", 2 "Privada" (incluye concertada). Hábitat: 0 "No fiable", 1 "Hasta 10.000 hab.",
2 "De 10.001 a 100.000 hab.", 3 "Más de 100.000 hab.".

### 5.2 Competencias (CompetenciaKey | CampoOrigen | CodigoMateria | Materia | MateriaOrden | Subcompetencia | SubcompetenciaOrden | EsGlobal | AnioInicio | AnioFin | PeriodoDisenoInicio | EsInformativa)
| 1 | PCAT | PCAT | Lengua catalana | 1 | Global | 0 | true | 2009 | null | 2018 | false |
| 2 | PCAT_CL | PCAT | Lengua catalana | 1 | Comprensión lectora | 1 | false | 2009 | null | 2018 | false |
| 3 | PCAT_EE | PCAT | Lengua catalana | 1 | Expresión escrita | 3 | false | 2009 | null | 2018 | false |
| 4 | PCAT_CO | PCAT | Lengua catalana | 1 | Comprensión oral | 2 | false | 2018 | null | 2018 | false |
| 5 | PCAST | PCAST | Lengua castellana | 2 | Global | 0 | true | 2009 | null | 2018 | false |
| 6 | PCAST_CL | PCAST | Lengua castellana | 2 | Comprensión lectora | 1 | false | 2009 | null | 2018 | false |
| 7 | PCAST_EE | PCAST | Lengua castellana | 2 | Expresión escrita | 3 | false | 2009 | null | 2018 | false |
| 8 | PCAST_CO | PCAST | Lengua castellana | 2 | Comprensión oral | 2 | false | 2018 | null | 2018 | false |
| 9 | PMAT | PMAT | Matemáticas | 3 | Global | 0 | true | 2009 | null | 2017 | false |
| 10 | PMAT_NC | PMAT | Matemáticas | 3 | Numeración y cálculo | 4 | false | 2009 | null | 2017 | false |
| 11 | PMAT_EFM | PMAT | Matemáticas | 3 | Espacio, medida y datos | 5 | false | 2009 | null | 2017 | false |
| 12 | PMAT_CR | PMAT | Matemáticas | 3 | Relaciones y cambio | 6 | false | 2009 | null | 2017 | false |
| 13 | PANG | PANG | Lengua inglesa | 4 | Global | 0 | true | 2010 | null | 2017 | false |
| 14 | PANG_CO | PANG | Lengua inglesa | 4 | Comprensión oral | 2 | false | 2010 | null | 2017 | false |
| 15 | PANG_CE | PANG | Lengua inglesa | 4 | Comprensión lectora | 1 | false | 2010 | null | 2017 | false |
| 16 | PANG_EE | PANG | Lengua inglesa | 4 | Expresión escrita | 3 | false | 2013 | null | 2017 | false |
| 17 | PFRAN | PFRAN | Lengua francesa | 5 | Global | 0 | true | 2010 | null | 2017 | true |
| 18 | PFRAN_CO | PFRAN | Lengua francesa | 5 | Comprensión oral | 2 | false | 2010 | null | 2017 | true |
| 19 | PFRAN_CE | PFRAN | Lengua francesa | 5 | Comprensión lectora | 1 | false | 2010 | null | 2017 | true |
| 20 | PFRAN_EE | PFRAN | Lengua francesa | 5 | Expresión escrita | 3 | false | 2013 | null | 2017 | true |
| 21 | PMED | PMED | Ciencias | 6 | Global | 0 | true | 2018 | null | 2018 | false |
| 22 | PMED_COMP1 | PMED | Ciencias | 6 | Explicar fenómenos naturales y tecnológicos | 7 | false | 2018 | null | 2018 | false |
| 23 | PMED_COMP2 | PMED | Ciencias | 6 | Reconocer la investigación científica | 8 | false | 2018 | null | 2018 | false |
| 24 | PMED_COMP3 | PMED | Ciencias | 6 | Interpretar datos y pruebas científicas | 9 | false | 2018 | null | 2018 | false |
SubcompetenciaOrden es un orden GLOBAL por texto (0 Global, 1 Comprensión lectora, 2 Comprensión oral, 3 Expresión escrita,
4-6 matemáticas, 7-9 ciencias), no el orden dentro de la materia: cambio de la integración para que sea sortByColumn válido.
PeriodoDisenoInicio: 2017 en matemáticas, inglés y francés (la global de inglés y francés era 2016 en la primera versión; pasa a 2017
porque la de 2016 se calculó con CO y CE comprimidas, R27/R28, y no es comparable con la de 2017; D-10) y 2018 en catalán, castellano y ciencias.

## 6. Valores esperados (para tests)
FactEvaluacion 1.102.324 filas; FactPuntuacion 17.728.085 (4.769.851 globales + 12.958.234 subcompetencias);
media castellano 2017 corregida 73,51 (oficial 73,4); 0 claves sin dimensión; DimContextoCentro 15x2x4 = 120 filas;
DimPerfilAlumno 182; DimCompetencia 24; DimNivelLogro 5; DimCalidadDato 16; DimAnio 17.
Medias oficiales de Cataluña (Quaderns d'avaluació, puntuación global). Dos umbrales (D-01): criterio de aceptación RNF06 = 0,5 puntos
(lo cumplen las 72 combinaciones; máximo 0,30) y alerta interna = 0,2 (70 de 72; inglés 2016 +0,24 y francés 2024 +0,30 explicadas en el informe §4.6):
2009 CAT 76,9 CAST 74,7 MAT 78,0 | 2010 CAT 73,7 CAST 71,2 ING 71,4 MAT 78,2 | 2011 CAT 77,2 CAST 73,6 ING 80,6 MAT 80,9 |
2012 CAT 79,6 CAST 76,6 MAT 80,2 ING 74,3 | 2013 CAT 71,1 CAST 73,0 MAT 76,3 ING 73,0 | 2014 CAT 75,5 CAST 75,4 MAT 81,0 ING 75,1 |
2015 CAT 74,5 CAST 75,7 ING 74,5 MAT 80,0 | 2016 CAT 74,5 CAST 74,1 ING 73,7 MAT 77,9 | 2017 CAT 75,8 CAST 73,4 ING 79,9 MAT 77,6 |
2018 CAT 73,6 CAST 77,0 ING 76,3 MAT 79,2 MED 70,2 | 2019 CAT 75,5 CAST 74,4 ING 78,2 MAT 78,2 MED 68,1 |
2021 CAT 76,7 CAST 73,5 ING 73,2 MAT 76,0 MED 75,6 | 2022 CAT 72,5 CAST 74,0 ING 76,9 MAT 71,1 MED 72,8 |
2023 CAT 72,7 CAST 72,1 ING 77,8 MAT 73,6 MED 71,6 | 2024 CAT 74,7 CAST 73,9 ING 73,2 MAT 74,3 MED 74,3 FRA 62,5 |
2025 CAT 73,5 CAST 76,5 ING 75,7 FRA 66,1 MAT 70,4 MED 66,3
(Fuente: Quaderns d'avaluació del Consell Superior d'Avaluació, handles https://hdl.handle.net/20.500.12694/390 ... /7383; ver informe §4.6.)

## 7. Medidas DAX (tabla _Medidas). Nombres EXACTOS, displayFolder indicado. Añade `description` a cada medida.
Notas comunes: "global" = DimCompetencia[EsGlobal] = TRUE. "Cataluña" = REMOVEFILTERS(DimContextoCentro).
Mínimo muestral: si el nº de puntuaciones en el contexto < 30 -> BLANK() (K01, K02, K03, K06 y las que dependen de ellas).
Comparaciones temporales: por DimAnio[IndiceConvocatoria] con REMOVEFILTERS(DimAnio), nunca Anio-1; BLANK si el
contexto tiene != 1 año con convocatoria. Puntuaciones NO equiparadas entre convocatorias: indicarlo en la description.

"0. Base":
- `Alumnos evaluados` = COUNTROWS(FactEvaluacion)
- `Puntuaciones globales` = nº filas de FactPuntuacion con EsGlobal
- `Puntuación media` = AVERAGE(FactPuntuacion[Puntuacion]) (sin filtro de competencia; uso técnico)
- `Puntuación media Cataluña` = [K01 Puntuación media competencia] con REMOVEFILTERS(DimContextoCentro)
"1. Rendimiento académico":
- `K01 Puntuación media competencia` = media de globales (KEEPFILTERS EsGlobal = TRUE), con mínimo muestral.
- `K02 Puntuación media subcompetencia` = media de no globales excluyendo DimCalidadDato[NoValida] = TRUE, mínimo muestral.
- `K03 % alumnado nivel bajo` = globales con NivelKey = 1 / globales; ambos excluyendo Censurada o NivelNoComparable.
- `Puntuaciones por nivel de logro` (D-13) = globales del nivel del contexto excluyendo Censurada o NivelNoComparable; BLANK si la
   competencia no llega a 30 globales sumando todos los niveles (REMOVEFILTERS(DimNivelLogro) para el total). Base del gráfico de niveles.
"2. Equidad e inclusión":
- `K04 Brecha de género (Niños - Niñas)` = K01 con Genero="Niño" - K01 con Genero="Niña" (filtros sobre DimPerfilAlumno[Genero], quitando el filtro de género existente).
- `K05 Brecha pública - privada` = K01 Pública - K01 Privada.
- `K06 Dispersión de resultados` = STDEV.P de globales excluyendo Censurada, mínimo muestral.
"3. Territorio y entorno":
- `K07 Desviación respecto a Cataluña` = K01 - [Puntuación media Cataluña].
- `K08 Diferencia urbano - rural` = K01 hábitat código 3 - K01 hábitat código 1 (el código 0 "No fiable" nunca entra).
- `K09 Posición del área` = RANKX sobre ALLSELECTED(DimContextoCentro[AreaTerritorial]) excluyendo "Desconocida", por K01 DESC,
   Dense; BLANK si != 1 área en contexto o si todas las competencias del contexto son EsInformativa.
"4. Eficiencia y progreso":
- `K10 Variación interanual` = K01(convocatoria actual) - K01(IndiceConvocatoria - 1), calculado SOLO sobre las competencias
   globales cuyo PeriodoDisenoInicio <= Anio de la convocatoria anterior (si no queda ninguna -> BLANK).
- `K11 Tendencia 5 convocatorias` = (K01(i) - K01(i-4)) / 4, solo competencias con PeriodoDisenoInicio <= Anio de i-4.
- `K12 % competencias que mejoran` = nº de materias globales NO informativas con K10 >= 1 / nº de materias globales no
   informativas con K10 no BLANK (iterar sobre VALUES(DimCompetencia[CodigoMateria]) con EsGlobal).
"5. Semáforos" (1 favorable, 0 neutro, -1 desfavorable):
- `Estado K01` = si hay filtro de contexto: K07 >= 1 -> 1, <= -1 -> -1, si no 0; sin filtro de contexto: usa K10 con ±0,5.
- `Estado K03` = K03 - K03 Cataluña: <= -2 pp -> 1; >= +2 pp -> -1; si no 0.
- `Estado K10` = K10 >= 0,5 -> 1; <= -0,5 -> -1; si no 0.
Formatos: puntuaciones "0.0"; porcentajes "0.0%"; brechas/variaciones "+0.0;-0.0;0.0"; posición "0"; recuentos "#,0";
semáforos `"▲ Favorable";"▼ Desfavorable";"● Neutro"` (secciones positivo;negativo;cero; en TMDL se escribe entrecomillado con las
comillas interiores duplicadas; D-12). Total: 20 medidas.

## 8. Informe PBIR — 3 páginas (lienzo 1280x720), 41 visuales (actualizado el 12/11/2026: D-11 a D-15 y D-19)
Etiquetas visibles: "Competencia" para DimCompetencia[Materia] y "Titularidad" para DimContextoCentro[Naturaleza] (D-15).
Aviso fijo de los tres paneles: "Puntuaciones no equiparadas entre convocatorias; 2020 sin prueba (COVID-19) y 2021 se compara con 2019" (D-11).
Los tres gráficos de líneas llevan showAll en el eje para que 2020 aparezca como hueco (D-14). La selección por defecto 2025 de los
segmentadores de año es un filtro Categorical en filterConfig (D-19).
1. "Estratégico - Departamento" (13 visuales): tarjetas K01, K03, K06, K10, Estado K10, K12, Alumnos evaluados; gráfico de líneas K01
   por DimAnio[Anio] con leyenda Competencia; tabla por Competencia con K01, K10, Estado K10, K11, K03; segmentadores Anio y Competencia;
   cuadro de texto con el aviso y "Niveles de logro internos del TFG (cortes 55/70/85), no los niveles oficiales".
2. "Táctico - Inspección" (14 visuales): barras K07 por DimContextoCentro[AreaTerritorial]; matriz AreaTerritorial x Titularidad con K01;
   tarjetas K04, K05, K08, K09, Estado K01, Estado K03 (área seleccionada frente a Cataluña); línea K01 por Anio con leyenda
   DimContextoCentro[AreaSerieComparable]; segmentadores Anio, Competencia, AreaTerritorial, Género (DimPerfilAlumno[Genero]).
   Interacciones NoFilter: segmentador Anio -> línea; segmentador AreaTerritorial -> barras K07 (las barras muestran siempre todas las
   áreas y el tooltip K09 coincide con la tarjeta).
3. "Operativo - Dirección de centro" (14 visuales): segmentadores AreaTerritorial, Titularidad, Habitat, Anio, Competencia; tarjetas K01, K07,
   Puntuación media Cataluña, Estado K01, Estado K03; barras K02 por DimCompetencia[Subcompetencia]; barras 100% apiladas de
   `Puntuaciones por nivel de logro` por DimNivelLogro[Nivel] (el visual solo excluye "No aplica"; las exclusiones de calidad y el mínimo
   de 30 van en la medida, D-13); líneas K01 y Puntuación media Cataluña por Anio.
