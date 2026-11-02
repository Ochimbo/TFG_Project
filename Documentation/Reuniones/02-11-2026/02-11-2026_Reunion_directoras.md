# Reunión de seguimiento del TFG

**Cuadro de Mando Integral para el soporte a la toma de decisiones en la educación primaria de Cataluña**

| | |
|---|---|
| Estudiante | Kiara Kristin Rodríguez Uribe |
| Directoras | Carme Martín Escofet · Maria Hitz Martinez |
| Fecha | 2 de noviembre de 2026 · 60 min |
| Momento del Gantt | Semana 8: fin de la fase de análisis e inicio del diseño del modelo |
| Objetivo | Presentar la fase de análisis y **validar con vosotras las decisiones abiertas** antes de construir |

> **Cómo usar este documento:** el texto normal es el guion de la exposición. Los bloques ** Si preguntan…** son notas de apoyo plegadas (clic para desplegar). Solo se abren si surge una pregunta concreta.

---

## Agenda (60 min)

| Min | Tema | Tareas del Gantt |
|---|---|---|
| 0–5 | 1. Estado según la planificación | T1–T6 |
| 5–15 | 2. Auditoría de calidad de los datos: qué he encontrado y cómo | T7 · T12 |
| 15–22 | 3. Requisitos por perfil y catálogo de KPIs | T8 · T9 |
| 22–27 | 4. Diseño del modelo dimensional (en curso) | T10 |
| 27–55 | **5. Cuestiones abiertas: vuestra validación**  | T9 · T10 · T12 |
| 55–60 | 6. Próximos pasos y, brevemente, el prototipo | — |

---

## 1. Estado según la planificación (5 min)

| Tarea | Semanas | Estado |
|---|---|---|
| T1–T4 Entregables de GEP (hito H1) | 1–4 | ✓ Entregados |
| T7 Perfilado y auditoría del dataset | 1–3 | ✓ Informe de calidad con 34 reglas |
| T8 Análisis de requisitos por perfil | 4–5 | ✓ 3 perfiles con sus preguntas de decisión (para validar hoy) |
| T9 Catálogo de KPIs del CMI | 6–7 | ✓ 12 KPIs en 4 perspectivas, con fichas |
| T12 ETL I: limpieza y homogeneización | 5–7 | ✓ Reglas definidas y probadas sobre el fichero completo |
| T10 Diseño del modelo dimensional | 8 | ⇄ Diseño hecho y en revisión (hoy) |
| T5 / T6 Seguimiento y memoria | continuas | ⇄ Hay documentación técnica reutilizable en la memoria |

**Conclusión:** voy al día según el Gantt, sin desviaciones. El riesgo R1 (inconsistencias en los datos) **se ha materializado**, pero se ha absorbido en T7/T12 sin necesidad del plan B.

<details>
<summary> Si preguntan: ¿qué era el riesgo R1 y por qué no ha hecho falta el plan B?</summary>

- **R1 (GEP2/GEP4):** «Inconsistencias en los datos fuente mayores de lo previsto». Probabilidad estimada: media (30 %); impacto: alto.
- **Plan B previsto:** reglas adicionales de limpieza (+20 h) y, en el peor caso, recortar el histórico a 2018–2025, el periodo con esquema estable.
- **Qué ha pasado:** las inconsistencias han aparecido (son las de la sección 2), pero todas se han podido tratar con reglas sin perder años. Se conserva el histórico completo, 2009–2025, que es lo que da valor a los KPIs de evolución.
- **Coste:** la auditoría ha sido más profunda de lo previsto, pero ha cabido en las horas de T7 y T12 (30 h + 35 h).
</details>

---

## 2. Auditoría de calidad de los datos (T7 · T12) — 10 min

### Cómo lo he hecho

1. **Perfilado sistemático** de las 32 columnas con Python + DuckDB. Leo el CSV entero **como texto** para que ninguna conversión de tipos esconda un valor anómalo.
2. **Evaluación por dimensiones de calidad** (ISO/IEC 25012): completitud, validez, consistencia y unicidad, más una dimensión propia de **comparabilidad temporal**, clave para un CMI que mide evolución.
3. **Verificación independiente:** unos scripts escritos desde cero, con otra vía de lectura del fichero, reproducen cada cifra.
4. **Contraste externo:** medias frente a los 16 *Quaderns d'avaluació* oficiales (2009–2025), metadatos oficiales del portal y decretos de reorganización territorial.
5. **Criterio de limpieza:** solo corrijo lo que es **demostrablemente un error**. Lo demás se conserva y se **marca con un indicador de calidad**. No se borra ningún registro.

<details>
<summary> Si preguntan: herramientas y por qué estas</summary>

- **Python + DuckDB** (con pandas y pyarrow), en un entorno virtual del proyecto.
- **¿Por qué DuckDB?** Es un motor SQL analítico que lee directamente el CSV de 240 MB y 1,1 M de filas en segundos, sin montar una base de datos. Permite consultas SQL reproducibles.
- **¿Por qué leer todo como texto?** Si se dejan inferir los tipos, un valor raro (por ejemplo «Fins a 10001» o una coma decimal) se convierte en nulo o se descarta sin avisar. Leyendo como texto, cada anomalía se ve.
- **Puntuaciones en centésimas enteras** («87,70» → 8770): así no hay errores de coma flotante al comparar valores exactos (necesario para detectar los suelos artificiales o los límites 55,00/70,00/85,00).
- Power BI se usa para el producto final; la auditoría se hace fuera para que sea **reproducible y auditable** con scripts.
</details>

