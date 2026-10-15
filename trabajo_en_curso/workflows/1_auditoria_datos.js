export const meta = {
  name: 'tfg-auditoria-datos',
  description: 'Perfilado exhaustivo del dataset de 6º de primaria, investigación de metadatos oficiales, verificación independiente y especificación de reglas de limpieza',
  phases: [
    { title: 'Perfilado', detail: 'Perfilado de categóricas/IDs/fechas y de puntuaciones con DuckDB, más investigación de metadatos oficiales' },
    { title: 'Verificación', detail: 'Re-ejecución independiente de cada hallazgo numérico' },
    { title: 'Síntesis', detail: 'Reglas de limpieza y redacción del informe de calidad de datos' },
  ],
}

const CTX = `
CONTEXTO DEL PROYECTO (TFG FIB-UPC, Kiara Rodríguez Uribe):
"Diseño e implementación de un Cuadro de Mando Integral (CMI) en Power BI para el soporte a la toma de decisiones en la educación primaria de Cataluña".
- Repo: /home/kiara-rodriguez-uribe/Uni/TFG_Project
- Dataset: /home/kiara-rodriguez-uribe/Uni/TFG_Project/Datos.csv (240 MB, 1.102.324 filas de datos, 32 columnas, UTF-8, separador coma, todos los valores entre comillas dobles, decimales con coma "87,70", vacíos = campo vacío sin comillas). Fuente: Portal de Dades Obertes de la Generalitat, dataset "Avaluació de sisè d'educació primària" id rk5x-gny6.
- Columnas: ANY, CODI_ALUMNE, PCAT, PCAT_CL, PCAT_EE, PCAST, PCAST_CL, PCAST_EE, PMAT, PMAT_NC, PMAT_EFM, PMAT_CR, PANG, PANG_CO, PANG_CE, PFRAN, PFRAN_CO, PFRAN_CE, PANG_EE, PFRAN_EE, PCAT_CO, PCAST_CO, PMED, PMED_COMP1, PMED_COMP2, PMED_COMP3, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT, AREA_TERRITORIAL, NATURALESA, HÀBITAT
- Python con duckdb, pandas y pyarrow: /home/kiara-rodriguez-uribe/Uni/TFG_Project/.venv/bin/python  (usa duckdb: read_csv('Datos.csv', all_varchar=true, header=true); la columna ANY es palabra reservada en SQL: cítala como "ANY"; igual "HÀBITAT").
- Hechos ya conocidos (confírmalos o corrígelos, no los des por buenos): 2020 no existe (COVID); 2009-2015 CODI_ALUMNE vacío; 914 CODI_ALUMNE aparecen en 2 años; duplicados dentro de un año en 2016-2018; GENERE usa H/D salvo 2021 (Home/Dona); NATURALESA Públic/Privat hasta 2023 y Pública/Privada en 2024-2025; HÀBITAT 'Més de 100000' hasta 2023 y 'Més de 100001' en 2024-2025; 13.357 filas de 2024 con 'Fins a 100xx' autoincrementado (error tipo arrastre Excel); 1 fila 2024 con AREA_TERRITORIAL vacía; áreas nuevas: Alt Pirineu i Aran y Penedès desde 2024, Barcelonès solo 2025, Barcelona Comarques hasta 2024.
- El objetivo final es un modelo en estrella (Kimball) en Power BI: FactPuntuacion (una fila por alumno-evaluación x competencia/subcompetencia con puntuación no nula), FactEvaluacion (una fila por alumno-evaluación), DimAnio, DimContextoCentro (área, naturaleza, hábitat), DimPerfilAlumno (género, mes nacimiento, edad en la prueba, situación de edad), DimCompetencia, DimNivelLogro. 12 KPIs: puntuación media por competencia, por subcompetencia, % alumnado en nivel bajo, brecha de género, brecha pública-privada, dispersión, desviación del área respecto a Cataluña, diferencia por hábitat, posición relativa del área, variación interanual, tendencia 5 convocatorias, % competencias que mejoran.
REGLAS: no modifiques Datos.csv ni Datos.zip. Escribe en castellano. Toda afirmación numérica debe venir de una consulta que hayas ejecutado de verdad (incluye la consulta o el script). No inventes.`

