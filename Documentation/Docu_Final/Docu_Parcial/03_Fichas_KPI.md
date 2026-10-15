# Fichas de los indicadores del Cuadro de Mando Integral

**Proyecto:** Cuadro de Mando Integral (CMI) en Power BI sobre la evaluación de sexto de educación primaria de Cataluña (TFG, FIB-UPC).
**Autora:** Kiara Rodríguez Uribe.
**Versión del modelo:** MVP v0.1 (`PowerBI/CMI_Educacion_Primaria.SemanticModel`).

Este documento recoge la ficha formal de los doce indicadores clave (KPI) del CMI y de los tres semáforos que los resumen. Todas las fórmulas DAX están copiadas literalmente de `PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl`, y todos los valores de referencia proceden de los ficheros de `validacion/resultados/`, generados por la réplica en Python (`validacion/kpis_referencia.py`). Las reglas de calidad citadas (R01–R34) remiten al informe `01_Informe_calidad_datos.md`.

---

## 1. El Cuadro de Mando Integral y su adaptación al sector público

### 1.1. Del *Balanced Scorecard* al CMI público

El Cuadro de Mando Integral (*Balanced Scorecard*) de Kaplan y Norton (1992) evalúa el rendimiento de una organización con un conjunto equilibrado de indicadores, agrupados en cuatro perspectivas (financiera, clientes, procesos internos y aprendizaje y crecimiento) y enlazados por relaciones causa-efecto. En el modelo original la perspectiva financiera ocupa la cúspide, porque el objetivo último de una empresa es crear valor para el accionista.

Niven (2008) adapta el modelo a las administraciones públicas y a las entidades sin ánimo de lucro con dos cambios principales:

1. **La misión se sitúa en la cúspide.** El éxito de una organización pública no se mide por el beneficio, sino por el grado en que cumple su misión ante la ciudadanía.
2. **La perspectiva de los usuarios gana protagonismo y la financiera deja de ser un fin.** Los recursos económicos pasan a ser una restricción o un medio, no el objetivo que se persigue.

### 1.2. Las cuatro perspectivas del CMI de este TFG

El dataset de la evaluación de sexto no contiene información económica (ni presupuestos ni costes por centro), así que la perspectiva financiera no se puede medir. Siguiendo la adaptación de Niven, el CMI organiza los indicadores en cuatro perspectivas alineadas con la misión del sistema educativo, con tres KPI en cada una. Las perspectivas coinciden con las carpetas de visualización (`displayFolder`) de la tabla `_Medidas`:

| Perspectiva del CMI | Equivalente en el BSC público (Niven) | Objetivo estratégico | KPI | Carpeta en `_Medidas` |
|---|---|---|---|---|
| Rendimiento académico | Usuarios (alumnado y familias) | Mejorar el dominio de las competencias básicas | K01, K02, K03 | `1. Rendimiento académico` |
| Equidad e inclusión | Procesos internos | Reducir las brechas entre grupos de alumnado | K04, K05, K06 | `2. Equidad e inclusión` |
| Territorio y entorno | Procesos internos | Equilibrio territorial de los resultados | K07, K08, K09 | `3. Territorio y entorno` |
| Eficiencia y progreso | Aprendizaje y crecimiento (sustituye además a la financiera) | Mejora continua entre convocatorias | K10, K11, K12 | `4. Eficiencia y progreso` |

Además, el modelo incluye cuatro medidas auxiliares (carpeta `0. Base`: `Alumnos evaluados`, `Puntuaciones globales`, `Puntuación media` y `Puntuación media Cataluña`) y tres semáforos (carpeta `5. Semáforos`: `Estado K01`, `Estado K03` y `Estado K10`).

### 1.3. Mapa estratégico

El mapa estratégico expresa la hipótesis causal que conecta las perspectivas con la misión. Como misión de trabajo del CMI se toma la siguiente formulación: *que todo el alumnado de sexto de primaria de Cataluña alcance las competencias básicas, con independencia de su perfil, del tipo de centro y del territorio*.

```
                    MISIÓN: que todo el alumnado de 6.º alcance las competencias básicas
                                               ▲
                    ┌──────────────────────────┴──────────────────────────┐
                    │ RENDIMIENTO ACADÉMICO (usuarios)                     │
                    │ Mejorar el dominio de las competencias  K01 K02 K03  │
                    └──────────────▲───────────────────────▲──────────────┘
                                   │                       │
        ┌──────────────────────────┴───────┐   ┌───────────┴──────────────────────┐
        │ EQUIDAD E INCLUSIÓN (procesos)    │   │ TERRITORIO Y ENTORNO (procesos)  │
        │ Reducir las brechas  K04 K05 K06  │   │ Equilibrio territorial K07 K08 K09│
        └──────────────────────────▲───────┘   └───────────▲──────────────────────┘
                                   │                       │
                    ┌──────────────┴───────────────────────┴──────────────┐
                    │ EFICIENCIA Y PROGRESO (aprendizaje y crecimiento)    │
                    │ Mejora continua entre convocatorias  K10 K11 K12     │
                    └──────────────────────────────────────────────────────┘
```

La lectura es ascendente: la mejora sostenida del sistema entre convocatorias (progreso) permite reducir las brechas entre grupos y territorios (procesos), lo que eleva y homogeneiza el dominio de las competencias (usuarios) y, con ello, el cumplimiento de la misión. Las relaciones del mapa son una hipótesis de gestión: el CMI no las contrasta estadísticamente.

### 1.4. Niveles de uso en el informe

El informe Power BI (`PowerBI/CMI_Educacion_Primaria.Report/`) tiene tres páginas, una por nivel de decisión. La tabla indica en qué página se muestra cada medida:

