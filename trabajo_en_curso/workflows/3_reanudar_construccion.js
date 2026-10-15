export const meta = {
  name: 'tfg-construccion-cmi-reanudar',
  description: 'Reanuda la construcción del CMI: modelo+ETL TMDL/M, completa Python de referencia, valida PBIR; verificación adversarial y corrección',
  phases: [
    { title: 'Construcción', detail: 'Modelo+ETL TMDL/M desde cero, tests y KPIs Python, validación y corrección del PBIR existente' },
    { title: 'Verificación', detail: 'Integración estructural, M vs Python, DAX vs referencia' },
    { title: 'Corrección', detail: 'Aplicar los problemas confirmados y revalidar todo' },
  ],
}

const R = '/home/kiara-rodriguez-uribe/Uni/TFG_Project'
const SCR = '/tmp/claude-1000/-home-kiara-rodriguez-uribe-Uni-TFG-Project/e4d67534-2cda-46c9-9607-3737fe5b6260/scratchpad'
const C = `${SCR}/contrato_diseno.md`
const GEN = `${R}/trabajo_en_curso/generadores`
const BASE = `Proyecto: TFG (FIB-UPC) "Cuadro de Mando Integral en Power BI para la educación primaria de Cataluña" de Kiara Rodríguez Uribe.
LEE PRIMERO Y SIGUE AL PIE DE LA LETRA el contrato de diseño: ${C}. Incluye las rutas de las herramientas de validación: validador TMDL, parser M y esquemas PBIR.
Estado del trabajo previo: ${R}/trabajo_en_curso/ESTADO.md. Informe de auditoría de datos (reglas R01-R34): ${R}/Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md
Repo: ${R}. Python: ${R}/.venv/bin/python. Datos: ${R}/Datos.csv (no modificar). Node 22 disponible.
Ya existen y son reutilizables: ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl (19 medidas; lo genera ${GEN}/gen_medidas.py <ruta_salida>), el informe PBIR en ${R}/PowerBI/CMI_Educacion_Primaria.Report/ (lo genera ${GEN}/gen_pbir.py) y ${R}/validacion/etl_referencia.py (réplica Python de la ETL, ya ejecutada; genera ${R}/validacion/salida/*.parquet).
REGLA DE GENERADORES: si cambias _Medidas.tmdl o el PBIR, cambia el GENERADOR correspondiente y regenera, para que generador y salida no diverjan.
No hagas commits de git. Escribe solo los ficheros de tu tarea. Power BI Desktop no existe aquí (Linux): la estudiante lo abrirá en Windows, así que la corrección sintáctica es crítica.`