const FINDINGS = {
  type: 'object',
  properties: {
    script_path: { type: 'string', description: 'ruta del script reproducible que has guardado' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'ID corto estable, p.ej. CAT-01, PUN-03' },
          category: { type: 'string', enum: ['completitud', 'consistencia', 'validez', 'unicidad', 'comparabilidad_temporal', 'semantica', 'otro'] },
          title: { type: 'string' },
          evidence: { type: 'string', description: 'cifras exactas obtenidas y la consulta SQL usada' },
          affected_rows: { type: 'integer' },
          impact: { type: 'string', description: 'impacto en el modelo/KPIs' },
          proposed_rule: { type: 'string', description: 'regla de limpieza o decisión de modelado propuesta, concreta e implementable' },
        },
        required: ['id', 'category', 'title', 'evidence', 'impact', 'proposed_rule'],
      },
    },
    summary_tables_md: { type: 'string', description: 'tablas resumen en Markdown con las cifras clave (por año, por columna) aptas para pegar en el informe' },
  },
  required: ['script_path', 'findings', 'summary_tables_md'],
}

const PROFILERS = [
  {
    key: 'categoricas',
    prompt: `${CTX}

TAREA: Perfilado exhaustivo de las columnas NO numéricas de puntuación: ANY, CODI_ALUMNE, GENERE, MES_NAIXEMENT, ANY_NAIXEMENT, AREA_TERRITORIAL, NATURALESA, HÀBITAT.
Guarda un script reproducible en /home/kiara-rodriguez-uribe/Uni/TFG_Project/validacion/perfilado/perfil_categoricas.py (crea la carpeta) que imprima todas las cifras, y ejecútalo.
Cubre como mínimo:
1. Filas por año; años presentes y ausentes en 2009-2025.
2. CODI_ALUMNE: vacíos por año; formato (longitud, solo dígitos); duplicados dentro del mismo año (¿son filas idénticas o difieren en puntuaciones/atributos? muestra ejemplos); IDs repetidos entre años (cuántos, qué pares de años, ¿coinciden género/fecha de nacimiento? ¿cuadra con repetición de curso: año de nacimiento compatible?). Uno de los grupos de conteo era la cadena vacía: sepáralo.
3. Valores distintos y frecuencias por año de GENERE, NATURALESA, HÀBITAT, AREA_TERRITORIAL (matriz área x año con conteos), incluidos vacíos y espacios en blanco al inicio/final.
4. HÀBITAT: rango exacto de los valores 'Fins a N' anómalos (min/max N, años), si los anómalos se concentran en algún área/naturaleza, y propuesta de mapeo a 3 categorías.
5. Fechas de nacimiento: rango de ANY_NAIXEMENT y MES_NAIXEMENT, vacíos, valores imposibles; distribución de EDAD = ANY - ANY_NAIXEMENT por año (la edad teórica en 6º en mayo del año ANY es 12 si nace en ANY-12; comprueba qué edad es la moda en cada año) y % de alumnado mayor de la edad teórica por año, género y naturaleza.
6. Ruptura territorial 2024-2025: para las áreas nuevas/desaparecidas, conteos por año, y comprueba con los datos si la suma de las áreas que aparecen en 2024/2025 es compatible con las que desaparecen (p.ej. comparar volúmenes de Barcelona Comarques 2023 vs Barcelona Comarques 2024 + Penedès 2024 + ..., y Lleida 2023 vs Lleida 2024 + Alt Pirineu i Aran 2024). Indica qué se puede afirmar con datos y qué no.
7. Cualquier otra anomalía que detectes.
Para cada problema da una regla de limpieza concreta e implementable en Power Query (M) y en Python.`,
  },
  {
    key: 'puntuaciones',
    prompt: `${CTX}

TAREA: Perfilado exhaustivo de las 24 columnas de puntuación (PCAT ... PMED_COMP3).
Guarda un script reproducible en /home/kiara-rodriguez-uribe/Uni/TFG_Project/validacion/perfilado/perfil_puntuaciones.py (crea la carpeta) que imprima todas las cifras, y ejecútalo.
Cubre como mínimo:
1. Formato: confirma decimal con coma, número de decimales, valores no parseables, valores fuera de [0,100], negativos.
2. Matriz de cobertura: % de no nulos por columna y año (24 x 16). Qué competencias existen en qué años. Para PFRAN* (francés) cuántos alumnos por año.
3. Por columna y año: media, desviación típica, mínimo, máximo, percentiles 10/25/50/75/90, y conteo de no nulos. Detecta saltos bruscos de media entre años que sugieran cambios de escala o de diseño de la prueba.
4. Relación global vs subcompetencias: para cada materia (PCAT, PCAST, PMAT, PANG, PFRAN, PMED) comprueba si la global es la media simple de sus subcompetencias, una media ponderada (estima los pesos por regresión lineal sin intercepto por año, con numpy/pandas), o ninguna; da el error máximo y medio. Ojo: PCAT_CO y PCAST_CO existen solo desde 2018, PANG_EE desde 2013: analiza por periodos.
5. Coherencia de nulos: alumnos con la global informada pero alguna subcompetencia nula y viceversa, por materia y año.
6. Alumnos sin ninguna puntuación (fila sin ninguna de las 24 columnas): cuántos por año.
7. Número de filas resultantes si se despivotan las 24 columnas descartando nulos (tamaño de FactPuntuacion), total y por año.
8. Distribución de las puntuaciones globales (histograma en tramos de 5 puntos, todos los años juntos y por materia) para proponer umbrales de niveles de logro. Propón 4 niveles (Bajo, Medio-bajo, Medio-alto, Alto) con límites redondos justificados y el % de alumnado que caería en cada nivel por materia con esos límites. Indica si conviene usar umbrales distintos por materia.
9. Cualquier otra anomalía.
Para cada problema da una regla de limpieza o decisión de modelado concreta.`,
  },
]