| Medida | Estratégico - Departamento | Táctico - Inspección | Operativo - Dirección de centro |
|---|:-:|:-:|:-:|
| K01 Puntuación media competencia | ✓ | ✓ | ✓ |
| K02 Puntuación media subcompetencia | | | ✓ |
| K03 % alumnado nivel bajo | ✓ | | |
| K04, K05, K08, K09 | | ✓ | |
| K06 Dispersión de resultados | ✓ | | |
| K07 Desviación respecto a Cataluña | | ✓ | ✓ |
| K10 Variación interanual, K11 Tendencia 5 convocatorias, K12 % competencias que mejoran | ✓ | | |
| Estado K01 | | | ✓ |
| Alumnos evaluados | ✓ | | |
| Puntuaciones globales (barras 100 % por nivel de logro) | | | ✓ |
| Puntuación media Cataluña | | | ✓ |

`Estado K03` y `Estado K10` están definidos en el modelo, pero en esta versión del informe ningún visual los utiliza.

---

## 2. Convenciones comunes a todas las fichas

**Escala.** Las puntuaciones son porcentajes de acierto en una escala de 0 a 100 (regla R02). Las diferencias entre puntuaciones se expresan en *puntos* de esa escala; las diferencias entre porcentajes, en *puntos porcentuales* (pp).

**Global y subcompetencia.** Cada materia tiene una puntuación global (`DimCompetencia[EsGlobal] = TRUE`) y varias subcompetencias. Las medidas nunca mezclan las dos clases de filas, salvo la medida técnica `Puntuación media`.

**«Cataluña».** El total de Cataluña se obtiene con `REMOVEFILTERS ( DimContextoCentro )`: quita los filtros de área, naturaleza y hábitat, pero conserva los de año, competencia y perfil del alumnado. Incluye el área «Desconocida».

**Mínimo muestral.** K01, K02, K03 y K06 devuelven `BLANK()` si el contexto tiene menos de 30 puntuaciones; los KPI que se construyen a partir de ellos heredan esa condición.

**Comparaciones temporales.** Se navega por `DimAnio[IndiceConvocatoria]` (índice 1..16 de las convocatorias con datos), nunca por `Anio - 1`: así 2021 se compara con 2019, porque 2020 no tuvo prueba por la COVID-19. Solo intervienen las competencias cuyo periodo de diseño estable (`DimCompetencia[PeriodoDisenoInicio]`) empieza como tarde en el año de la convocatoria de referencia: 2016 en inglés y francés, 2017 en matemáticas y 2018 en catalán, castellano y ciencias (contrato §5.2).

**Limitaciones generales.**

- **Puntuaciones no equiparadas.** Las pruebas de cada convocatoria no comparten ítems de anclaje, así que una diferencia entre años mezcla el cambio de rendimiento con el cambio de dificultad de la prueba. Todos los indicadores temporales (K10, K11, K12, `Estado K10` y `Estado K01` cuando usa K10) son **orientativos**; la advertencia figura en la `description` de cada medida y en un cuadro de texto de la página estratégica.
- **Francés, solo informativo.** El francés lo realiza una muestra muy pequeña (243 puntuaciones globales en 2025 y 266 en 2024, frente a unas 66.000–70.000 en las demás materias). Se marca con `DimCompetencia[EsInformativa] = TRUE` (regla R30): queda fuera de K09 y K12, pero sí entra en K01 y en los KPI derivados cuando no se filtra la materia.
- **Niveles de logro internos.** Los cortes 55/70/85 de `DimNivelLogro` son una aproximación del TFG a los niveles oficiales, no los niveles oficiales (informe de calidad, §6.3).
- **Población.** El CSV solo contiene al alumnado con corrección externa; los recuentos pueden diferir hasta en unos 1.000 alumnos de los Quaderns d'avaluació (informe §7.1).

**Valores de referencia.** Salvo que se indique otra cosa, son los de Cataluña en la convocatoria de 2025, tomados de `kpi_cataluna_por_anio_materia.csv` (por materia), `kpi_global_por_anio.csv` (sin filtro de materia), `kpi_subcompetencia_2025.csv`, `kpi_area_2025.csv` y `semaforos_2025.csv`. Los CSV tienen dos decimales; el informe muestra uno, según el formato de cada medida. Una celda vacía equivale a `BLANK()` en DAX.

---

## 3. Fichas de los KPI

### 3.1. Perspectiva de rendimiento académico

#### K01 — Puntuación media competencia

| Campo | Contenido |
|---|---|
| Código y nombre | K01 · `K01 Puntuación media competencia` |
| Perspectiva | Rendimiento académico (usuarios) |
| Objetivo estratégico | Mejorar el dominio de las competencias básicas |
| Definición | Media aritmética de las puntuaciones globales de las materias en el contexto de filtro. Es el indicador base: K04, K05, K07, K08, K09, K10 y K11 se calculan a partir de él. |
| Unidad y formato | Puntos (escala 0–100) · `0.0` |
| Interpretación | Cuanto más alto, mejor. |
| Filtros y exclusiones de calidad | Solo competencias globales (`KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () )`). Las rotaciones de columnas de 2016 y 2017 (R03, R04) se corrigen en la ETL. No excluye las celdas censuradas ni las convocatorias marcadas en `DimCalidadDato`. |
| Mínimo muestral | 30 puntuaciones globales (medida `Puntuaciones globales`); por debajo, `BLANK()`. |
| Limitaciones | Sin filtro de materia promedia todas las materias, francés incluido, ponderadas por su número de puntuaciones. Comparación entre años orientativa (puntuaciones no equiparadas). Las medias de materias distintas no son directamente comparables, porque cada prueba tiene su propia dificultad. |

```dax
Puntuaciones globales =
CALCULATE (
    COUNTROWS ( FactPuntuacion ),
    KEEPFILTERS ( DimCompetencia[EsGlobal] = TRUE () )
)
```

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

