# Reunión de seguimiento del TFG

**Cuadro de Mando Integral para el soporte a la toma de decisiones en la educación primaria de Cataluña**

| | |
|---|---|
| Estudiante | Kiara Kristin Rodríguez Uribe |
| Directoras | Carme Martín Escofet · Maria Hitz Martinez |
| Fecha | ____ de noviembre de 2026 · 60 min |
| Momento del Gantt | Semana 8: fin de la fase de análisis e inicio del diseño del modelo |
| Objetivo | Presentar la fase de análisis y **validar con vosotras las decisiones abiertas** antes de construir |

---

## Agenda (60 min)

| Min | Tema | Tareas del Gantt |
|---|---|---|
| 0–5 | 1. Estado según la planificación | T1–T6 |
| 5–15 | 2. Auditoría de calidad de los datos: qué he encontrado y cómo | T7 · T12 |
| 15–22 | 3. Requisitos por perfil y catálogo de KPIs | T8 · T9 |
| 22–27 | 4. Diseño del modelo dimensional (en curso) | T10 |
| 27–55 | **5. Cuestiones abiertas: vuestra validación** ⭐ | T9 · T10 · T12 |
| 55–60 | 6. Próximos pasos y, brevemente, el prototipo | — |

---

## 1. Estado según la planificación (5 min)

| Tarea | Semanas | Estado |
|---|---|---|
| T1–T4 Entregables de GEP (hito H1) | 1–4 | ✅ Entregados |
| T7 Perfilado y auditoría del dataset | 1–3 | ✅ Informe de calidad con 34 reglas |
| T8 Análisis de requisitos por perfil | 4–5 | ✅ 3 perfiles con sus preguntas de decisión (para validar hoy) |
| T9 Catálogo de KPIs del CMI | 6–7 | ✅ 12 KPIs en 4 perspectivas, con fichas |
| T12 ETL I: limpieza y homogeneización | 5–7 | ✅ Reglas definidas y probadas sobre el fichero completo |
| T10 Diseño del modelo dimensional | 8 | 🔄 Diseño hecho y en revisión (hoy) |
| T5 / T6 Seguimiento y memoria | continuas | 🔄 Hay documentación técnica reutilizable en la memoria |

**Conclusión:** voy al día según el Gantt, sin desviaciones. El riesgo R1 (inconsistencias en los datos) **se ha materializado**, pero se ha absorbido en T7/T12 sin necesidad del plan B: no hace falta recortar el histórico a 2018–2025.

---

## 2. Auditoría de calidad de los datos (T7 · T12) — 10 min

### Cómo lo he hecho

1. **Perfilado sistemático** de las 32 columnas con Python + DuckDB. Leo el CSV entero **como texto** para que ninguna conversión de tipos esconda un valor anómalo, y comparo las puntuaciones en centésimas enteras para evitar errores de redondeo.
2. **Evaluación por dimensiones de calidad** (ISO/IEC 25012): completitud, validez, consistencia y unicidad, más una dimensión propia de **comparabilidad temporal**, clave para un CMI que mide evolución.
3. **Verificación independiente:** unos scripts escritos desde cero, con otra vía de lectura del fichero, reproducen cada cifra. Se confirmaron 38 de 41 hallazgos; los 3 restantes se corrigieron.
4. **Contraste externo:**
   - Medias de mis datos frente a los 16 *Quaderns d'avaluació* oficiales del Consell Superior d'Avaluació (2009–2025).
   - Metadatos oficiales del portal (API Socrata).
   - Decretos de reorganización territorial (Decret 59/2022 y 120/2023).
5. **Criterio de limpieza:** solo corrijo lo que es **demostrablemente un error**. Lo demás se conserva y se **marca con un indicador de calidad**. No se borra ningún registro.

Todo es reproducible: los scripts y sus salidas están en `validacion/perfilado/`.

### Qué he encontrado (los 5 hallazgos clave)