const VERIFY = {
  type: 'object',
  properties: {
    checks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          confirmed: { type: 'boolean', description: 'true solo si tu re-ejecución independiente reproduce las cifras clave' },
          corrected_evidence: { type: 'string', description: 'cifras correctas obtenidas por ti y consulta usada' },
          rule_assessment: { type: 'string', description: 'si la regla propuesta es correcta, segura y suficiente; si no, la regla corregida' },
        },
        required: ['id', 'confirmed', 'corrected_evidence', 'rule_assessment'],
      },
    },
    missed: { type: 'array', items: { type: 'string' }, description: 'problemas relevantes que el perfilado no detectó, con cifras' },
  },
  required: ['checks', 'missed'],
}

const RESEARCH = {
  type: 'object',
  properties: {
    columns: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string' },
          official_description: { type: 'string' },
          name_es: { type: 'string', description: 'nombre legible en castellano para el modelo (materia/subcompetencia/atributo)' },
          source: { type: 'string' },
        },
        required: ['field', 'name_es'],
      },
    },
    any_meaning: { type: 'string', description: 'qué representa ANY (año de la prueba / curso escolar), con fuente' },
    territorial_changes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          change: { type: 'string' },
          year_effective: { type: 'string' },
          previous_area: { type: 'string' },
          source_url: { type: 'string' },
          confidence: { type: 'string', enum: ['alta', 'media', 'baja'] },
        },
        required: ['change', 'source_url', 'confidence'],
      },
    },
    achievement_levels: { type: 'string', description: 'cómo define el Consell Superior d Avaluació los niveles de logro de 6º (nombres, puntos de corte si se publican), con fuentes' },
    official_reference_values: { type: 'string', description: 'valores oficiales publicados (medias o % por nivel por competencia y año) útiles para validar KPIs, con URL exacta; o explica por qué no se encontraron' },
    covid_2020: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['columns', 'any_meaning', 'territorial_changes', 'achievement_levels', 'official_reference_values', 'notes'],
}

phase('Perfilado')
const researchP = agent(`${CTX}

TAREA: Investigación documental (no perfiles el CSV salvo para comprobar algo puntual). Usa WebFetch/WebSearch (cárgalas con ToolSearch si hace falta).
1. Metadatos oficiales del dataset: la API Socrata expone descripciones de columnas en https://analisi.transparenciacatalunya.cat/api/views/rk5x-gny6.json (y la página about_data). Extrae la descripción oficial de cada una de las 32 columnas, en especial el significado de los sufijos: _CL, _EE, _CO, _CE, _NC, _EFM, _CR, PMED_COMP1/2/3. Propón un nombre legible en castellano para cada campo (materia y subcompetencia).
2. Qué representa ANY (año de la prueba en mayo / curso escolar).
3. Por qué no hay 2020 (fuente).
4. Reorganización de los servicios territoriales del Departament d'Educació: creación del Servei Territorial del Penedès, de Alt Pirineu i Aran como área propia, y de Barcelonès (y desaparición de Barcelona Comarques): año efectivo, de qué área(s) proceden las comarcas, con fuentes oficiales (DOGC, web educació gencat). Marca la confianza.
5. Niveles de logro que usa el Consell Superior d'Avaluació del Sistema Educatiu en la avaluació de 6è (nombres de los niveles, si publica puntos de corte en la escala 0-100 o no).
6. Valores oficiales publicados (resultados globales de Cataluña por competencia y año: medias o % por nivel) que puedan servir para contrastar KPIs; da URL exactas y cifras textuales.
Cita URL concretas para todo. Si algo no se encuentra, dilo explícitamente: no inventes.`, { label: 'investigacion-metadatos', phase: 'Perfilado', schema: RESEARCH })

