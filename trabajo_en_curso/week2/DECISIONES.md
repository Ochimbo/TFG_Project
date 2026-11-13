# Decisiones de la Week_2

Registro de los problemas detectados, las decisiones tomadas y su justificación. Formato en `GUIA_AGENTES.md`.

## Nombres

Fijados por la issue #12 (decisión D-E01). Son vinculantes para toda la memoria: un concepto, un nombre, y se
define en un solo apartado; los demás lo referencian.

### Glosario

| Concepto | Nombre único | Dónde se define | No usar |
|---|---|---|---|
| Diagrama de clases UML del dominio, independiente de la herramienta. Es el diseño conceptual de la base de datos | modelo conceptual | 7.2 (`sec:modelo_conceptual`) | «diseño conceptual» como título o apartado del capítulo 8, «modelo de dominio», «modelo de datos» |
| Condiciones que el diagrama no expresa (RI1–RI7); RI2, RI3 y RI5 también en OCL | restricciones de integridad | 7.2.1 (`sec:restricciones`, `tab:restricciones`) | «reglas de integridad», «restricciones textuales» |
| Modelo de la base de datos del sistema: tablas de hechos y dimensiones que se cargan en Power BI | modelo dimensional | 8.1 (`sec:modelo_dimensional`) | «modelo en estrella», «modelo de datos», «modelo lógico», «almacén de datos» |
| Paso que traduce el modelo conceptual a tablas | diseño lógico | 8.1.1 (`sec:diseno_logico`) | «diseño conceptual», «modelo lógico» |
| Forma del modelo dimensional (hechos en el centro y dimensiones alrededor) y la figura que la dibuja («diagrama en estrella» de la issue #11) | esquema en estrella | 8.1.1 (`sec:diseno_logico`) | «modelo en estrella», «diagrama de estrella» como concepto distinto |
| El modelo dimensional ya implementado en Power BI (carpeta `.SemanticModel`) | modelo semántico | 8.1.4 y 8.5 | «modelo» a secas cuando pueda confundirse con el conceptual |
| Tabla con una fila por hecho medido | tabla de hechos | 8.1.2 (`sec:tablas_hechos`) | «tabla de medidas», «fact» |
| Nivel de detalle de una tabla de hechos | granularidad | 8.1.2 | «grano» |
| Tabla de contexto de análisis | dimensión | 8.1.3 (`sec:dimensiones`) | «tabla de dimensiones» como título |
| Etapas del sistema y recorrido de los datos (fuente, ETL, modelo dimensional, lógica analítica, interfaz) | arquitectura general | 7.3 (`sec:arquitectura`); no se mueve (issue #14) | «arquitectura del sistema» como apartado del capítulo 8 |
| Carpetas y ficheros del repositorio y control de versiones | organización del repositorio | 8.5 (`sec:organizacion_proyecto`) | «organización del proyecto», «arquitectura» |
| Etapa que lee, comprueba, limpia y carga los datos (Power Query) | ETL | etapa en 7.3; diseño en 8.2 (`sec:diseno_etl`) | «proceso de carga», «integración» como nombre de la etapa |
| Reglas R01–R34 de la auditoría que aplica la ETL | reglas de limpieza | 8.2.2 (`sec:reglas_limpieza`); el verbo «depurar» (CU01) designa su aplicación | «reglas de validación», «saneamiento», «normalización» |
| Comprobación del sistema ya construido | validación | 4.3 (`sec:validacion`); la «validación independiente» en Python, en 7.3 | «validación» para las comprobaciones de la ETL (son «comprobaciones») |
| Medidas DAX que calculan KPIs, semáforos y regla de las 30 puntuaciones | lógica analítica | etapa en 7.3; diseño en 8.3 (`sec:diseno_dax`) | «capa semántica», «capa de cálculo» |
| Cada uno de los 12 indicadores K01–K12 del catálogo | KPI (en prosa también «indicador») | 3.3 (`sec:kpis`); fichas en 8.3.1 | «métrica»; «medida» se reserva para la expresión DAX |
| Lo que ve y maneja el usuario: el informe de Power BI con sus tres paneles | interfaz | prototipo en 3.5; etapa en 7.3; diseño en 8.4 (`sec:diseno_interfaz`) | «presentación», «capa de presentación», «front-end» |
| Cada una de las tres páginas del informe (E, T, O) | panel | 3.5 y 8.4.2 | «dashboard», «página», «vista» |
| Bocetos de los paneles previos al diseño | prototipo (de la interfaz) | 3.5 (`sec:mockups`) | «bocetos» en títulos |
| Valor medible que debe cumplir un requisito no funcional | criterio de aceptación | 3.4.3 (`tab:rnf`) y fichas de 7.4 | «criterio de verificación» |
| Ficha de cinco campos de cada RNF | ficha Volere | 7.4 (`sec:rnf_volere`) | «tarjeta», «plantilla» para una ficha concreta |

### Títulos y labels definitivos de los capítulos 7 y 8

```
7   Especificación                                        cap:especificacion
7.1   Modelo de casos de uso                              sec:casos_uso
7.1.1   Descripción de los casos de uso                   (sin label; fichas tab:cu01..tab:cu10)
7.2   Modelo conceptual                                   sec:modelo_conceptual
7.2.1   Restricciones de integridad                       sec:restricciones (tab:restricciones)
7.3   Arquitectura general                                sec:arquitectura
7.4   Especificación de los requisitos no funcionales     sec:rnf_volere (fichas tab:rnf01..tab:rnf11)
7.5   Historias de usuario                                sec:historias
8   Diseño                                                cap:diseno
8.1   Diseño del modelo dimensional                       sec:modelo_dimensional
8.1.1   Diseño lógico: esquema en estrella                sec:diseno_logico
8.1.2   Tablas de hechos                                  sec:tablas_hechos
8.1.3   Dimensiones                                       sec:dimensiones
8.1.4   Diccionario de datos                              sec:diccionario_datos
8.2   Diseño de la ETL                                    sec:diseno_etl
8.2.1   Flujo de consultas                                sec:flujo_consultas
8.2.2   Reglas de limpieza                                sec:reglas_limpieza
8.3   Diseño de la lógica analítica                       sec:diseno_dax
8.3.1   Fichas de los KPIs                                sec:fichas_kpis
8.3.2   Semáforos y referencias                           sec:semaforos
8.4   Diseño de la interfaz                               sec:diseno_interfaz
8.4.1   Estructura común y navegación                     sec:estructura_comun
8.4.2   Diseño final de los paneles                       sec:paneles
8.5   Organización del repositorio                        sec:organizacion_proyecto
```

El capítulo 8 no tiene apartado de diseño conceptual: el 8.1 empieza remitiendo al modelo conceptual (7.2) y lo
traduce en el 8.1.1. Los labels que ya existían no cambian; los de los subapartados son nuevos.

## Decisiones


## D-E01 Nombres y títulos de los capítulos 7 y 8 (issue #12)
- Problema: los capítulos 7 y 8 nombraban lo mismo de varias maneras: «modelo en estrella» (7.2, 7.3 y figura de la arquitectura), «esquema en estrella» (comentario del 8.1) y «modelo dimensional» (título del 8.1, SO3, T10); «Presentación» (etapa del 7.3) e «interfaz» (3.5 y 8.4); «Lógica analítica» como etapa del 7.3 y como título idéntico del 8.3; «Organización del proyecto» (8.5), que se confunde con la arquitectura general (7.3) y con la gestión del proyecto; «Reglas de limpieza y validación» (8.2.2) frente a «Métodos de validación» (4.3). Además, la issue #11 pide en el capítulo 8 un «diseño conceptual», que es lo mismo que el «Modelo conceptual» del 7.2.
- Opciones: (a) repetir en el 8.1 un apartado «Diseño conceptual»; (b) mover el modelo conceptual al capítulo 8; (c) dejar el modelo conceptual en el 7.2 como único diseño conceptual y hacer que el 8.1 remita a él y empiece en el diseño lógico.
- Decisión: opción (c). Glosario y títulos de la sección «Nombres». Cambios de título: 8.1 «Diseño del modelo dimensional» (antes «Modelo dimensional»), 8.1.1 nuevo «Diseño lógico: esquema en estrella», 8.1.2 «Tablas de hechos» (antes «Granularidad y tablas de hechos»), 8.2.2 «Reglas de limpieza», 8.3 «Diseño de la lógica analítica», 8.5 «Organización del repositorio». En el 7.3 las etapas pasan a llamarse «Modelo dimensional» e «Interfaz». Los labels existentes se conservan.
- Justificación: en el ciclo de Kimball que sigue la memoria (4.1) el modelo conceptual pertenece a la especificación y el diseño empieza al traducirlo a tablas; repetirlo en el capítulo 8 es justo el sinónimo que las directoras piden evitar. «Modelo dimensional» es el nombre que ya usan SO3 y la tarea T10 («Diseño del modelo dimensional») en capítulos que no se tocan, así que se mantiene, y «esquema en estrella» queda para su forma y su figura. Los apartados 8.1–8.4 se llaman «Diseño de» seguido del nombre de la etapa del 7.3, de modo que cada etapa se presenta una vez (7.3) y se diseña una vez (8.x). «Interfaz» ya es el nombre del 3.5 y del RNF04.
- Cambios aplicados: `main.tex` (7.2, 7.3, estructura y comentarios guía del capítulo 8), `gen_arquitectura.py` y `arquitectura.png` (rótulos «Modelo dimensional», «Interfaz» y «Lectura y comprobación»; ruta de la fuente Lato válida en Linux y Windows). El 7.3 no se mueve (issue #14).

## D-E02 Ubicación y formato de las fichas Volere (issue #10)
- Problema: las fichas de los RNF deben ir «en el capítulo 7», que no tenía apartado para ellas, y la tabla resumen del 3.4.3 llamaba «criterio de verificación» a lo que la ficha llama «criterio de aceptación».
- Opciones: (a) apartado 7.2, tras los casos de uso, renumerando 7.2–7.4; (b) apartado al final, 7.5; (c) apartado 7.4, entre la arquitectura general y las historias de usuario.
- Decisión: opción (c): nuevo 7.4 «Especificación de los requisitos no funcionales» (`sec:rnf_volere`); las historias de usuario pasan a 7.5. Una tabla `[H]` por ficha (`tab:rnf01`–`tab:rnf11`), con el mismo formato que las fichas de casos de uso. Campos: «Requisito de» (característica ISO/IEC 25010 y subcaracterística entre paréntesis), Descripción, Justificación, Criterio de aceptación y Método de evaluación; el identificador y un nombre corto van en la cabecera. La columna del 3.4.3 pasa a llamarse «Criterio de aceptación» y el 3.4.3 remite al 7.4.
- Justificación: las notas de la reunión y la issue #14 citan «7.2» y «7.3» por su número, así que no se renumeran; las historias de usuario cierran el capítulo porque «traducen todo lo anterior al backlog» y ya citan RNF03 y RNF09. Referencia de la plantilla comprobada en la web: S. Robertson y J. Robertson, *Mastering the Requirements Process: Getting Requirements Right*, 3.ª ed., Addison-Wesley, 2012, ISBN 978-0-321-81574-3.
- Cambios aplicados: `main.tex` (3.4.3, introducción del capítulo 7, nuevo 7.4), `bibliografia.bib` (`robertson2012mastering`).

## D-E03 Criterios y métodos de las fichas Volere que la memoria no fijaba (issue #10)
- Problema: la tabla del 3.4.3 fija los umbrales (3 s, SUS ≥ 68, 1280 × 720, contraste 4,5:1, 0,5 puntos), pero no cómo se mide cada uno ni las subcaracterísticas ISO/IEC 25010.
- Opciones: (a) copiar el criterio de la tabla sin concretar el método; (b) concretar el método con las herramientas que el proyecto ya tiene, sin cambiar ningún umbral.
- Decisión: opción (b). No se crea ni se cambia ningún umbral. Se concreta: RNF01, batería de interacciones (cada filtro y cada cambio de panel en los tres paneles), tres repeticiones, peor tiempo, analizador de rendimiento y DAX Studio; RNF02, al menos 5 participantes (como el 4.3); RNF03, comprobación de tamaño y posición en los ficheros del informe e inspección en Power BI Desktop; RNF04, los nombres de las competencias son la traducción al castellano de los oficiales y los de las áreas se mantienen como en la fuente; RNF05, razón de contraste con la fórmula de WCAG 2.1 y simulación de deuteranopía y protanopía; RNF06, validación independiente (`validacion/kpis_referencia.py`, `contraste_oficial.csv`); RNF07, informe de calidad y `validacion/test_modelo.py`; RNF08, inspección de las columnas del modelo (el código de alumno no se carga) y de los elementos visuales; RNF09, carga en dos pasos (fichero sin la última convocatoria y fichero completo); RNF10, inspección del repositorio (sin `.pbix`); RNF11, prueba en un equipo sin cuenta de Power BI. Subcaracterísticas: RNF01 comportamiento temporal; RNF02 capacidad de aprendizaje y operabilidad; RNF03 operabilidad; RNF04 capacidad para reconocer su adecuación; RNF05 accesibilidad; RNF06 y RNF07 corrección funcional; RNF08 confidencialidad; RNF09 capacidad para ser modificado; RNF10 analizabilidad; RNF11 capacidad para ser instalado.
- Justificación: un criterio de aceptación Volere (*fit criterion*) debe poder medirse, y el método debe poder ejecutarse con lo que hay (Power BI Desktop, `validacion/`). Evidencia para RNF06: `validacion/resultados/contraste_oficial.csv` tiene 72 comparaciones y la diferencia máxima es de 0,30 puntos, así que el umbral de 0,5 de la memoria se cumple sin excepciones. Las características de cada requisito son las de la tabla del 3.4.3, que no se reclasifica.
- Cambios aplicados: `main.tex` (7.4). Pendiente en la memoria: los resultados de estas evaluaciones irán en el capítulo de validación cuando se ejecuten; las fichas solo fijan el método.

## D-E04 Restricciones que se formalizan en OCL y convención de nombres (issue #9)
- Problema: hay que escribir en OCL solo las restricciones principales del modelo conceptual, el diagrama no tiene nombres de rol y sus identificadores llevan tilde y «ñ».
- Opciones: (a) formalizar todas; (b) formalizar las que relacionan varias clases (RI2, RI3 y RI5) y dejar en lenguaje natural claves, intervalos y rangos (RI1, RI4, RI6 y RI7); (c) añadir nombres de rol al diagrama o quitar las tildes de los identificadores.
- Decisión: opción (b). Cuatro invariantes: `elementoVigente` (RI2), `nivelSoloEnCompetencias` y `nivelSegúnValor` (RI3) y `sinPruebaSinEvaluaciones` (RI5). No se añaden roles al diagrama: se navega con el nombre de la clase de destino con la inicial en minúscula (`self.evaluación`, `self.elementoEvaluado`, `self.nivelDeLogro`, `self.convocatoria`). Los identificadores conservan las tildes del diagrama. El código va en `verbatim` con `\small` e interlineado 1,0.
- Justificación: RI2, RI3 y RI5 son las que el lenguaje natural deja más abiertas (navegan por asociaciones y por la clase asociativa) y las que la ETL y `validacion/test_modelo.py` comprueban sobre los hechos; RI1, RI4, RI6 y RI7 son claves y rangos que en OCL serían `isUnique` y comparaciones triviales. La navegación con el nombre de la clase en minúscula cuando falta el rol, también hacia la clase asociativa y desde ella a sus extremos, es la regla de OCL 2.4 (OMG, formal/14-02-03), cuya gramática admite letras acentuadas en los identificadores. `verbatim` sale bien en el PDF (Tectonic) y Pandoc lo convierte en un bloque de código del .docx.
- Cambios aplicados: `main.tex` (nuevo 7.2.1 «Restricciones de integridad»), `bibliografia.bib` (`omg_ocl24`).

## D-E05 Errores del modelo conceptual detectados al formalizarlo (issue #9)
- Problema: (1) en el diagrama, `valor: Real [0..100]` usaba la notación de multiplicidad de UML para expresar un rango de valores (leído literalmente, «de 0 a 100 valores reales»), y el rango no figuraba en ninguna RI. (2) RI3 dice que el nivel es «el único cuyo intervalo contiene el valor», pero RI4 no decía si los límites se incluyen, y con intervalos cerrados 55, 70 y 85 pertenecerían a dos niveles.
- Opciones: (a) dejarlo; (b) corregir el atributo, añadir el rango como restricción y precisar los límites en RI4.
- Decisión: opción (b). El atributo pasa a `valor: Real` y se añade RI7 «El valor de una puntuación está entre 0 y 100». RI4 precisa que cada intervalo incluye su límite inferior y excluye el superior, salvo el del nivel más alto, que incluye el 100.
- Justificación: en UML los corchetes tras el tipo son la multiplicidad del atributo. Los límites son los de la implementación (contrato de diseño §3, DimNivelLogro: <55, [55,70), [70,85), >=85) y la regla R02 de la ETL ya detiene la carga con puntuaciones fuera de [0,100].
- Cambios aplicados: `gen_modelo_conceptual.py` (atributo y ruta de Lato válida en Linux y Windows), `modelo_conceptual.png` regenerado, `main.tex` (Tabla de restricciones: RI4 y RI7).

<!-- D-01 a D-19: agente de datos e implementación. Decididas el 10/11/2026 y aplicadas el 11-12/11/2026 (PROGRESO_datos.md).
     Los apartados «Cambios aplicados» describen lo que realmente hay en el repositorio tras la aplicación. -->

## D-01 Tolerancia del contraste con las medias oficiales: 0,5 (requisito) y 0,2 (alerta interna)
- Problema: la memoria fija una tolerancia de 0,5 puntos (RNF06 en la tabla de requisitos no funcionales; Sección 4.3; HU01) y la validación usa ±0,2 (`validacion/kpis_referencia.py`, `test_modelo.py`, `03_Fichas_KPI.md` §5.2, `04_Guia_de_uso.md`). Con ±0,2 hay dos combinaciones «fuera de tolerancia» (inglés 2016, +0,24; francés 2024, +0,30) que sí cumplen el requisito.
- Opciones: (a) bajar el requisito a 0,2 y aceptar dos incumplimientos; (b) subir la validación a 0,5 y perder sensibilidad; (c) mantener los dos umbrales con nombres distintos.
- Decisión: (c). El criterio de aceptación de RNF06 es 0,5 puntos. El umbral de 0,2 se conserva como alerta interna: toda diferencia mayor que 0,2 debe estar explicada en el informe de calidad (§4.6).
- Justificación: las medias oficiales se publican con un decimal y el CSV no contiene exactamente la misma población (diferencias de n de 41 a 1.024 alumnos, informe §4.6), así que 0,5 es un criterio de aceptación razonable y ya revisado por las directoras. El umbral de 0,2 detecta antes un error de carga: fue el que obligó a investigar inglés 2016 y francés 2024. Resultado real: 72 de 72 combinaciones dentro de 0,5 (máximo 0,30); 70 de 72 dentro de 0,2.
- Cambios aplicados: `validacion/kpis_referencia.py` (`TOLERANCIA_RNF06 = 0.5`, columna `dentro_RNF06` en `contraste_oficial.csv`; `dentro_tolerancia` sigue siendo la alerta de 0,2), `validacion/test_modelo.py` (`test_criterio_aceptacion_rnf06`: 72 de 72 dentro de 0,5, máximo 0,30; el test de 0,2 se mantiene y exige explicación en §4.6), `validacion/README.md`, `01_Informe_calidad_datos.md` §4.6, `02_Modelo_y_diccionario.md` §7.4, `03_Fichas_KPI.md` §5.2, `04_Guia_de_uso.md` §3.2 y §8, `contrato_diseno.md` §6.
- Pendiente en la memoria: ninguno obligatorio. En el capítulo 8 o en la validación conviene decir: «El criterio de aceptación es de 0,5 puntos (RNF06). La validación usa además un umbral de alerta de 0,2: 70 de las 72 medias quedan dentro, y las dos restantes (inglés 2016, +0,24; francés 2024, +0,30) están explicadas en el informe de calidad».

## D-02 Textos desfasados sobre las dos medias fuera de ±0,2
- Problema: `02_Modelo_y_diccionario.md` §7.4, `03_Fichas_KPI.md` §5.2, `04_Guia_de_uso.md` §8 y `validacion/README.md` dicen que inglés 2016 y francés 2024 están «pendientes de documentar en §4.6», pero `01_Informe_calidad_datos.md` §4.6 ya las documenta y `contraste_oficial.csv` las marca como «esperada fuera de tolerancia (informe §4.6)».
- Opciones: (a) dejarlo; (b) actualizar los cuatro textos.
- Decisión: (b).
- Justificación: el informe de calidad es la fuente; los demás documentos deben remitir a él y no contradecirlo.
- Cambios aplicados: los cuatro ficheros citados. Queda abierto solo lo que el propio §4.6 reconoce: contrastar la n oficial de inglés 2016 y francés 2024 en los Quaderns.

## D-03 Reglas del informe de calidad que la ETL aplica de otra forma (R01, R02, R09, R10, R34)
- Problema: `01_Informe_calidad_datos.md` §5 propone cosas que la ETL implementada (`m_stg.m`) hace distinto: R01 define `EvaluacionID` como número de línea (2…1.102.325) y el modelo usa la posición 1…N; R02 pide validar el patrón `ddd,dd` y el M solo convierte con es-ES y comprueba el rango; R09 y R10 mandan los valores no previstos a «Desconocido» y el M detiene la carga; R34 exige 1.102.324 filas fijas y pruebas de regresión de R03/R04 en la carga, que el M no hace.
- Opciones: (a) cambiar el M para que siga el informe al pie de la letra; (b) mantener el M y dejar constancia en el informe de cómo se aplica cada regla y por qué.
- Decisión: (b), sin tocar `m_stg.m`.
- Justificación: R01: posición = línea − 1; es la misma clave y no depende de la cabecera. R09/R10: detener la carga cumple RF05 y HU14 (un código nuevo no debe pasar inadvertido); hoy hay 0 casos. R34: un número fijo de filas contradice RNF09 y HU13 (incorporar una convocatoria sin rediseñar); el recuento y las regresiones de R03/R04 se comprueban en `validacion/test_modelo.py`. R02: con cultura es-ES, un valor con punto se lee como miles y queda fuera de [0, 100] («87.70» → 8770), así que la carga falla igual; solo pasaría un valor con punto y un único decimal («8.7» → 87), caso que no existe (0 valores con punto, comprobado sobre `Datos.csv`) y que la réplica Python sí rechaza con el patrón estricto. Añadir la comprobación de patrón al M supone unos 26 millones de operaciones de texto más en una actualización que ya relee el CSV tres veces, sin poder medirlo todavía en Power BI Desktop.
- Cambios aplicados: nota «Cómo aplica la ETL estas reglas» al final de `01_Informe_calidad_datos.md` §5.
- Pendiente en la memoria: en el 8.2.2 (reglas de limpieza y validación) decir que la carga se detiene ante una cabecera, un código o una puntuación no previstos (RF05) y que el recuento por convocatoria se comprueba en la validación independiente, no en la carga.

## D-04 El modelo propuesto en el informe de calidad (§6) no es el modelo implementado
- Problema: `01_Informe_calidad_datos.md` §6.1–6.2 describe la propuesta previa a la construcción: `FactPuntuacion` con `EvaluacionID` y cinco indicadores, `FactEvaluacion` con ocho indicadores y `CodiAlumne`, dimensiones con las combinaciones observadas (86 y 169 filas), nombres `IdCompetencia`, `IdNivelLogro`, `FlagValida`… El modelo real (TMDL, `02_Modelo_y_diccionario.md`) tiene claves `…Key`, dimensiones estáticas de 120 y 182 filas, una máscara `CalidadKey` y no carga `CODI_ALUMNE`.
- Opciones: (a) reescribir el §6 del informe; (b) conservarlo como propuesta de la auditoría y añadir una nota que remita al modelo definitivo y liste las diferencias.
- Decisión: (b).
- Justificación: el informe es el entregable de la tarea T7 y refleja lo que se sabía entonces; reescribirlo borraría la trazabilidad. La fuente única del modelo definitivo es `02_Modelo_y_diccionario.md` y la sección «Datos para el capítulo 8» de este fichero.
- Cambios aplicados: nota al inicio de `01_Informe_calidad_datos.md` §6 con la tabla de diferencias.
- Pendiente en la memoria: el capítulo 8 debe describir el modelo implementado (120 y 182 filas, máscara de calidad), no el del informe §6.

## D-05 «Barcelona Comarques» de 2024 se muestra como «Barcelonès»
- Problema: el CSV llama «Barcelona Comarques» al área en 2024 y «Barcelonès» en 2025, con el mismo perímetro. El modelo conservaba el texto del CSV en `AreaTerritorial` (códigos 3 y 4 con el mismo nombre) y solo `AreaPerimetro2025` las unía. Consecuencias: el Barcelonès no tenía variación interanual (K10) en 2025 aunque su perímetro no cambió (`03_Fichas_KPI.md`, K10), un mismo nombre designaba dos perímetros distintos (hasta 2023 y 2024), y el nombre de 2024 no coincidía con el del informe oficial de ese año.
- Opciones: (a) dejar el texto del CSV; (b) usar `AreaPerimetro2025` en los segmentadores; (c) asignar «Barcelonès» a `AreaTerritorial` del código 4.
- Decisión: (c). `AreaTerritorial` = «Barcelonès» para 2024 y 2025 (códigos 4 y 5) y «Barcelona Comarques» solo hasta 2023 (código 3). `AreaOrden` del código 4 pasa a 5.
- Justificación: evidencia de `Datos.csv` (`analisis/evidencia_cuestiones_abiertas.py`): Barcelona Comarques 2024 tiene 5.386 alumnos y Barcelonès 2025, 5.408, con la misma composición (pública 3.166 y 3.182; privada 2.220 y 2.226; ningún alumno en municipios de hasta 10.000 habitantes en los dos años, frente a 660 en 2023). El informe de calidad §4.5 recoge además que el Quadern 62 ya publica el área de 2024 como «Barcelonès» con la misma n, y que el Decret 120/2023 está operativo desde octubre de 2023. Con el cambio se cumple RNF04 (nombres de los informes oficiales) y K10 por área funciona en 2025. No cambia ninguna cifra de Cataluña ni de 2025 por área; solo aparecen K10 y `Estado K10` del Barcelonès en 2025, antes en blanco.
- Cambios aplicados: `generadores/modelo/m_DimContextoCentro.m` (código 4 → «Barcelonès», `AreaOrden` 5) y `gen_modelo.py` (descripciones de `AreaCodigo`, `AreaTerritorial`, `AreaOrden`), `PowerBI/` regenerado, `validacion/etl_referencia.py`, `validacion/test_modelo.py` (`test_area_barcelona_comarques_por_anio` comprueba nombres, órdenes y años por nombre), `herramientas/verificar_claves.py` (misma regla de `AreaOrden`), `contrato_diseno.md` §3 y §5.1, `02_Modelo_y_diccionario.md` §4.4, §5.2 y §7.3, `03_Fichas_KPI.md` (K07, K10), `04_Guia_de_uso.md` §4.2. En `validacion/resultados/semaforos_2025.csv` el Barcelonès pasa a tener K10 (catalán −1,03, castellano +2,20, matemáticas −4,05, inglés +1,76, ciencias −8,27) y `Estado K10`; `kpi_area_2025.csv` no cambia. Pendiente de comprobar en Power BI Desktop.
- Pendiente en la memoria: ninguno en los capítulos 3 y 7. En el capítulo 8, la tabla de áreas debe decir que el área de 2024 se muestra como «Barcelonès» y por qué.

## D-06 Girona se queda como serie propia (cuestión abierta 4 del informe de calidad)
- Problema: la Cerdanya, antes repartida entre Girona y Lleida, pasa en 2024 a Alt Pirineu i Aran. El informe de calidad §7.2 (4) pregunta si Girona debe entrar en el grupo «Lleida + Alt Pirineu i Aran» y si el grupo grande de Barcelona (27 % de Cataluña) sirve para los KPIs temporales.
- Opciones: (a) fusionar Girona con Lleida y Alt Pirineu i Aran; (b) dejar Girona sola, con nota; (c) limitar los KPIs temporales por área a las áreas estables.
- Decisión: (b) para Girona, y se mantienen los dos grupos de `AreaSerieComparable` para las áreas que cambian de perímetro. La nota de Girona se añade al diccionario y a la ficha de K10.
- Justificación: cifras de `Datos.csv`: de 2023 a 2024 las áreas estables sin Girona pasan de 41.346 a 39.721 alumnos (factor 0,9607). Con ese factor, a Lleida le faltan unos 440 alumnos y Alt Pirineu i Aran tiene 514: la aportación de Girona es de unos 75–90 alumnos, en torno al 1 % de los 7.758 de Girona en 2023. La caída de Girona (factor 0,9388) queda dentro de lo que varían otras áreas estables (Vallès Occidental 0,9409; Terres de l'Ebre 0,9441), así que el efecto no se distingue del ruido. Aunque esos alumnos puntuaran 10 puntos por encima o por debajo de la media de Girona, la media del área cambiaría como mucho 0,1–0,2 puntos, menos que el umbral del semáforo (0,5). Fusionar Girona (7.283 alumnos en 2024) con Lleida y Alt Pirineu (3.980) crearía un grupo dominado por Girona y dejaría a las dos sin serie propia, para corregir un efecto de décimas. El grupo de Barcelona se mantiene porque es la única agrupación con perímetro constante (20.261, 19.395 y 19.148 alumnos en 2023–2025, con los mismos factores que las áreas estables).
- Cambios aplicados: `02_Modelo_y_diccionario.md` §7.3, `03_Fichas_KPI.md` (K10), `01_Informe_calidad_datos.md` §7.2. Sin cambios en el modelo.
- Pendiente en la memoria: en el capítulo 8 (dimensiones), una frase: «Girona pierde en 2024 la parte de la Cerdanya que pasa a Alt Pirineu i Aran (alrededor del 1 % de su alumnado); se mantiene como serie propia porque el efecto sobre su media es de una o dos décimas como máximo».

## D-07 Pesos de ciencias: se documenta la discrepancia y la global no se recalcula (cuestión abierta 8)
- Problema: el Quadern 68 publica para ciencias los pesos 42 % / 25 % / 33 % (informe de calidad §4.3), pero la puntuación global del CSV es la media simple de las tres subcompetencias.
- Opciones: (a) recalcular la global con los pesos oficiales; (b) cargar la global publicada y documentar la discrepancia; y, aparte, comunicarla o no al titular del dataset.
- Decisión: (b). La global nunca se recalcula. Se recomienda comunicar la incidencia al titular a través del portal, junto con las otras tres incidencias objetivas (rotación de castellano 2017, rotación de francés 2016 y texto de `HÀBITAT` de 2024); es una acción de la estudiante, no del sistema, y no condiciona el TFG.
- Justificación: recalculado sobre `Datos.csv`: la media simple reproduce la global en el 100 % de las filas de las siete convocatorias (2018–2025, 496.745 filas con las cuatro puntuaciones), con una diferencia máxima de 0,01; los pesos 42/25/33 solo la reproducen en el 4,7 %–8,7 % (error medio de 1,32 a 1,62 puntos) y ninguna permutación de esos pesos pasa del 9 %. Con los pesos oficiales la media anual de Cataluña cambiaría entre −0,55 y +1,06 puntos y dejaría de coincidir con la media oficial publicada (2018: 70,20 con la global del CSV, oficial 70,2; 71,14 con 42/25/33). Es decir, las medias oficiales también salen de la global publicada. Los KPIs usan la global (K01) o cada subcompetencia por separado (K02), así que ningún indicador depende de los pesos. La cita del Quadern 68 procede del informe de calidad; no se ha vuelto a abrir el PDF en esta revisión.
- Cambios aplicados: `01_Informe_calidad_datos.md` §7.2 (resolución) y `02_Modelo_y_diccionario.md` §7.4. Texto propuesto para el aviso al titular en la sección «Incidencias para comunicar al titular del dataset (D-07)», después de D-19.
- Pendiente en la memoria: en el capítulo 8 (reglas de limpieza), una frase: «La puntuación global se carga tal como se publica y no se recalcula. En ciencias, los pesos publicados (42/25/33) no reproducen la global del fichero, que es la media simple de las tres subcompetencias en el 100 % de los registros».

## D-08 Los cortes de nivel 55/70/85 quedan como definitivos (cuestión abierta 1)
- Problema: los cortes figuraban como «provisionales» en el modelo, el informe y los avisos, a la espera de las directoras.
- Opciones: 50/70/85; 55/70/85; cortes por materia y año calibrados con los informes.
- Decisión: 55/70/85 fijos, comunes a todas las materias y años, sobre la puntuación global. Se presentan como «niveles internos del TFG, no oficiales» y se retira la palabra «provisionales».
- Justificación: informe de calidad §6.3: cada corte cae dentro de la horquilla oficial (nivel mínimo entre 50 y 60, óptimo en 70, alto entre 80 y 90; Quadern 68, p. 9); frente a los % oficiales de 35 combinaciones materia-año (2018–2025), 55 da un error medio de 2,70 pp y un sesgo de −0,14 pp en el nivel bajo, frente a −4,39 pp con 50 y +5,22 pp con 60; la mediana de los cortes que reproducen exactamente los oficiales es 55,98 / 70,70 / 85,69. Los cortes calibrados por año solo existen para los años con informe y harían depender el modelo de una tabla externa que hay que mantener a mano (contra RNF09). Las convocatorias donde el corte fijo no es fiable se excluyen de K03 con `NivelNoComparable` (R28).
- Cambios aplicados: `m_DimNivelLogro.m`, `gen_modelo.py` (descripción), `gen_pbir.py` (aviso `AVISO_NIVELES`), `etl_referencia.py` (comentario), `PowerBI/` regenerado, `contrato_diseno.md` §3, `01_Informe_calidad_datos.md` §6.3 y §7.2, `02_Modelo_y_diccionario.md` §4.7 y §8.1, `04_Guia_de_uso.md` §4.
- Pendiente en la memoria: en 8.3 (ficha de K03 o semáforos y referencias), justificar los cortes con las tres cifras anteriores.

## D-09 Inglés 2015 y catalán 2018 se marcan y no se excluyen; criterio de «Censurada» (cuestión abierta 2)
- Problema: la cuestión abierta 2 pregunta si basta con marcar. Además, K06 (dispersión) excluye inglés 2015 pero no catalán 2018, cuando el informe §6.4 dice que la dispersión no es comparable en ninguno de los dos.
- Opciones: (a) excluir las dos convocatorias del CMI; (b) marcar y que cada KPI decida; dentro de (b), que K06 excluya también `NivelNoComparable`.
- Decisión: (b), sin cambiar K06. Criterio explícito: `Censurada` marca una columna-año cuya propia distribución tiene una masa de puntos en un suelo; K03 y K06 la excluyen. `NivelNoComparable` marca globales cuya distribución está comprimida o desplazada sin masa en un punto; solo K03 las excluye, y K06 las muestra con advertencia en la descripción.
- Justificación: evidencia de `Datos.csv`: en inglés 2015 el 12,9 % de las globales vale exactamente 48,79 (suelo; el percentil 1 es 48,79); en catalán 2018 la global no tiene ninguna masa (el valor más frecuente es 89,29, con el 0,86 %), solo la cola baja comprimida (percentil 1 en 37,59 frente a 28,18 en 2017 y 32,30 en 2019; desviación típica 13,01, la menor de la serie). Una desviación típica calculada sobre una masa artificial es un artefacto; la de catalán 2018 es la dispersión real de las puntuaciones publicadas. Excluir las convocatorias enteras rompería la conciliación con las medias oficiales (inglés 2015: 74,42 frente a 74,5).
- Cambios aplicados: `02_Modelo_y_diccionario.md` §7.2 y `03_Fichas_KPI.md` (K06), solo texto.
- Pendiente en la memoria: en la ficha de K06 del capítulo 8, recoger el criterio en una frase.

## D-10 El periodo de diseño de la global de inglés y francés empieza en 2017, no en 2016
- Problema: `DimCompetencia[PeriodoDisenoInicio]` valía 2016 para las globales de inglés y francés y 2017 para sus subcompetencias. Pero la misma auditoría marca la global de inglés 2016 como `NivelNoComparable` (R28) y sus subcompetencias CO y CE de 2016 como escala no comparable (R27). K10 comparaba 2017 con 2016 (+6,03 puntos) y K12 de 2017 valía 100 % con esa única materia.
- Opciones: (a) dejar 2016 «con nota»; (b) pasar a 2017.
- Decisión: (b), para `PANG` y `PFRAN`.
- Justificación: evidencia de `Datos.csv`: la global de inglés de 2016 tiene el máximo en 95,55 (100 en 2015 y 2017), solo un 4,35 % de puntuaciones de 95 o más (18,83 % en 2015 y 19,44 % en 2017) y 1.210 valores distintos, frente a 204–214 desde 2017 (salvo 2023, con 842). Una global calculada con subcompetencias de escala comprimida no es comparable con la del año siguiente; mantener 2016 era incoherente con R27 y R28. Efecto: K10 de 2017 queda en blanco para inglés y francés y, por tanto, también K12 de 2017 (antes 100 % con una sola materia); K11 de 2021 (ventana 2016–2021) queda en blanco. No cambia ninguna cifra desde 2018 en K10, ni desde 2022 en K11, ni el contraste con las medias oficiales.
- Cambios aplicados: `m_DimCompetencia.m`, `gen_modelo.py` (descripción de `PeriodoDisenoInicio`), `PowerBI/` regenerado, `validacion/etl_referencia.py`, `validacion/test_modelo.py` (`test_periodo_diseno_coherente_por_materia`), CSV de `validacion/resultados/` (K10 y K12 de 2017 y K11 de 2021 pasan a vacío; K10 existe desde 2018, K11 desde 2022, K12 desde 2018 con 50 %), `contrato_diseno.md` §5.2, `01_Informe_calidad_datos.md` §4.5, `02_Modelo_y_diccionario.md` §4.6, `03_Fichas_KPI.md` §2, K10, K11, K12. Pendiente de comprobar en Power BI Desktop.
- Pendiente en la memoria: ninguno en los capítulos 3 y 7. En la ficha de K10 del capítulo 8: periodos de diseño 2017 (matemáticas, inglés y francés) y 2018 (catalán, castellano y ciencias).

## D-11 Resto de cuestiones abiertas del informe de calidad: se confirman las opciones por defecto (3, 5, 6, 7, 9 y 10)
- Problema: las cuestiones 3 (2010), 5 (KPIs temporales sin equiparación), 6 (2021 frente a 2019), 7 (francés), 9 (grano de FactPuntuacion) y 10 (edad) seguían formalmente abiertas, con una opción por defecto aplicada.
- Opciones: las del informe §7.2 en cada caso.
- Decisión: se confirman. (3) Hábitat y edad de 2010 como «No fiable», sin imputar. (5) K10, K11 y K12 se mantienen con el aviso de no equiparación, el umbral de 1 punto en K12 y los periodos de diseño (D-10); no se añade puntuación estandarizada. (6) 2021 se compara con 2019 y el aviso de los paneles lo dice. (7) El francés se mantiene como informativo. (9) Se conservan las 17.728.085 puntuaciones con la máscara de calidad. (10) `EdadAnioNatural` y situación de edad por cohorte.
- Justificación: (3) el 12,22 % de las filas de 2010 tiene combinaciones área-hábitat imposibles y la diferencia de matemáticas entre 12 y 13 años es −0,05 puntos, frente a 10,37–16,86 en los otros años (informe §4.3): usar esos valores daría brechas falsas, y área, titularidad y género de 2010 sí son fiables. (5) El propio organismo evaluador advierte de que la comparación longitudinal es orientativa (Quadern 68, p. 8, citado en el informe §2.3); quitar los KPIs temporales dejaría sin respuesta las preguntas del perfil estratégico, y una puntuación z por año borra por construcción la evolución de Cataluña, que es lo que se pregunta. (6) Con `IndiceConvocatoria` la comparación es homogénea con el resto y el usuario ve la advertencia; romper la serie dejaría 2021 sin K10 ni K12. (7) Con 243–505 alumnos al año solo aporta el 0,1 % de las puntuaciones globales, queda fuera de K09 y K12 y la regla de las 30 puntuaciones oculta los segmentos pequeños; excluirlo rompería la conciliación de filas con el CSV. (9) Borrar `PANG_EE` 2015 (68.342 celdas) impediría conciliar con el fichero y no ahorra nada apreciable. (10) El fichero solo trae mes y año de nacimiento y no la fecha de la prueba, así que la «edad en la prueba» no se puede calcular con exactitud.
- Cambios aplicados: `gen_pbir.py` (el aviso añade «2021 se compara con 2019»), `01_Informe_calidad_datos.md` §7.2 (resolución de las diez cuestiones en una nota al inicio del apartado), `02_Modelo_y_diccionario.md` §8.1, `04_Guia_de_uso.md` §8, `ESTADO.md`.
- Pendiente en la memoria: ninguno; el capítulo 8 puede remitir a estas resoluciones.

## D-12 Semáforos: referencia de cada KPI, presentación y paneles en los que aparecen
- Problema: RF13 pide semáforo para los perfiles E, T y O; el mockup, CU02 y HU01 lo ponen en K01, K03 y K10 del panel estratégico, y CU03/CU07 en el táctico. En el informe solo había una tarjeta `Estado K01` en el operativo, que mostraba el número 1, 0 o −1; `Estado K03` y `Estado K10` no se usaban en ningún visual. Además, sin filtro de contexto `Estado K03` vale siempre 0 (Cataluña frente a sí misma) y `Estado K01` coincide con `Estado K10`.
- Opciones: (a) dejarlo y rebajar el requisito; (b) añadir un modo temporal a `Estado K03` para cubrir el panel estratégico; (c) mostrar cada semáforo donde su referencia tiene sentido, con las medidas actuales.
- Decisión: (c). Referencias: K01 y K03 se comparan con Cataluña cuando hay un contexto filtrado (±1 punto y ±2 pp); K10 se compara con 0 (±0,5 puntos); sin contexto, `Estado K01` usa K10. Panel estratégico: semáforo de K10 (tarjeta y columna de la tabla por competencia). Panel táctico: `Estado K01` y `Estado K03` del área seleccionada. Panel operativo: `Estado K01` y `Estado K03` del contexto. Presentación: las tres medidas siguen devolviendo 1, 0 o −1 y se muestran con la cadena de formato «▲ Favorable», «● Neutro», «▼ Desfavorable».
- Justificación: un semáforo temporal de K03 sería el indicador menos defendible del cuadro: las pruebas no están equiparadas y el % por debajo de un corte fijo oscila mucho con la dificultad de cada prueba (ciencias pasa del 13,2 % al 26,9 % de 2024 a 2025). En el panel estratégico no hay territorio de referencia, así que K03 no lleva semáforo y el de K01 sería el mismo que el de K10. El símbolo con palabra cumple RNF05 (no depende solo del color) y evita reglas de formato condicional, que no se pueden validar sin Power BI Desktop. No cambia ningún valor de `semaforos_2025.csv` por esta decisión.
- Cambios aplicados: `gen_medidas.py` (`FMT_SEMAFORO` en los tres `Estado`, descripciones; función `tmdl_value`, porque TOM exige escribir en TMDL una cadena con comillas como `"""▲ Favorable"";""▼ Desfavorable"";""● Neutro"""`: la forma sin escapar dio `InvalidValueFormat` en `tmdlcheck`), `gen_pbir.py` (tarjeta `Estado K10` y columna en la tabla del estratégico; tarjetas `Estado K01` y `Estado K03` en el táctico; tarjeta `Estado K03` y nuevo subtítulo de `Estado K01` en el operativo), `PowerBI/` regenerado (TOM lee el formato correctamente), `02_Modelo_y_diccionario.md` §4.9, `03_Fichas_KPI.md` §1.2, §1.4 y §4, `04_Guia_de_uso.md`, `contrato_diseno.md` §7–8. Pendiente de comprobar en Power BI Desktop que la tarjeta muestra «▲ Favorable» y no 1.
- Pendiente en la memoria: (1) Sección 3.5, panel estratégico, punto 2. Actual: «K01, K03 y K10 llevarán un semáforo que indica si el valor es favorable, neutro o desfavorable (RF13).» Propuesto: «K10 llevará un semáforo que indica si la variación es favorable, neutra o desfavorable (RF13). K01 y K03 lo llevan en los paneles táctico y operativo, donde se comparan con Cataluña.» (2) CU02, paso 2. Actual: «La puntuación media, el alumnado en nivel bajo y la variación llevan semáforo.» Propuesto: «La variación lleva semáforo.» (3) HU01, segundo criterio. Actual: «Cada tarjeta lleva un semáforo favorable, neutro o desfavorable.» Propuesto: «La variación respecto a la convocatoria anterior lleva un semáforo favorable, neutro o desfavorable.» (4) Sección 3.5, panel táctico, punto 2: añadir «y el estado del área frente a Cataluña en K01 y K03». (5) El mockup del estratégico (`gen_mockups.py`) dibuja semáforo en tres tarjetas: o se regenera o el 8.4.2 lo cita como cambio respecto al boceto.

## D-13 Distribución por nivel de logro con mínimo muestral y las mismas exclusiones que K03
- Problema: CU09 (1b) y RF14 piden dejar en blanco la distribución con menos de 30 puntuaciones, pero el gráfico de barras al 100 % usaba `Puntuaciones globales`, que no aplica el mínimo. Las exclusiones de calidad estaban en filtros del visual y no en una medida, así que nada garantizaba que el % de «Bajo» del gráfico coincidiera con K03. CU09 (1a) y HU11 hablan de puntuaciones «no válidas», pero ninguna global lo es (R25 solo afecta a `PANG_EE` 2015): lo que se excluye son las censuradas y las de nivel no comparable.
- Opciones: (a) cambiar solo el texto de la memoria; (b) medida nueva que cuente las puntuaciones por nivel con las exclusiones de K03 y el mínimo de 30 sobre el total de la competencia.
- Decisión: (b). Medida `Puntuaciones por nivel de logro` (carpeta «1. Rendimiento académico»), usada en el gráfico. El modelo pasa de 19 a 20 medidas.
- Justificación: con la medida, el tramo «Bajo» del gráfico es K03 por construcción y RF14 se cumple también en CU09. La réplica comprueba que la proporción de «Bajo» coincide con K03.
- Cambios aplicados: `gen_medidas.py` (medida nueva, lineageTag `58ea587f-4ba5-5009-8f0d-29ea7fd32148`), `gen_pbir.py` (el gráfico usa la medida; se quitan los dos filtros de calidad del visual y se conserva solo el que excluye «No aplica (subcompetencia)» de la leyenda, porque las globales nunca tienen nivel 0), `PowerBI/` regenerado, `validacion/kpis_referencia.py` (`Modelo.puntuaciones_por_nivel`, CSV nuevo `kpi_niveles_2025.csv`, 24 filas), `validacion/test_modelo.py` (`test_distribucion_por_nivel_coincide_con_k03`: el tramo Bajo coincide con K03 en todas las combinaciones año-materia con K03), `contrato_diseno.md` §7–8, `02_Modelo_y_diccionario.md` §4.9 y §7.2, `03_Fichas_KPI.md` (ficha nueva), `04_Guia_de_uso.md` §3.2 y §4.3. Pendiente de comprobar en Power BI Desktop.
- Pendiente en la memoria: (1) CU09, extensión 1a. Actual: «Hay puntuaciones marcadas como no válidas: no se cuentan en ningún nivel.» Propuesto: «Hay puntuaciones censuradas o de una convocatoria con niveles no comparables: no se cuentan en ningún nivel.» (2) HU11, segundo criterio. Actual: «Las puntuaciones marcadas como no válidas no se cuentan.» Propuesto: «Las puntuaciones censuradas o de convocatorias con niveles no comparables no se cuentan.» (3) RF12 dice «(E, O)», pero la distribución solo está en el panel operativo: cambiar el origen a «O» o citarlo en 8.4.2 como cambio respecto a los requisitos.

## D-14 2020 aparece como hueco en los gráficos de evolución
- Problema: la memoria (3.5, CU06, HU02) dice que 2020 aparece como un hueco señalado. Los gráficos de líneas usan el eje categórico `DimAnio[Anio]`, que omite las categorías sin datos: 2019 y 2021 quedaban contiguos y unidos por la línea.
- Opciones: (a) eje continuo (deja el espacio, pero une 2019 con 2021); (b) activar «mostrar elementos sin datos» en el eje, de modo que 2020 aparece como categoría vacía y la línea se corta.
- Decisión: (b), en los tres gráficos de líneas (`showAll` en la proyección del eje, propiedad del esquema oficial de PBIR).
- Justificación: es lo que describe la memoria y evita que una línea 2019–2021 sugiera una medida en 2020. `DimAnio` solo contiene 2009–2025, así que no aparecen otros años vacíos.
- Cambios aplicados: `gen_pbir.py` (`"showAll": true` en el objeto del rol `Category` de `line_chart`, propiedad `ProjectionState.showAll` de visualConfiguration 2.2.0, la que referencia visualContainer 2.4.0), informe regenerado y validado contra los esquemas (0 errores). Pendiente de comprobar en Power BI Desktop que la línea se interrumpe en 2020.
- Pendiente en la memoria: ninguno.

## D-15 Etiquetas de la interfaz («Competencia», «Titularidad») y filtro de género
- Problema: la memoria (RF06, mockups, casos de uso) habla de «competencia» y «titularidad»; el informe mostraba «Materia» y «Naturaleza». RF06 y CU05 incluyen el filtro por género y ningún panel tenía ese segmentador.
- Opciones: (a) renombrar las columnas del modelo; (b) cambiar solo los textos visibles del informe; para el género, (c) añadir un segmentador o (d) remitir al panel de filtros.
- Decisión: (b) y (c). Los títulos y etiquetas del informe dicen «Competencia» y «Titularidad»; las columnas `DimCompetencia[Materia]` y `DimContextoCentro[Naturaleza]` conservan su nombre técnico. Se añade un segmentador de género al panel táctico (el de equidad).
- Justificación: RNF04 pide los nombres de los informes oficiales, que hablan de competencias, y un concepto debe tener un solo nombre de cara al usuario. Renombrar columnas obligaría a tocar M, TMDL, réplica, tests y los CSV de resultados sin ganar nada para el usuario. `DimCompetencia` tiene 24 filas (competencias y subcompetencias); `Materia` es el atributo que las agrupa en las 6 competencias, y así debe explicarse en el diccionario. K04 sustituye el filtro de género por diseño, así que el segmentador afecta al resto de visuales del panel.
- Cambios aplicados: `gen_pbir.py` (constantes `ETQ_COMPETENCIA` y `ETQ_TITULARIDAD` en segmentadores, leyendas, columnas y títulos; segmentador `p2_seg_genero` sobre `DimPerfilAlumno[Genero]`, grupo de sincronización `Genero`; la cabecera del táctico pasa de 660 a 480 px para dejar sitio a cuatro segmentadores de 184 px), informe regenerado, `04_Guia_de_uso.md` §4, `02_Modelo_y_diccionario.md` §1 (nota de nombres), `contrato_diseno.md` §8.
- Pendiente en la memoria: en el diccionario del capítulo 8, indicar la correspondencia: competencia = `DimCompetencia[Materia]`; titularidad = `DimContextoCentro[Naturaleza]`. RF06 dice «(E, T, O)» para todos los filtros; en el diseño final, titularidad y hábitat solo están en el operativo y género en el táctico (el panel de filtros de Power BI permite el resto): citarlo en 8.4.2.

## D-16 Desajustes entre la memoria y el comportamiento implementado que se resuelven en la memoria
- Problema: (1) CU07, extensión 1a: «la desviación queda en blanco» sin área ni contexto; la medida K07 devuelve 0 y `Estado K01` pasa a usar K10. (2) HU04: «la elegida queda destacada»; el segmentador de área no filtra ni resalta el gráfico de K07 (interacción desactivada a propósito). (3) Sección 3.6 (obstáculos): «conocimiento del medio y expresión oral desde 2018»; lo que empieza en 2018 es ciencias y la comprensión oral de catalán y castellano. (4) Sección 3.5: «al pie habrá un aviso fijo» en los tres paneles; en el táctico y el operativo el aviso está en la cabecera. (5) SO3 cita cuatro dimensiones y el modelo tiene seis. (6) K03 se llama «% de alumnado en nivel bajo» y cuenta puntuaciones: coincide con alumnado cuando se filtra una competencia.
- Opciones: cambiar la implementación o corregir el texto.
- Decisión: corregir el texto en los seis casos; la implementación es correcta.
- Justificación: (1) Cataluña menos Cataluña es 0 y así está documentado en la ficha, el contrato y la descripción de la medida. (2) Mantener todas las áreas visibles es lo que pide RF09; resaltar exige formato condicional no validable sin Power BI Desktop, y la posición y el estado del área ya salen en las tarjetas. (3) a (6) son imprecisiones de redacción.
- Cambios aplicados: ninguno en el código.
- Pendiente en la memoria: (1) CU07 1a. Propuesto: «No hay ningún área ni contexto seleccionado: la desviación vale 0, porque la selección es toda Cataluña, y el semáforo indica la variación respecto a la convocatoria anterior.» (2) HU04, segundo criterio. Propuesto: «Al seleccionar un área se siguen viendo las demás, y su posición y su estado aparecen en las tarjetas.» (3) Sección 3.6. Propuesto: «(inglés desde 2010; ciencias y comprensión oral de catalán y castellano desde 2018)». (4) Sección 3.5. Propuesto: «y cada panel mostrará un aviso fijo sobre las limitaciones de los datos (RF15)», sin fijar la posición, o citarlo en 8.4.2. (5) SO3: dejarlo (es el objetivo inicial) y explicar en 8.1 que el diseño añade nivel de logro y calidad del dato. (6) En la ficha de K03 del capítulo 8: «porcentaje de puntuaciones globales por debajo de 55; con una competencia seleccionada equivale al porcentaje de alumnado».

## D-17 Correspondencia entre el modelo conceptual (7.2) y el modelo en estrella
- Problema: el modelo conceptual de la memoria (clases y RI1–RI6) y el modelo implementado no se corresponden uno a uno y ningún documento lo explicaba: `ContextoDeCentro` se identifica por (área, titularidad, hábitat) y la dimensión tiene 120 filas con un código de área; el perfil del alumno es una dimensión aparte; `Indicador` y `Perspectiva` no son tablas; RI3 dice que solo las competencias tienen nivel y el hecho lleva `NivelKey` = 0 en las subcompetencias; RI2 (vigencia) no se comprobaba en ningún test.
- Opciones: cambiar el modelo conceptual o documentar la traducción y comprobar las restricciones.
- Decisión: documentar la traducción (tabla en «Datos para el capítulo 8») y añadir a `test_modelo.py` la comprobación de RI2. RI3–RI6 ya tienen test.
- Justificación: el conceptual es independiente de la herramienta; las diferencias son decisiones de diseño lógico (miembro «No aplica» para evitar claves nulas, dimensiones de combinaciones, medidas en lugar de tablas). Evidencia de RI2 sobre `Datos.csv`: 0 puntuaciones antes del año de inicio de cada columna.
- Cambios aplicados: `validacion/test_modelo.py` (`test_vigencia_competencias_ri2`: 0 puntuaciones fuera de [`AnioInicio`, `AnioFin`] y `AnioInicio` igual al primer año real con datos de cada columna). La tabla de correspondencia está en «Datos para el capítulo 8», apartado 8.1.1.
- Pendiente en la memoria: RI1 dice que un área territorial se identifica por el nombre; con D-05 es cierto: «Barcelona Comarques» (hasta 2023) y «Barcelonès» (desde 2024) son áreas distintas. No requiere cambio. El 8.1 debe incluir la tabla de correspondencia.

## D-18 Contrato de diseño y estado: rutas y cifras desfasadas
- Problema: `contrato_diseno.md` §0 tiene rutas absolutas de Linux y de un directorio temporal que ya no existe; `ESTADO.md` describe el estado del 15/10/2026 (19 medidas, 36 visuales, 27 tests, decisiones «pendientes con las directoras»).
- Opciones: dejarlos como registro histórico o actualizarlos.
- Decisión: actualizarlos, porque son los documentos de entrada para quien retome el trabajo.
- Justificación: una ruta que no existe o un recuento antiguo hacen perder tiempo y generan dudas sobre qué versión es la buena.
- Cambios aplicados: `contrato_diseno.md` (§0 rutas de Windows y herramientas en carpeta temporal, §1 compat 1606, §3, §5.1, §5.2, §6, §7 y §8), `ESTADO.md` (reescrito el 12/11/2026: 20 medidas, 41 visuales, 31 tests, 7 CSV, Desktop abierto el 15/10/2026, lista de comprobación pendiente) y `validacion/README.md` (reescrito).

## D-19 Lo que Power BI Desktop añade al proyecto se conserva al regenerar
- Problema: `ESTADO.md`, `04_Guia_de_uso.md` (INT-03) y `02_Modelo_y_diccionario.md` §8.1 dicen que el modelo nunca se ha abierto en Power BI Desktop, pero el commit `6adfe70` (15/10/2026, «Actualizacion Project en Windows probado, cambio de ruta para el uso del proyecto») contiene lo que Desktop escribe al guardar: `compatibilityLevel` 1606 (el generador escribía 1567), `definition/cultures/es-ES.tmdl` con `ref cultureInfo es-ES` en `model.tmdl`, `.platform` en el modelo y en el informe, `.pbi/editorSettings.json`, `RutaDatos` fijada a la ruta del repositorio de la estudiante (con un espacio final), los `visual.json` reescritos con el esquema 2.13.0 y los filtros por defecto de los segmentadores de año (`objects.general.filter` con 2025) sustituidos por `{}`, de modo que el informe se abre sin año seleccionado. Los generadores, tal como estaban, borraban todo eso al regenerar (`gen_pbir.py` eliminaba la carpeta `.Report` entera) y devolvían `RutaDatos` al valor por defecto.
- Opciones: (a) regenerar y perder los cambios de Desktop; (b) dejar de regenerar y editar `PowerBI/` a mano; (c) que los generadores respeten lo que añade Desktop y solo escriban lo que es suyo.
- Decisión: (c). `gen_modelo.py` escribe `compatibilityLevel: 1606`, conserva `cultures/` y añade `ref cultureInfo` por cada cultura existente, no toca `.platform` ni `.pbi/`, y toma el valor de `RutaDatos` del `expressions.tmdl` existente (recortando espacios) en lugar de fijar el de por defecto. `gen_pbir.py` borra solo `definition/`, `definition.pbir` y `StaticResources/`, y expresa la selección por defecto de los segmentadores de año como filtro `Categorical` en `filterConfig` (la forma en que Desktop guarda las selecciones), no en `objects.general.filter`. No se adopta la ordenación por K10 descendente que quedó guardada en la tabla del panel estratégico (es un clic del usuario, no un diseño) ni la página activa (Desktop guardó la última abierta).
- Justificación: la regla «`PowerBI/` no se edita a mano» solo es sostenible si regenerar no destruye lo que la herramienta necesita (`.platform` identifica los artefactos para la integración con git de Fabric; `cultures/` guarda los metadatos lingüísticos de Q&A) ni la configuración local de la estudiante. El valor 1606 es el que Desktop impone al guardar; mantener 1567 obligaría a Desktop a volver a subirlo en cada guardado. El espacio final de la ruta no impidió la carga en Windows (el sistema lo ignora), pero se recorta porque en otro sistema sí fallaría. El commit prueba que el M se ejecutó en Windows («probado»), aunque no quedó registrado el resultado de la lista de comprobación del apartado 3.2 de la guía; por eso `ESTADO.md` pasa a decir que la primera apertura se hizo y que falta anotar los recuentos.
- Cambios aplicados: `gen_modelo.py`, `gen_pbir.py`, `PowerBI/` regenerado, `ESTADO.md`, `04_Guia_de_uso.md` (INT-03 y apartado 2.3), `02_Modelo_y_diccionario.md` §8.1, `contrato_diseno.md` §1. Pendiente de comprobar en Power BI Desktop: que los segmentadores de año arrancan en 2025 con el filtro en `filterConfig`.
- Pendiente en la memoria: ninguno; el capítulo de validación debe recoger el resultado de la lista de comprobación cuando la estudiante lo anote.

## Incidencias para comunicar al titular del dataset (D-07)

Texto propuesto para el formulario de contacto del Portal de Dades Obertes (conjunto `rk5x-gny6`, *Avaluació de sisè d'educació primària*). Es una acción de la estudiante, no del sistema, y no condiciona el TFG. Todas las cifras proceden del informe de calidad (`01_Informe_calidad_datos.md`, §4.3, §4.1 y §7.2) y de `Datos.csv`.

> En el conjunto de datos «Avaluació de sisè d'educació primària» (versión con 1.102.324 registros, 2009–2025) se han detectado cuatro incidencias que conviene revisar:
> 1. En 2017, las columnas de lengua castellana están rotadas: `PCAST_EE` contiene la puntuación global, `PCAST` la comprensión lectora y `PCAST_CL` la expresión escrita (en el 99,07 % de las 71.036 filas `PCAST_EE` = 0,6·`PCAST` + 0,4·`PCAST_CL`, que son los pesos de 2016).
> 2. En 2016, las columnas de lengua francesa están rotadas: `PFRAN_EE` contiene la global, `PFRAN` la comprensión oral, `PFRAN_CO` la comprensión lectora y `PFRAN_CE` la expresión escrita (en el 100 % de las 389 filas `PFRAN_EE` = 0,35·`PFRAN` + 0,50·`PFRAN_CO` + 0,15·`PFRAN_CE`).
> 3. En 2024, 13.357 valores de `HÀBITAT` son un texto autoincrementado («Fins a 10001» … «Fins a 23357») en lugar de la categoría «Fins a 10000».
> 4. En ciencias (`PMED`, 2018–2025) la puntuación global es la media simple de las tres subcompetencias en el 100 % de los 496.745 registros con las cuatro puntuaciones (diferencia máxima 0,01), mientras que el Quadern d'avaluació 68 publica los pesos 42 % / 25 % / 33 %.

## D-D06 Coherencia de los capítulos 1 a 7 con el diseño final
- Problema: tras el capítulo 8, varios apartados describían un comportamiento distinto del implementado: semáforos de K01 y K03 en el panel estratégico (CU02, HU01), desviación «en blanco» sin selección (CU07 1a), barra destacada al elegir un área (HU04), exclusión de puntuaciones «no válidas» en la distribución por nivel (CU09 1a, HU11), RF12 con origen E aunque la distribución solo está en el operativo, competencias de 2018 mal nombradas (3.6), «naturaleza» en lugar de «titularidad» (1.3, tabla de agentes y cabecera del panel operativo).
- Opciones: (a) dejar los capítulos y explicar las diferencias en el 8.4.2; (b) corregir los apartados que describen el sistema y dejar en el 8.4.2 solo los cambios respecto al prototipo (3.5).
- Decisión: (b), a petición de la estudiante (13/11/2026). Se aplican los textos propuestos en D-12 (2, 3), D-13 (1, 2, 3) y D-16 (1, 2, 3); CU03 menciona además el estado de K01 y K03. El prototipo del 3.5 y sus mockups no se tocan: son bocetos previos y el 8.4.2 explica qué cambia respecto a ellos. SO3 se mantiene (objetivo inicial) y el 8.1 explica las dos dimensiones añadidas.
- Justificación: los casos de uso, las historias y los requisitos especifican el sistema, así que deben coincidir con lo construido; el prototipo es un documento de partida y sus diferencias con el diseño son esperables.
- Cambios aplicados: `main.tex` (1.3, tabla de agentes, RF12, 3.6, CU02, CU03, CU07, CU09, HU01, HU04, HU11, 8.4.2), `gen_pbir.py` (cabecera del panel operativo), informe regenerado (solo cambia `p3_cabecera/visual.json`), `gen_paneles_diseno.py` y `panel_operativo.png` regenerado.

## Datos para el capítulo 8 (diseño)

Esta sección reúne, con cifras comprobadas sobre el repositorio y sobre `Datos.csv` el 12/11/2026, todo lo que el capítulo 8 de la memoria necesita. Quien escriba el capítulo solo necesita esta sección y `Docu_Parcial/02`, `03` y `04`; los nombres son los de la sección «Nombres» de este fichero. La memoria no debe copiar las tablas enteras del diccionario: basta con las columnas visibles y su significado, y remitir a los documentos para el detalle. Las medidas y los visuales de esta sección se han extraído con un script de los ficheros reales (`gen_medidas.py` y los `visual.json` del informe), no copiados a mano.

### 8.1.1 Diseño lógico: correspondencia entre el modelo conceptual (7.2) y el esquema en estrella (D-17)

| Clase o asociación del modelo conceptual | Tabla del modelo dimensional | Cómo se traduce |
|---|---|---|
| `Evaluación` (participación anónima de un alumno en una convocatoria; atributos de género, edad y mes de nacimiento) | `FactEvaluacion` (hechos, 1.102.324 filas) + `DimPerfilAlumno` (182 filas) | Cada evaluación es una fila de hechos. Sus atributos descriptivos (género, edad en el año natural, situación de edad, mes y trimestre de nacimiento) se sacan a una dimensión de combinaciones, `DimPerfilAlumno`, con clave determinista `PerfilKey`. El código de alumno no se carga (RNF08); solo se guarda si existía (`TieneCodigoAlumno`). |
| `Convocatoria` (año, hayPrueba) | `DimAnio` (17 filas, 2009–2025) | Una fila por año, incluido 2020 sin prueba (`TieneConvocatoria` = falso, `IndiceConvocatoria` nulo). `IndiceConvocatoria` numera 1..16 solo los años con prueba y es la base de las comparaciones temporales (RI5: 2020 no tiene hechos). |
| `ContextoDeCentro` (área territorial, titularidad, hábitat) | `DimContextoCentro` (120 filas) | Dimensión de combinaciones: producto cartesiano de 15 áreas × 2 titularidades × 4 hábitats, con clave determinista `ContextoKey` = `AreaCodigo`·100 + `NaturalezaCodigo`·10 + `HabitatCodigo`. Se generan todas las combinaciones válidas, no solo las observadas (86), para garantizar la integridad referencial sin combinar consultas. RI1 (clave por área + titularidad + hábitat) se cumple con la clave compuesta codificada. |
| `ElementoEvaluado` con subclases `Competencia` y `Subcompetencia` (nombre, añoInicio, añoFin) | `DimCompetencia` (24 filas) | Una fila por columna de puntuación del CSV. La especialización se aplana en el atributo `EsGlobal` (verdadero en las 6 competencias, falso en las 18 subcompetencias); `Materia` agrupa las subcompetencias en su competencia y `CodigoMateria` es la columna de su global. `AnioInicio`/`AnioFin` son el periodo de vigencia (RI2). `PeriodoDisenoInicio` y `EsInformativa` son atributos de diseño que el modelo conceptual no necesita. |
| `Puntuación` (clase asociativa Evaluación–ElementoEvaluado: valor, marcas de calidad) | `FactPuntuacion` (hechos, 17.728.085 filas) | Cada puntuación no nula es una fila de hechos con las claves de la evaluación (`AnioKey`, `ContextoKey`, `PerfilKey`), la del elemento (`CompetenciaKey`), el `valor` (`Puntuacion`, decimal fijo, RI7: 0–100) y dos claves derivadas: `NivelKey` y `CalidadKey`. No lleva `EvaluacionID`: ninguna medida lo necesita y ahorraría 17,7 millones de valores distintos. |
| Asociación `Puntuación`–`NivelDeLogro` (solo competencias, RI3) | `DimNivelLogro` (5 filas) y `FactPuntuacion[NivelKey]` | Para evitar claves nulas en el hecho, la dimensión tiene un miembro 0 «No aplica (subcompetencia)» que reciben todas las subcompetencias; las globales reciben 1–4 según los cortes 55/70/85 (RI3 y RI4). Los límites están en la dimensión (`LimiteInferior` incluido, `LimiteSuperior` excluido salvo 100). |
| Marcas de calidad de la puntuación (no válida, censurada, no comparable en serie, nivel no comparable) | `DimCalidadDato` (16 filas) y `FactPuntuacion[CalidadKey]` | Las cuatro marcas booleanas se codifican como bits de una máscara (1, 2, 4, 8) y la dimensión enumera las 16 combinaciones; una sola clave en el hecho en lugar de cuatro columnas de 17,7 millones de filas. |
| `Indicador` y `Perspectiva` (catálogo de los 12 KPIs) | No son tablas | Se resuelven en la lógica analítica: cada indicador es una medida DAX de la tabla `_Medidas` y cada perspectiva, una carpeta de visualización (`displayFolder`). `_Medidas` es una tabla sin filas ni relaciones (una columna oculta `Columna` vacía) que solo agrupa las 20 medidas. |

Cómo garantiza el diseño cada restricción de integridad: RI1, claves deterministas únicas en cada dimensión (`test_claves_unicas_en_dimensiones`) y 0 hechos huérfanos (`test_claves_huerfanas_cero`); RI2, comprobación de vigencia `AnioKey` dentro de [`AnioInicio`, `AnioFin`] en `test_vigencia_competencias_ri2` (0 puntuaciones fuera de vigencia; además `AnioInicio` coincide con el primer año real con datos de cada columna); RI3, `NivelKey` = 0 en toda subcompetencia y 1–4 en toda global (`test_nivel_coherente_con_limites_en_todas_las_filas`); RI4, cortes exactos 54,99→1, 55,00→2, 69,99→2, 70,00→3, 84,99→3, 85,00→4, 100→4 (`test_umbrales_nivel_en_limites_exactos`); RI5, 0 filas de 2020 en los hechos y `TieneConvocatoria` falso (`test_2020_sin_datos`); RI6, `EdadAnioNatural` entre 10 y 14 o nula (`test_edad_y_situacion_fila_a_fila`); RI7, 0 ≤ `Puntuacion` ≤ 100 sin nulos (`test_puntuacion_en_rango_0_100`) y la ETL detiene la carga ante un valor fuera de rango (R02). Con D-05, RI1 («un área territorial se identifica por el nombre») sigue siendo cierta: «Barcelona Comarques» (hasta 2023) y «Barcelonès» (desde 2024) son áreas distintas, con perímetros distintos.

Esquema en estrella: 2 tablas de hechos y 6 dimensiones; `DimAnio`, `DimContextoCentro` y `DimPerfilAlumno` son dimensiones conformadas (compartidas por los dos hechos); `DimCompetencia`, `DimNivelLogro` y `DimCalidadDato` solo se relacionan con `FactPuntuacion`. Los dos hechos no se relacionan entre sí. La figura del esquema (`imagenes/diseno/`, pendiente de generar con Pillow) debe dibujar las 9 relaciones de la tabla siguiente.

### Relaciones (9, todas muchos a uno, filtro en una sola dirección, activas; TOM las lista como Many:One OneDirection)

| Desde (lado muchos) | Hacia (lado uno) |
|---|---|
| `FactPuntuacion[AnioKey]` | `DimAnio[AnioKey]` |
| `FactPuntuacion[ContextoKey]` | `DimContextoCentro[ContextoKey]` |
| `FactPuntuacion[PerfilKey]` | `DimPerfilAlumno[PerfilKey]` |
| `FactPuntuacion[CompetenciaKey]` | `DimCompetencia[CompetenciaKey]` |
| `FactPuntuacion[NivelKey]` | `DimNivelLogro[NivelKey]` |
| `FactPuntuacion[CalidadKey]` | `DimCalidadDato[CalidadKey]` |
| `FactEvaluacion[AnioKey]` | `DimAnio[AnioKey]` |
| `FactEvaluacion[ContextoKey]` | `DimContextoCentro[ContextoKey]` |
| `FactEvaluacion[PerfilKey]` | `DimPerfilAlumno[PerfilKey]` |

### 8.1.2 Tablas de hechos (granularidad y filas comprobadas con `etl_referencia.py` el 12/11/2026)

| Tabla | Granularidad (una fila es…) | Filas | Columnas (todas ocultas, `int64` salvo indicación) | Base de |
|---|---|---|---|---|
| `FactEvaluacion` | Un registro de `Datos.csv`: un alumno evaluado en una convocatoria | 1.102.324 | `EvaluacionID` (posición 1..N en el fichero, R01), `AnioKey`, `ContextoKey`, `PerfilKey`, `TieneCodigoAlumno` (boolean), `CompetenciasEvaluadas` (nº de globales no nulas; su suma es 4.769.851) | `Alumnos evaluados` |
| `FactPuntuacion` | Una puntuación no nula de un registro en una de las 24 columnas de puntuación (despivotado, R33) | 17.728.085 (4.769.851 globales + 12.958.234 de subcompetencias) | `AnioKey`, `ContextoKey`, `PerfilKey`, `CompetenciaKey`, `NivelKey`, `CalidadKey`, `Puntuacion` (decimal fijo, formato `0.00`, 0–100) | K01–K12, semáforos, `Puntuaciones globales`, `Puntuaciones por nivel de logro`, `Puntuación media` |

Por qué dos tablas de hechos: participación y resultado son dos procesos con granos distintos; con `FactEvaluacion` el recuento de alumnado es un `COUNTROWS` independiente de la competencia filtrada (no se relaciona con `DimCompetencia`), y con el despivotado la competencia pasa a ser una dimensión y una sola medida sirve para las 24 columnas. Por convocatoria, `FactPuntuacion` va de 589.644 filas (2009) a 1.466.352 (2019).

### 8.1.3 Dimensiones (filas comprobadas; origen en `trabajo_en_curso/generadores/modelo/m_*.m`)

| Dimensión | Filas | Origen | Clave | Columnas visibles (tipo) | Columnas ocultas (tipo, uso) |
|---|---|---|---|---|---|
| `DimAnio` | 17 (2009–2025) | Derivada de los años distintos de `stg_Evaluaciones`: de 2009 al último año con datos, 2020 incluido | `AnioKey` = `Anio` | `Anio` (int64), `Curso` (string, «2024-2025», ordenada por `Anio`), `TieneConvocatoria` (boolean), `EsUltimaConvocatoria` (boolean), `NotaConvocatoria` (string: «Sin prueba por la COVID-19» en 2020; «Primera convocatoria tras la COVID-19 (se compara con 2019)» en 2021; vacía en el resto) | `AnioKey`, `IndiceConvocatoria` (int64, 1..16 solo con datos; nulo en 2020) |
| `DimContextoCentro` | 120 = 15 × 2 × 4 | Estática en M (producto cartesiano de las tablas de códigos) | `ContextoKey` = `AreaCodigo`·100 + `NaturalezaCodigo`·10 + `HabitatCodigo` | `AreaTerritorial` (string; 15 valores: 14 áreas + «Desconocida»; «Barcelona Comarques» hasta 2023 y «Barcelonès» desde 2024, D-05), `AreaPerimetro2025` (string), `AreaSerieComparable` (string: «Lleida + Alt Pirineu i Aran», «Barcelonès-Penedès y áreas afectadas» o el nombre del área), `AreaConRupturaSerie` (boolean), `RupturaHabitat2024` (boolean: Girona y Maresme - Vallès Oriental), `Naturaleza` (string: Pública/Privada; en el informe «Titularidad»), `Habitat` (string: No fiable / Hasta 10.000 hab. / De 10.001 a 100.000 hab. / Más de 100.000 hab.) | `ContextoKey`, `AreaCodigo` (1–14 y 99; 3 = Barcelona Comarques ≤ 2023, 4 = Barcelonès 2024, 5 = Barcelonès ≥ 2025), `AreaOrden` (orden de `AreaTerritorial`; = `AreaCodigo` salvo el 4, que vale 5), `NaturalezaCodigo` (1, 2; orden de `Naturaleza`), `HabitatCodigo` (0–3; orden de `Habitat`) |
| `DimPerfilAlumno` | 182 = 2 × 7 × 13 | Estática en M: géneros × combinaciones válidas (edad, situación) {(10,4), (11,4), (12,1), (13,2), (14,3), (sin edad,8), (sin edad,9)} × meses 0–12 | `PerfilKey` = `GeneroCodigo`·100000 + `SituacionEdadCodigo`·10000 + (`EdadAnioNatural` o 0)·100 + `MesNacimiento` | `Genero` (string: Niña/Niño), `EdadAnioNatural` (int64, 10–14 o nula), `SituacionEdad` (string: Adelantado, Edad teórica (12 años), Retraso de 1 año, Retraso de 2 años, No fiable (2010), Desconocida), `MesNacimiento` (int64, 1–12 o nulo), `TrimestreNacimiento` (string: T1–T4 / No informado) | `PerfilKey`, `GeneroCodigo` (orden de `Genero`), `SituacionEdadCodigo` (1, 2, 3, 4, 8, 9), `SituacionEdadOrden` (orden de presentación 4, 1, 2, 3, 8, 9) |
| `DimCompetencia` | 24 | Estática en M (contrato §5.2) | `CompetenciaKey` 1–24 | `CampoOrigen` (string, columna del CSV), `CodigoMateria` (string: PCAT, PCAST, PMAT, PANG, PFRAN, PMED), `Materia` (string; en el informe «Competencia»: Lengua catalana, Lengua castellana, Matemáticas, Lengua inglesa, Lengua francesa, Ciencias), `Subcompetencia` (string, o «Global»), `EsGlobal` (boolean), `AnioInicio` (int64: 2009, 2010 inglés y francés, 2013 EE de lenguas extranjeras, 2018 CO de catalán y castellano y ciencias), `AnioFin` (int64, nulo: todas vigentes), `PeriodoDisenoInicio` (int64: 2017 matemáticas, inglés y francés; 2018 catalán, castellano y ciencias; D-10), `EsInformativa` (boolean: francés) | `CompetenciaKey`, `MateriaOrden` (1–6), `SubcompetenciaOrden` (único por texto: 0 Global, 1 Comprensión lectora, 2 Comprensión oral, 3 Expresión escrita, 4–6 matemáticas, 7–9 ciencias) |
| `DimNivelLogro` | 5 | Estática en M | `NivelKey` 0–4 | `Nivel` (string: No aplica (subcompetencia), Bajo, Medio-bajo, Medio-alto, Alto), `LimiteInferior` (double: –, 0, 55, 70, 85), `LimiteSuperior` (double: –, 55, 70, 85, 100) | `NivelKey`, `NivelOrden` |
| `DimCalidadDato` | 16 | Estática en M: las 16 combinaciones de 4 bits | `CalidadKey` 0–15 (máscara) | `NoValida` (bit 1, R25: `PANG_EE` 2015), `Censurada` (bit 2, R26: `PCAT_EE` 2018; `PANG`, `PANG_CO`, `PANG_CE` 2015), `NoComparableSerie` (bit 4, R27), `NivelNoComparable` (bit 8, R28: `PANG` 2015 y 2016, `PMAT` 2015 y 2019, `PCAT` 2018, `PFRAN` 2022), `DescripcionCalidad` (string: «Válido» o lista de problemas) | `CalidadKey` |

Decisiones físicas comunes (TMDL): modo Import; `compatibilityLevel` 1606; `culture` y `sourceQueryCulture` es-ES; `discourageImplicitMeasures`; claves `int64` con `summarizeBy: none`; en los hechos todas las columnas ocultas; en las dimensiones las columnas de código y orden ocultas y usadas como `sortByColumn` del atributo de texto (cada texto tiene un único valor de orden, comprobado por `test_sort_by_column_uno_a_uno`); `Puntuacion` en decimal fijo (`Currency.Type` en M) para evitar errores de redondeo binario. Cada tabla y cada columna tiene una `description` en el TMDL (generada por `gen_modelo.py`).

### 8.2 Diseño de la ETL

**Flujo de consultas (orden real de `PBI_QueryOrder` en `model.tmdl`):** `RutaDatos` (parámetro, grupo «Parámetros») → `stg_Evaluaciones` (expresión compartida, grupo «Staging», no se carga) → `DimAnio`, `DimContextoCentro`, `DimPerfilAlumno`, `DimCompetencia`, `DimNivelLogro`, `DimCalidadDato` (grupo «Dimensiones») → `FactEvaluacion`, `FactPuntuacion` (grupo «Hechos») → `_Medidas`. Solo `DimAnio`, `FactEvaluacion` y `FactPuntuacion` referencian `stg_Evaluaciones` (cada una vuelve a leer el CSV: 3 lecturas de 240 MB por actualización); las otras cinco dimensiones son literales estáticos en M y no leen el fichero. No hay ninguna combinación de consultas (*merge*): todas las claves son aritméticas.

**Reglas que aplica cada consulta, en orden (R = regla del informe de calidad §5; «detiene la carga» = la actualización falla con un `Error.Record` cuyo mensaje indica la regla, el valor y el `EvaluacionID`):**

| Consulta | Paso | Regla | Detiene la carga |
|---|---|---|---|
| `stg_Evaluaciones` | 1. `Csv.Document` (UTF-8, coma, 32 columnas, `QuoteStyle.Csv`) y promoción de cabeceras; todo como texto | R01 | — |
| | 2. Comprobación de la cabecera: debe ser exactamente las 32 columnas esperadas | R34 (parcial) | Sí: «Estructura de Datos.csv» |
| | 3. `EvaluacionID` = índice 1..N antes de cualquier filtro | R01 | — |
| | 4. `Text.Trim` en todas las columnas; cadena vacía → null | R05 | — |
| | 5. Las 24 puntuaciones con `Number.FromText(texto, "es-ES")` sobre el texto original; fuera de [0, 100] o no convertible → error | R02 | Sí: «R02 Puntuación no válida» |
| | 6. `ANY` → `Anio` entero | — | Sí: «Año no válido» |
| | 7. Rotaciones con asignación simultánea desde las columnas originales: 2017 `PCAST` := `PCAST_EE`, `PCAST_CL` := `PCAST`, `PCAST_EE` := `PCAST_CL`; 2016 `PFRAN` := `PFRAN_EE`, `PFRAN_CO` := `PFRAN`, `PFRAN_CE` := `PFRAN_CO`, `PFRAN_EE` := `PFRAN_CE` | R03, R04 | — |
| | 8. `GeneroCodigo`: H/Home → 2 Niño; D/Dona → 1 Niña | R09 | Sí: «R09 Género no reconocido» |
| | 9. `NaturalezaCodigo`: Públic/Pública → 1; Privat/Privada → 2 | R10 | Sí: «R10 Naturaleza no reconocida» |
| | 10. Hábitat por prefijo: «Fins a…» → 1; «De 10001 a 100000» → 2; «Més de…» → 3 | R11 | Sí: «R11 Hábitat no reconocido» |
| | 11. `AreaCodigo`: vacío → 99; «Barcelona Comarques» → 4 en 2024 y 3 hasta 2023; resto por tabla de códigos | R13, R14 | Sí: «Área territorial desconocida» |
| | 12. `Table.SelectRowsWithErrors` sobre año, género, naturaleza, hábitat, área y puntuaciones: el primer error se eleva a toda la consulta (sin esto Power BI cargaría la celda vacía con un aviso) | R02, R09–R11, R34 | Sí (es el mecanismo de los pasos anteriores; RF05) |
| | 13. `HabitatCodigo` final: 0 «No fiable» en 2010 y en Baix Llobregat 2014 con «Més de 100000» (29 filas) | R12 | — |
| | 14. Año y mes de nacimiento a entero; `FechaNacimientoDudosa` = sin código en 2016 o 2018, o 1/2001 en 2016 (83 filas) | R16, R19 | — |
| | 15. `EdadAnioNatural` = `Anio` − año de nacimiento; nula si falta, 2010, fecha dudosa o fuera de [10, 14] | R16–R19 | — |
| | 16. `MesNacimiento` 1–12, 0 si falta (1.335 filas sin mes) | R16 | — |
| | 17. `SituacionEdadCodigo`: 2010 → 8; edad nula → 9; <12 → 4; 12 → 1; 13 → 2; 14 → 3 | R21 | — |
| | 18. `AnioKey`, `ContextoKey`, `PerfilKey` (fórmulas de 8.1.3) | — | — |
| | 19. `TieneCodigoAlumno`; `CODI_ALUMNE` se descarta | R06 | — |
| `FactEvaluacion` | `CompetenciasEvaluadas` = nº de globales no nulas; selección de 6 columnas | R06 | — |
| `FactPuntuacion` | `Table.UnpivotOtherColumns` de las 24 columnas (descarta nulos); `Puntuacion` a `Currency.Type`; `CompetenciaKey` por búsqueda en un registro estático; `NivelKey` (<55 → 1; <70 → 2; <85 → 3; resto 4; subcompetencias 0); `CalidadKey` por búsqueda «CAMPO|AÑO» en un registro con las reglas R25–R28 expandidas una sola vez | R33, R29, R25–R28 | — |
| `DimAnio` | Años distintos de `stg_Evaluaciones`; una fila por año de 2009 al máximo; `IndiceConvocatoria` solo con datos; notas de 2020 y 2021 | R22 | — |
| Resto de dimensiones | Literales M (tablas de códigos) | R10–R15, R21, R29, R25–R28, R30, R32 | — |

Qué hace el sistema cuando una comprobación falla: la actualización se detiene, no se carga ninguna tabla nueva y Power BI muestra el mensaje de la regla (tabla de mensajes en `04_Guia_de_uso.md` §3.3). Con los datos actuales no se dispara ninguna (0 valores fuera de patrón, 0 códigos no previstos). Lo que no comprueba la carga y sí la validación independiente: recuento de filas (1.102.324), regresiones de las rotaciones, medias oficiales (D-03). Reglas fuera del MVP, documentadas como extensiones: R07, R08, R20, R23, R24, R31, número fijo de filas de R34 (`02_Modelo_y_diccionario.md` §8.2). La global de ciencias no se recalcula (D-07).

### 8.3 Diseño de la lógica analítica: las 20 medidas DAX (extraídas de `gen_medidas.py` el 12/11/2026)

Reglas comunes: «global» = `DimCompetencia[EsGlobal] = TRUE` con `KEEPFILTERS`; «Cataluña» = `REMOVEFILTERS ( DimContextoCentro )`; mínimo muestral de 30 puntuaciones (RF14) en K01, K02, K03, K06 y `Puntuaciones por nivel de logro`, heredado por las demás; comparaciones temporales por `DimAnio[IndiceConvocatoria]`, nunca por `Anio − 1`, con `BLANK` si el contexto no tiene exactamente un año con convocatoria; solo competencias con `PeriodoDisenoInicio` ≤ año de la convocatoria de referencia. Cada medida tiene una `description` en el modelo (reproducida en el párrafo que precede a cada fórmula).

| # | Medida | Carpeta | Formato |
|---|---|---|---|
| 1 | `Alumnos evaluados` | 0. Base | `#,0` |
| 2 | `Puntuaciones globales` | 0. Base | `#,0` |
| 3 | `Puntuación media` | 0. Base | `0.0` |
| 4 | `Puntuación media Cataluña` | 0. Base | `0.0` |
| 5 | `K01 Puntuación media competencia` | 1. Rendimiento académico | `0.0` |
| 6 | `K02 Puntuación media subcompetencia` | 1. Rendimiento académico | `0.0` |
| 7 | `K03 % alumnado nivel bajo` | 1. Rendimiento académico | `0.0%` |
| 8 | `Puntuaciones por nivel de logro` | 1. Rendimiento académico | `#,0` |
| 9 | `K04 Brecha de género (Niños - Niñas)` | 2. Equidad e inclusión | `+0.0;-0.0;0.0` |
| 10 | `K05 Brecha pública - privada` | 2. Equidad e inclusión | `+0.0;-0.0;0.0` |
| 11 | `K06 Dispersión de resultados` | 2. Equidad e inclusión | `0.0` |
| 12 | `K07 Desviación respecto a Cataluña` | 3. Territorio y entorno | `+0.0;-0.0;0.0` |
| 13 | `K08 Diferencia urbano - rural` | 3. Territorio y entorno | `+0.0;-0.0;0.0` |
| 14 | `K09 Posición del área` | 3. Territorio y entorno | `0` |
| 15 | `K10 Variación interanual` | 4. Eficiencia y progreso | `+0.0;-0.0;0.0` |
| 16 | `K11 Tendencia 5 convocatorias` | 4. Eficiencia y progreso | `+0.0;-0.0;0.0` |
| 17 | `K12 % competencias que mejoran` | 4. Eficiencia y progreso | `0.0%` |
| 18 | `Estado K01` | 5. Semáforos | `"▲ Favorable";"▼ Desfavorable";"● Neutro"` |
| 19 | `Estado K03` | 5. Semáforos | `"▲ Favorable";"▼ Desfavorable";"● Neutro"` |
| 20 | `Estado K10` | 5. Semáforos | `"▲ Favorable";"▼ Desfavorable";"● Neutro"` |

**`Alumnos evaluados`** (carpeta «0. Base», formato `#,0`). Número de alumnos evaluados (filas de FactEvaluacion) en el contexto. No le afectan los filtros de competencia, nivel de logro ni calidad del dato, porque FactEvaluacion solo se relaciona con DimAnio, DimContextoCentro y DimPerfilAlumno.

```dax
Alumnos evaluados = COUNTROWS ( FactEvaluacion )
```

**`Puntuaciones globales`** (carpeta «0. Base», formato `#,0`). Número de puntuaciones globales (filas de FactPuntuacion con DimCompetencia[EsGlobal] = TRUE, aplicado con KEEPFILTERS) en el contexto. Es el tamaño muestral del mínimo de 30 que aplica K01.

```dax
Puntuaciones globales =
CALCULATE (
    COUNTROWS ( FactPuntuacion ),
    KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () )
)
```

**`Puntuación media`** (carpeta «0. Base», formato `0.0`). Media de FactPuntuacion[Puntuacion] sin ningún filtro de competencia: si el contexto no separa globales y subcompetencias, las mezcla. Uso técnico (conciliación con la ETL de referencia); para el análisis usar K01 o K02.

```dax
Puntuación media = AVERAGE ( FactPuntuacion[Puntuacion] )
```

**`Puntuación media Cataluña`** (carpeta «0. Base», formato `0.0`). K01 calculada para toda Cataluña: quita todos los filtros de DimContextoCentro (área, naturaleza y hábitat) y conserva los de año, competencia y perfil del alumnado. Incluye el área «Desconocida». Es la referencia de K07 y de Estado K01. BLANK si hay menos de 30 puntuaciones globales.

```dax
Puntuación media Cataluña =
CALCULATE (
    [K01 Puntuación media competencia],
    REMOVEFILTERS ( DimContextoCentro )
)
```

**`K01 Puntuación media competencia`** (carpeta «1. Rendimiento académico», formato `0.0`). K01. Puntuación media de las competencias globales (DimCompetencia[EsGlobal] = TRUE, con KEEPFILTERS). BLANK si el contexto tiene menos de 30 puntuaciones globales (mínimo muestral). Sin filtro de materia promedia todas las materias evaluadas, francés incluido. Las puntuaciones no están equiparadas entre convocatorias: la comparación entre años es orientativa.

```dax
K01 Puntuación media competencia =
VAR _n = [Puntuaciones globales]
RETURN
    IF (
        _n >= 30,
        CALCULATE (
            AVERAGE ( FactPuntuacion[Puntuacion] ),
            KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () )
        )
    )
```

**`K02 Puntuación media subcompetencia`** (carpeta «1. Rendimiento académico», formato `0.0`). K02. Puntuación media de las subcompetencias (DimCompetencia[EsGlobal] = FALSE), excluyendo las puntuaciones no válidas (DimCalidadDato[NoValida] = TRUE: expresión escrita de inglés 2015). BLANK si quedan menos de 30 puntuaciones. No excluye las escalas no comparables en serie (DimCalidadDato[NoComparableSerie]): para series temporales, filtrar por esa columna.

```dax
K02 Puntuación media subcompetencia =
VAR _n =
    CALCULATE (
        COUNTROWS ( FactPuntuacion ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = FALSE () ),
        KEEPFILTERS ( DimCalidadDato[NoValida] = FALSE () )
    )
VAR _media =
    CALCULATE (
        AVERAGE ( FactPuntuacion[Puntuacion] ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = FALSE () ),
        KEEPFILTERS ( DimCalidadDato[NoValida] = FALSE () )
    )
RETURN
    IF ( _n >= 30, _media )
```

**`K03 % alumnado nivel bajo`** (carpeta «1. Rendimiento académico», formato `0.0%`). K03. Porcentaje de puntuaciones globales en nivel Bajo (< 55 puntos, DimNivelLogro[NivelKey] = 1) sobre el total de puntuaciones globales. Numerador y denominador excluyen las celdas censuradas (DimCalidadDato[Censurada]) y las convocatorias con nivel no comparable (DimCalidadDato[NivelNoComparable]). Ignora los filtros de DimNivelLogro. BLANK si el denominador tiene menos de 30 puntuaciones. Niveles internos del TFG (cortes 55/70/85), no los niveles oficiales.

```dax
K03 % alumnado nivel bajo =
VAR _globales =
    CALCULATE (
        COUNTROWS ( FactPuntuacion ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCalidadDato[Censurada] = FALSE () ),
        KEEPFILTERS ( DimCalidadDato[NivelNoComparable] = FALSE () ),
        REMOVEFILTERS ( DimNivelLogro )
    )
VAR _bajo =
    CALCULATE (
        COUNTROWS ( FactPuntuacion ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCalidadDato[Censurada] = FALSE () ),
        KEEPFILTERS ( DimCalidadDato[NivelNoComparable] = FALSE () ),
        REMOVEFILTERS ( DimNivelLogro ),
        DimNivelLogro[NivelKey] = 1
    )
RETURN
    IF ( _globales >= 30, DIVIDE ( COALESCE ( _bajo, 0 ), _globales ) )
```

**`Puntuaciones por nivel de logro`** (carpeta «1. Rendimiento académico», formato `#,0`). Número de puntuaciones globales en el nivel de logro del contexto (DimNivelLogro en el eje o la leyenda), con las mismas exclusiones que K03: celdas censuradas (DimCalidadDato[Censurada]) y convocatorias con nivel no comparable (DimCalidadDato[NivelNoComparable]). BLANK si la competencia tiene menos de 30 puntuaciones globales en total, sumando todos los niveles (RF14). Es la base del gráfico de distribución por nivel: su tramo Bajo coincide con K03 por construcción. Niveles internos del TFG (cortes 55/70/85), no los niveles oficiales.

```dax
Puntuaciones por nivel de logro =
VAR _total =
    CALCULATE (
        COUNTROWS ( FactPuntuacion ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCalidadDato[Censurada] = FALSE () ),
        KEEPFILTERS ( DimCalidadDato[NivelNoComparable] = FALSE () ),
        REMOVEFILTERS ( DimNivelLogro )
    )
VAR _nivel =
    CALCULATE (
        COUNTROWS ( FactPuntuacion ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCalidadDato[Censurada] = FALSE () ),
        KEEPFILTERS ( DimCalidadDato[NivelNoComparable] = FALSE () )
    )
RETURN
    IF ( _total >= 30, _nivel )
```

**`K04 Brecha de género (Niños - Niñas)`** (carpeta «2. Equidad e inclusión», formato `+0.0;-0.0;0.0`). K04. Diferencia de K01 entre niños y niñas (Niño - Niña). Sustituye cualquier filtro de género del contexto (DimPerfilAlumno[Genero] y su columna de orden GeneroCodigo). Positivo: los niños puntúan más. BLANK si alguno de los dos grupos no llega al mínimo de 30 puntuaciones globales.

```dax
K04 Brecha de género (Niños - Niñas) =
VAR _ninos =
    CALCULATE (
        [K01 Puntuación media competencia],
        REMOVEFILTERS ( DimPerfilAlumno[Genero], DimPerfilAlumno[GeneroCodigo] ),
        DimPerfilAlumno[Genero] = "Niño"
    )
VAR _ninas =
    CALCULATE (
        [K01 Puntuación media competencia],
        REMOVEFILTERS ( DimPerfilAlumno[Genero], DimPerfilAlumno[GeneroCodigo] ),
        DimPerfilAlumno[Genero] = "Niña"
    )
RETURN
    IF ( NOT ISBLANK ( _ninos ) && NOT ISBLANK ( _ninas ), _ninos - _ninas )
```

**`K05 Brecha pública - privada`** (carpeta «2. Equidad e inclusión», formato `+0.0;-0.0;0.0`). K05. Diferencia de K01 entre centros públicos y privados (Pública - Privada; «Privada» incluye la concertada). Sustituye el filtro de naturaleza del contexto (Naturaleza y NaturalezaCodigo). Positivo: la pública puntúa más. BLANK si alguno de los dos grupos no llega al mínimo de 30.

```dax
K05 Brecha pública - privada =
VAR _publica =
    CALCULATE (
        [K01 Puntuación media competencia],
        REMOVEFILTERS ( DimContextoCentro[Naturaleza], DimContextoCentro[NaturalezaCodigo] ),
        DimContextoCentro[Naturaleza] = "Pública"
    )
VAR _privada =
    CALCULATE (
        [K01 Puntuación media competencia],
        REMOVEFILTERS ( DimContextoCentro[Naturaleza], DimContextoCentro[NaturalezaCodigo] ),
        DimContextoCentro[Naturaleza] = "Privada"
    )
RETURN
    IF ( NOT ISBLANK ( _publica ) && NOT ISBLANK ( _privada ), _publica - _privada )
```

**`K06 Dispersión de resultados`** (carpeta «2. Equidad e inclusión», formato `0.0`). K06. Desviación típica poblacional (STDEV.P) de las puntuaciones globales, excluyendo las celdas censuradas (DimCalidadDato[Censurada]: suelos artificiales de inglés 2015). BLANK si quedan menos de 30 puntuaciones. Sin filtro de materia mezcla materias. Interpretar con cautela en catalán 2018, inglés 2011 y matemáticas 2015 y 2019 (informe de calidad, sección 6.4).

```dax
K06 Dispersión de resultados =
VAR _n =
    CALCULATE (
        COUNTROWS ( FactPuntuacion ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCalidadDato[Censurada] = FALSE () )
    )
VAR _desviacion =
    CALCULATE (
        STDEV.P ( FactPuntuacion[Puntuacion] ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCalidadDato[Censurada] = FALSE () )
    )
RETURN
    IF ( _n >= 30, _desviacion )
```

**`K07 Desviación respecto a Cataluña`** (carpeta «3. Territorio y entorno», formato `+0.0;-0.0;0.0`). K07. K01 del contexto menos la puntuación media de Cataluña (mismo año, competencia y perfil). Positivo: el contexto supera la media catalana. Vale 0 si no hay ningún filtro de DimContextoCentro. BLANK si alguna de las dos medias está en blanco.

```dax
K07 Desviación respecto a Cataluña =
VAR _k01 = [K01 Puntuación media competencia]
VAR _cataluna = [Puntuación media Cataluña]
RETURN
    IF ( NOT ISBLANK ( _k01 ) && NOT ISBLANK ( _cataluna ), _k01 - _cataluna )
```

**`K08 Diferencia urbano - rural`** (carpeta «3. Territorio y entorno», formato `+0.0;-0.0;0.0`). K08. K01 en municipios de más de 100.000 habitantes (HabitatCodigo = 3) menos K01 en municipios de hasta 10.000 (HabitatCodigo = 1). Sustituye el filtro de hábitat del contexto. El hábitat 0 «No fiable» (2010 y parte de Baix Llobregat 2014) nunca entra, así que 2010 queda en blanco. Girona y Maresme - Vallès Oriental tienen ruptura de clasificación del hábitat desde 2024.

```dax
K08 Diferencia urbano - rural =
VAR _urbano =
    CALCULATE (
        [K01 Puntuación media competencia],
        REMOVEFILTERS ( DimContextoCentro[Habitat], DimContextoCentro[HabitatCodigo] ),
        DimContextoCentro[HabitatCodigo] = 3
    )
VAR _rural =
    CALCULATE (
        [K01 Puntuación media competencia],
        REMOVEFILTERS ( DimContextoCentro[Habitat], DimContextoCentro[HabitatCodigo] ),
        DimContextoCentro[HabitatCodigo] = 1
    )
RETURN
    IF ( NOT ISBLANK ( _urbano ) && NOT ISBLANK ( _rural ), _urbano - _rural )
```

**`K09 Posición del área`** (carpeta «3. Territorio y entorno», formato `0`). K09. Posición del área territorial (1 = mejor) por K01 descendente, con empates densos (DENSE), dentro del mismo año, competencia, naturaleza y hábitat. Con DimContextoCentro[AreaTerritorial] en el eje del visual compara con las áreas visibles (ALLSELECTED); en una tarjeta con el área elegida en un segmentador compara con todas las áreas. «Desconocida» nunca entra en la comparación. BLANK si el contexto no tiene exactamente un área, si el área es «Desconocida», si su K01 está en blanco o si todas las competencias del contexto son informativas (francés).

```dax
K09 Posición del área =
VAR _area = SELECTEDVALUE ( DimContextoCentro[AreaTerritorial] )
VAR _hayNoInformativas =
    NOT ISEMPTY (
        CALCULATETABLE (
            VALUES ( DimCompetencia[CompetenciaKey] ),
            KEEPFILTERS ( DimCompetencia[EsInformativa] = FALSE () )
        )
    )
RETURN
    IF (
        NOT ISBLANK ( _area )
            && _area <> "Desconocida"
            && _hayNoInformativas,
        VAR _enEje = ISINSCOPE ( DimContextoCentro[AreaTerritorial] )
        VAR _seleccionadas = ALLSELECTED ( DimContextoCentro[AreaTerritorial] )
        VAR _areas =
            FILTER (
                ALL ( DimContextoCentro[AreaTerritorial] ),
                DimContextoCentro[AreaTerritorial] <> "Desconocida"
                    && ( NOT _enEje || DimContextoCentro[AreaTerritorial] IN _seleccionadas )
            )
        VAR _valor =
            CALCULATE (
                [K01 Puntuación media competencia],
                REMOVEFILTERS (
                    DimContextoCentro[AreaCodigo],
                    DimContextoCentro[AreaOrden],
                    DimContextoCentro[AreaPerimetro2025],
                    DimContextoCentro[AreaSerieComparable],
                    DimContextoCentro[AreaConRupturaSerie],
                    DimContextoCentro[RupturaHabitat2024]
                ),
                DimContextoCentro[AreaTerritorial] = _area
            )
        RETURN
            IF (
                NOT ISBLANK ( _valor ),
                RANKX (
                    _areas,
                    CALCULATE (
                        [K01 Puntuación media competencia],
                        REMOVEFILTERS (
                            DimContextoCentro[AreaCodigo],
                            DimContextoCentro[AreaOrden],
                            DimContextoCentro[AreaPerimetro2025],
                            DimContextoCentro[AreaSerieComparable],
                            DimContextoCentro[AreaConRupturaSerie],
                            DimContextoCentro[RupturaHabitat2024]
                        )
                    ),
                    _valor,
                    DESC,
                    DENSE
                )
            )
    )
```

**`K10 Variación interanual`** (carpeta «4. Eficiencia y progreso», formato `+0.0;-0.0;0.0`). K10. K01 de la convocatoria del contexto menos K01 de la convocatoria anterior, navegando por DimAnio[IndiceConvocatoria] (2021 se compara con 2019; 2020 no tiene prueba). Solo usa las competencias globales cuyo periodo de diseño estable empieza como tarde el año de la convocatoria anterior (DimCompetencia[PeriodoDisenoInicio]); si no queda ninguna, BLANK. BLANK también si el contexto no tiene exactamente un año con convocatoria o si es la primera convocatoria. Funciona con DimAnio[Anio] en el eje y con un segmentador de un solo año. ATENCIÓN: las puntuaciones no están equiparadas entre convocatorias (no hay ítems de anclaje), así que la diferencia mezcla la dificultad de cada prueba con el rendimiento real y solo es orientativa.

```dax
K10 Variación interanual =
VAR _i =
    CALCULATE (
        SELECTEDVALUE ( DimAnio[IndiceConvocatoria] ),
        KEEPFILTERS ( DimAnio[TieneConvocatoria] = TRUE () )
    )
RETURN
    IF (
        _i > 1,
        VAR _anioAnterior =
            CALCULATE (
                MAX ( DimAnio[Anio] ),
                REMOVEFILTERS ( DimAnio ),
                DimAnio[IndiceConvocatoria] = _i - 1
            )
        VAR _actual =
            CALCULATE (
                [K01 Puntuación media competencia],
                KEEPFILTERS ( DimCompetencia[PeriodoDisenoInicio] <= _anioAnterior )
            )
        VAR _anterior =
            CALCULATE (
                [K01 Puntuación media competencia],
                REMOVEFILTERS ( DimAnio ),
                DimAnio[IndiceConvocatoria] = _i - 1,
                KEEPFILTERS ( DimCompetencia[PeriodoDisenoInicio] <= _anioAnterior )
            )
        RETURN
            IF ( NOT ISBLANK ( _actual ) && NOT ISBLANK ( _anterior ), _actual - _anterior )
    )
```

**`K11 Tendencia 5 convocatorias`** (carpeta «4. Eficiencia y progreso», formato `+0.0;-0.0;0.0`). K11. Variación media por convocatoria en una ventana de 5 convocatorias: (K01 de la convocatoria i - K01 de la convocatoria i-4) / 4, navegando por DimAnio[IndiceConvocatoria]. Solo usa las competencias globales con PeriodoDisenoInicio <= año de la convocatoria i-4. BLANK si el contexto no tiene exactamente un año con convocatoria, si no hay 4 convocatorias anteriores o si no queda ninguna competencia comparable. ATENCIÓN: las puntuaciones no están equiparadas entre convocatorias (no hay ítems de anclaje), así que la diferencia mezcla la dificultad de cada prueba con el rendimiento real y solo es orientativa.

```dax
K11 Tendencia 5 convocatorias =
VAR _i =
    CALCULATE (
        SELECTEDVALUE ( DimAnio[IndiceConvocatoria] ),
        KEEPFILTERS ( DimAnio[TieneConvocatoria] = TRUE () )
    )
RETURN
    IF (
        _i > 4,
        VAR _anioInicio =
            CALCULATE (
                MAX ( DimAnio[Anio] ),
                REMOVEFILTERS ( DimAnio ),
                DimAnio[IndiceConvocatoria] = _i - 4
            )
        VAR _actual =
            CALCULATE (
                [K01 Puntuación media competencia],
                KEEPFILTERS ( DimCompetencia[PeriodoDisenoInicio] <= _anioInicio )
            )
        VAR _inicio =
            CALCULATE (
                [K01 Puntuación media competencia],
                REMOVEFILTERS ( DimAnio ),
                DimAnio[IndiceConvocatoria] = _i - 4,
                KEEPFILTERS ( DimCompetencia[PeriodoDisenoInicio] <= _anioInicio )
            )
        RETURN
            IF ( NOT ISBLANK ( _actual ) && NOT ISBLANK ( _inicio ), DIVIDE ( _actual - _inicio, 4 ) )
    )
```

**`K12 % competencias que mejoran`** (carpeta «4. Eficiencia y progreso», formato `0.0%`). K12. Porcentaje de materias globales no informativas (sin francés) que mejoran al menos 1 punto respecto a la convocatoria anterior (K10 >= 1), sobre las materias con K10 calculable. Itera por DimCompetencia[CodigoMateria] y hereda todas las condiciones de K10 (un solo año con convocatoria, periodo de diseño comparable y mínimo muestral). BLANK si ninguna materia tiene K10. ATENCIÓN: las puntuaciones no están equiparadas entre convocatorias (no hay ítems de anclaje), así que la diferencia mezcla la dificultad de cada prueba con el rendimiento real y solo es orientativa.

```dax
K12 % competencias que mejoran =
VAR _materias =
    CALCULATETABLE (
        VALUES ( DimCompetencia[CodigoMateria] ),
        KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () ),
        KEEPFILTERS ( DimCompetencia[EsInformativa] = FALSE () )
    )
VAR _variaciones =
    ADDCOLUMNS ( _materias, "@Variacion", [K10 Variación interanual] )
VAR _comparables =
    FILTER ( _variaciones, NOT ISBLANK ( [@Variacion] ) )
VAR _mejoran =
    FILTER ( _comparables, [@Variacion] >= 1 )
RETURN
    DIVIDE ( COALESCE ( COUNTROWS ( _mejoran ), 0 ), COUNTROWS ( _comparables ) )
```

**`Estado K01`** (carpeta «5. Semáforos», formato `"▲ Favorable";"▼ Desfavorable";"● Neutro"`). Semáforo de K01: 1 favorable, 0 neutro, -1 desfavorable; el formato lo muestra como ▲ Favorable, ● Neutro o ▼ Desfavorable. Con algún filtro de DimContextoCentro (área, naturaleza o hábitat) compara con Cataluña mediante K07 (>= 1 -> 1; <= -1 -> -1; resto 0). Sin filtro de contexto de centro usa K10 (>= 0,5 -> 1; <= -0,5 -> -1; resto 0), que exige un solo año con convocatoria. BLANK si el indicador usado está en blanco. Cuando usa K10, las puntuaciones no están equiparadas entre convocatorias y el semáforo es orientativo.

```dax
Estado K01 =
VAR _conContexto = ISFILTERED ( DimContextoCentro )
VAR _valor =
    IF (
        _conContexto,
        [K07 Desviación respecto a Cataluña],
        [K10 Variación interanual]
    )
VAR _umbral = IF ( _conContexto, 1, 0.5 )
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _valor ), BLANK (),
        _valor >= _umbral, 1,
        _valor <= -_umbral, -1,
        0
    )
```

**`Estado K03`** (carpeta «5. Semáforos», formato `"▲ Favorable";"▼ Desfavorable";"● Neutro"`). Semáforo de K03: compara el % en nivel bajo del contexto con el de Cataluña (sin filtros de DimContextoCentro). Diferencia <= -2 puntos porcentuales -> 1 (▲ Favorable); >= +2 puntos porcentuales -> -1 (▼ Desfavorable); resto 0 (● Neutro). Sin ningún filtro de contexto de centro compara Cataluña consigo misma y vale 0: tiene sentido en los paneles táctico y operativo, no en el estratégico. BLANK si alguno de los dos K03 está en blanco.

```dax
Estado K03 =
VAR _k03 = [K03 % alumnado nivel bajo]
VAR _k03Cataluna =
    CALCULATE (
        [K03 % alumnado nivel bajo],
        REMOVEFILTERS ( DimContextoCentro )
    )
RETURN
    IF (
        NOT ISBLANK ( _k03 ) && NOT ISBLANK ( _k03Cataluna ),
        VAR _diferencia = _k03 - _k03Cataluna
        RETURN
            SWITCH (
                TRUE (),
                _diferencia <= -0.02, 1,
                _diferencia >= 0.02, -1,
                0
            )
    )
```

**`Estado K10`** (carpeta «5. Semáforos», formato `"▲ Favorable";"▼ Desfavorable";"● Neutro"`). Semáforo de K10: >= 0,5 puntos -> 1 (▲ Favorable); <= -0,5 -> -1 (▼ Desfavorable); resto 0 (● Neutro). BLANK si K10 está en blanco. ATENCIÓN: las puntuaciones no están equiparadas entre convocatorias (no hay ítems de anclaje), así que la diferencia mezcla la dificultad de cada prueba con el rendimiento real y solo es orientativa.

```dax
Estado K10 =
VAR _k10 = [K10 Variación interanual]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _k10 ), BLANK (),
        _k10 >= 0.5, 1,
        _k10 <= -0.5, -1,
        0
    )
```

### 8.3.2 Semáforos y referencias (D-12)

| Semáforo | Referencia | Umbral | Donde se muestra | Valores 2025 (`semaforos_2025.csv`) |
|---|---|---|---|---|
| `Estado K01` | Con algún filtro de `DimContextoCentro`: K07 = K01 del contexto − K01 de Cataluña. Sin filtro de contexto: K10 (variación interanual de Cataluña) | ±1 punto (K07); ±0,5 puntos (K10) | Táctico (área seleccionada) y operativo (contexto seleccionado) | Barcelonès −1 en las cinco competencias (K07 entre −2,86 y −3,88); Consorci d'Educació de Barcelona +1 en las cinco (K07 entre +1,06 y +3,34) |
| `Estado K03` | K03 del contexto − K03 de Cataluña | ±2 puntos porcentuales | Táctico y operativo (sin contexto vale 0: Cataluña frente a sí misma; por eso no está en el estratégico) | Barcelonès −1 en las cinco (ciencias 35,07 % frente a 26,93 %); Consorci +1 en inglés (12,08 % frente a 15,36 %) y 0 en el resto; Lleida +1 en ciencias (24,15 %) |
| `Estado K10` | K10 (variación frente a la convocatoria anterior, por `IndiceConvocatoria`) frente a 0 | ±0,5 puntos | Estratégico (tarjeta y columna de la tabla por competencia) | Cataluña: catalán −1 (−1,32), castellano +1 (+2,58), matemáticas −1 (−3,94), inglés +1 (+2,47), francés +1 (+3,29), ciencias −1 (−8,16); sin filtro de competencia −1 (−1,66) |

Presentación: las tres medidas devuelven 1, 0 o −1 y la cadena de formato `"▲ Favorable";"▼ Desfavorable";"● Neutro"` (secciones positivo;negativo;cero) las muestra con símbolo y palabra, de modo que el estado no depende solo del color (RNF05) y no hace falta formato condicional. En TMDL la cadena se escribe entrecomillada con las comillas interiores duplicadas (`"""▲ Favorable"";""▼ Desfavorable"";""● Neutro"""`), forma que exige el deserializador TOM. No existe un semáforo temporal de K03: el porcentaje por debajo de un corte fijo oscila mucho con la dificultad de cada prueba (ciencias pasa del 13,2 % al 26,9 % de 2024 a 2025) y las pruebas no están equiparadas. Los umbrales son propuestas del TFG.

Regla de las 30 puntuaciones (RF14): K01, K02, K03, K06 y `Puntuaciones por nivel de logro` devuelven `BLANK` si el contexto tiene menos de 30 puntuaciones (en K03 se cuenta el denominador ya filtrado; en K06 las no censuradas; en la distribución por nivel el total de la competencia, no cada nivel). Las demás medidas lo heredan. Ejemplo real: francés en el Vallès Occidental 2025 queda en blanco en K01 (24 puntuaciones); francés en Cataluña 2025 no (243).

Justificación de los cortes 55/70/85 (D-08; informe de calidad §6.3): cada corte cae dentro de la horquilla oficial (nivel mínimo entre 50 y 60, óptimo en 70, alto entre 80 y 90; Quadern 68, p. 9); frente a los porcentajes oficiales de 35 combinaciones materia-año (2018–2025), el corte 55 da un error medio de 2,70 puntos porcentuales y un sesgo de −0,14 en el nivel bajo, frente a −4,39 con 50 y +5,22 con 60; la mediana de los cortes que reproducen exactamente los oficiales es 55,98 / 70,70 / 85,69. Son niveles internos del TFG, no los oficiales, y las convocatorias donde el corte fijo no es fiable se excluyen de K03 con `NivelNoComparable` (R28).

Contraste con las medias oficiales (D-01): las 72 medias de Cataluña por materia y convocatoria (2009–2025) cumplen el criterio de aceptación de 0,5 puntos (RNF06; diferencia máxima 0,30); la validación aplica además una alerta interna de 0,2: 70 de 72 dentro, y las dos restantes (inglés 2016, +0,24; francés 2024, +0,30) están explicadas en el informe de calidad §4.6. Castellano 2017 corregido: 73,51 frente a 73,4 oficial (74,30 sin la rotación R03).

### 8.4 Diseño de la interfaz: páginas, visuales y filtros (extraídos de los `visual.json` del informe el 12/11/2026)

Estructura común (8.4.1): lienzo de 1280 × 720 (RNF03); cabecera de texto arriba a la izquierda y segmentadores desplegables a la derecha en la misma fila; fila de tarjetas debajo; tres visuales grandes en la zona central; en el estratégico, un aviso al pie; en los otros dos, el aviso va en el subtítulo de la cabecera. Segmentadores de año de selección única con 2025 por defecto (filtro `Categorical` en `filterConfig`, D-19). Grupos de sincronización entre páginas: `Anio`, `Materia`, `AreaTerritorial`, `Naturaleza`, `Habitat`, `Genero`. Tema base `CY24SU10` (tema por defecto de Power BI). Colores de los niveles de logro en el gráfico de distribución: Bajo `#B35806`, Medio-bajo `#F1A340`, Medio-alto `#998EC3`, Alto `#542788` (paleta divergente naranja-violeta de ColorBrewer PuOr, distinguible con deuteranopía y protanopía; RNF05). Tipografía Segoe UI (cabeceras 16 pt en negrita, subtítulos 10 pt gris `#605E5C`, aviso 10 pt con «Aviso:» en rojo `#A4262C`). Texto alternativo (`altText`) en todos los visuales. Etiquetas visibles «Competencia» (`DimCompetencia[Materia]`) y «Titularidad» (`DimContextoCentro[Naturaleza]`) (D-15). Los tres gráficos de líneas usan eje categórico con `showAll` para que 2020 aparezca como hueco (D-14). Las interacciones desactivadas evitan que el segmentador de año filtre las líneas de evolución y que el de área filtre las barras K07 (RF09).

Cambios respecto al prototipo de la Sección 3.5 y a los requisitos, que el 8.4.2 debe citar: (1) el semáforo del estratégico va solo en K10, no en K01 y K03 (D-12); (2) la distribución por nivel está solo en el operativo (RF12 decía E y O) (D-13); (3) titularidad y hábitat solo se filtran en el operativo y género solo en el táctico (RF06 decía los tres paneles; el panel de filtros de Power BI permite el resto) (D-15); (4) en el táctico y el operativo el aviso está en la cabecera y no al pie (D-16); (5) al seleccionar un área en el táctico las barras K07 siguen mostrando todas las áreas sin resaltar la elegida; su posición y su estado salen en las tarjetas (D-16); (6) sin área ni contexto, K07 vale 0 y `Estado K01` usa K10 (D-16); (7) el mockup del estratégico (`gen_mockups.py`) dibuja semáforo en tres tarjetas.


### Páginas y visuales del informe (41 visuales)

**Página `Estrategico_Departamento` («Estratégico - Departamento», 1280×720, 13 visuales).** Interacciones desactivadas (NoFilter): `p1_seg_anio` → `p1_linea_k01_materia`.

| Visual | Tipo | Posición (x, y, ancho, alto) | Título / subtítulo | Campos | Filtros propios |
|---|---|---|---|---|---|
| `p1_cabecera` | textbox | 16, 8, 860, 60 |  | Texto: Cuadro de Mando Integral - Educación primaria de Cataluña / Visión estratégica (Departamento de Educación): resultados de la convocatoria seleccionada y evolución | — |
| `p1_seg_anio` | slicer | 884, 8, 186, 60 | Año | Values: DimAnio[Anio] («Año»); Grupo de sincronización: Anio; Selección única | en DimAnio[Anio] {2025L} |
| `p1_seg_materia` | slicer | 1078, 8, 186, 60 | Competencia | Values: DimCompetencia[Materia] («Competencia»); Grupo de sincronización: Materia | — |
| `p1_tarjeta_k01` | card | 16, 76, 171.4, 100 | Puntuación media (K01) / Competencias globales | Values: _Medidas[K01 Puntuación media competencia] | — |
| `p1_tarjeta_k03` | card | 195.4, 76, 171.4, 100 | % alumnado en nivel bajo (K03) / Puntuación global < 55 | Values: _Medidas[K03 % alumnado nivel bajo] | — |
| `p1_tarjeta_k06` | card | 374.9, 76, 171.4, 100 | Dispersión de resultados (K06) / Desviación típica | Values: _Medidas[K06 Dispersión de resultados] | — |
| `p1_tarjeta_k10` | card | 554.3, 76, 171.4, 100 | Variación interanual (K10) / Frente a la convocatoria anterior | Values: _Medidas[K10 Variación interanual] | — |
| `p1_tarjeta_estado_k10` | card | 733.7, 76, 171.4, 100 | Estado de la variación (K10) / Semáforo: ±0,5 puntos | Values: _Medidas[Estado K10] | — |
| `p1_tarjeta_k12` | card | 913.1, 76, 171.4, 100 | % competencias que mejoran (K12) / Mejora de 1 punto o más | Values: _Medidas[K12 % competencias que mejoran] | — |
| `p1_tarjeta_alumnos` | card | 1092.6, 76, 171.4, 100 | Alumnos evaluados / Registros de evaluación | Values: _Medidas[Alumnos evaluados] | — |
| `p1_linea_k01_materia` | lineChart | 16, 188, 724, 462 | Evolución de la puntuación media (K01) por competencia / Todas las convocatorias; no se filtra por el segmentador de año | Category: DimAnio[Anio] («Año»); Category: showAll; Series: DimCompetencia[Materia] («Competencia»); Y: _Medidas[K01 Puntuación media competencia] («Puntuación media (K01)»); Orden: DimAnio[Anio] Ascending | — |
| `p1_tabla_materia` | tableEx | 748, 188, 516, 462 | Resumen por competencia / Convocatoria seleccionada | Values: DimCompetencia[Materia] («Competencia»); Values: _Medidas[K01 Puntuación media competencia] («K01 Puntuación media»); Values: _Medidas[K10 Variación interanual] («K10 Variación interanual»); Values: _Medidas[Estado K10] («Estado K10»); Values: _Medidas[K11 Tendencia 5 convocatorias] («K11 Tendencia (5 conv.)»); Values: _Medidas[K03 % alumnado nivel bajo] («K03 % nivel bajo»); Orden: DimCompetencia[Materia] Ascending | — |
| `p1_aviso` | textbox | 16, 658, 1248, 50 |  | Texto: Aviso: Puntuaciones no equiparadas entre convocatorias; 2020 sin prueba (COVID-19) y 2021 se compara con 2019 / Niveles de logro internos del TFG (cortes 55/70/85), no los niveles oficiales. Se oculta un valor si se basa en menos de 30 puntuaciones. | — |

**Página `Tactico_Inspeccion` («Táctico - Inspección», 1280×720, 14 visuales).** Interacciones desactivadas (NoFilter): `p2_seg_anio` → `p2_linea_k01_serie`; `p2_seg_area` → `p2_barras_k07_area`.

| Visual | Tipo | Posición (x, y, ancho, alto) | Título / subtítulo | Campos | Filtros propios |
|---|---|---|---|---|---|
| `p2_cabecera` | textbox | 16, 8, 480, 60 |  | Texto: Visión táctica - Inspección educativa / Comparación territorial y equidad. Puntuaciones no equiparadas entre convocatorias; 2020 sin prueba (COVID-19) y 2021 se compara con 2019 | — |
| `p2_seg_anio` | slicer | 504, 8, 184, 60 | Año | Values: DimAnio[Anio] («Año»); Grupo de sincronización: Anio; Selección única | en DimAnio[Anio] {2025L} |
| `p2_seg_materia` | slicer | 696, 8, 184, 60 | Competencia | Values: DimCompetencia[Materia] («Competencia»); Grupo de sincronización: Materia | — |
| `p2_seg_area` | slicer | 888, 8, 184, 60 | Área territorial | Values: DimContextoCentro[AreaTerritorial] («Área territorial»); Grupo de sincronización: AreaTerritorial | — |
| `p2_seg_genero` | slicer | 1080, 8, 184, 60 | Género | Values: DimPerfilAlumno[Genero] («Género»); Grupo de sincronización: Genero | — |
| `p2_tarjeta_k04` | card | 16, 76, 201.3, 100 | Brecha de género: niños - niñas (K04) / Puntos de diferencia | Values: _Medidas[K04 Brecha de género (Niños - Niñas)] | — |
| `p2_tarjeta_k05` | card | 225.3, 76, 201.3, 100 | Brecha pública - privada (K05) / Puntos de diferencia | Values: _Medidas[K05 Brecha pública - privada] | — |
| `p2_tarjeta_k08` | card | 434.7, 76, 201.3, 100 | Diferencia urbano - rural (K08) / Más de 100.000 hab. frente a hasta 10.000 | Values: _Medidas[K08 Diferencia urbano - rural] | — |
| `p2_tarjeta_k09` | card | 644, 76, 201.3, 100 | Posición del área (K09) / Requiere una sola área en contexto | Values: _Medidas[K09 Posición del área] | — |
| `p2_tarjeta_estado_k01` | card | 853.3, 76, 201.3, 100 | Estado de K01 (área frente a Cataluña) / Semáforo: ±1 punto | Values: _Medidas[Estado K01] | — |
| `p2_tarjeta_estado_k03` | card | 1062.7, 76, 201.3, 100 | Estado de K03 (área frente a Cataluña) / Semáforo: ±2 puntos porcentuales | Values: _Medidas[Estado K03] | — |
| `p2_barras_k07_area` | clusteredBarChart | 16, 188, 410, 520 | Desviación de cada área respecto a Cataluña (K07) / Puntos de diferencia sobre la media de Cataluña | Category: DimContextoCentro[AreaTerritorial] («Área territorial»); Y: _Medidas[K07 Desviación respecto a Cataluña] («Desviación respecto a Cataluña (K07)»); Tooltips: _Medidas[K01 Puntuación media competencia] («Puntuación media (K01)»); Tooltips: _Medidas[K09 Posición del área] («Posición del área (K09)»); Orden: _Medidas[K07 Desviación respecto a Cataluña] Descending | — |
| `p2_matriz_area_naturaleza` | pivotTable | 434, 188, 410, 520 | Puntuación media (K01) por área y titularidad / Centros públicos y privados | Rows: DimContextoCentro[AreaTerritorial] («Área territorial»); Columns: DimContextoCentro[Naturaleza] («Titularidad»); Values: _Medidas[K01 Puntuación media competencia] («Puntuación media (K01)») | — |
| `p2_linea_k01_serie` | lineChart | 852, 188, 412, 520 | Evolución de K01 por serie territorial comparable / Todas las convocatorias | Category: DimAnio[Anio] («Año»); Category: showAll; Series: DimContextoCentro[AreaSerieComparable] («Serie territorial comparable»); Y: _Medidas[K01 Puntuación media competencia] («Puntuación media (K01)»); Orden: DimAnio[Anio] Ascending | — |

**Página `Operativo_Direccion_Centro` («Operativo - Dirección de centro», 1280×720, 14 visuales).** Interacciones desactivadas (NoFilter): `p3_seg_anio` → `p3_linea_k01_cataluna`.

| Visual | Tipo | Posición (x, y, ancho, alto) | Título / subtítulo | Campos | Filtros propios |
|---|---|---|---|---|---|
| `p3_cabecera` | textbox | 16, 8, 1248, 40 |  | Texto: Visión operativa - Dirección de centro / Seleccione el contexto del centro (área, naturaleza, hábitat) para compararlo con Cataluña. Puntuaciones no equiparadas entre convocatorias; 2020 sin prueba (COVID-19) y 2021 se compara con 2019 | — |
| `p3_seg_area` | slicer | 16, 52, 243.2, 60 | Área territorial | Values: DimContextoCentro[AreaTerritorial] («Área territorial»); Grupo de sincronización: AreaTerritorial | — |
| `p3_seg_naturaleza` | slicer | 267.2, 52, 243.2, 60 | Titularidad | Values: DimContextoCentro[Naturaleza] («Titularidad»); Grupo de sincronización: Naturaleza | — |
| `p3_seg_habitat` | slicer | 518.4, 52, 243.2, 60 | Hábitat | Values: DimContextoCentro[Habitat] («Hábitat»); Grupo de sincronización: Habitat | — |
| `p3_seg_anio` | slicer | 769.6, 52, 243.2, 60 | Año | Values: DimAnio[Anio] («Año»); Grupo de sincronización: Anio; Selección única | en DimAnio[Anio] {2025L} |
| `p3_seg_materia` | slicer | 1020.8, 52, 243.2, 60 | Competencia | Values: DimCompetencia[Materia] («Competencia»); Grupo de sincronización: Materia | — |
| `p3_tarjeta_k01` | card | 16, 120, 243.2, 96 | Puntuación media del contexto (K01) / Competencias globales | Values: _Medidas[K01 Puntuación media competencia] | — |
| `p3_tarjeta_k07` | card | 267.2, 120, 243.2, 96 | Desviación respecto a Cataluña (K07) / Puntos de diferencia | Values: _Medidas[K07 Desviación respecto a Cataluña] | — |
| `p3_tarjeta_cataluna` | card | 518.4, 120, 243.2, 96 | Puntuación media de Cataluña / Referencia sin filtros de contexto | Values: _Medidas[Puntuación media Cataluña] | — |
| `p3_tarjeta_estado_k01` | card | 769.6, 120, 243.2, 96 | Estado de K01 (contexto frente a Cataluña) / Semáforo: ±1 punto; sin contexto, variación interanual (±0,5) | Values: _Medidas[Estado K01] | — |
| `p3_tarjeta_estado_k03` | card | 1020.8, 120, 243.2, 96 | Estado de K03 (contexto frente a Cataluña) / Semáforo: ±2 puntos porcentuales | Values: _Medidas[Estado K03] | — |
| `p3_barras_k02_subcomp` | clusteredBarChart | 16, 228, 410, 480 | Puntuación media por subcompetencia (K02) / Excluye datos no válidos | Category: DimCompetencia[Subcompetencia] («Subcompetencia»); Series: DimCompetencia[Materia] («Competencia»); Y: _Medidas[K02 Puntuación media subcompetencia] («Puntuación media (K02)»); Orden: _Medidas[K02 Puntuación media subcompetencia] Descending | — |
| `p3_barras100_nivel` | hundredPercentStackedBarChart | 434, 228, 410, 480 | Distribución por nivel de logro / Puntuaciones globales; mismas exclusiones y mínimo de 30 que K03 | Category: DimCompetencia[Materia] («Competencia»); Series: DimNivelLogro[Nivel] («Nivel de logro»); Y: _Medidas[Puntuaciones por nivel de logro] («Puntuaciones por nivel de logro») | NO en DimNivelLogro[Nivel] {'No aplica (subcompetencia)'} |
| `p3_linea_k01_cataluna` | lineChart | 852, 228, 412, 480 | Evolución: contexto seleccionado frente a Cataluña / Todas las convocatorias | Category: DimAnio[Anio] («Año»); Category: showAll; Y: _Medidas[K01 Puntuación media competencia] («Contexto seleccionado (K01)»); Y: _Medidas[Puntuación media Cataluña] («Cataluña»); Orden: DimAnio[Anio] Ascending | — |

### 8.5 Organización del repositorio (estructura real el 12/11/2026)

```
TFG_Project/
  README.md
  Datos.zip                       dataset comprimido (versionado); Datos.csv (240 MB) en la raíz, no versionado (.gitignore)
  Documentation/
    GEP/                          entregas de gestión de proyectos
    Reuniones/<fecha>/            notas de las reuniones con las directoras
    Docu_Final/
      Memoria/Latex_Memoria/      main.tex, bibliografia.bib, imagenes/<capítulo>/, compilar.sh (Tectonic + Pandoc -> PDF y .docx)
      Docu_Parcial/               01_Informe_calidad_datos.md, 02_Modelo_y_diccionario.md, 03_Fichas_KPI.md, 04_Guia_de_uso.md
  PowerBI/                        proyecto Power BI en formato PBIP (texto, versionable). GENERADO: no se edita a mano
    CMI_Educacion_Primaria.pbip
    CMI_Educacion_Primaria.SemanticModel/
      .platform, .pbi/editorSettings.json   (escritos por Power BI Desktop; se conservan)
      definition.pbism
      definition/database.tmdl, model.tmdl, expressions.tmdl (RutaDatos y stg_Evaluaciones), relationships.tmdl
      definition/tables/*.tmdl    las 8 tablas y _Medidas.tmdl
      definition/cultures/es-ES.tmdl        (metadatos lingüísticos escritos por Desktop; se conservan)
    CMI_Educacion_Primaria.Report/
      .platform, .pbi/            (Desktop; se conservan)
      definition.pbir, definition/report.json, version.json, pages/pages.json
      definition/pages/<página>/page.json y visuals/<visual>/visual.json   (3 páginas, 41 visuales)
      StaticResources/SharedResources/BaseThemes/CY24SU10.json
  trabajo_en_curso/               carpeta de trabajo (no es entregable)
    contrato_diseno.md, ESTADO.md
    generadores/                  gen_modelo.py + modelo/m_*.m (modelo TMDL y PBIP), gen_medidas.py (_Medidas.tmdl), gen_pbir.py (informe),
                                  pbir_referencias.json, gen_modelo_conceptual.py, gen_arquitectura.py, gen_casos_uso.py, gen_mockups.py (figuras PNG con Pillow)
    herramientas/                 tmdlcheck/ (TOM, .NET), tmdldump/, mparser/ (parser oficial de M, Node), validar_m.py, validar_pbir.py, verificar_claves.py
    referencias_pbir/             documentación y ejemplos del formato PBIR
    workflows/                    scripts de los flujos de trabajo con Claude Code
    week2/                        GUIA_AGENTES.md, DECISIONES.md, PROGRESO_*.md, analisis/evidencia_cuestiones_abiertas.py
  validacion/                     validación independiente en Python (DuckDB, pyarrow, pandas)
    README.md, requirements.txt
    etl_referencia.py             réplica de la ETL -> salida/*.parquet (no versionada)
    test_modelo.py                31 tests de integridad
    kpis_referencia.py            KPIs de referencia -> resultados/*.csv (7 CSV versionados)
    perfilado/                    scripts y salidas de la auditoría de calidad (T7)
```

Control de versiones (RNF10): todo el proyecto Power BI está en texto (TMDL y JSON), así que `git diff` muestra cualquier cambio del modelo o del informe; no hay ningún `.pbix`. `.gitignore` excluye `Datos.csv`, `.venv/`, `validacion/salida/`, `node_modules/` y los binarios de las herramientas; `PowerBI/.gitignore` excluye `.pbi/localSettings.json` y `.pbi/cache.abf`. Flujo de cambio: editar generador o `m_*.m` → regenerar (`gen_modelo.py PowerBI`, `gen_medidas.py …/_Medidas.tmdl`, `gen_pbir.py`) → `etl_referencia.py`, `test_modelo.py`, `kpis_referencia.py` → `tmdlcheck`, `validar_m.py`, `validar_pbir.py`, `verificar_claves.py` → abrir en Power BI Desktop. Los generadores conservan lo que Desktop añade al guardar (D-19).

### Cifras de validación para citar (12/11/2026)

`etl_referencia.py`: 8 tablas, 1.102.324 evaluaciones y 17.728.085 puntuaciones en 9,3 s. `test_modelo.py`: 31 de 31 tests. `kpis_referencia.py`: 7 CSV; 72 de 72 medias dentro de 0,5 (máximo 0,30), 70 de 72 dentro de 0,2. `tmdlcheck` (TOM): 9 tablas, 20 medidas, 9 relaciones, `Model.Validate()` 0 errores. `validar_m.py`: 11 de 11 bloques M correctos. `validar_pbir.py`: 49 ficheros validados contra 7 esquemas, 41 visuales, 27 campos referenciados (9 columnas, 18 medidas), 0 errores y 0 avisos. `verificar_claves.py`: 0 fallos (dimensiones reconstruidas desde el M idénticas al parquet; 0 combinaciones huérfanas en el dominio de staging; 85 contextos y 169 perfiles observados en los hechos).

<!-- D-D01 en adelante: agente de diseño (capítulo 8, issues #11 y #13), 13/11/2026. Progreso en PROGRESO_diseno.md. -->

## D-D01 `ÁreaTerritorial` en la correspondencia del diseño lógico
- Problema: el modelo conceptual (7.2, `modelo_conceptual.png`) tiene una clase `ÁreaTerritorial` asociada a `ContextoDeCentro`, pero la tabla de correspondencia de «Datos para el capítulo 8» (D-17) no la nombra.
- Opciones: (a) omitirla; (b) añadir una dimensión de áreas encadenada a `DimContextoCentro` (copo de nieve); (c) decir que se funde con `ContextoDeCentro` en `DimContextoCentro`.
- Decisión: (c). En la Tabla `tab:correspondencia` del 8.1.1 la fila es «ContextoDeCentro y ÁreaTerritorial → DimContextoCentro»; sus atributos `serieComparable` y `conRupturaDeSerie` son las columnas `AreaSerieComparable` y `AreaConRupturaSerie`.
- Justificación: es lo que hace el modelo implementado (`m_DimContextoCentro.m`); Kimball recomienda dimensiones desnormalizadas en lugar de copos de nieve, y con 15 áreas repetir sus atributos en 120 filas no cuesta nada. Sin cambios en el modelo.
- Cambios aplicados: `main.tex` (8.1.1).

## D-D02 Contenido de la figura del esquema en estrella
- Problema: la figura debe dibujar las 8 tablas, sus claves y las 9 relaciones; con todas las columnas (hasta 13 por dimensión) no se leería al ancho de la página.
- Opciones: (a) todas las columnas; (b) solo las claves; (c) claves y las columnas principales, con el diccionario (8.1.4) como referencia completa.
- Decisión: (c). Cada caja lleva el nombre, «hechos» o «dimensión» con su número de filas, la clave primaria (PK) o las claves externas (FK) y de 1 a 4 columnas principales. Cada relación sale de la fila de la FK y llega a la de la PK, con «*» en el lado de los hechos y «1» en el de la dimensión. La leyenda indica que filtran en un solo sentido. `EvaluacionID` no se marca como PK porque ninguna relación la usa. Las dimensiones solo de `FactPuntuacion` van a la izquierda y las conformadas entre los dos hechos, de modo que ninguna línea se cruza.
- Justificación: legibilidad a 15 cm de ancho, y el diccionario ya lista todas las columnas.
- Cambios aplicados: `trabajo_en_curso/generadores/gen_esquema_estrella.py` (nuevo), `Latex_Memoria/imagenes/diseno/esquema_estrella.png`.

## D-D03 Fichas de los KPIs: tabla compacta y tres fórmulas DAX
- Problema: el comentario guía del 8.3.1 pedía «una ficha por KPI: definición, fórmula DAX, filtros que respeta y perspectiva»; 12 fichas completas con su DAX (y las 20 medidas) ocuparían más de 10 páginas y repetirían `03_Fichas_KPI.md`.
- Opciones: (a) 12 fichas en tablas `[H]`; (b) una `longtable` con una fila por KPI agrupada por perspectiva y el DAX de unas pocas medidas representativas; (c) solo remitir al documento.
- Decisión: (b). Tabla `tab:fichas_kpis` (KPI, cálculo, filtros y exclusiones, panel) y el DAX de K01 (mínimo de 30 y filtro de globales) y K10 (navegación por `IndiceConvocatoria` y periodo de diseño); K03 se describe en una frase (en la primera versión iba también su DAX, que se quitó para acercar el capítulo a la extensión orientativa). Las fórmulas se copian de `gen_medidas.py` sin cambiar nada; solo K10 se reindenta con dos espacios por nivel y va en `\footnotesize` para que ninguna línea pase de 80 caracteres. Las fichas completas quedan en `03_Fichas_KPI.md`.
- Justificación: extensión orientativa del capítulo (12–18 páginas) y la regla de no repetir contenido de otro documento.
- Cambios aplicados: `main.tex` (8.3.1).

## D-D04 Disposición final de los paneles generada desde el informe
- Problema: el 8.4.2 debe mostrar el diseño final de los paneles, pero no hay capturas de Power BI Desktop (el informe no se ha vuelto a abrir desde el 15/10/2026) y dibujar bocetos nuevos a mano podría no coincidir con el informe.
- Opciones: (a) solo texto; (b) capturas (requieren Power BI Desktop); (c) figuras generadas a partir de los `visual.json` del informe.
- Decisión: (c). Nuevo `trabajo_en_curso/generadores/gen_paneles_diseno.py`, que lee la posición, el tipo, el título, el subtítulo y los campos de cada visual y los dibuja a escala sobre el lienzo de 1280 × 720 (`imagenes/diseno/panel_estrategico.png`, `panel_tactico.png`, `panel_operativo.png`). Las cabeceras y el aviso reproducen el texto del informe.
- Justificación: la figura no puede contradecir el informe porque sale de él, y se regenera si el informe cambia. Cuando haya capturas reales de Power BI Desktop pueden sustituirlas o acompañarlas (lo decide la estudiante).
- Cambios aplicados: generador nuevo, tres PNG, `main.tex` (8.4.2).
- Observación: la cabecera del panel operativo dice «(área, naturaleza, hábitat)», mientras que el segmentador y la memoria dicen «Titularidad» (D-15). Es un texto de `gen_pbir.py`; no se ha tocado porque queda fuera del capítulo 8. Propuesta: cambiarlo por «(área, titularidad, hábitat)» y regenerar el informe y la figura.

## D-D05 Fuente de la paleta de los niveles de logro
- Problema: el 8.4.1 dice que la paleta PuOr de ColorBrewer se distingue con deuteranopía y protanopía (RNF05), y la memoria no tenía ninguna referencia de ColorBrewer.
- Opciones: (a) sin cita; (b) citar la web; (c) citar el artículo de ColorBrewer.
- Decisión: (c). `harrower2003colorbrewer`: M. Harrower y C. A. Brewer, «ColorBrewer.org: An Online Tool for Selecting Colour Schemes for Maps», The Cartographic Journal, 40(1), 27–37, 2003, DOI 10.1179/000870403235002042 (comprobado en Crossref el 13/11/2026).
- Justificación: es la publicación de referencia de la herramienta. El cumplimiento de RNF05 se comprobará en la validación; el texto no lo da por comprobado.
- Cambios aplicados: `bibliografia.bib`, `main.tex` (8.4.1).