<details>
<summary> Si preguntan: ¿qué son las dimensiones de calidad ISO/IEC 25012?</summary>

| Dimensión | Qué se comprueba | Ejemplo en el dataset |
|---|---|---|
| Completitud | Hay valor donde debería | `CODI_ALUMNE` vacío en 2009–2015 (40,72 % de las filas) |
| Validez | El valor está en su dominio y rango | Puntuaciones en [0,100]; hábitat «Fins a 23357» no válido |
| Consistencia | El mismo hecho se codifica igual; los campos relacionados cuadran | H/D frente a Home/Dona; la global no cuadra con sus subcompetencias en castellano 2017 |
| Unicidad | No hay duplicados | 914 alumnos en dos convocatorias consecutivas (repetidores, no duplicados) |
| Comparabilidad temporal *(añadida)* | Los años miden lo mismo | Pesos que cambian, 2020 sin prueba, mapa territorial nuevo en 2024 |
</details>

<details>
<summary> Si preguntan: ¿cómo funciona la verificación independiente?</summary>

- **Paso 1:** dos scripts de perfilado (columnas categóricas y de puntuación) documentan cada hallazgo con su consulta, cifra, impacto y regla propuesta.
- **Paso 2:** otros dos scripts, **escritos desde cero** y con **otra vía de lectura** (pyarrow y lectura línea a línea con el número de línea real), reproducen cada cifra sin reutilizar el código anterior.
- **Resultado:** **38 de 41 hallazgos confirmados**. Se corrigieron 3 recuentos, y la verificación encontró problemas nuevos (los suelos artificiales de inglés 2015 y la magnitud real del problema de 2010).
- **Paso 3:** el informe final usa solo cifras confirmadas.
- Todo está en `validacion/perfilado/` (scripts y salidas), así que cualquier cifra se puede regenerar.
</details>

### Qué he encontrado (los 5 hallazgos clave)

| # | Hallazgo | Cómo lo detecté | Tratamiento |
|---|---|---|---|
| 1 | **Columnas rotadas en origen** (castellano 2017, francés 2016) | Regresión de la global sobre sus subcompetencias: daba pesos imposibles | Reasignar las columnas. Castellano 2017 pasa de 74,30 a **73,51**, frente al **73,4 oficial** ✔️ |
| 2 | **2010 desalineado:** el hábitat y el año de nacimiento no corresponden al alumno | Combinaciones imposibles; el efecto de la edad desaparece | Marcar como «No fiable (2010)» |
| 3 | **Codificaciones que cambian por año** | Frecuencias de valores por año | Normalizar con mapeos explícitos |
| 4 | **Rupturas temporales** (2020, mapa territorial, pesos, puntuaciones no equiparadas) | Cobertura por año, regresión de pesos y decretos | Índice de convocatoria, series comparables y nota de «no equiparada» |
| 5 | **Suelos artificiales** en inglés 2015 y catalán 2018 | Histogramas por año | Indicador de calidad «censurada» |

<details>
<summary> Hallazgo 1 en detalle: columnas rotadas</summary>

- **Idea:** la nota global de cada materia es una media ponderada de sus subcompetencias (por ejemplo, castellano 2016: 0,60·comprensión lectora + 0,40·expresión escrita). Si se hace una regresión de la global sobre las subcompetencias, deberían salir esos pesos.
- **Castellano 2017 (71.036 alumnos):**
  - La regresión de `PCAST` daba pesos **−0,67 y 1,67**, imposibles.
  - En cambio, la columna `PCAST_EE` = 0,6·`PCAST` + 0,4·`PCAST_CL` en el **99,07 %** de las filas.
  - Es decir: la global real está en `PCAST_EE`, la comprensión lectora real en `PCAST` y la expresión escrita real en `PCAST_CL`.
  - La correlación con las subcompetencias de catalán del mismo año lo confirma de forma independiente.
  - **Efecto:** la media pasa de 74,30 a **73,51** (oficial **73,4**) y la desviación típica de 19,63 a 16,55.
- **Francés 2016 (389 alumnos):** la misma situación con 4 columnas; la fórmula 0,35·CO + 0,50·CE + 0,15·EE cuadra en el **100 %** de las filas tras reordenarlas.
- **Corrección:** se reasignan las columnas solo en ese año. Un test automático comprueba que, tras la corrección, la global cuadra con sus subcompetencias en ≥ 99 % de las filas, y que sobre el CSV original sin corregir **no** cuadra (control negativo).
</details>

<details>
<summary> Hallazgo 2 en detalle: 2010 desalineado</summary>

