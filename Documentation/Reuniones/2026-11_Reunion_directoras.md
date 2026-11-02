# Reunión de seguimiento del TFG

**Cuadro de Mando Integral para el soporte a la toma de decisiones en la educación primaria de Cataluña**

| | |
|---|---|
| Estudiante | Kiara Kristin Rodríguez Uribe |
| Directoras | Carme Martín Escofet · Maria Hitz Martinez |
| Fecha | ____ de noviembre de 2026 · 60 min |
| Objetivo | Presentar el avance de la fase técnica y **cerrar las decisiones de diseño pendientes** |

---

## Agenda (60 min)

| Min | Tema | Qué busco |
|---|---|---|
| 0–10 | 1. Dónde estamos | Visión general del avance |
| 10–20 | 2. Qué dicen los datos | Hallazgos de calidad que condicionan el CMI |
| 20–30 | 3. Qué he construido | Modelo, KPIs y cuadros de mando (demostración) |
| 30–55 | 4. Decisiones abiertas | **Vuestra validación** de 10 decisiones (las 4 primeras, las importantes) |
| 55–60 | 5. Próximos pasos | Acordar el calendario hasta enero |

---

## 1. Dónde estamos (10 min)

**En una frase:** la gestión del proyecto (GEP) está entregada y ya tengo una **primera versión completa y funcional del CMI**, que he abierto y actualizado en Power BI Desktop. Esto va **unas 4–6 semanas por delante** del Gantt.

| Fase (Gantt GEP) | Planificado | Estado |
|---|---|---|
| Gestión del proyecto: GEP 1–4 (T1–T4) | Sem. 1–4 | ✅ Entregado |
| Perfilado y auditoría del dataset (T7) | Sem. 1–3 | ✅ Hecho: informe de calidad con 34 reglas de limpieza |
| Requisitos y catálogo de KPIs (T8–T9) | Sem. 4–7 | ✅ 12 KPIs en 4 perspectivas |
| Modelo dimensional (T10) | Sem. 8 | ✅ Esquema en estrella, 2 hechos y 6 dimensiones |
| ETL en Power Query (T12–T13) | Sem. 5–10 | ✅ Implementada |
| Medidas DAX (T14–T15) | Sem. 11–14 | ✅ 19 medidas (12 KPIs y semáforos) |
| Cuadros de mando (T16–T18) | Sem. 13–16 | 🟡 Versión mínima con 3 páginas; falta el diseño visual fino |
| Validación: rendimiento, KPIs y usabilidad (T19–T21) | Sem. 15–18 | 🟡 Validación de KPIs hecha; faltan rendimiento y usabilidad con usuarios |
| Memoria (T6, T22) | Sem. 5–19 | 🟡 Hay documentación técnica reutilizable (4 documentos) |

**Cómo he trabajado:** sigo el ciclo de vida de Kimball (requisitos → modelo → ETL → aplicación BI), iterando en versiones. Primero he hecho una versión mínima de extremo a extremo para validar el diseño con datos reales antes de pulirla.

---

## 2. Qué dicen los datos (10 min)

El dataset (1.102.324 alumnos, 2009–2025) **está bien formado, pero tiene errores de contenido** que habrían falseado los KPIs si no se hubieran detectado. Los más relevantes:

1. **Columnas cambiadas de sitio en origen.** En castellano 2017 (71.036 alumnos) la nota global está en la columna de una subcompetencia. Corregido, la media pasa de 74,30 a **73,51**, que coincide con el 73,4 oficial. Ocurre lo mismo en francés 2016.
2. **Datos de 2010 desalineados.** El hábitat y el año de nacimiento no corresponden al alumno de la fila (por ejemplo, alumnado de la ciudad de Barcelona en municipios de menos de 10.000 habitantes). Los he marcado como «No fiable».
3. **Cambios de codificación entre años.** H/D frente a Home/Dona, Públic frente a Pública, y 13.357 valores de hábitat «autoincrementados» en 2024 (un error típico de arrastrar una celda en Excel). Están normalizados.
4. **Rupturas de comparabilidad temporal.** No hay 2020 (COVID), el mapa territorial cambia en 2024 (aparecen Penedès, Alt Pirineu i Aran y Barcelonès), los pesos de las subcompetencias cambian casi cada año y **las puntuaciones no están equiparadas entre convocatorias**.
5. **Los niveles de logro oficiales no vienen en los datos.** He definido unos umbrales propios calibrados con los porcentajes publicados.

**Principio aplicado:** solo corrijo lo que es demostrablemente un error. Lo demás se conserva y se **marca con indicadores de calidad** que las medidas usan para filtrar o anotar. No se borra ningún registro.

---

## 3. Qué he construido (10 min, con demostración)

**Arquitectura:** CSV del portal → ETL en Power Query (limpieza y reglas de calidad) → modelo en estrella (Kimball) → medidas DAX → 3 cuadros de mando, uno por perfil.

- **Modelo:** `FactEvaluacion` (una fila por alumno y convocatoria, 1,1 M) y `FactPuntuacion` (una por alumno y competencia, 17,7 M), con las dimensiones Año, Contexto del centro, Perfil del alumno, Competencia, Nivel de logro y Calidad del dato.
- **12 KPIs en las 4 perspectivas del CMI** adaptado al sector público (Niven):