| # | Hallazgo | Cómo lo detecté | Tratamiento |
|---|---|---|---|
| 1 | **Columnas rotadas en origen:** en castellano 2017 la nota global está en la columna de una subcompetencia; ocurre lo mismo en francés 2016 | Regresión de la global sobre sus subcompetencias: daba pesos imposibles (−0,67 y 1,67) | Reasignar las columnas. Castellano 2017 pasa de 74,30 a **73,51**, frente al **73,4 oficial** ✔️ |
| 2 | **2010 desalineado:** el hábitat y el año de nacimiento no corresponden al alumno de la fila | Combinaciones imposibles (alumnado del Consorci de Barcelona en municipios de menos de 10.000 habitantes); el efecto de la edad sobre la nota desaparece | Marcar como «No fiable (2010)» |
| 3 | **Codificaciones que cambian por año:** H/D frente a Home/Dona (2021), Públic frente a Pública (2024–25) y 13.357 hábitats «Fins a 10001… 23357» (arrastre en Excel, 2024) | Frecuencias de valores por año | Normalizar con mapeos explícitos; un valor desconocido hace fallar la carga |
| 4 | **Rupturas temporales:** no hay 2020 (COVID); el mapa territorial cambia en 2024; los pesos de las subcompetencias cambian casi cada año; **las puntuaciones no están equiparadas** entre convocatorias | Matriz de cobertura por año, regresión de pesos por año y consulta de los decretos | Índice de convocatoria (2021 sigue a 2019), series territoriales comparables y nota de «no equiparada» |
| 5 | **Suelos artificiales** en inglés 2015 y catalán 2018 (muchos alumnos con exactamente la misma nota mínima) | Histogramas por año | Indicador de calidad («censurada») |

**Resultado del contraste:** con las reglas aplicadas, **70 de las 72 medias** por materia y año coinciden con las oficiales dentro de ±0,2 puntos. Las 2 restantes (inglés 2016 y francés 2024) están analizadas y documentadas.

---

## 3. Requisitos por perfil y catálogo de KPIs (T8 · T9) — 7 min

### Perfiles y preguntas de decisión (T8)

| Perfil | Nivel de decisión | Preguntas que debe poder responder |
|---|---|---|
| **Departamento de Educación** | Estratégico | ¿Cómo evolucionan las competencias en Cataluña? ¿Crece el alumnado en nivel bajo? ¿Qué materias mejoran? |
| **Inspección y coordinación territorial** | Táctico | ¿Qué áreas se desvían de la media? ¿Hay brechas de género, de titularidad o de hábitat? ¿Dónde priorizar los recursos de refuerzo? |
| **Dirección de centro** | Operativo | ¿Cómo rinden los centros de mi contexto (área, naturaleza, hábitat) frente a Cataluña? ¿En qué subcompetencias hay carencias? |

**Limitación detectada:** el dataset **no incluye el código de centro**, así que el perfil de Dirección no puede ver su propio centro. Verá **centros de contexto similar**. Hay que confirmarlo con vosotras (cuestión 11).

### Catálogo de KPIs (T9)

**Cómo:** he partido del CMI de Kaplan y Norton adaptado al sector público según Niven, donde la misión sustituye a la perspectiva financiera, porque el dataset no tiene datos económicos. Cada KPI tiene una ficha con su objetivo, fórmula, unidad, interpretación, exclusiones de calidad, mínimo muestral (n ≥ 30) y valores de referencia calculados (documento 03).

| Perspectiva | KPIs |
|---|---|
| Rendimiento académico | K01 media por competencia · K02 media por subcompetencia · K03 % alumnado en nivel bajo |
| Equidad e inclusión | K04 brecha de género · K05 brecha pública–privada · K06 dispersión |
| Territorio y entorno | K07 desviación respecto a Cataluña · K08 diferencia urbano–rural · K09 posición del área |
| Eficiencia y progreso | K10 variación interanual · K11 tendencia de 5 convocatorias · K12 % de competencias que mejoran |

Además, hay semáforos de estado (favorable, neutro o desfavorable) para K01, K03 y K10.

---

## 4. Diseño del modelo dimensional (T10) — 5 min

**Cómo:** metodología de Kimball. Primero se declara el grano, después las dimensiones y por último los hechos.

- **Dos tablas de hechos** que comparten dimensiones:
  - `FactEvaluacion`: una fila por alumno y convocatoria (1.102.324). Sirve para contar alumnado.
  - `FactPuntuacion`: una fila por alumno y competencia con nota (17.728.085). Sirve para las medias y los niveles.
- **6 dimensiones:** Año (con índice de convocatoria), Contexto del centro (área, naturaleza y hábitat), Perfil del alumno (género y situación de edad), Competencia (6 materias y 24 campos), Nivel de logro y **Calidad del dato** (los indicadores de la auditoría).
- **Decisiones de diseño:**
  - La nota global **nunca se recalcula**: se carga la publicada, porque los pesos cambian por año y recalcular daría errores de hasta 19 puntos.
  - Los problemas de calidad se guardan como **dimensión filtrable**, no se borran.