**Valores de referencia (Cataluña, 2025).**

| Materia | K01 | Puntuaciones globales |
|---|---:|---:|
| Lengua catalana | 73,53 | 66.151 |
| Lengua castellana | 76,47 | 67.212 |
| Matemáticas | 70,42 | 66.995 |
| Lengua inglesa | 75,74 | 66.813 |
| Lengua francesa (informativa) | 66,09 | 243 |
| Ciencias | 66,32 | 66.509 |
| **Todas las materias** | **72,50** | — |

**Ejemplo por área (2025).** El Consorci d'Educació de Barcelona obtiene 79,08 en lengua inglesa y el Barcelonès, 66,78 en matemáticas. En el Vallès Occidental, K01 de francés queda en blanco por no llegar al mínimo de 30 puntuaciones.

#### K02 — Puntuación media subcompetencia

| Campo | Contenido |
|---|---|
| Código y nombre | K02 · `K02 Puntuación media subcompetencia` |
| Perspectiva | Rendimiento académico (usuarios) |
| Objetivo estratégico | Mejorar el dominio de las competencias básicas (detalle de los puntos fuertes y débiles de cada materia) |
| Definición | Media aritmética de las puntuaciones de las subcompetencias (comprensión lectora, comprensión oral, expresión escrita, bloques de matemáticas y de ciencias) en el contexto de filtro. Se analiza con `DimCompetencia[Subcompetencia]` en el eje. |
| Unidad y formato | Puntos (escala 0–100) · `0.0` |
| Interpretación | Cuanto más alto, mejor. |
| Filtros y exclusiones de calidad | Solo subcompetencias (`EsGlobal = FALSE`). Excluye las puntuaciones no válidas (`DimCalidadDato[NoValida] = TRUE`, regla R25: expresión escrita de inglés de 2015). |
| Mínimo muestral | 30 puntuaciones válidas de subcompetencia. |
| Limitaciones | No excluye las escalas no comparables en serie (`DimCalidadDato[NoComparableSerie]`, R27): para analizar series temporales hay que filtrar por esa columna. No todas las subcompetencias existen en todos los años (por ejemplo, la comprensión oral de catalán y castellano empieza en 2018). Francés solo informativo. |

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

**Valores de referencia (Cataluña, 2025, `kpi_subcompetencia_2025.csv`).**

| Materia | Subcompetencia | K02 | Puntuaciones válidas |
|---|---|---:|---:|
| Lengua catalana | Comprensión lectora | 78,05 | 66.151 |
| Lengua catalana | Comprensión oral | 73,77 | 66.151 |
| Lengua catalana | Expresión escrita | 66,98 | 66.151 |
| Lengua castellana | Comprensión lectora | 79,03 | 67.212 |
| Lengua castellana | Comprensión oral | 81,15 | 67.212 |
| Lengua castellana | Expresión escrita | 70,80 | 67.212 |
| Matemáticas | Numeración y cálculo | 74,13 | 66.995 |
| Matemáticas | Espacio, medida y datos | 71,54 | 66.995 |
| Matemáticas | Relaciones y cambio | 66,13 | 66.995 |
| Lengua inglesa | Comprensión lectora | 73,77 | 66.813 |
| Lengua inglesa | Comprensión oral | 77,89 | 66.813 |
| Lengua inglesa | Expresión escrita | 77,27 | 66.813 |
| Lengua francesa (informativa) | Comprensión lectora | 55,78 | 243 |
| Lengua francesa (informativa) | Comprensión oral | 75,72 | 243 |
| Lengua francesa (informativa) | Expresión escrita | 77,98 | 243 |
| Ciencias | Explicar fenómenos naturales y tecnológicos | 66,70 | 66.509 |
| Ciencias | Reconocer la investigación científica | 64,72 | 66.509 |
| Ciencias | Interpretar datos y pruebas científicas | 67,55 | 66.509 |

En 2025 la expresión escrita es la subcompetencia más baja en catalán y castellano, y «Relaciones y cambio», la más baja de matemáticas. Los ficheros de validación no incluyen K02 por área.

#### K03 — % alumnado nivel bajo

| Campo | Contenido |
|---|---|
| Código y nombre | K03 · `K03 % alumnado nivel bajo` |
| Perspectiva | Rendimiento académico (usuarios) |
| Objetivo estratégico | Mejorar el dominio de las competencias básicas (reducir el alumnado que no alcanza el nivel mínimo) |
| Definición | Porcentaje de puntuaciones globales en el nivel Bajo (menos de 55 puntos, `DimNivelLogro[NivelKey] = 1`) sobre el total de puntuaciones globales del contexto. |
| Unidad y formato | Porcentaje · `0.0%` |
| Interpretación | Cuanto más bajo, mejor. |
| Filtros y exclusiones de calidad | Numerador y denominador excluyen las celdas censuradas (`Censurada`, R26; entre las globales, inglés 2015, con suelos artificiales) y las convocatorias con nivel no comparable (`NivelNoComparable`, R28: inglés 2015 y 2016, matemáticas 2015 y 2019, catalán 2018 y francés 2022). Ignora los filtros de `DimNivelLogro`. |
| Mínimo muestral | 30 puntuaciones en el denominador ya filtrado. |
| Limitaciones | Los cortes 55/70/85 son internos del TFG: aproximan los % oficiales por nivel con un error medio de 2,70 pp en el nivel bajo, pero no los reproducen en cada año (informe de calidad, §6.3). En las convocatorias marcadas con `NivelNoComparable` la medida queda en blanco si el contexto solo contiene esas convocatorias. |

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

**Valores de referencia (Cataluña, 2025).**