const BUILD_OUT = {
  type: 'object',
  properties: {
    files_written: { type: 'array', items: { type: 'string' } },
    validation_done: { type: 'string', description: 'validaciones ejecutadas y resultado literal' },
    deviations_from_contract: { type: 'array', items: { type: 'string' } },
    known_risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['files_written', 'validation_done', 'deviations_from_contract', 'known_risks'],
}

const BUILDERS = [
  {
    key: 'modelo-etl',
    prompt: `${BASE}

TAREA: Construye el modelo semántico TMDL (salvo _Medidas.tmdl, que ya existe y NO debes tocar) y el andamiaje PBIP.
Ficheros: ${R}/PowerBI/.gitignore, ${R}/PowerBI/CMI_Educacion_Primaria.pbip, ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition.pbism y, en .../definition/: database.tmdl, model.tmdl (con 'ref table' de las 9 tablas, _Medidas incluida), expressions.tmdl, relationships.tmdl, tables/DimAnio.tmdl, DimContextoCentro.tmdl, DimPerfilAlumno.tmdl, DimCompetencia.tmdl, DimNivelLogro.tmdl, DimCalidadDato.tmdl, FactEvaluacion.tmdl y FactPuntuacion.tmdl.
- Reutiliza como referencia de las reglas lo que ya hace ${R}/validacion/etl_referencia.py, que está probado contra los datos: el M debe implementar exactamente las mismas reglas y claves (contrato §2-§5). También puedes inspirarte en ${R}/validacion/perfilado/limpieza_categoricas.pq, pero actualízalo a las reglas finales del contrato.
- .pbip -> artifacts report.path "CMI_Educacion_Primaria.Report". Valida .pbip y definition.pbism con sus esquemas JSON locales (versiones estables) y pon "$schema" con la URL oficial.
- ETL M: parámetro RutaDatos y expresión compartida stg_Evaluaciones en expressions.tmdl; particiones M en cada tabla; tablas estáticas con #table y tipos explícitos; Number.FromText(texto, "es-ES"); errores de validación (R02, R09-R11 y área desconocida) que abortan la actualización con Error.Record; claves deterministas sin merges; Table.UnpivotOtherColumns para FactPuntuacion; tipos Int64.Type y Currency.Type, y cada Table.AddColumn con su tipo. Comentarios en castellano que citen la regla R0x implementada (el tribunal leerá el código).
- Metadatos: descriptions, sortByColumn, isHidden, summarizeBy none, formatString y lineageTag (GUID determinista) en tablas y columnas. Además, en model.tmdl: annotation PBI_QueryOrder y culture es-ES.
- VALIDA, iterando hasta que todo pase:
  (1) Validador TMDL sobre la carpeta definition real (ya incluye _Medidas.tmdl): 0 errores, y todas las columnas que usa _Medidas existen.
  (2) Parser M: extrae a .m CADA expresión de expressions.tmdl y CADA partición M, y analízalas con mcheck.js. Todas OK.
  (3) Un script Python que reimplemente la fórmula de claves y compruebe que todas las combinaciones posibles de staging caen en filas de las dimensiones estáticas, comparando con validacion/salida/*.parquet si hace falta: 0 huérfanas.
  (4) Relee el M buscando errores que el parser no detecta: nombres de columna mal escritos, campos [x] inexistentes, tipos y uso de null en comparaciones.
- Deja en ${R}/trabajo_en_curso/herramientas/validar_m.py el script reutilizable que extrae el M de los TMDL y llama a mcheck.js.`,
  },
  {
    key: 'python-completar',
    prompt: `${BASE}

TAREA: Completa la réplica Python. etl_referencia.py ya existe y se ha ejecutado: revísalo contra el contrato y corrige si hace falta (si lo cambias, vuelve a ejecutarlo).
1. ${R}/validacion/test_modelo.py: tests ejecutables con python, con asserts que expliquen el fallo, sobre validacion/salida/*.parquet. Deben comprobar todo lo del contrato §6: recuentos, claves huérfanas = 0, regresión de rotaciones R03/R04 (global ≈ ponderada de sus subcompetencias en >= 99 % tras la corrección; usa los pesos del informe §4.3), códigos sin mapear = 0, rango [0,100], 2020 sin datos, IndiceConvocatoria consecutivo, umbrales de nivel en los límites exactos (55,00 -> Medio-bajo; 70,00 -> Medio-alto; 85,00 -> Alto), máscara de DimCalidadDato en casos concretos, y medias de Cataluña frente a las oficiales de §6 con tolerancia 0,2. Las excepciones documentadas en el informe §4.6 se marcan como "esperadas fuera de tolerancia" y no como fallos. Ejecútalo y haz que pase.
2. ${R}/validacion/kpis_referencia.py: los 12 KPIs y los 3 semáforos con la semántica EXACTA del contrato §7: mínimo muestral, exclusiones por DimCalidadDato, PeriodoDisenoInicio en K10/K11, K12 por materia con umbral >= 1, K09 sin "Desconocida", etc. Genera en ${R}/validacion/resultados/: kpi_cataluna_por_anio_materia.csv (Anio, Materia: K01, K03, K06, K04, K05, K08, K10, K11, Alumnos evaluados, Puntuaciones globales), kpi_area_2025.csv (AreaTerritorial x Materia en 2025: K01, K07, K09), kpi_global_por_anio.csv (por año sin filtro de materia: K01, K03, K06, K10, K11, K12), semaforos_2025.csv y contraste_oficial.csv (Anio, Materia, media calculada, media oficial de §6, diferencia, dentro_tolerancia). Valores con 2 decimales y separador de campo coma.
3. Escribe ${R}/validacion/README.md: cómo instalar (pip install -r requirements.txt), el orden de ejecución y qué produce cada script. Breve.
4. Ejecuta todo y devuelve en validation_done las cifras clave: recuentos, castellano 2017, nº de combinaciones dentro de tolerancia frente al total y K01 de Cataluña 2025 por materia.`,
  },
  {
    key: 'pbir-validar',
    prompt: `${BASE}

TAREA: El informe PBIR ya está generado en ${R}/PowerBI/CMI_Educacion_Primaria.Report/ por ${GEN}/gen_pbir.py, pero NUNCA se ha validado.
1. Corrige en gen_pbir.py las rutas que apuntan a /tmp (variable SCRATCH): que el fichero de referencias se escriba en ${GEN}/pbir_referencias.json.
2. Valida CADA JSON del informe contra su esquema oficial local (${SCR}/json-schemas/fabric/item/report/...) con python jsonschema, resolviendo los $ref remotos con referencing.Registry (prefijo https://developer.microsoft.com/json-schemas/fabric/ -> ${SCR}/json-schemas/fabric/). Usa el "$schema" de cada fichero para elegir el esquema. Corrige el GENERADOR hasta 0 errores y regenera.
3. Comprueba la coherencia estructural: definition.pbir con datasetReference byPath "../CMI_Educacion_Primaria.SemanticModel", pages.json (pageOrder y activePageName) frente a las carpetas, nombres de carpeta válidos, tema base referenciado presente en StaticResources (y declarado en report.json resourcePackages si el esquema lo exige), y posiciones dentro de 1280x720 sin solapes.
4. Comprueba que cada (Entity, Property) que usa el informe existe en el contrato §3/§7 (columnas) o en _Medidas.tmdl (medidas), con el tipo correcto (Column/Measure) y el nombre exacto, tildes incluidas.
5. Compara la estructura de los visual.json con los ejemplos reales de ${R}/trabajo_en_curso/referencias_pbir/ (pbir_format_docs y ejemplos): nombres de roles de proyección por tipo de visual (Category/Y/Values/Rows/Columns/Series), queryState y sortDefinition. Corrige las diferencias que harían fallar la apertura o dejarían un visual vacío.
6. Añade un validador reutilizable en ${R}/trabajo_en_curso/herramientas/validar_pbir.py (esquemas + referencias del modelo), ejecútalo y devuelve su salida.`,
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
          evidence: { type: 'string' },
          fix: { type: 'string' },
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

TAREA: Eres el verificador de INTEGRACIÓN. NO edites el repo: trabaja sobre copias en ${SCR}/ver_integracion.
1. Ejecuta el validador TMDL sobre la carpeta definition real y completa, y el parser M sobre todo el M (usa ${R}/trabajo_en_curso/herramientas/validar_m.py si existe).
2. Ejecuta ${R}/trabajo_en_curso/herramientas/validar_pbir.py y además comprueba por tu cuenta que cada (Entity, Property) de los visual.json existe en el modelo TMDL real con su tipo.
3. Coherencia PBIP: .pbip -> Report; definition.pbir -> ../SemanticModel; definition.pbism; .gitignore. Riesgos de apertura en Power BI Desktop: versiones de esquema demasiado nuevas, campos obligatorios ausentes, lineageTag duplicados, 'ref table' sin fichero, sortByColumn con cardinalidad incompatible (la columna de orden debe tener un único valor por cada valor del atributo; compruébalo con los datos de las tablas estáticas), relaciones con tipos de clave distintos y columnas ocultas usadas en visuales.
Reporta cada problema con evidencia. Resultado de los constructores:
${buildSummary}`,
  },
  {
    key: 'etl-m-vs-python',
    prompt: `${BASE}

TAREA: Eres un verificador ADVERSARIAL de la ETL. Compara las dos implementaciones independientes, el M de los TMDL (${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition) y ${R}/validacion/etl_referencia.py, contra el contrato §2-§5 y entre sí, regla por regla (R01-R04, R09-R14, R16-R19, R21, R25-R29 y las claves).
- Busca contraejemplos concretos en los datos con DuckDB: 2014 Baix Llobregat "Més de 100000", 2016 con 1/2001, rotaciones de castellano 2017 y francés 2016, la fila de 2024 con área vacía, "Fins a 13xxx", globales exactamente 55,00, 70,00 u 85,00, edad 10 y 14, MES_NAIXEMENT vacío o 0, filas de 2016 o 2018 sin código. Para cada uno, traza a mano qué produce el M y qué produce Python.
- Errores de M típicos: cultura, null en comparaciones (null = "x" devuelve null, no false; "if null then" da error), Text.StartsWith con null, columnas sin tipo tras AddColumn, UnpivotOtherColumns con las columnas equivocadas, rotaciones no simultáneas, Int64 frente a number en las claves, #table con tipos inconsistentes, Record.Field con un campo inexistente y errores de rendimiento graves (Table.Buffer de 17 M de filas, por ejemplo).
- Ejecuta ${R}/validacion/test_modelo.py y comprueba que sus asserts verifican de verdad lo que dicen.
Reporta solo problemas reales, con evidencia. Resultado de los constructores:
${buildSummary}`,
  },
  {
    key: 'dax-semantica',
    prompt: `${BASE}

TAREA: Eres un verificador ADVERSARIAL del DAX de ${R}/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl (generado por ${GEN}/gen_medidas.py). Compáralo con el contrato §7 y con los valores de referencia de Python (${R}/validacion/resultados/*.csv y kpis_referencia.py).
- Para cada medida, razona paso a paso qué devuelve en tres contextos: (a) tarjeta sin filtros; (b) DimAnio[Anio] en el eje con una materia filtrada; (c) un área en 2025. Contrasta (b) y (c) con un corte concreto de los CSV.
- Busca errores clásicos: KEEPFILTERS frente a filtro que sobrescribe; ALL/REMOVEFILTERS sobre la tabla equivocada; transición de contexto en iteradores; RANKX con empates o con "Desconocida"; SELECTEDVALUE sin alternativa; BLANK frente a 0 en DIVIDE; K10/K11 con Anio en el eje (que REMOVEFILTERS(DimAnio) no pierda el año actual); K12 con materias sin datos; K04/K05/K08 sin quitar el filtro existente de género, naturaleza o hábitat; mínimo muestral; formatos; y funciones o nombres de columna que no existan en el modelo TMDL real.
- Comprueba también que kpis_referencia.py implementa la misma semántica. Si difiere del contrato, el problema es de Python.
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
    final_validation: { type: 'string', description: 'salida literal final del validador TMDL, del parser M, de validar_pbir.py y de test_modelo.py' },
    remaining_risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['fixed', 'rejected', 'final_validation', 'remaining_risks'],
}
const fix = await agent(`${BASE}

TAREA: Eres el integrador final. Abajo tienes los problemas que han encontrado tres verificadores independientes. Para CADA uno: compruébalo tú mismo (descártalo con justificación si es un falso positivo) y, si es real, corrígelo en el fichero que toque. Mantén la coherencia entre el M y la réplica Python, y entre el DAX y kpis_referencia.py, y recuerda la REGLA DE GENERADORES.
Después, revalida TODO y devuelve la salida literal: validador TMDL (0 errores), parser M (todo OK), ${R}/trabajo_en_curso/herramientas/validar_pbir.py (0 errores), y vuelve a ejecutar validacion/etl_referencia.py (si cambió la ETL), validacion/test_modelo.py y validacion/kpis_referencia.py.
No cambies nombres del contrato salvo que sean imposibles. Si cambias algo respecto al contrato, actualiza también ${C} y ${R}/trabajo_en_curso/contrato_diseno.md, y menciónalo en remaining_risks.

PROBLEMAS:
${JSON.stringify(allIssues, null, 1)}

CHECKS QUE YA PASARON:
${JSON.stringify(vok.map(v => ({ v: v.key, ok: v.r.checks_passed })), null, 1)}`, { label: 'integrar-corregir', phase: 'Corrección', schema: FIX_OUT })

return { builders: ok.map(b => ({ key: b.key, files: b.r.files_written, validation: b.r.validation_done, deviations: b.r.deviations_from_contract, risks: b.r.known_risks })), issues: allIssues, fix }