El detalle completo y el diccionario de datos están en el documento 02.

---

## 5. Cuestiones abiertas: vuestra validación (28 min) ⭐

Para cada cuestión propongo una opción por defecto, justificada con los datos. Las cuatro primeras **condicionan lo que comunica el CMI**; las demás se pueden resolver con un sí o un no.

### A. Las importantes (≈ 5 min cada una)

**1. Umbrales de nivel de logro** (T9)
Los datos no traen el nivel oficial del alumno, y los informes no publican cortes fijos (los recalculan cada año).
- **Propuesta:** cortes fijos **55 / 70 / 85**. Los he comparado con los % oficiales de 35 combinaciones materia-año y son los que mejor los reproducen (error medio de 2,7 pp, sesgo ≈ 0). Además, cada corte cae dentro de la horquilla oficial (nivel mínimo 50–60, umbral óptimo 70, nivel alto 80–90).
- *Alternativas:* 50/70/85, más simple pero infravalora el nivel bajo en 4,4 pp · cortes calibrados por materia y año, solo posibles en los años con informe.

**2. KPIs de evolución con puntuaciones no equiparadas** (T9)
Las pruebas cambian cada año y el Consell no equipara las puntuaciones.
- **Propuesta:** mantener K10–K12 con la etiqueta «no equiparada», exigir |Δ| ≥ 1 punto para considerar que hay mejora, y no comparar entre diseños de prueba distintos.
- *Alternativas:* añadir una puntuación estandarizada (z) por año · quitar los KPIs de evolución.

**3. Series territoriales tras la reorganización de 2024** (T10/T12)
En 2024 se crean Penedès y Alt Pirineu i Aran, y Barcelona Comarques pasa a llamarse Barcelonès.
- **Propuesta:** para comparar en el tiempo, agrupar las áreas afectadas en series comparables. Un grupo reúne el ≈ 27 % de Cataluña.
- *Alternativas:* limitar la evolución por área a las áreas estables · comparar solo 2024–2025.

**4. Comparar 2021 con 2019** (no hay convocatoria en 2020)
- **Propuesta:** tratarlo como variación interanual, con nota de la COVID-19.
- *Alternativa:* romper la serie en 2020, como hace el Quadern 68.

### B. Las rápidas (≈ 1 min cada una)

| # | Cuestión | Propuesta |
|---|---|---|
| 5 | Inglés 2015 y catalán 2018 (suelos artificiales) | Marcar, no excluir |
| 6 | Hábitat y edad de 2010 (desalineados) | Excluirlos como «No fiable», con nota |
| 7 | Francés (243–505 alumnos al año) | Solo informativo: mínimo de 30 alumnos y fuera de los rankings |
| 8 | Errores del dataset de origen (rotaciones, hábitat 2024, pesos de ciencias publicados ≠ datos) | Documentarlos en la memoria. ¿Los comunicamos a la Generalitat? |
| 9 | 68.342 celdas inválidas de inglés 2015 | Conservarlas con indicador, no borrarlas |
| 10 | Edad del alumno | Usar la edad por cohorte (año de la prueba − año de nacimiento) y su situación (en edad, con retraso, adelantado) |
| 11 | Perfil de Dirección sin código de centro | Comparar con centros de contexto similar |

### C. Preguntas para vosotras

- **Validación con usuarios (T21):** ¿tenéis contacto con algún director/a o inspector/a? Si no, aplico el plan B del GEP: perfiles simulados y una evaluación heurística.
- **Memoria:** ¿qué peso debe tener la auditoría de datos frente al desarrollo del CMI?

---

## 6. Próximos pasos y prototipo (5 min)

| Semanas | Tareas del Gantt |
|---|---|
| 8–10 | T10 cerrar el modelo con vuestras decisiones · T11 prototipo UX/UI · T13 ETL II (construcción de la estrella) |
| 11–14 | T14–T15 medidas DAX · T16 panel estratégico |
| 15–18 | T17–T18 paneles táctico y operativo · T19–T21 rendimiento, validación de los KPIs y usabilidad |
| 18–19 | T22–T23 memoria y defensa (19–25 de enero) |

**Sobre el prototipo:** para comprobar que el diseño funciona con los datos reales, he montado un **prototipo exploratorio** en Power BI, que ya abre y se actualiza con el dataset completo. Me ha servido para validar las reglas de limpieza y los KPIs antes de cerrar el diseño. Si os parece, os lo enseño en 2 minutos. Las decisiones de hoy se incorporarán directamente en él.

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

-