| Materia | K03 |
|---|---:|
| Lengua catalana | 14,24 % |
| Lengua castellana | 9,82 % |
| Matemáticas | 22,66 % |
| Lengua inglesa | 15,36 % |
| Lengua francesa (informativa) | 21,81 % |
| Ciencias | 26,93 % |
| **Todas las materias** | **17,80 %** |

**Ejemplo por área (2025, `semaforos_2025.csv`).** En ciencias, el Barcelonès tiene un 35,07 % de puntuaciones en nivel bajo (8,14 pp por encima de Cataluña); en castellano, Maresme - Vallès Oriental tiene un 7,70 % (2,12 pp por debajo).

### 3.2. Perspectiva de equidad e inclusión

#### K04 — Brecha de género (Niños - Niñas)

| Campo | Contenido |
|---|---|
| Código y nombre | K04 · `K04 Brecha de género (Niños - Niñas)` |
| Perspectiva | Equidad e inclusión (procesos internos) |
| Objetivo estratégico | Reducir las brechas entre grupos de alumnado |
| Definición | Diferencia entre K01 de los niños y K01 de las niñas en el contexto de filtro. Sustituye cualquier filtro de género previo (`DimPerfilAlumno[Genero]` y su columna de orden `GeneroCodigo`). |
| Unidad y formato | Puntos · `+0.0;-0.0;0.0` (con signo) |
| Interpretación | Positivo: los niños puntúan más; negativo: las niñas puntúan más. El objetivo es un valor cercano a 0. |
| Filtros y exclusiones de calidad | Las del K01. El género se normaliza en la ETL (R09: «H»/«Home» → Niño; «D»/«Dona» → Niña); sin esa regla, 2021 no tendría datos de género. |
| Mínimo muestral | Cada uno de los dos grupos debe tener al menos 30 puntuaciones globales; si no, `BLANK()`. |
| Limitaciones | Brecha bruta, no estandarizada por la dispersión del año. Sin filtro de materia mezcla materias con brechas de signo opuesto. Francés solo informativo. |

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

**Valores de referencia (Cataluña, 2025).**

| Materia | K04 |
|---|---:|
| Lengua catalana | −3,98 |
| Lengua castellana | −4,35 |
| Matemáticas | +4,59 |
| Lengua inglesa | −3,37 |
| Lengua francesa (informativa) | −4,51 |
| Ciencias | +0,59 |

Las niñas obtienen mejores resultados en las lenguas y los niños, en matemáticas; en ciencias la brecha es pequeña. Los ficheros de validación no incluyen K04 por área.

#### K05 — Brecha pública - privada

| Campo | Contenido |
|---|---|
| Código y nombre | K05 · `K05 Brecha pública - privada` |
| Perspectiva | Equidad e inclusión (procesos internos) |
| Objetivo estratégico | Reducir las brechas entre tipos de centro |
| Definición | Diferencia entre K01 de los centros públicos y K01 de los centros privados en el contexto de filtro. Sustituye el filtro de naturaleza previo (`Naturaleza` y `NaturalezaCodigo`). |
| Unidad y formato | Puntos · `+0.0;-0.0;0.0` |
| Interpretación | Positivo: la pública puntúa más; negativo: la privada puntúa más. El objetivo es un valor cercano a 0. |
| Filtros y exclusiones de calidad | Las del K01. La naturaleza se normaliza en la ETL (R10). La categoría «Privada» incluye la concertada: el dataset no las distingue. |
| Mínimo muestral | 30 puntuaciones globales en cada grupo. |
| Limitaciones | Brecha bruta: no controla el nivel socioeconómico del alumnado, que el dataset no recoge, así que no puede atribuirse a la titularidad del centro. Francés solo informativo. |

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

**Valores de referencia (Cataluña, 2025).**

| Materia | K05 |
|---|---:|
| Lengua catalana | −5,16 |
| Lengua castellana | −4,42 |
| Matemáticas | −4,31 |
| Lengua inglesa | −8,72 |
| Lengua francesa (informativa) | en blanco (un grupo con menos de 30 puntuaciones) |
| Ciencias | −4,01 |

La privada supera a la pública en todas las materias calculables; la brecha mayor es la de inglés. Los ficheros de validación no incluyen K05 por área.

#### K06 — Dispersión de resultados

| Campo | Contenido |
|---|---|
| Código y nombre | K06 · `K06 Dispersión de resultados` |
| Perspectiva | Equidad e inclusión (procesos internos) |
| Objetivo estratégico | Reducir la desigualdad de resultados dentro del alumnado |
| Definición | Desviación típica poblacional (`STDEV.P`) de las puntuaciones globales del contexto. |
| Unidad y formato | Puntos · `0.0` |
| Interpretación | Cuanto más baja, más homogéneos son los resultados (más equidad). |
| Filtros y exclusiones de calidad | Solo globales; excluye las celdas censuradas (`Censurada`, R26). |
| Mínimo muestral | 30 puntuaciones globales no censuradas. |
| Limitaciones | Sin filtro de materia mezcla las distribuciones de varias materias. Debe interpretarse con cautela en catalán 2018, inglés 2011 (techo en la comprensión oral) y matemáticas 2015 y 2019 (escala y compresión), según el informe de calidad (§6.4). Francés solo informativo. |

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

**Valores de referencia (Cataluña, 2025).**

| Materia | K06 |
|---|---:|
| Lengua catalana | 16,61 |
| Lengua castellana | 15,21 |
| Matemáticas | 19,67 |
| Lengua inglesa | 18,22 |
| Lengua francesa (informativa) | 14,37 |
| Ciencias | 17,98 |
| **Todas las materias** | **18,00** |

La serie sin filtro de materia sube de 15,40 en 2009 a 18,00 en 2025 (`kpi_global_por_anio.csv`). Los ficheros de validación no incluyen K06 por área.

