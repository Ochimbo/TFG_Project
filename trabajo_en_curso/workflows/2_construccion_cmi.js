export const meta = {
  name: 'tfg-construccion-cmi',
  description: 'Construye el proyecto Power BI (PBIP: ETL M + modelo TMDL + DAX + informe PBIR) y la réplica Python de referencia; verifica de forma adversarial y corrige',
  phases: [
    { title: 'Construcción', detail: 'Modelo+ETL TMDL, medidas DAX, informe PBIR y réplica Python en paralelo' },
    { title: 'Verificación', detail: 'Integración estructural, M vs Python, DAX vs referencia' },
    { title: 'Corrección', detail: 'Aplicar los problemas confirmados y revalidar' },
  ],
}

const C = '/tmp/claude-1000/-home-kiara-rodriguez-uribe-Uni-TFG-Project/e4d67534-2cda-46c9-9607-3737fe5b6260/scratchpad/contrato_diseno.md'
const R = '/home/kiara-rodriguez-uribe/Uni/TFG_Project'
const SCR = '/tmp/claude-1000/-home-kiara-rodriguez-uribe-Uni-TFG-Project/e4d67534-2cda-46c9-9607-3737fe5b6260/scratchpad'
const BASE = `Proyecto: TFG (FIB-UPC) "Cuadro de Mando Integral en Power BI para la educación primaria de Cataluña" de Kiara Rodríguez Uribe.
LEE PRIMERO Y SIGUE AL PIE DE LA LETRA el contrato de diseño: ${C}
Informe de auditoría de datos (reglas R01-R34, detalle): ${R}/Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md
Repo: ${R}. Python: ${R}/.venv/bin/python. Datos: ${R}/Datos.csv (no modificar).
No hagas commits de git. Escribe SOLO los ficheros que te asigna tu tarea. Power BI Desktop no existe en esta máquina (Linux): el resultado lo abrirá la estudiante en Windows, así que la corrección sintáctica es crítica.`

const BUILD_OUT = {
  type: 'object',
  properties: {
    files_written: { type: 'array', items: { type: 'string' } },
    validation_done: { type: 'string', description: 'qué validaciones ejecutaste y su resultado literal' },
    deviations_from_contract: { type: 'array', items: { type: 'string' } },
    known_risks: { type: 'array', items: { type: 'string' }, description: 'aspectos que no has podido validar en Linux y que la estudiante debe comprobar en Power BI' },
  },
  required: ['files_written', 'validation_done', 'deviations_from_contract', 'known_risks'],
}