| Perspectiva | KPIs |
|---|---|
| Rendimiento académico | Puntuación media por competencia · por subcompetencia · % alumnado en nivel bajo |
| Equidad e inclusión | Brecha de género · brecha pública–privada · dispersión de resultados |
| Territorio y entorno | Desviación del área respecto a Cataluña · diferencia urbano–rural · posición del área |
| Eficiencia y progreso | Variación interanual · tendencia de 5 convocatorias · % de competencias que mejoran |

- **Cuadros de mando:** Estratégico (Departamento), Táctico (Inspección) y Operativo (Dirección de centro).
- **Validación de los KPIs:** los he calculado dos veces de forma independiente, en DAX (Power BI) y en Python, y los he contrastado con los informes oficiales del Consell Superior d'Avaluació. **70 de las 72 medias** por materia y año coinciden dentro de ±0,2 puntos; las 2 restantes están explicadas.

**Una lectura de los datos (Cataluña, 2025):** catalán 73,5 · castellano 76,5 · matemáticas 70,4 · inglés 75,7 · ciencias 66,3. El % de alumnado en nivel bajo sube del 13,7 % en 2021 al 17,8 % en 2025.

> 💻 Demostración: abrir `PowerBI/CMI_Educacion_Primaria.pbip` y recorrer las 3 páginas.

---

## 4. Decisiones abiertas (25 min) ⭐

Para avanzar he aplicado una **opción por defecto** en cada caso, pero necesito vuestro criterio. Las cuatro primeras afectan a lo que el CMI comunica; las demás se pueden resolver con un sí o un no.

### Las importantes (≈ 5 min cada una)

| # | Decisión | Opción aplicada ahora | Alternativas |
|---|---|---|---|
| **1** | **Umbrales de nivel de logro** (los oficiales no vienen en los datos) | Cortes fijos **55 / 70 / 85**, con un error medio de 2,7 pp frente a los % oficiales | a) 50/70/85, más simple pero infravalora el nivel bajo · b) cortes calibrados por materia y año, solo para los años con informe |
| **2** | **KPIs de evolución con puntuaciones no equiparadas** | Se mantienen con la nota «no equiparada», el umbral \|Δ\| ≥ 1 y sin comparar entre diseños de prueba distintos | a) Añadir una puntuación estandarizada (z) por año · b) Quitar la evolución del CMI |
| **3** | **Series territoriales** tras la reorganización de 2024 | Agrupar las áreas afectadas en series comparables (un grupo reúne ≈ 27 % de Cataluña) | a) Limitar la evolución por área a las áreas estables · b) Comparar solo 2024–2025 |
| **4** | **Comparar 2021 con 2019** (no hay 2020) | Variación interanual con nota de la COVID-19 | Romper la serie en 2020, como hace el Quadern 68 |

### Las rápidas (≈ 1 min cada una)

| # | Decisión | Opción aplicada ahora |
|---|---|---|
| 5 | Inglés 2015 y catalán 2018 (suelos artificiales en las notas) | Marcar, no excluir |
| 6 | Hábitat y edad de 2010 (desalineados) | Excluirlos como «No fiable», con nota |
| 7 | Francés (243–505 alumnos al año) | Solo informativo, con un mínimo de 30 alumnos y fuera de los rankings |
| 8 | Errores del dataset de origen (rotaciones, hábitat 2024, pesos de ciencias) | Documentarlos en la memoria. ¿Los comunicamos a la Generalitat? |
| 9 | Celdas inválidas (inglés 2015, 68.342) | Conservarlas con indicador, no borrarlas |
| 10 | Edad del alumno | Usar la edad por cohorte (año de la prueba − año de nacimiento) y su situación (en edad, con retraso…) |

### Otras preguntas para vosotras

- **Validación con usuarios:** ¿tenéis contacto con algún director/a de escuela o inspector/a para la prueba de usabilidad? Si no, la haré con perfiles simulados y una evaluación heurística (plan B del GEP).
- **Alcance:** con la versión mínima ya hecha, ¿priorizo pulir el diseño y validar con usuarios, o incorporar alguna extensión (publicación web, seguridad por territorio, análisis predictivo)?
- **Memoria:** ¿qué peso esperáis en la memoria para la auditoría de datos frente al desarrollo del CMI?

---

## 5. Próximos pasos (5 min)

| Cuándo | Qué |
|---|---|
| Noviembre (sem. 9–12) | Aplicar las decisiones de hoy · pulir el diseño visual de los 3 cuadros de mando · revisar el rendimiento |
| Diciembre (sem. 13–16) | Prueba de usabilidad (SUS) · validación final de los KPIs · redacción de la memoria |
| Enero (sem. 17–19) | Cierre de la memoria · preparación de la defensa (19–25 de enero) |

**Propuesta:** siguiente reunión a mediados de noviembre con las decisiones aplicadas y los cuadros de mando pulidos.

---

## Anexo: dónde está cada cosa (repositorio del proyecto)

| Documento | Ruta |
|---|---|
| Informe de calidad de datos (hallazgos y 34 reglas) | `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md` |
| Modelo y diccionario de datos | `Documentation/Docu_Final/Docu_Parcial/02_Modelo_y_diccionario.md` |
| Fichas de los 12 KPIs (fórmula, interpretación y valores) | `Documentation/Docu_Final/Docu_Parcial/03_Fichas_KPI.md` |
| Guía de uso | `Documentation/Docu_Final/Docu_Parcial/04_Guia_de_uso.md` |
| Proyecto Power BI | `PowerBI/CMI_Educacion_Primaria.pbip` |
| Validación en Python y resultados | `validacion/` |

---

## Notas de la reunión

| # | Decisión tomada | Comentarios |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5–10 | | |

**Otros acuerdos:**

-