### 3.3. Perspectiva de territorio y entorno

#### K07 — Desviación respecto a Cataluña

| Campo | Contenido |
|---|---|
| Código y nombre | K07 · `K07 Desviación respecto a Cataluña` |
| Perspectiva | Territorio y entorno (procesos internos) |
| Objetivo estratégico | Equilibrio territorial de los resultados |
| Definición | K01 del contexto menos la puntuación media de Cataluña con el mismo año, competencia y perfil (medida auxiliar `Puntuación media Cataluña`). |
| Unidad y formato | Puntos · `+0.0;-0.0;0.0` |
| Interpretación | Positivo: el contexto (área, naturaleza, hábitat o su combinación) supera la media catalana; negativo: queda por debajo. Vale 0 si no hay ningún filtro de `DimContextoCentro`. |
| Filtros y exclusiones de calidad | Las del K01. La media de Cataluña incluye el área «Desconocida». |
| Mínimo muestral | Heredado: `BLANK()` si alguna de las dos medias está en blanco. |
| Limitaciones | Comparación válida dentro de cada año. Las áreas cambian de perímetro (Decret 120/2023; regla R14): «Barcelona Comarques» existe hasta 2024 y el «Barcelonès» aparece en 2025. Francés solo informativo. |

```dax
Puntuación media Cataluña =
CALCULATE (
    [K01 Puntuación media competencia],
    REMOVEFILTERS ( DimContextoCentro )
)
```

```dax
K07 Desviación respecto a Cataluña =
VAR _k01 = [K01 Puntuación media competencia]
VAR _cataluna = [Puntuación media Cataluña]
RETURN
    IF ( NOT ISBLANK ( _k01 ) && NOT ISBLANK ( _cataluna ), _k01 - _cataluna )
```

**Valores de referencia (2025, `kpi_area_2025.csv`).** Para Cataluña sin filtro de contexto, K07 vale 0 por definición. Ejemplos por área:

| Área | Materia | K01 | Media de Cataluña | K07 |
|---|---|---:|---:|---:|
| Consorci d'Educació de Barcelona | Lengua inglesa | 79,08 | 75,74 | +3,34 |
| Terres de l'Ebre | Matemáticas | 72,45 | 70,42 | +2,03 |
| Alt Pirineu i Aran | Ciencias | 68,35 | 66,32 | +2,03 |
| Barcelonès | Ciencias | 62,44 | 66,32 | −3,88 |
| Barcelonès | Matemáticas | 66,78 | 70,42 | −3,64 |

El Barcelonès queda por debajo de la media catalana en todas las materias calculables de 2025 (entre −2,86 y −3,88), y el Consorci d'Educació de Barcelona, por encima en todas (entre +1,06 y +3,34).

#### K08 — Diferencia urbano - rural

| Campo | Contenido |
|---|---|
| Código y nombre | K08 · `K08 Diferencia urbano - rural` |
| Perspectiva | Territorio y entorno (procesos internos) |
| Objetivo estratégico | Equilibrio de resultados entre entornos urbanos y rurales |
| Definición | K01 en municipios de más de 100.000 habitantes (`HabitatCodigo = 3`) menos K01 en municipios de hasta 10.000 habitantes (`HabitatCodigo = 1`). Sustituye el filtro de hábitat previo. |
| Unidad y formato | Puntos · `+0.0;-0.0;0.0` |
| Interpretación | Positivo: el entorno urbano puntúa más; negativo: el rural puntúa más. El objetivo es un valor cercano a 0. |
| Filtros y exclusiones de calidad | Las del K01. El hábitat 0 «No fiable» nunca entra (R11, R12: todo 2010 y parte de Baix Llobregat 2014), así que en 2010 K08 queda en blanco. El tramo intermedio (10.001–100.000 habitantes) no interviene. |
| Mínimo muestral | 30 puntuaciones globales en cada uno de los dos grupos. |
| Limitaciones | Girona y Maresme - Vallès Oriental tienen una ruptura en la clasificación del hábitat desde 2024 (`DimContextoCentro[RupturaHabitat2024]`). Francés solo informativo. |

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

**Valores de referencia (Cataluña, 2025).**

| Materia | K08 |
|---|---:|
| Lengua catalana | −2,12 |
| Lengua castellana | −1,06 |
| Matemáticas | −1,91 |
| Lengua inglesa | +0,49 |
| Lengua francesa (informativa) | en blanco (un grupo con menos de 30 puntuaciones) |
| Ciencias | −2,53 |

En 2025 los municipios pequeños puntúan algo más que las grandes ciudades en todas las materias calculables salvo inglés. Los ficheros de validación no incluyen K08 por área.

#### K09 — Posición del área

| Campo | Contenido |
|---|---|
| Código y nombre | K09 · `K09 Posición del área` |
| Perspectiva | Territorio y entorno (procesos internos) |
| Objetivo estratégico | Equilibrio territorial: situar cada área respecto a las demás |
| Definición | Puesto del área territorial (1 = mejor) al ordenar las áreas por K01 descendente, con empates densos (`DENSE`), dentro del mismo año, competencia, naturaleza y hábitat. Con `DimContextoCentro[AreaTerritorial]` en el eje del visual compara con las áreas visibles (`ALLSELECTED`); en una tarjeta con el área elegida en un segmentador, compara con todas las áreas. |
| Unidad y formato | Posición ordinal · `0` |
| Interpretación | Cuanto más bajo, mejor (1 = área con mayor K01). |
| Filtros y exclusiones de calidad | Las del K01. «Desconocida» nunca entra en la comparación. Excluye el francés: devuelve `BLANK()` si todas las competencias del contexto son informativas. |
| Mínimo muestral | Heredado del K01 del área; un área con K01 en blanco no recibe posición. |
| Limitaciones | Es un indicador ordinal: no informa de la distancia entre áreas (para eso está K07). El número de áreas cambia con los perímetros territoriales (R14). |

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