- **Síntoma:** en 2010 aparecen combinaciones área × hábitat que no existen en ningún otro año. Por ejemplo, el Consorci d'Educació de Barcelona (la ciudad) tiene 744 alumnos en municipios de **menos de 10.000 habitantes**, y Terres de l'Ebre 505 en municipios de **más de 100.000**.
- **Magnitud:** 7.252 filas imposibles (12,2 % del año). Comparando con 2009 y 2011, la cota inferior es de **al menos 15.186 filas mal asignadas (25,6 %)**.
- **Mecanismo:** siguiendo el orden del fichero, el hábitat cambia de valor 198 veces en 2010 frente a 448 y 490 en 2009 y 2011, mientras que el área cambia un número parecido de veces. Es un **desplazamiento por bloques**: el valor pertenece a otra fila.
- **El año de nacimiento tiene el mismo problema:** la diferencia de nota en matemáticas entre los alumnos de 12 y 13 años es de **−0,05 puntos en 2010**, frente a 10–17 puntos en el resto de años.
- **Lo que sí es fiable en 2010:** área, naturaleza, género, mes de nacimiento y puntuaciones (la correlación de medias por área con 2009 es 0,945).
- **Decisión propuesta:** hábitat y edad de 2010 = «No fiable», con nota (cuestión 6).
</details>

<details>
<summary> Hallazgo 3 en detalle: codificaciones</summary>

| Columna | Variantes | Años | Filas afectadas |
|---|---|---|---|
| `GENERE` | H/D · Home/Dona | Home/Dona solo en 2021 | 73.674 |
| `NATURALESA` | Públic/Privat · Pública/Privada | Pública/Privada en 2024–2025 | 139.291 |
| `HÀBITAT` | «Més de 100000» · «Més de 100001» | 2024–2025 | 53.512 |
| `HÀBITAT` | «Fins a 10001»… «Fins a 23357» | 2024 | 13.357 (arrastre de celda en Excel) |
| `AREA_TERRITORIAL` | vacío | 2024 | 1 fila |

- **Sin normalizar**, la brecha de género no tendría datos en 2021 y la brecha pública–privada no los tendría en 2024–2025.
- La regla es **explícita**: cualquier valor no previsto hace fallar la carga, en lugar de pasar en silencio.
- «Privada» incluye la concertada: el dataset no las distingue.
</details>

<details>
<summary> Hallazgo 4 en detalle: rupturas temporales</summary>