const profiled = pipeline(
  PROFILERS,
  p => agent(p.prompt, { label: `perfil:${p.key}`, phase: 'Perfilado', schema: FINDINGS }),
  (res, p) => {
    if (!res) return null
    return agent(`${CTX}

TAREA: Eres un verificador escéptico e independiente. Otro agente ha perfilado el dataset (${p.key}) y afirma los hallazgos siguientes. Para CADA hallazgo, re-ejecuta TÚ una consulta independiente (escríbela de nuevo, no reutilices su script; guarda tus consultas en /home/kiara-rodriguez-uribe/Uni/TFG_Project/validacion/perfilado/verificacion_${p.key}.py) y decide si las cifras clave se reproducen exactamente. Evalúa además si la regla de limpieza propuesta es correcta y segura (¿podría mapear mal algún valor? ¿pierde filas?). Busca también problemas relevantes que se le hayan escapado en su ámbito.

HALLAZGOS A VERIFICAR (JSON):
${JSON.stringify(res.findings, null, 1)}`, { label: `verificar:${p.key}`, phase: 'Verificación', schema: VERIFY }).then(v => ({ key: p.key, profile: res, verify: v }))
  },
)

const [research, profiles] = await Promise.all([researchP, profiled])
const ok = (profiles || []).filter(Boolean)
log(`Perfiles completados: ${ok.length}/2; investigación: ${research ? 'ok' : 'fallida'}`)

phase('Síntesis')
const RULES = {
  type: 'object',
  properties: {
    report_path: { type: 'string' },
    cleaning_rules: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'R01, R02...' },
          column: { type: 'string' },
          rule: { type: 'string', description: 'regla precisa: condición -> acción, con mapeos completos de valores' },
          rows_affected: { type: 'string' },
          based_on: { type: 'string', description: 'IDs de hallazgos' },
        },
        required: ['id', 'column', 'rule', 'rows_affected', 'based_on'],
      },
    },
    field_names_es: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string' }, materia: { type: 'string' }, subcompetencia: { type: 'string' }, es_global: { type: 'boolean' }, anios: { type: 'string' },
        },
        required: ['field', 'materia', 'subcompetencia', 'es_global', 'anios'],
      },
      description: 'las 24 columnas de puntuación',
    },
    proposed_levels: { type: 'string', description: 'umbrales de nivel de logro propuestos con justificación y % por nivel' },
    fact_rows_estimate: { type: 'string' },
    modeling_decisions: { type: 'array', items: { type: 'string' }, description: 'decisiones de modelado derivadas (p.ej. tratamiento de la ruptura territorial, edad teórica, IDs)' },
    open_questions: { type: 'array', items: { type: 'string' }, description: 'decisiones que debe validar la estudiante con sus directoras' },
  },
  required: ['report_path', 'cleaning_rules', 'field_names_es', 'proposed_levels', 'fact_rows_estimate', 'modeling_decisions', 'open_questions'],
}

const synth = await agent(`${CTX}

TAREA: Sintetiza la auditoría de calidad de datos (tarea T7 del TFG) a partir del material verificado de abajo. Usa SOLO cifras confirmadas por el verificador (si confirmed=false usa corrected_evidence). Si necesitas una cifra que falta, ejecútala tú con el venv.

1. Escribe el informe en /home/kiara-rodriguez-uribe/Uni/TFG_Project/Documentation/Docu_final/Docu_Parcial/01_Informe_calidad_datos.md (crea las carpetas). Castellano académico, apto para reutilizar en la memoria del TFG. Estructura sugerida: 1) Objetivo y alcance de la auditoría; 2) Descripción del dataset y fuente (con URL y metadatos oficiales); 3) Metodología (DuckDB/Python, scripts en validacion/perfilado/, verificación independiente); 4) Resultados por dimensión de calidad (completitud, validez, consistencia, unicidad, comparabilidad temporal) con tablas Markdown de cifras clave; 5) Reglas de limpieza R01..Rnn (tabla: columna, problema, regla, filas afectadas); 6) Decisiones de modelado derivadas; 7) Limitaciones y cuestiones abiertas para validar con las directoras. Cita las fuentes oficiales con URL. No exageres ni inventes.
2. Devuelve las reglas de limpieza, los nombres legibles de los 24 campos de puntuación, los umbrales de nivel propuestos, la estimación de filas de FactPuntuacion, las decisiones de modelado y las cuestiones abiertas.

MATERIAL VERIFICADO:
${JSON.stringify(ok.map(o => ({ ambito: o.key, script: o.profile.script_path, hallazgos: o.profile.findings, tablas: o.profile.summary_tables_md, verificacion: o.verify })), null, 1)}

INVESTIGACIÓN DOCUMENTAL:
${JSON.stringify(research, null, 1)}`, { label: 'sintesis-informe', phase: 'Síntesis', schema: RULES })

return { synth, research, profiles: ok.map(o => ({ key: o.key, n_findings: o.profile.findings.length, unconfirmed: (o.verify?.checks || []).filter(c => !c.confirmed).map(c => c.id), missed: o.verify?.missed || [] })) }