**Valores de referencia (2025, comparación con todas las áreas, `kpi_area_2025.csv`).**

| Materia | Primera área (K09 = 1) | Última área |
|---|---|---|
| Lengua catalana | Consorci d'Educació de Barcelona (75,01) | Barcelonès (12; 70,07) |
| Lengua castellana | Consorci d'Educació de Barcelona (77,72) | Barcelonès (12; 73,61) |
| Matemáticas | Terres de l'Ebre (72,45) | Barcelonès (12; 66,78) |
| Lengua inglesa | Consorci d'Educació de Barcelona (79,08) | Alt Pirineu i Aran (12; 72,51) |
| Ciencias | Alt Pirineu i Aran (68,35) | Barcelonès (12; 62,44) |
| Lengua francesa | en blanco (materia informativa) | — |

### 3.4. Perspectiva de eficiencia y progreso

#### K10 — Variación interanual

| Campo | Contenido |
|---|---|
| Código y nombre | K10 · `K10 Variación interanual` |
| Perspectiva | Eficiencia y progreso (aprendizaje y crecimiento) |
| Objetivo estratégico | Mejora continua entre convocatorias |
| Definición | K01 de la convocatoria del contexto menos K01 de la convocatoria anterior, navegando por `DimAnio[IndiceConvocatoria]` (2021 se compara con 2019). Solo usa las competencias globales cuyo `PeriodoDisenoInicio` es menor o igual que el año de la convocatoria anterior. |
| Unidad y formato | Puntos · `+0.0;-0.0;0.0` |
| Interpretación | Positivo: mejora respecto a la convocatoria anterior; negativo: empeora. |
| Filtros y exclusiones de calidad | Las del K01, más la restricción de periodo de diseño comparable. `BLANK()` si el contexto no tiene exactamente un año con convocatoria, si es la primera convocatoria o si no queda ninguna competencia comparable. |
| Mínimo muestral | Heredado: K01 de las dos convocatorias con al menos 30 puntuaciones. |
| Limitaciones | **Puntuaciones no equiparadas:** la diferencia mezcla la dificultad de cada prueba con el rendimiento real y solo es orientativa. Antes de que empiecen los periodos de diseño estables, la medida solo cubre algunas materias (en 2017, solo inglés y francés). Por área, las series se rompen con los cambios de perímetro: el Barcelonès no tiene K10 en 2025 porque en 2024 ese perímetro figuraba como «Barcelona Comarques». |

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

**Valores de referencia (Cataluña, 2025 frente a 2024).**

| Materia | K10 |
|---|---:|
| Lengua catalana | −1,32 |
| Lengua castellana | +2,58 |
| Matemáticas | −3,94 |
| Lengua inglesa | +2,47 |
| Lengua francesa (informativa) | +3,29 |
| Ciencias | −8,16 |
| **Todas las materias** | **−1,66** |

**Ejemplo por área (2025, `semaforos_2025.csv`).** Alt Pirineu i Aran: −7,18 en matemáticas y +0,77 en inglés. Barcelonès: en blanco en todas las materias.

#### K11 — Tendencia 5 convocatorias

| Campo | Contenido |
|---|---|
| Código y nombre | K11 · `K11 Tendencia 5 convocatorias` |
| Perspectiva | Eficiencia y progreso (aprendizaje y crecimiento) |
| Objetivo estratégico | Mejora continua sostenida |
| Definición | Variación media por convocatoria en una ventana de cinco convocatorias: (K01 de la convocatoria *i* − K01 de la convocatoria *i*−4) / 4, navegando por `DimAnio[IndiceConvocatoria]`. Solo usa las competencias globales con `PeriodoDisenoInicio` menor o igual que el año de la convocatoria *i*−4. |
| Unidad y formato | Puntos por convocatoria · `+0.0;-0.0;0.0` |
| Interpretación | Positivo: tendencia de mejora; negativo: tendencia de empeoramiento. |
| Filtros y exclusiones de calidad | Las del K10. `BLANK()` si el contexto no tiene exactamente un año con convocatoria, si no hay cuatro convocatorias anteriores o si no queda ninguna competencia comparable. |
| Mínimo muestral | Heredado: K01 de las convocatorias *i* e *i*−4 con al menos 30 puntuaciones. |
| Limitaciones | **Puntuaciones no equiparadas** (orientativo). Solo usa los extremos de la ventana, no las convocatorias intermedias. Para 2025 la ventana es 2021–2025; antes de 2023 solo cubre algunas materias (por ejemplo, en 2021 solo inglés y francés). |

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

**Valores de referencia (Cataluña, 2025: ventana 2021–2025).**

| Materia | K11 |
|---|---:|
| Lengua catalana | −0,78 |
| Lengua castellana | +0,73 |
| Matemáticas | −1,40 |
| Lengua inglesa | +0,64 |
| Lengua francesa (informativa) | −2,42 |
| Ciencias | −2,31 |
| **Todas las materias** | **−0,62** |

Los ficheros de validación no incluyen K11 por área.

#### K12 — % competencias que mejoran