const BUILDERS = [
  {
    key: 'modelo-etl',
    prompt: `${BASE}

TAREA: Construye el modelo semántico en formato TMDL y el andamiaje PBIP, salvo las medidas.
Ficheros: ${R}/PowerBI/.gitignore, ${R}/PowerBI/CMI_Educacion_Primaria.pbip, ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition.pbism y, en .../definition/: database.tmdl, model.tmdl, expressions.tmdl, relationships.tmdl, tables/DimAnio.tmdl, DimContextoCentro.tmdl, DimPerfilAlumno.tmdl, DimCompetencia.tmdl, DimNivelLogro.tmdl, DimCalidadDato.tmdl, FactEvaluacion.tmdl y FactPuntuacion.tmdl. NO escribas _Medidas.tmdl: lo hace otro agente. model.tmdl SÍ debe incluir 'ref table _Medidas' en el orden de tablas.
- El .pbip referencia el informe (artifacts -> report.path "CMI_Educacion_Primaria.Report"). Valida .pbip y definition.pbism con los esquemas JSON de ${SCR}/json-schemas/fabric/pbip y .../fabric/item/semanticModel/definitionProperties: elige versiones estables, no la última si es muy reciente, y pon el "$schema" correspondiente con la URL oficial https://developer.microsoft.com/json-schemas/fabric/...
- ETL M (contrato §2): parámetro RutaDatos y expresión compartida stg_Evaluaciones en expressions.tmdl. Las particiones M de cada tabla. Las tablas estáticas se definen con #table y tipos explícitos. Usa la cultura "es-ES" en Number.FromText. Haz que los errores de validación de R02 y R09-R11 aborten la actualización con un mensaje claro (error Error.Record(...)). Evita los merges: usa claves deterministas y registros de búsqueda. FactPuntuacion: despivota con Table.UnpivotOtherColumns, que descarta nulos. Optimiza: elimina columnas pronto y tipa los enteros como Int64.Type y la Puntuacion como Currency.Type (decimal fijo). Comenta el código M en castellano con moderación, explicando cada regla (R0x) que se implementa: es un TFG y el tribunal leerá el código.
- Metadatos: descriptions en las tablas y columnas visibles, sortByColumn según el contrato, isHidden según el contrato, summarizeBy none en claves y códigos, y lineageTag (GUID) en tablas y columnas, como hace Power BI.
- VALIDA: copia la carpeta definition a ${SCR}/val_modelo, añade un _Medidas.tmdl stub mínimo (una tabla con una medida trivial y una partición M #table vacía) y ejecuta el validador TMDL del contrato §0 hasta obtener 0 errores. Repite tras cada cambio. Comprueba también que las claves calculadas en M para las combinaciones posibles caen dentro de las filas de las dimensiones estáticas. Hazlo razonando y con un script Python que enumere las combinaciones del contrato.
- Revisa que el M sea sintácticamente válido. Sin motor M en Linux, sé meticuloso: comas, "each", tipos y nombres de pasos con #"...".`,
  },
  {
    key: 'medidas-dax',
    prompt: `${BASE}

TAREA: Escribe ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl con TODAS las medidas del contrato §7: nombres exactos, displayFolder, formatString y description en castellano (indica en la description de las medidas temporales que las puntuaciones no están equiparadas entre convocatorias). La tabla _Medidas debe ser válida en TMDL: una partición M con #table de una columna oculta, por ejemplo, y un lineageTag.
- DAX correcto e idiomático: usa VAR/RETURN, KEEPFILTERS para EsGlobal, REMOVEFILTERS en lugar de ALL cuando corresponda, DIVIDE, y SELECTEDVALUE/HASONEVALUE para los contextos de un año o un área. K10 y K11 deben funcionar tanto con DimAnio[Anio] en el eje como con un segmentador de un solo año: navega por IndiceConvocatoria con REMOVEFILTERS(DimAnio) y filtra el conjunto de competencias comparables por PeriodoDisenoInicio. K12 itera por materia. Respeta el mínimo muestral de 30. Ojo con el patrón de K09 (RANKX con ALLSELECTED y la exclusión de "Desconocida"). Comprueba que cada referencia a una columna existe exactamente con ese nombre en el contrato §3.
- VALIDA: crea en ${SCR}/val_dax un modelo TMDL stub con las tablas y columnas del contrato §3 (particiones M #table vacías con los tipos correctos y las relaciones de §4), añade tu _Medidas.tmdl y ejecuta el validador TMDL (§0) hasta tener 0 errores. El validador no comprueba la semántica DAX: relee cada medida comprobando paréntesis, comas y nombres de funciones DAX reales.
- Además, escribe ${SCR}/dax_semantica.md explicando en una línea por medida qué devuelve en: (a) la tarjeta sin filtros, (b) DimAnio[Anio] en el eje con Materia filtrada, (c) un área seleccionada en 2025. Lo usará el verificador.`,
  },
  {
    key: 'informe-pbir',
    prompt: `${BASE}

TAREA: Crea el informe en formato PBIR (enhanced report format) en ${R}/PowerBI/CMI_Educacion_Primaria.Report/: definition.pbir (datasetReference byPath -> "../CMI_Educacion_Primaria.SemanticModel") y la carpeta definition/ con version.json, report.json, pages/pages.json y, por cada una de las 3 páginas del contrato §8, pages/<nombrePagina>/page.json y pages/<nombrePagina>/visuals/<nombreVisual>/visual.json. Los nombres de carpeta son identificadores sin espacios, de hasta 50 caracteres.
- Esquemas oficiales locales: ${SCR}/json-schemas/fabric/item/report/ (definition/*, definitionProperties). Elige versiones de esquema publicadas hace al menos varios meses (mira los CHANGELOG.md) para que funcionen en una versión reciente de Power BI Desktop, y usa la misma familia coherente en todos los ficheros. Pon en cada fichero el "$schema" con la URL oficial https://developer.microsoft.com/json-schemas/fabric/item/report/definition/... correspondiente.
- VALIDA cada JSON contra su esquema con python jsonschema. Resuelve los $ref remotos hacia los ficheros locales con referencing.Registry, mapeando el prefijo https://developer.microsoft.com/json-schemas/fabric/ a ${SCR}/json-schemas/fabric/. Itera hasta 0 errores. Si report.json hace referencia a un tema base (themeCollection/baseTheme), incluye el recurso que corresponda en StaticResources/SharedResources/BaseThemes/ o no lo referencies: un tema referenciado y ausente impide abrir el informe. Investiga en la documentación oficial de Microsoft (WebSearch/WebFetch: "Power BI Desktop project report folder PBIR") la estructura mínima válida y los campos obligatorios.
- Visuales: usa tipos estándar (card, lineChart, clusteredBarChart, tableEx, pivotTable, slicer, hundredPercentStackedBarChart, textbox). Las consultas (query.queryState) referencian Entity = nombre de la tabla del modelo y Property = columna o medida (Measure para las medidas de _Medidas), con los nombres EXACTOS del contrato §3 y §7. Distribuye los visuales sin solapes en un lienzo de 1280x720, con título en cada visual y en castellano. Diseño sobrio y accesible.
- Escribe también ${SCR}/pbir_referencias.json: la lista de todas las parejas (Entity, Property, tipo Column/Measure) que usa el informe, para que el verificador compruebe que existen en el modelo.`,
  },
  {
    key: 'python-referencia',
    prompt: `${BASE}

TAREA: Implementa la réplica de referencia en Python, independiente de Power BI, que sirve para validar el modelo y la ETL (método de validación del TFG, sección 4.3 del GEP).
1. ${R}/validacion/requirements.txt (pandas, duckdb, pyarrow, numpy, jsonschema; versiones mínimas).
2. ${R}/validacion/etl_referencia.py: implementa EXACTAMENTE las reglas del contrato §2 y las tablas §3/§5 con DuckDB (SQL) o pandas, y genera la estrella en ${R}/validacion/salida/*.parquet (DimAnio, DimContextoCentro, DimPerfilAlumno, DimCompetencia, DimNivelLogro, DimCalidadDato, FactEvaluacion, FactPuntuacion). Mismos nombres de columnas y mismas fórmulas de claves que el contrato. Código claro y comentado en castellano (el tribunal lo leerá), ejecutable con: python validacion/etl_referencia.py. Añade validacion/salida/ al .gitignore de la raíz del repo, sin borrar lo que ya tiene.
3. ${R}/validacion/test_modelo.py: tests ejecutables con python (asserts con mensajes) que comprueben lo de §6: recuentos, claves huérfanas = 0, rotaciones (regresión de R03/R04: global ≈ ponderada de sus subcompetencias en >= 99 % tras la corrección), códigos sin mapear = 0, rango [0,100], 2020 sin datos, IndiceConvocatoria consecutivo y medias de Cataluña frente a los valores oficiales de §6 (tolerancia 0,2; anota las excepciones documentadas como pruebas "esperadas fuera de tolerancia", no como fallos). Ejecútalo y deja que pase.
4. ${R}/validacion/kpis_referencia.py: calcula los 12 KPIs y los semáforos con la semántica EXACTA del contrato §7 (mínimo muestral, exclusiones por DimCalidadDato, PeriodoDisenoInicio en K10/K11, K12 por materia, etc.). Genera en ${R}/validacion/resultados/: kpi_cataluna_por_anio_materia.csv (Anio, Materia: K01, K03, K06, K04, K05, K08, K10, K11, Alumnos evaluados, Puntuaciones globales), kpi_area_2025.csv (AreaTerritorial x Materia en 2025: K01, K07, K09), kpi_global_por_anio.csv (por año sin filtro de materia: K01, K03, K06, K10, K11, K12) y contraste_oficial.csv (Anio, Materia, media calculada, media oficial §6, diferencia). Valores con 2 decimales.
5. Ejecuta todo (etl, test y kpis) y devuelve en validation_done las cifras clave obtenidas: recuentos, la media de castellano 2017 y el resumen del contraste oficial.`,
  },
]