- **2020:** no hubo prueba por la COVID-19 (Quadern 50: «no es va poder dur a terme l'avaluació de sisè… programada per al mes de maig del 2020»).
- **Mapa territorial en 2024** (Decret 59/2022 y Decret 120/2023, operativos desde octubre de 2023):
  - Se crea **Penedès** (Alt Penedès y Garraf, que venían de Barcelona Comarques; Baix Penedès, de Tarragona; Anoia, de Catalunya Central).
  - Se crea **Alt Pirineu i Aran** (comarcas que venían de Lleida y la Cerdanya, de Girona y Lleida).
  - **Barcelona Comarques** pasa a llamarse **Barcelonès**. En el dataset, 2024 todavía lleva el nombre antiguo y 2025 el nuevo.
  - Filas 2023 → 2024: Barcelona Comarques 8.211 → 5.386; Catalunya Central 5.565 → 4.106; Tarragona 6.485 → 5.164; Lleida 4.066 → 3.466.
- **Pesos de las subcompetencias:** cambian en 2011, 2012, 2013, 2016, 2017 y 2018. Por eso la nota global nunca se recalcula: hacerlo con una media simple daría errores de hasta 19 puntos.
- **Puntuaciones no equiparadas:** cada año la prueba es distinta y el Consell no publica una escala común (Quadern 68). Comparar 74 de un año con 72 de otro no garantiza que el alumnado sepa menos: la prueba puede haber sido más difícil.
- **Diseños de prueba:** catalán y castellano cambian en 2018 (se añade comprensión oral); matemáticas en 2017; inglés en 2016–2017; ciencias empieza en 2018.
</details>

<details>
<summary> Hallazgo 5 en detalle: suelos artificiales</summary>

- **Qué es:** muchos alumnos con exactamente la misma nota mínima, por encima de 0. Indica que en origen se recortó la escala.
- **Casos:** catalán expresión escrita 2018 (suelo en 49,40); inglés 2015, global (48,79), comprensión oral (53,19) y comprensión lectora (45,00).
- **Ejemplo:** en inglés 2015, 8.801 de los 14.733 alumnos en nivel bajo están exactamente en el suelo.
- **Efecto:** distorsiona el % en nivel bajo y la dispersión.
- **Tratamiento:** se conservan las notas y se marcan como «censurada»; los KPIs de % en nivel bajo y de dispersión las excluyen (cuestión 5).
- Además, la expresión escrita de inglés 2015 tiene una escala anómala y se marca como «no válida» (68.342 celdas, cuestión 9).
</details>

**Resultado del contraste:** **70 de las 72 medias** por materia y año coinciden con las oficiales dentro de ±0,2 puntos.

<details>
<summary> Si preguntan: ¿qué pasa con las 2 que no cuadran? ¿Y otros datos curiosos?</summary>

- **Inglés 2016:** 73,94 frente a 73,7 oficial (+0,24). No es redondeo ni un error de carga. Causa más probable: ese año la escala está comprimida (la global no llega a 100; el máximo es 95,55).
- **Francés 2024:** 62,80 frente a 62,5 (+0,30). Muy pocos alumnos: 266 en el CSV frente a 272 oficiales. Unos pocos alumnos de diferencia mueven la media.
- **Diferencia media en las 70 restantes:** unos 0,05 puntos.
- **Identificador de alumno (`CODI_ALUMNE`):** no existe antes de 2016. Desde 2016, 914 alumnos aparecen en dos convocatorias consecutivas; casi todos tienen un año más en la segunda, así que son **repetidores**, no duplicados.
- **Edad:** el 92–97 % del alumnado de cada año tiene 12 años (la edad teórica); el resto, sobre todo 13 (retraso de un curso).
</details>

<details>
<summary> Si preguntan: ¿qué son las 34 reglas de limpieza?</summary>

| Grupo | Reglas | Qué hacen |
|---|---|---|
| Carga y formato | R01–R02, R05 | Lectura como texto, identificador de fila, coma decimal, rango [0,100]; los vacíos son nulos, nunca 0 |
| Correcciones de errores | R03–R04 | Rotaciones de castellano 2017 y francés 2016 |
| Identificador de alumno | R06–R08 | No se usa como clave; no se deduplica; repetidores marcados |
| Normalización de códigos | R09–R11, R13 | Género, naturaleza, hábitat y área vacía |
| Datos no fiables | R12, R16–R21 | Hábitat y edad de 2010; edad fuera de rango; fechas de relleno |
| Territorio | R14–R15 | Perímetros y series comparables tras 2024 |
| Calidad de las notas | R23–R28 | Globales incoherentes, suelos, escalas anómalas y niveles no comparables |
| Niveles y diseño | R29–R32 | Umbrales de nivel, francés informativo, periodos de diseño |
| Controles | R33–R34 | Despivotado sin borrar y comprobaciones que hacen fallar la carga si algo no cuadra |

El detalle de cada regla, con las filas afectadas, está en el informe de calidad, §5.
</details>

---

## 3. Requisitos por perfil y catálogo de KPIs (T8 · T9) — 7 min

### Perfiles y preguntas de decisión (T8)

| Perfil | Nivel de decisión | Preguntas que debe poder responder |
|---|---|---|
| **Departamento de Educación** | Estratégico | ¿Cómo evolucionan las competencias en Cataluña? ¿Crece el alumnado en nivel bajo? ¿Qué materias mejoran? |
| **Inspección y coordinación territorial** | Táctico | ¿Qué áreas se desvían de la media? ¿Hay brechas de género, de titularidad o de hábitat? ¿Dónde priorizar el refuerzo? |
| **Dirección de centro** | Operativo | ¿Cómo rinden los centros de mi contexto frente a Cataluña? ¿En qué subcompetencias hay carencias? |

**Limitación detectada:** el dataset **no incluye el código de centro**. El perfil de Dirección verá **centros de contexto similar** (cuestión 11).

<details>
<summary> Si preguntan: ¿de dónde salen estos perfiles y requisitos?</summary>

- Parten de los **stakeholders definidos en el GEP1** (tabla de agentes implicados) y de los **tres niveles de decisión** clásicos de los sistemas de información: estratégico, táctico y operativo.
- Las preguntas de decisión se han acotado a **lo que el dataset permite responder**. Por ejemplo, no hay datos socioeconómicos ni de centro, así que no se pueden plantear preguntas sobre un centro concreto ni sobre el nivel socioeconómico.
- **No ha habido entrevistas con usuarios reales**: esta reunión sirve precisamente para validar los requisitos, y la validación con usuarios está prevista en T21 (prueba de usabilidad).
- Los requisitos funcionales y no funcionales (RF01–RF06 y RNF01–RNF05) son los del GEP4 §3.3.
</details>

### Catálogo de KPIs (T9)

**Cómo:** CMI de Kaplan y Norton adaptado al sector público según Niven. Cada KPI tiene una ficha (documento 03) con su objetivo, fórmula, interpretación, exclusiones y valores de referencia.

| Perspectiva | KPIs |
|---|---|
| Rendimiento académico | K01 media por competencia · K02 media por subcompetencia · K03 % alumnado en nivel bajo |
| Equidad e inclusión | K04 brecha de género · K05 brecha pública–privada · K06 dispersión |
| Territorio y entorno | K07 desviación respecto a Cataluña · K08 diferencia urbano–rural · K09 posición del área |
| Eficiencia y progreso | K10 variación interanual · K11 tendencia de 5 convocatorias · K12 % de competencias que mejoran |

<details>
<summary> Si preguntan: ¿por qué estas 4 perspectivas y no las 4 clásicas del CMI?</summary>

- **CMI clásico** (Kaplan y Norton, 1992): financiera, clientes, procesos internos, y aprendizaje y crecimiento. Está pensado para empresas con ánimo de lucro.
- **Sector público** (Niven, 2008): la **misión** pasa a la cúspide y la perspectiva financiera deja de ser el objetivo final. Además, este dataset **no tiene datos económicos**.
- **Equivalencias:**

| Perspectiva del CMI | Equivalente clásico | Justificación |
|---|---|---|
| Rendimiento académico | Clientes / resultados | El «resultado» que recibe el ciudadano es el aprendizaje |
| Equidad e inclusión | Procesos internos | Mide si el sistema funciona igual para todos |
| Territorio y entorno | Procesos internos | Mide el equilibrio entre territorios |
| Eficiencia y progreso | Aprendizaje y crecimiento | Mide la mejora del sistema en el tiempo |
</details>

<details>
<summary> Si preguntan: ¿qué calcula exactamente cada KPI?</summary>

| KPI | Definición (en palabras) | Unidad |
|---|---|---|
| K01 | Media de las notas globales de la materia | puntos (0–100) |
| K02 | Media de las notas de subcompetencia (excluye las celdas no válidas) | puntos |
| K03 | % de notas globales por debajo de 55 (excluye las censuradas y los años no comparables) | % |
| K04 | Media de los niños − media de las niñas | puntos (+ = ventaja de los niños) |
| K05 | Media de la pública − media de la privada | puntos (− = ventaja de la privada) |
| K06 | Desviación típica de las notas globales | puntos |
| K07 | Media del contexto filtrado − media de Cataluña | puntos |
| K08 | Media en municipios de más de 100.000 hab. − media en municipios de hasta 10.000 | puntos |
| K09 | Ranking del área por K01 (1 = mejor) | posición |
| K10 | Media del año − media de la convocatoria anterior (2021 se compara con 2019) | puntos |
| K11 | (Media actual − media de hace 4 convocatorias) / 4 | puntos por convocatoria |
| K12 | % de materias con K10 ≥ +1 punto (sin francés) | % |

- **Mínimo muestral:** si hay menos de 30 notas en el contexto, el KPI se muestra vacío. Evita conclusiones sobre grupos muy pequeños (por ejemplo, francés en un área concreta).
- **Semáforos:**
  - **Estado K01:** desviación respecto a Cataluña ≥ +1 punto → favorable; ≤ −1 → desfavorable.
  - **Estado K03:** % en nivel bajo 2 pp por debajo de Cataluña → favorable; 2 pp por encima → desfavorable.
  - **Estado K10:** variación ≥ +0,5 → favorable; ≤ −0,5 → desfavorable.
</details>

<details>
<summary> Si preguntan: ¿qué dicen los datos? (Cataluña, 2025)</summary>

| Materia | K01 media | K03 % nivel bajo | K04 niños − niñas | K05 pública − privada | K10 respecto a 2024 |
|---|---|---|---|---|---|
| Catalán | 73,5 | 14,2 % | −4,0 | −5,2 | −1,3 |
| Castellano | 76,5 | 9,8 % | −4,4 | −4,4 | +2,6 |
| Matemáticas | 70,4 | 22,7 % | **+4,6** | −4,3 | −3,9 |
| Inglés | 75,7 | 15,4 % | −3,4 | **−8,7** | +2,5 |
| Ciencias | 66,3 | 26,9 % | +0,6 | −4,0 | **−8,2** |

- **Género:** las niñas puntúan más en lenguas; los niños, en matemáticas.
- **Titularidad:** la privada supera a la pública en todas las materias; la brecha mayor es en inglés.
- **Nivel bajo global:** pasa del 13,7 % (2021) al **17,8 % (2025)**.
- **Territorio (catalán 2025):** el Consorci de Barcelona es 1.º (+1,5 sobre Cataluña) y el Barcelonès, 12.º (−3,5).
- ⚠️ Las variaciones entre años son de puntuaciones **no equiparadas** (cuestión 2).
</details>

---

## 4. Diseño del modelo dimensional (T10) — 5 min

**Cómo:** metodología de Kimball: primero se declara el grano, después las dimensiones y por último los hechos.

- **Dos tablas de hechos:** `FactEvaluacion` (alumno × convocatoria, 1,1 M de filas) y `FactPuntuacion` (alumno × competencia, 17,7 M).
- **6 dimensiones:** Año, Contexto del centro, Perfil del alumno, Competencia, Nivel de logro y **Calidad del dato**.
- **Decisiones clave:** la nota global **nunca se recalcula**, y los problemas de calidad son una **dimensión filtrable**, no se borran.

<details>
<summary> Si preguntan: ¿por qué dos tablas de hechos y no una?</summary>

- **Granos distintos.** Contar alumnado requiere una fila por alumno (`FactEvaluacion`); las medias por competencia requieren una fila por nota (`FactPuntuacion`). Con una sola tabla, contar alumnos exigiría un recuento distinto sobre un identificador que **no existe antes de 2016**.
- **Despivotado:** el CSV tiene 24 columnas de notas por fila. En `FactPuntuacion` cada nota es una fila con un enlace a la dimensión Competencia, de modo que se puede filtrar por materia o subcompetencia sin 24 medidas distintas. Las celdas vacías no generan fila.
- **Dimensiones compartidas** (Año, Contexto y Perfil): las dos tablas de hechos se filtran a la vez con los mismos segmentadores (*conformed dimensions* de Kimball).
- **Volumen:** 17,7 M de filas es asumible para el motor en memoria de Power BI (VertiPaq) con claves enteras y pocas columnas.
</details>

<details>
<summary> Si preguntan: ¿qué es la dimensión «Calidad del dato»?</summary>

- Una tabla de 16 filas que combina 4 indicadores (una máscara de bits):
  - **No válida:** expresión escrita de inglés 2015.
  - **Censurada:** los suelos artificiales.
  - **No comparable en la serie:** escalas distintas en algunas subcompetencias y años.
  - **Nivel no comparable:** 6 combinaciones materia-año en las que el % por nivel no se puede comparar.
- Cada nota de `FactPuntuacion` apunta a su combinación.
- **Ventaja:** los KPIs excluyen lo que no procede (por ejemplo, K03 excluye las censuradas), pero el dato **sigue en el modelo** y se puede auditar o mostrar con un filtro.
- En la memoria demuestra la **trazabilidad**: cada nota sabe qué problema de calidad tiene.
</details>

<details>
<summary> Si preguntan: otras decisiones (claves, áreas, Año)</summary>

- **Dimensiones *junk*** (Kimball): Contexto (área × naturaleza × hábitat) y Perfil (género × edad × mes) agrupan atributos de baja cardinalidad en una sola dimensión de 120 y 182 filas.
- **Claves deterministas:** la clave se calcula con una fórmula (por ejemplo, Contexto = área·100 + naturaleza·10 + hábitat), así que no hace falta cruzar tablas en la ETL. Es más rápido y menos propenso a errores.
- **Área con tres vistas:**
  - el nombre publicado;
  - el perímetro de 2025 (Barcelona Comarques 2024 = Barcelonès);
  - la **serie comparable** para la evolución (cuestión 3).
- **Año con índice de convocatoria:** 2009 = 1… 2019 = 11, 2021 = 12. La «convocatoria anterior» de 2021 es 2019 sin trucos (cuestión 4).
- **Identificador de alumno:** no se carga al modelo (privacidad y memoria); solo se guarda un indicador de si existía.
</details>

---

## 5. Cuestiones abiertas: vuestra validación (28 min) ⭐

Para cada cuestión propongo una opción por defecto, justificada con los datos. Las cuatro primeras **condicionan lo que comunica el CMI**.

### A. Las importantes (≈ 5 min cada una)

**1. Umbrales de nivel de logro** (T9)
- **Propuesta:** cortes fijos **55 / 70 / 85**, los que mejor reproducen los % oficiales (error medio de 2,7 pp).
- *Alternativas:* 50/70/85 · cortes calibrados por materia y año.

<details>
<summary> Detalle: comparación de umbrales</summary>

- **El problema:** el CSV no trae el nivel oficial de cada alumno, y los informes **no publican cortes fijos**: los recalculan cada año con la media y la dispersión. Solo dan horquillas: nivel mínimo entre 50 y 60, «llindar òptim» en 70 y nivel alto entre 80 y 90.
- **Método:** se probaron varios cortes y se compararon con los % oficiales por nivel en 35 combinaciones materia-año (2018–2025).

| Cortes | Error medio en % Bajo | Sesgo en % Bajo |
|---|---|---|
| 50 / 70 / 85 | 4,39 pp | −4,39 (infravalora el nivel bajo) |
| **55 / 70 / 85** | **2,70 pp** | **−0,14** |
| 60 / 70 / 85 | 5,57 pp | +5,22 (sobrevalora) |

- **Distribución resultante (2009–2025):** 13 % bajo, 20 % medio-bajo, 34 % medio-alto y 33 % alto.
- **Ventajas del corte fijo:** es simple, igual para todas las materias y años, y explicable.
- **Inconveniente:** **no son los niveles oficiales**, sino niveles internos del TFG, y hay que decirlo así en el CMI.
- **Alternativa calibrada:** reproduciría los % oficiales exactamente, pero solo en los años con informe, y cambiaría cada año.
</details>

**2. KPIs de evolución con puntuaciones no equiparadas** (T9)
- **Propuesta:** mantener K10–K12 con la etiqueta «no equiparada», un umbral |Δ| ≥ 1 y sin comparar entre diseños de prueba distintos.
- *Alternativas:* añadir una puntuación estandarizada (z) · quitar los KPIs de evolución.

<details>
<summary> Detalle: qué significa «no equiparada» y qué sería la puntuación z</summary>

- **Equiparar** (*equating*) es ajustar las puntuaciones de pruebas distintas a una escala común, de modo que 70 signifique lo mismo cada año. El Consell **no lo hace** en esta prueba (Quadern 68).
- **Consecuencia:** si la media baja de 74 a 72, puede ser que el alumnado sepa menos **o** que la prueba fuera más difícil. No se puede distinguir.
- **Qué propongo:**
  - **Etiquetar** los KPIs de evolución como «no equiparada».
  - Exigir **|Δ| ≥ 1 punto** para considerar que una materia mejora (filtra el ruido).
  - **No comparar** entre diseños distintos. Por ejemplo, catalán antes y después de 2018 (cuando entra la comprensión oral) no se compara.
- **Puntuación z:** (nota − media del año) / desviación típica del año. Mide la **posición relativa** del alumno dentro de su año, no el nivel absoluto. Sirve para las brechas y los rankings («¿la brecha de género crece en términos relativos?»), pero no responde a «¿se aprende más?».
- **Pregunta para vosotras:** ¿es aceptable presentar la evolución con esta advertencia, o es preferible limitarse a las comparaciones dentro del mismo año?
</details>

**3. Series territoriales tras la reorganización de 2024** (T10/T12)
- **Propuesta:** agrupar las áreas afectadas en series comparables (un grupo reúne el ≈ 27 % de Cataluña).
- *Alternativas:* evolución solo de las áreas estables · comparar solo 2024–2025.

<details>
<summary> Detalle: qué áreas se agrupan y por qué</summary>

| Serie comparable | Áreas que agrupa | Motivo |
|---|---|---|
| Lleida + Alt Pirineu i Aran | Lleida, Alt Pirineu i Aran | El Alt Pirineu sale de Lleida en 2024 |
| Barcelonès-Penedès y áreas afectadas | Barcelona Comarques / Barcelonès, Penedès, Tarragona, Catalunya Central | Penedès se forma con comarcas de estas tres áreas |
| Resto (sin cambios) | Baix Llobregat, Consorci de Barcelona, Girona, Maresme-Vallès Oriental, Terres de l'Ebre, Vallès Occidental | Perímetro estable |

- **Problema del grupo grande:** al juntar 4 áreas (≈ 27 % del alumnado), la serie pierde detalle territorial.
- **Girona:** perdió la Cerdanya (pocos centros) en favor de Alt Pirineu i Aran. Propongo dejarla con una nota en lugar de agruparla.
- **Las comparaciones de un solo año** (desviación respecto a Cataluña, ranking) usan siempre el área publicada: el problema solo afecta a la evolución.
- Fuentes: Decret 59/2022 y Decret 120/2023, y el directorio de centros del portal de datos abiertos.
</details>

**4. Comparar 2021 con 2019** (no hay convocatoria en 2020)
- **Propuesta:** tratarlo como variación interanual, con nota de la COVID-19.
- *Alternativa:* romper la serie en 2020.

<details>
<summary> Detalle</summary>

- 2021 fue la primera prueba tras el confinamiento, y los informes oficiales la tratan como «primera onada» después de la COVID.
- El Quadern 68 (gráfico 3) dibuja **dos series separadas**, antes y después de 2020.
- **Opción A (propuesta):** 2021 se compara con 2019 como «convocatoria anterior», con una nota visible. La serie se ve continua y el salto se explica.
- **Opción B:** la variación de 2021 aparece vacía y la tendencia de 5 convocatorias no cruza 2020. Es más prudente, pero hasta 2025 no hay 5 convocatorias seguidas después de la COVID.
- **Ejemplo de por qué importa:** ciencias 2021 sube +7,4 respecto a 2019. Puede ser un efecto real o un cambio de prueba.
</details>

### B. Las rápidas (≈ 1 min cada una)

| # | Cuestión | Propuesta |
|---|---|---|
| 5 | Inglés 2015 y catalán 2018 (suelos artificiales) | Marcar, no excluir |
| 6 | Hábitat y edad de 2010 (desalineados) | Excluirlos como «No fiable», con nota |
| 7 | Francés (243–505 alumnos al año) | Solo informativo: mínimo de 30 alumnos y fuera de los rankings |
| 8 | Errores del dataset de origen | Documentarlos en la memoria. ¿Los comunicamos a la Generalitat? |
| 9 | 68.342 celdas inválidas de inglés 2015 | Conservarlas con indicador, no borrarlas |
| 10 | Edad del alumno | Edad por cohorte (año de la prueba − año de nacimiento) y su situación |
| 11 | Dirección sin código de centro | Comparar con centros de contexto similar |

<details>
<summary> Detalle de las cuestiones 5 a 11</summary>

- **5. Marcar en lugar de excluir:** excluir convocatorias enteras crearía huecos en la serie. Marcándolas, las medias siguen disponibles y solo se excluyen donde distorsionan (el % en nivel bajo y la dispersión).
- **6. 2010:** usar valores que se sabe que están mal daría brechas por hábitat falsas. Las puntuaciones de 2010 sí se usan.
- **7. Francés:**
  - Solo lo hace un grupo pequeño (243–505 alumnos al año) que no representa a Cataluña.
  - En 2022, el 45 % de las globales no cuadran con sus subcompetencias.
  - Se muestra como informativo; queda fuera de los rankings y del % de competencias que mejoran.
- **8. Errores del dataset de origen:**
  - Rotaciones de castellano 2017 y francés 2016.
  - Hábitat de 2024 («Fins a 10001…»).
  - Hábitat y año de nacimiento de 2010.
  - Ciencias: el Quadern 68 publica unos pesos de 42/25/33, pero los datos siguen una **media simple** en el 100 % de las filas.

  Comunicarlo al portal sería un valor añadido del TFG (transparencia), pero es una decisión vuestra.
- **9. Inglés 2015, expresión escrita:** tiene una escala anómala. Las celdas se conservan con el indicador «no válida» y las medias de subcompetencia las excluyen. Quedan 17.728.085 filas, frente a 17.659.743 si se borraran.
- **10. Edad:** el dataset solo da el año y el mes de nacimiento, no la fecha de la prueba con precisión.
  - Edad por cohorte: 12 = edad teórica; 13 = retraso de 1 año; 14 = retraso de 2 años; < 12 = adelantado.
  - Permite analizar el alumnado con retraso, un indicador de equidad.
- **11. Sin código de centro:** la Dirección selecciona su contexto (área, naturaleza, hábitat) y compara esos centros con Cataluña. No puede ver su propio centro. Sería una extensión futura si el Departament cediera datos por centro.
</details>

### C. Preguntas para vosotras

- **Validación con usuarios (T21):** ¿tenéis contacto con algún director/a o inspector/a? Si no, aplico el plan B del GEP: perfiles simulados y una evaluación heurística.
- **Memoria:** ¿qué peso debe tener la auditoría de datos frente al desarrollo del CMI?

<details>
<summary> Detalle: cómo sería la prueba de usabilidad</summary>

- **Plan (GEP4 §4.3):** al menos 5 usuarios con perfiles representativos, tareas guiadas (por ejemplo, «encuentra el área con más alumnado en nivel bajo en matemáticas en 2025») y el cuestionario **SUS** (System Usability Scale, Brooke 1996). Objetivo: SUS ≥ 68.
- **Plan B (riesgo R4):** perfiles simulados (estudiantes o docentes conocidos) más una **evaluación heurística** según las heurísticas de Nielsen.
</details>

---

## 6. Próximos pasos y prototipo (5 min)

| Semanas | Tareas del Gantt |
|---|---|
| 8–10 | T10 cerrar el modelo con vuestras decisiones · T11 prototipo UX/UI · T13 ETL II (construcción de la estrella) |
| 11–14 | T14–T15 medidas DAX · T16 panel estratégico |
| 15–18 | T17–T18 paneles táctico y operativo · T19–T21 rendimiento, validación de los KPIs y usabilidad |
| 18–19 | T22–T23 memoria y defensa (19–25 de enero) |

**Sobre el prototipo:** para comprobar que el diseño funciona con los datos reales, he montado un **prototipo exploratorio** en Power BI, que ya abre y se actualiza con el dataset completo. Si os parece, os lo enseño en 2 minutos.

<details>
<summary> Si preguntan: ¿qué tiene el prototipo y cómo se ha validado?</summary>

- **Formato:** proyecto Power BI en formato de texto (PBIP), versionable en Git: modelo (TMDL), ETL en Power Query (M), 19 medidas DAX e informe de 3 páginas.
- **Páginas:**
  - Estratégico: tarjetas de los KPIs, evolución por materia y tabla resumen.
  - Táctico: desviación por área, matriz área × naturaleza y brechas.
  - Operativo: selección de contexto, subcompetencias y distribución por nivel.
- **Validación:**
  - Validación estructural con las herramientas y los esquemas oficiales de Microsoft.
  - **Réplica independiente en Python** de toda la ETL y de los 12 KPIs: 27 tests automáticos que comparan recuentos, claves y medias.
  - Contraste con los Quaderns (70/72).
- **Estado:** abierto y actualizado en Power BI Desktop. Falta el diseño visual fino y aplicar las decisiones de hoy.
- **Por qué ya existe:** construir pronto una versión de extremo a extremo permitía comprobar con datos reales que las reglas de limpieza y los KPIs funcionan, antes de cerrar el diseño. Reduce los riesgos R1 y R2 del GEP.
</details>

---

## Glosario rápido

<details>
<summary> Términos técnicos por si hace falta explicarlos</summary>

| Término | Significado |
|---|---|
| CMI / BSC | Cuadro de Mando Integral / *Balanced Scorecard*: indicadores equilibrados en perspectivas ligadas a la estrategia |
| Esquema en estrella | Modelo con una tabla de hechos central y tablas de dimensiones alrededor (Kimball) |
| Tabla de hechos / grano | Tabla con las medidas; el grano es lo que representa cada fila |
| Dimensión *junk* | Dimensión que agrupa varios atributos pequeños sin relación entre sí |
| ETL | *Extract, Transform, Load*: extraer, limpiar y cargar los datos |
| Power Query (M) | Lenguaje de ETL de Power BI |
| DAX | Lenguaje de fórmulas de las medidas de Power BI |
| DuckDB | Motor SQL analítico embebido, usado para la auditoría |
| Puntuación no equiparada | Puntuaciones de pruebas distintas sin escala común entre años |
| Puntuación z | (valor − media) / desviación típica: posición relativa dentro del año |
| SUS | System Usability Scale: cuestionario estándar de usabilidad (0–100) |
| Quaderns d'avaluació | Informes oficiales anuales del Consell Superior d'Avaluació del Sistema Educatiu |
</details>

---

## Anexo: documentación de soporte

| Documento | Ruta |
|---|---|
| Informe de calidad de datos (T7/T12) | `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md` (§7.2: cuestiones abiertas) |
| Modelo y diccionario (T10) | `Documentation/Docu_Final/Docu_Parcial/02_Modelo_y_diccionario.md` |
| Fichas de KPIs (T9) | `Documentation/Docu_Final/Docu_Parcial/03_Fichas_KPI.md` |
| Scripts de la auditoría | `validacion/perfilado/` |

---

## Notas de la reunión

| # | Decisión | Comentarios |
|---|---|---|
| 1 Umbrales | | |
| 2 Evolución | | |
| 3 Territorio | | |
| 4 2021–2019 | | |
| 5–11 | | |
| Usuarios | | |

**Otros acuerdos:**

Notes Reunió 02/11/2026

- Informes latex -- .docx
- Lectura rigurosa text, redaccio no complexa i no artificiosa
- Los apartados que estiguin acabats marcarlos, no mes revisions
- afegir resum previ al informe en els idiomes
- Parlar i adelantar en el estat del art, porque un CMI es una solución única, comentar, el upc + una externa, mirar reunió. (Apartat 2)

- Justificación solo porque uso powerBI, i no solo porque los beneficions, mas allá de la herramienta. (Cohernecia justificación solución propuesta, e introducir solucion) [Partat 2 y 3]

- Extender Requisits queda pobre per la metodologia GEP






//Setmana que ve

sosenibilitat ->8
especificasio -> 7
Haig de fer el que he fet a er, IES
- Diagrama de casos, d'us, Diagrama general
- Hostories de usuari.

//Despres sota especificasio s afegira disseny disseny

Aprattat 3 -> faltan mockups