| Campo | Contenido |
|---|---|
| Código y nombre | K12 · `K12 % competencias que mejoran` |
| Perspectiva | Eficiencia y progreso (aprendizaje y crecimiento) |
| Objetivo estratégico | Mejora continua generalizada a todas las materias |
| Definición | Porcentaje de materias globales no informativas que mejoran al menos 1 punto respecto a la convocatoria anterior (K10 ≥ 1), sobre las materias con K10 calculable. Itera por `DimCompetencia[CodigoMateria]`. |
| Unidad y formato | Porcentaje · `0.0%` |
| Interpretación | Cuanto más alto, mejor. |
| Filtros y exclusiones de calidad | Excluye el francés (`EsInformativa = TRUE`). Hereda todas las condiciones del K10: un solo año con convocatoria, periodo de diseño comparable y mínimo muestral. `BLANK()` si ninguna materia tiene K10. |
| Mínimo muestral | Heredado del K10 de cada materia; no hay un mínimo de materias. |
| Limitaciones | **Puntuaciones no equiparadas** (orientativo). El denominador es pequeño (como máximo cinco materias), así que el indicador varía a saltos de 20 pp; en 2017 solo el inglés era comparable y el resultado (100 %) se basa en una sola materia. Tiene sentido sin filtro de materia. |

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

**Valores de referencia (Cataluña, sin filtro de materia, `kpi_global_por_anio.csv`).**

| Convocatoria | 2017 | 2018 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| K12 | 100,0 % | 50,0 % | 40,0 % | 40,0 % | 20,0 % | 40,0 % | 60,0 % | 40,0 % |

En 2025 mejoran al menos 1 punto dos de las cinco materias comparables (castellano, +2,58, e inglés, +2,47). Los ficheros de validación no incluyen K12 por área.

---

## 4. Fichas de los semáforos

Los semáforos traducen un KPI a tres estados: **1 favorable**, **0 neutro** y **−1 desfavorable** (formato `0`). Están en la carpeta `5. Semáforos` de `_Medidas`.

#### Estado K01 — Semáforo de la puntuación media

| Campo | Contenido |
|---|---|
| Código y nombre | `Estado K01` |
| Perspectiva | Rendimiento académico |
| Objetivo estratégico | Señalar de un vistazo si el rendimiento del contexto es favorable |
| Definición | Regla con dos modos. **Con algún filtro de `DimContextoCentro`** (área, naturaleza o hábitat) usa K07: ≥ +1 punto → 1; ≤ −1 → −1; resto → 0. **Sin filtro de contexto de centro** usa K10: ≥ +0,5 → 1; ≤ −0,5 → −1; resto → 0. |
| Unidad y formato | Estado {−1, 0, 1} · `0` |
| Interpretación | 1: el contexto supera a Cataluña en al menos 1 punto (o Cataluña mejora al menos 0,5 respecto a la convocatoria anterior). |
| Filtros y exclusiones de calidad | Las de K07 o K10, según el modo. |
| Mínimo muestral | Heredado; `BLANK()` si el indicador usado está en blanco. |
| Limitaciones | El mismo semáforo responde a dos preguntas distintas según haya o no filtro de contexto (posición frente a Cataluña o evolución en el tiempo). En el modo K10 es orientativo (puntuaciones no equiparadas). Los umbrales son propuestas del TFG. Se muestra en la página «Operativo - Dirección de centro». |

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

**Valores de referencia (2025, `semaforos_2025.csv`).** Para Cataluña (modo K10): catalán −1, castellano 1, matemáticas −1, inglés 1, francés 1 y ciencias −1. Por área (modo K07): el Barcelonès tiene −1 en las cinco materias calculables y el Consorci d'Educació de Barcelona, 1 en las cinco.

#### Estado K03 — Semáforo del nivel bajo

| Campo | Contenido |
|---|---|
| Código y nombre | `Estado K03` |
| Perspectiva | Rendimiento académico |
| Objetivo estratégico | Señalar los contextos con más alumnado en nivel bajo que la media |
| Definición | Diferencia entre K03 del contexto y K03 de Cataluña (sin filtros de `DimContextoCentro`): ≤ −2 pp → 1 (favorable); ≥ +2 pp → −1 (desfavorable); resto → 0. |
| Unidad y formato | Estado {−1, 0, 1} · `0` |
| Interpretación | 1: el contexto tiene al menos 2 pp menos de alumnado en nivel bajo que Cataluña. |
| Filtros y exclusiones de calidad | Las de K03 (sin celdas censuradas ni convocatorias con nivel no comparable). |
| Mínimo muestral | Heredado; `BLANK()` si alguno de los dos K03 está en blanco. |
| Limitaciones | Sin filtro de contexto siempre vale 0 (Cataluña frente a sí misma). Niveles internos del TFG. En esta versión del informe ningún visual lo muestra. |

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

**Valores de referencia (2025, `semaforos_2025.csv`).** Cataluña: 0 en todas las materias. Lleida en ciencias: 24,15 % frente a 26,93 % (−2,78 pp) → 1. Barcelonès en ciencias: 35,07 % frente a 26,93 % (+8,14 pp) → −1.

#### Estado K10 — Semáforo de la variación interanual

| Campo | Contenido |
|---|---|
| Código y nombre | `Estado K10` |
| Perspectiva | Eficiencia y progreso |
| Objetivo estratégico | Señalar si el contexto mejora o empeora respecto a la convocatoria anterior |
| Definición | K10 ≥ +0,5 puntos → 1; K10 ≤ −0,5 → −1; resto → 0. |
| Unidad y formato | Estado {−1, 0, 1} · `0` |
| Interpretación | 1: mejora de al menos medio punto respecto a la convocatoria anterior. |
| Filtros y exclusiones de calidad | Las de K10. |
| Mínimo muestral | Heredado; `BLANK()` si K10 está en blanco. |
| Limitaciones | **Puntuaciones no equiparadas** (orientativo). En esta versión del informe ningún visual lo muestra. |

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

**Valores de referencia (2025, `semaforos_2025.csv`).** Cataluña: catalán −1, castellano 1, matemáticas −1, inglés 1, francés 1 y ciencias −1. Ejemplo de lectura conjunta: en catalán, el Consorci d'Educació de Barcelona tiene `Estado K01` = 1 (K07 = +1,48) pero `Estado K10` = −1 (K10 = −1,59): está por encima de Cataluña, pero empeora respecto a 2024.