phase('Construcción')
const built = await parallel(BUILDERS.map(b => () => agent(b.prompt, { label: `construir:${b.key}`, phase: 'Construcción', schema: BUILD_OUT }).then(r => ({ key: b.key, r }))))
const ok = built.filter(Boolean)
log(`Constructores completados: ${ok.length}/${BUILDERS.length}`)
const buildSummary = JSON.stringify(ok, null, 1)

phase('Verificación')
const ISSUES = {
  type: 'object',
  properties: {
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          severity: { type: 'string', enum: ['bloqueante', 'alta', 'media', 'baja'] },
          file: { type: 'string' },
          problem: { type: 'string' },
          evidence: { type: 'string', description: 'cómo lo has comprobado (salida de validador, comparación, contraejemplo)' },
          fix: { type: 'string', description: 'corrección concreta' },
        },
        required: ['id', 'severity', 'file', 'problem', 'evidence', 'fix'],
      },
    },
    checks_passed: { type: 'array', items: { type: 'string' } },
  },
  required: ['issues', 'checks_passed'],
}

const VERIFIERS = [
  {
    key: 'integracion',
    prompt: `${BASE}

TAREA: Eres el verificador de INTEGRACIÓN. NO edites ficheros del repo: trabaja sobre copias en ${SCR}/ver_integracion.
1. Ejecuta el validador TMDL (§0) sobre la carpeta definition COMPLETA y real (con _Medidas.tmdl) y anota cualquier error.
2. Comprueba que cada (Entity, Property) que usa el informe existe en el modelo con el tipo correcto (Column o Measure). Saca las parejas de los visual.json, no solo de ${SCR}/pbir_referencias.json, y compáralas con la salida del validador TMDL.
3. Valida todos los JSON del informe y del pbip/pbism contra sus esquemas locales (${SCR}/json-schemas/fabric, con resolución local de $ref) y comprueba la coherencia de rutas: .pbip -> Report, definition.pbir -> ../SemanticModel, pages.json -> carpetas de páginas existentes (pageOrder/activePageName), y que no quede ningún recurso referenciado y ausente.
4. Revisa los riesgos de apertura en Power BI Desktop: versiones de esquema demasiado nuevas, campos obligatorios ausentes, nombres de carpeta inválidos, lineageTag duplicados y "ref table" que no tengan su fichero.
Reporta cada problema con evidencia. Resultado de los constructores:
${buildSummary}`,
  },
  {
    key: 'etl-m-vs-python',
    prompt: `${BASE}

TAREA: Eres un verificador ADVERSARIAL de la ETL. Hay dos implementaciones independientes de las mismas reglas: el M de ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition (expressions.tmdl y particiones) y la réplica Python ${R}/validacion/etl_referencia.py. Tu objetivo es encontrar dónde se equivoca cualquiera de las dos frente al contrato §2/§3/§5 y donde difieren entre sí.
- Recorre regla por regla (R01-R04, R09-R14, R16-R19, R21, R25-R29 y las claves) y compara el contrato, el M y Python. Busca contraejemplos concretos en los datos con DuckDB: por ejemplo, filas de 2014 en Baix Llobregat con "Més de 100000", 2016 con fecha 1/2001, 2017 castellano, 2016 francés, la fila de 2024 con área vacía, "Fins a 13xxx" o puntuación global exactamente 55,00, 70,00 u 85,00 (límites de nivel).
- Errores de M típicos: Number.FromText sin cultura, comparaciones de texto con null que dan error, Table.ReplaceValue mal aplicado, tipos de columna perdidos tras Table.AddColumn (sin tipo -> type any), UnpivotOtherColumns sin las columnas correctas, "each" mal anidado, rotaciones no simultáneas (usar valores ya modificados), Int64 vs number y #table con tipos inconsistentes. Señala también la sintaxis M sospechosa, porque no se puede ejecutar aquí.
- Ejecuta ${R}/validacion/test_modelo.py y revisa que sus asserts comprueban de verdad lo que dicen.
Reporta solo problemas reales, con evidencia. Resultado de los constructores:
${buildSummary}`,
  },
  {
    key: 'dax-semantica',
    prompt: `${BASE}

TAREA: Eres un verificador ADVERSARIAL del DAX de ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl. Compáralo con el contrato §7, con la explicación del autor (${SCR}/dax_semantica.md) y con los valores de referencia de Python (${R}/validacion/resultados/*.csv y ${R}/validacion/kpis_referencia.py).
- Para cada medida, razona paso a paso qué devuelve en tres contextos: tarjeta sin filtros, DimAnio[Anio] en el eje con una materia filtrada, y un área en 2025. Para los casos (b) y (c), compáralo con el valor de los CSV de referencia de un corte concreto y explica cualquier discrepancia esperable. Busca errores clásicos: KEEPFILTERS frente a filtro que sobrescribe, ALL/REMOVEFILTERS sobre la tabla equivocada, transición de contexto en iteradores, RANKX con empates o con el área "Desconocida", SELECTEDVALUE sin alternativa, BLANK frente a 0 en DIVIDE, K10/K11 cuando el eje es Anio (¿se pierde el filtro de año?), K12 con materias sin datos, K04/K05/K08 que no eliminan el filtro existente de género/naturaleza/hábitat, mínimo muestral, formatos y nombres de función inexistentes.
- Comprueba también que kpis_referencia.py implementa la misma semántica (si discrepa del contrato, es un problema de Python).
Reporta solo problemas reales, con contraejemplo o razonamiento verificable. Resultado de los constructores:
${buildSummary}`,
  },
]