---

## 5. Validación de los indicadores

### 5.1. Método: doble implementación

Las medidas DAX solo pueden evaluarse dentro de Power BI. Para comprobar que calculan lo que dicen las fichas, el TFG sigue un método de **doble implementación**: los mismos indicadores se programan dos veces, de forma independiente, y se comparan los resultados.

| Implementación | Componentes | Resultado |
|---|---|---|
| Power BI | ETL en Power Query (M) y 19 medidas DAX en `_Medidas.tmdl` | Modelo semántico TMDL y el informe de tres páginas |
| Réplica de referencia en Python | `validacion/etl_referencia.py` (ETL con pandas y DuckDB, reglas R01–R29 del contrato de diseño) y `validacion/kpis_referencia.py` (los 12 KPI y los 3 semáforos con la misma semántica que las medidas DAX) | Las ocho tablas del modelo en estrella (`validacion/salida/*.parquet`) y seis CSV de valores de referencia (`validacion/resultados/`) |

Ambas implementaciones parten del mismo contrato de diseño (`trabajo_en_curso/contrato_diseno.md`), que fija nombres, claves, reglas de limpieza y la semántica de cada medida: mínimo muestral de 30, `REMOVEFILTERS ( DimContextoCentro )` para Cataluña, navegación por `IndiceConvocatoria`, periodo de diseño comparable y exclusión del francés en K09 y K12. La réplica Python se completa con `validacion/test_modelo.py`, que comprueba recuentos (1.102.324 evaluaciones y 17.728.085 puntuaciones, 4.769.851 de ellas globales), ausencia de claves huérfanas, las rotaciones R03/R04 (con control negativo sobre el CSV original), la media corregida de castellano 2017 (73,51) y el contraste con las medias oficiales; los 27 tests pasan.

La validación tiene dos niveles:

1. **Validación externa** de la ETL y del K01: las medias de Cataluña por materia y año se contrastan con las publicadas por el Consell Superior d'Avaluació del Sistema Educatiu (apartado 5.2).
2. **Validación cruzada DAX–Python**: al abrir el modelo en Power BI Desktop, las cifras de cada visual se comparan con las de `validacion/resultados/*.csv`. En la versión actual, la correspondencia semántica entre las medidas DAX y la réplica se ha revisado sobre el código, y el modelo TMDL se ha validado con la librería oficial de Microsoft (TOM, `Model.Validate()` sin errores). Sin embargo, el código M y las medidas DAX todavía no se han ejecutado en Power BI Desktop, así que el contraste numérico de este segundo nivel queda pendiente de la primera apertura del modelo (`trabajo_en_curso/ESTADO.md`).

### 5.2. Contraste con las medias oficiales

El fichero `validacion/resultados/contraste_oficial.csv` compara K01 de Cataluña por materia y convocatoria (columna `media_calculada`) con la media oficial de los *Quaderns d'avaluació* (contrato de diseño, §6). La tolerancia es de ±0,2 puntos, ya que las medias oficiales se publican con un decimal.

| Resultado | Valor |
|---|---|
| Combinaciones materia-convocatoria contrastadas (2009–2025, sin 2020) | 72 |
| Dentro de la tolerancia de ±0,2 puntos | **70 (97,2 %)** |
| Diferencia absoluta ≤ 0,1 puntos | 65 |
| Diferencia absoluta media / mediana | 0,048 / 0,03 puntos |
| Diferencia máxima dentro de tolerancia | 0,18 (ciencias 2024) |

Las dos combinaciones fuera de tolerancia son:

| Convocatoria | Materia | Calculada | Oficial | Diferencia | Explicación provisional (columna `nota`) |
|---|---|---:|---:|---:|---|
| 2016 | Lengua inglesa | 73,94 | 73,7 | +0,24 | Convocatoria con nota de calidad: escalas de comprensión oral y lectora comprimidas y % por nivel no comparable (R27, R28); falta contrastar la *n* oficial. |
| 2024 | Lengua francesa | 62,80 | 62,5 | +0,30 | Francés solo informativo, con *n* = 266 (PUN-19). |

Ambas figuran en el CSV como «fuera de tolerancia, pendiente de documentar en §4.6» del informe de calidad, y `test_modelo.py` las trata como excepciones conocidas. Ninguna afecta a una materia troncal en una convocatoria sin incidencias de calidad conocidas. Otras diferencias dentro de la tolerancia se explican por diferencias de población ya documentadas en el informe de calidad (§4.6): en 2017 el CSV tiene 756 alumnos menos en castellano y 791 en inglés; en 2024, 1.024 menos en catalán y 395 en matemáticas; y en 2025, 41 más en matemáticas.

El contraste confirma que la lectura del CSV, las correcciones de la ETL (en particular la rotación de castellano 2017, que lleva la media de 74,30 sin corregir a 73,51) y la definición de K01 reproducen las cifras oficiales de Cataluña.

---

## Referencias

- Kaplan, R. S. y Norton, D. P. (1992). The Balanced Scorecard: Measures That Drive Performance. *Harvard Business Review*.
- Niven, P. R. (2008). *Balanced Scorecard Step-by-Step for Government and Nonprofit Agencies* (2.ª ed.). Wiley.
- Consell Superior d'Avaluació del Sistema Educatiu. *Quaderns d'avaluació* de sexto de primaria, 2009–2025 (handles en el informe de calidad, §2.3).
- Rodríguez Uribe, K. *Informe de calidad de datos del dataset «Avaluació de sisè d'educació primària»* (`01_Informe_calidad_datos.md`).