const verified = await parallel(VERIFIERS.map(v => () => agent(v.prompt, { label: `verificar:${v.key}`, phase: 'Verificación', schema: ISSUES }).then(r => ({ key: v.key, r }))))
const vok = verified.filter(Boolean)
const allIssues = vok.flatMap(v => (v.r.issues || []).map(i => ({ ...i, verifier: v.key })))
log(`Problemas encontrados: ${allIssues.length} (${allIssues.filter(i => i.severity === 'bloqueante' || i.severity === 'alta').length} bloqueantes/altos)`)

phase('Corrección')
const FIX_OUT = {
  type: 'object',
  properties: {
    fixed: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, what: { type: 'string' } }, required: ['id', 'what'] } },
    rejected: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, why: { type: 'string' } }, required: ['id', 'why'] } },
    final_validation: { type: 'string', description: 'salida literal final del validador TMDL, de la validación de esquemas PBIR y de test_modelo.py' },
    remaining_risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['fixed', 'rejected', 'final_validation', 'remaining_risks'],
}
const fix = await agent(`${BASE}

TAREA: Eres el integrador final. Abajo tienes los problemas que han encontrado tres verificadores independientes. Para CADA uno:
1. Compruébalo tú mismo. Puede ser un falso positivo: si lo descartas, justifícalo en rejected.
2. Si es real, corrígelo en el fichero que toque (M/TMDL, _Medidas.tmdl, PBIR o Python), manteniendo la coherencia entre la ETL M y la réplica Python, y entre el DAX y kpis_referencia.py.
Después, revalida TODO: el validador TMDL sobre la carpeta definition real (0 errores), la validación de esquemas de todos los JSON PBIR/PBIP (0 errores), la comprobación de que las referencias del informe existen en el modelo, y ejecuta de nuevo python validacion/etl_referencia.py (si has cambiado la ETL), validacion/test_modelo.py y validacion/kpis_referencia.py. Devuelve la salida literal final.
No cambies nombres del contrato salvo que sean imposibles. Si cambias algo respecto al contrato, inclúyelo en remaining_risks.

PROBLEMAS:
${JSON.stringify(allIssues, null, 1)}

CHECKS QUE YA PASARON:
${JSON.stringify(vok.map(v => ({ v: v.key, ok: v.r.checks_passed })), null, 1)}`, { label: 'integrar-corregir', phase: 'Corrección', schema: FIX_OUT })

return { builders: ok.map(b => ({ key: b.key, files: b.r.files_written, validation: b.r.validation_done, deviations: b.r.deviations_from_contract, risks: b.r.known_risks })), issues: allIssues, fix }
