# Guía de uso del Cuadro de Mando Integral

**Proyecto:** Cuadro de Mando Integral (CMI) en Power BI sobre la evaluación de 6.º de educación primaria de Cataluña
**Autora:** Kiara Rodríguez Uribe (TFG, FIB-UPC)
**Destinatarios:** la propia autora y cualquier usuario técnico que tenga que abrir, actualizar, validar o ampliar el CMI.

Esta guía describe cómo poner en marcha el cuadro de mando a partir del repositorio, cómo comprobar que la carga es correcta, cómo se usa cada página y cómo se mantiene el proyecto cuando se publica una nueva convocatoria. Todo lo que se describe corresponde a los ficheros que existen en el repositorio: el proyecto Power BI (`PowerBI/`), la réplica de validación en Python (`validacion/`) y los generadores y herramientas de `trabajo_en_curso/`.

> **Aviso importante.** El código Power Query (M) del modelo se ha validado sintácticamente y contrastado con la réplica Python, pero **todavía no se ha ejecutado nunca en Power BI Desktop** (punto INT-03, apartado 8). La primera actualización descrita en el apartado 3 es, por tanto, también la prueba de integración final del proyecto.

---

## 1. Requisitos

| Requisito | Detalle |
|---|---|
| Sistema operativo | Windows (Power BI Desktop solo existe para Windows). |
| Power BI Desktop | Versión actualizada (Microsoft Store o instalador oficial). El proyecto usa el formato de proyecto PBIP, con el modelo semántico en TMDL y el informe en PBIR. |
| Datos | `Datos.csv` (unos 240 MB, 1.102.324 registros, 32 columnas), que se obtiene descomprimiendo `Datos.zip` (apartado 2). |
| Memoria | Recomendable disponer de memoria holgada: la tabla `FactPuntuacion` tiene 17.728.085 filas. |
| Validación (opcional) | Python 3 con las dependencias de `validacion/requirements.txt` (pandas, duckdb, pyarrow, etc.). Las herramientas de `trabajo_en_curso/herramientas` necesitan además Node.js y .NET 8 (apartado 6). |

### 1.1. Activar el formato PBIP/PBIR si la versión lo requiere

En las versiones más recientes de Power BI Desktop el formato de proyecto ya está disponible de forma general. Si al abrir `CMI_Educacion_Primaria.pbip` aparece un error de formato no admitido, o la opción no está disponible, hay que activarlo como característica en versión preliminar:

1. **Archivo > Opciones y configuración > Opciones**.
2. En **Global**, abrir **Características en versión preliminar**.
3. Marcar las opciones relativas a:
   - el formato de guardado de proyecto de Power BI (`.pbip`);
   - el almacenamiento del modelo semántico en formato TMDL;
   - el almacenamiento de informes en formato de metadatos mejorado (PBIR).
4. Aceptar y **reiniciar Power BI Desktop**.

El nombre exacto de cada opción puede variar ligeramente entre versiones; si alguna ya no aparece es porque ha dejado de ser preliminar.

---

## 2. Obtención y ubicación del dataset

El dataset original (Avaluació de sisè d'educació primària, Generalitat de Catalunya) se versiona comprimido como `Datos.zip` en la raíz del repositorio, porque el CSV supera el límite de 100 MB por fichero de GitHub. `Datos.csv` **no** está en git (está en `.gitignore`) y no debe subirse.

### 2.1. Descomprimir

En PowerShell, desde la raíz del repositorio:

```powershell
Expand-Archive -Path .\Datos.zip -DestinationPath . -Force
```

El zip contiene un único fichero, `Datos.csv` (240.120.178 bytes).

### 2.2. Opción A: copiarlo a la ruta por defecto

El modelo lee el fichero desde el parámetro de Power Query `RutaDatos`, cuyo valor por defecto es:

```text
C:\TFG_Project\Datos.csv
```

Basta con crear la carpeta `C:\TFG_Project` y copiar en ella `Datos.csv`. No hay que modificarlo: la ETL lo lee como texto y no lo altera.

### 2.3. Opción B: cambiar el parámetro `RutaDatos`

Si el fichero está en otra ubicación (por ejemplo, en la raíz del repositorio clonado):

1. En Power BI Desktop, **Inicio > Transformar datos > Editar parámetros** (o, dentro del Editor de Power Query, **Administrar parámetros**).
2. Seleccionar `RutaDatos` (grupo de consultas *Parámetros*) y escribir la ruta completa del fichero, incluido el nombre `Datos.csv`.
3. Aceptar y aplicar los cambios.

El parámetro es de tipo texto y obligatorio. Cambiarlo desde Power BI Desktop modifica `expressions.tmdl`; si después se regenera el modelo con los generadores (apartado 7), el valor vuelve al de por defecto.

---

## 3. Apertura y primera actualización

### 3.1. Abrir el proyecto

1. Abrir `PowerBI/CMI_Educacion_Primaria.pbip` con Power BI Desktop. El fichero `.pbip` apunta al informe `CMI_Educacion_Primaria.Report`, que a su vez referencia el modelo `CMI_Educacion_Primaria.SemanticModel`.
2. Como el modelo se distribuye sin datos, al abrirlo las tablas están vacías y los visuales no muestran valores.
3. Comprobar o ajustar `RutaDatos` (apartado 2).
4. Pulsar **Inicio > Actualizar**.

La actualización ejecuta la consulta compartida `stg_Evaluaciones` (grupo *Staging*, no se carga en el modelo), que lee `Datos.csv` y aplica las reglas de limpieza R01–R21 del informe de calidad, y después las consultas de las ocho tablas del modelo en estrella:

| Grupo | Tablas |
|---|---|
| Dimensiones | `DimAnio`, `DimContextoCentro`, `DimPerfilAlumno`, `DimCompetencia`, `DimNivelLogro`, `DimCalidadDato` |
| Hechos | `FactEvaluacion`, `FactPuntuacion` |
| Medidas | `_Medidas` (19 medidas DAX) |

### 3.2. Lista de comprobación tras la primera actualización

Los valores esperados proceden del contrato de diseño (§6) y de la réplica Python (`validacion/resultados/*.csv`), que se ha contrastado con los Quaderns d'avaluació oficiales.

**Recuentos de filas** (vista de tabla o una tarjeta con `COUNTROWS`):

| Tabla | Filas esperadas |
|---|---|
| `FactEvaluacion` | 1.102.324 |
| `FactPuntuacion` | 17.728.085 (4.769.851 puntuaciones globales + 12.958.234 de subcompetencias) |
| `DimAnio` | 17 (2009–2025, incluido 2020 sin prueba) |
| `DimContextoCentro` | 120 (15 áreas × 2 naturalezas × 4 hábitats) |
| `DimPerfilAlumno` | 182 |
| `DimCompetencia` | 24 |
| `DimNivelLogro` | 5 |
| `DimCalidadDato` | 16 |

**Valores de control de las medidas:**

| Comprobación | Valor esperado | Fuente |
|---|---|---|
| K01 Lengua castellana, 2017 (rotación de columnas R03 corregida) | **73,51** (oficial 73,4) | `contraste_oficial.csv` |
| Alumnos evaluados 2025 | 68.911 | `kpi_cataluna_por_anio_materia.csv` |
| *Puntuación media Cataluña* 2025, Matemáticas (página 3) | 70,42, igual que K01 de Cataluña | `kpi_area_2025.csv` |

**K01 de Cataluña en 2025 por materia** (página *Estratégico - Departamento*, segmentador de año en 2025, tabla *Resumen por materia*), según `validacion/resultados/kpi_cataluna_por_anio_materia.csv`:

| Materia | K01 | K03 (% nivel bajo) | K06 | K10 | K11 | Puntuaciones globales |
|---|---|---|---|---|---|---|
| Lengua catalana | 73,53 | 14,24 | 16,61 | −1,32 | −0,78 | 66.151 |
| Lengua castellana | 76,47 | 9,82 | 15,21 | 2,58 | 0,73 | 67.212 |
| Matemáticas | 70,42 | 22,66 | 19,67 | −3,94 | −1,40 | 66.995 |
| Lengua inglesa | 75,74 | 15,36 | 18,22 | 2,47 | 0,64 | 66.813 |
| Lengua francesa | 66,09 | 21,81 | 14,37 | 3,29 | −2,42 | 243 |
| Ciencias | 66,32 | 26,93 | 17,98 | −8,16 | −2,31 | 66.509 |

Para el conjunto de materias en 2025 (`kpi_global_por_anio.csv`): K01 = 72,50; K03 = 17,80 %; K06 = 18,00; K10 = −1,66; K11 = −0,62; K12 = 40,0 %.

Los formatos de Power BI redondean a un decimal (`0.0`), por lo que, por ejemplo, 73,51 se verá como 73,5. Para el resto de visuales hay referencias en:

| Fichero | Sirve para comprobar |
|---|---|
| `kpi_cataluna_por_anio_materia.csv` | Tarjetas y tabla de la página 1, línea de evolución de K01 por materia (2009–2025). |
| `kpi_global_por_anio.csv` | Tarjetas de la página 1 sin materia seleccionada. |
| `kpi_area_2025.csv` | Barras K07 y tooltip K09 de la página 2; tarjetas K01 y K07 de la página 3 al elegir un área. |
| `kpi_subcompetencia_2025.csv` | Barras K02 por subcompetencia de la página 3 (por ejemplo, Comprensión lectora de castellano = 79,03). |
| `semaforos_2025.csv` | Tarjeta *Estado K01* de la página 3 (1 favorable, 0 neutro, −1 desfavorable). |
| `contraste_oficial.csv` | Medias de Cataluña frente a los Quaderns d'avaluació (tolerancia ±0,2). |

Celda vacía en los CSV equivale a `BLANK()` en DAX (mínimo muestral de 30, convocatoria sin anterior, periodo no comparable, francés en K09, etc.). K03 y K12 están en porcentaje en los CSV y en formato `0.0%` en Power BI.

**Prueba negativa recomendada** (pendiente en `ESTADO.md`): en una **copia** de `Datos.csv`, poner una puntuación inválida (por ejemplo `150,00` o `abc`), apuntar `RutaDatos` a la copia y comprobar que la actualización falla con el mensaje de la regla R02. No hay que modificar nunca el fichero original.

### 3.3. Si la actualización falla

La consulta `stg_Evaluaciones` está diseñada para **detener la actualización** cuando los datos no cumplen las reglas, en lugar de cargar celdas con error como vacías (que es lo que haría Power BI por defecto). Para ello busca la primera fila con algún error y eleva su `Error.Record` a toda la consulta; el mensaje indica la regla, el valor encontrado y el `EvaluacionID` (posición del registro en el fichero).

| Motivo (Reason) | Mensaje | Causa probable y solución |
|---|---|---|
| — (error de acceso a archivo) | No se encuentra el fichero | `RutaDatos` no apunta a un `Datos.csv` existente. Revisar el apartado 2. |
| `Estructura de Datos.csv` | «La cabecera no coincide con las 32 columnas esperadas.» (con la lista de columnas encontradas) | El fichero no es el original o la Generalitat ha cambiado la estructura (columnas añadidas, renombradas o reordenadas). Comparar la cabecera con la lista `ColumnasCsv` de `m_stg.m`. |
| `R02 Puntuación no válida` | «La columna X contiene «valor», que no es un número es-ES dentro de [0, 100].» | Puntuación no convertible con cultura es-ES (coma decimal) o fuera de rango. |
| `Año no válido` | «La columna ANY contiene «valor», que no es un año.» | Año vacío o no entero. |
| `R09 Género no reconocido` | «La columna GENERE contiene «valor».» | Solo se admiten `H`/`Home` y `D`/`Dona`. |
| `R10 Naturaleza no reconocida` | «La columna NATURALESA contiene «valor».» | Solo se admiten `Públic`/`Pública` y `Privat`/`Privada`. |
| `R11 Hábitat no reconocido` | «La columna HÀBITAT contiene «valor».» | Se admiten textos que empiezan por `Fins a`, el valor exacto `De 10001 a 100000` y textos que empiezan por `Més de`. |
| `Área territorial desconocida` | «La columna AREA_TERRITORIAL contiene «valor» en el año N.» | Área no incluida en la tabla de códigos (§5.1 del contrato) o `Barcelona Comarques` en un año posterior a 2024. |

Con los datos actuales ninguna de estas validaciones debería dispararse: el informe de calidad comprobó que los 17.728.085 valores de puntuación cumplen el formato y el rango (PUN-01). Si salta una, lo normal es que el fichero no sea el esperado o que corresponda a una convocatoria nueva (apartado 5).

---

## 4. Uso del cuadro de mando por perfil

El informe tiene tres páginas, una por nivel de decisión, con un lienzo de 1280 × 720. Todos los segmentadores son desplegables. El de **Año** es de selección única y arranca en **2025**. Los segmentadores con el mismo campo están **sincronizados entre páginas** (grupos `Anio`, `Materia` y `AreaTerritorial`): un año elegido en una página se mantiene al cambiar de página.

Avisos que acompañan a todas las páginas: las puntuaciones **no están equiparadas** entre convocatorias (las comparaciones temporales son orientativas) y **2020 no tuvo prueba** (COVID-19). Los umbrales de nivel de logro (55/70/85) son provisionales e internos del TFG, no oficiales. Una medida queda en blanco si se basa en menos de 30 puntuaciones.

### 4.1. Página 1. «Estratégico - Departamento»

Perfil: Departamento de Educación. Visión global de la convocatoria y de su evolución.

| Elemento | Contenido |
|---|---|
| Segmentadores | Año (único), Materia. |
| Tarjetas | K01 Puntuación media; K03 % de alumnado en nivel bajo (global < 55); K06 Dispersión (desviación típica); K10 Variación interanual; K12 % de competencias que mejoran (1 punto o más); Alumnos evaluados. |
| Gráfico de líneas | Evolución de K01 por año y materia. **No** se filtra por el segmentador de año: muestra siempre todas las convocatorias. |
| Tabla «Resumen por materia» | K01, K10, K11 (tendencia de 5 convocatorias) y K03 por materia, para el año seleccionado. |
| Cuadro de texto | Aviso de no equiparación y de 2020, umbrales provisionales y mínimo muestral. |

Uso típico: dejar el año en 2025 y leer la tabla para ver qué materias empeoran (K10 negativo) y cuáles tienen más alumnado en nivel bajo; elegir una materia en el segmentador para que las tarjetas muestren solo esa materia.

Nota: *Alumnos evaluados* cuenta registros de `FactEvaluacion`, que no se relaciona con `DimCompetencia`; por eso no cambia al filtrar por materia.

### 4.2. Página 2. «Táctico - Inspección»

Perfil: Inspección educativa. Comparación territorial y equidad.

| Elemento | Contenido |
|---|---|
| Segmentadores | Año (único), Materia, Área territorial. |
| Tarjetas | K04 Brecha de género (niños − niñas); K05 Brecha pública − privada; K08 Diferencia urbano − rural (más de 100.000 habitantes frente a hasta 10.000); K09 Posición del área (requiere una sola área seleccionada). |
| Barras K07 por área | Desviación de cada área respecto a Cataluña, con K01 y K09 en la información sobre herramientas. El segmentador de área **no** filtra este gráfico: siempre muestra todas las áreas, y el tooltip K09 coincide con la tarjeta. |
| Matriz área × naturaleza | K01 por área territorial y por centro público/privado. |
| Línea por serie territorial comparable | Evolución de K01 agrupando las áreas cuyo perímetro cambió en 2024–2025 (`AreaSerieComparable`). No se filtra por el segmentador de año. |

Uso típico: seleccionar año y materia, identificar en las barras las áreas por debajo de Cataluña y seleccionar una de ellas en el segmentador de área para ver su posición (K09) y sus brechas. K08 queda en blanco en 2010 (hábitat no fiable); Girona y Maresme - Vallès Oriental tienen ruptura en la clasificación del hábitat desde 2024.

### 4.3. Página 3. «Operativo - Dirección de centro»

Perfil: dirección de centro. Permite situar un contexto similar al del centro (no hay datos por centro) frente a Cataluña.

| Elemento | Contenido |
|---|---|
| Segmentadores | Área territorial, Naturaleza, Hábitat, Año (único), Materia. |
| Tarjetas | K01 del contexto seleccionado; K07 Desviación respecto a Cataluña; Puntuación media de Cataluña (sin filtros de contexto); Estado K01 (1 favorable, 0 neutro, −1 desfavorable). |
| Barras K02 | Puntuación media por subcompetencia, coloreada por materia; excluye los datos no válidos. |
| Barras 100 % apiladas | Distribución de puntuaciones globales por nivel de logro (Bajo, Medio-bajo, Medio-alto, Alto) por materia. Filtros fijos del visual: excluye «No aplica (subcompetencia)», los datos censurados y las convocatorias con nivel no comparable. |
| Línea | Evolución de K01 del contexto frente a Cataluña. No se filtra por el segmentador de año. |

Uso típico: elegir el área, la naturaleza y el hábitat que corresponden al centro, y leer la desviación (K07) y el estado. Sin área seleccionada, *Estado K01* se calcula con K10 (±0,5); con área, con K07 (±1).

---

## 5. Incorporación de una nueva convocatoria (ejemplo: 2026)

Cuando la Generalitat publique un nuevo fichero con 2026, el procedimiento general es: sustituir `Datos.csv` (manteniendo el original como copia), actualizar el modelo y repetir la lista de comprobación del apartado 3.2 con nuevos valores de referencia.

### 5.1. Qué se adapta automáticamente

| Elemento | Por qué |
|---|---|
| `DimAnio` | Se genera desde 2009 hasta `List.Max` de los años presentes en los datos; añade 2026 con su `Curso`, `TieneConvocatoria`, `IndiceConvocatoria` y marca `EsUltimaConvocatoria` en el último año. |
| K10, K11 y K12 | Las comparaciones temporales usan `IndiceConvocatoria` (no `Anio − 1`), por lo que 2026 se compara con 2025 sin cambios. |
| `FactEvaluacion` y `FactPuntuacion` | Se recalculan a partir de `stg_Evaluaciones`; las claves son deterministas (aritméticas). |
| Líneas de evolución | Muestran todas las convocatorias; 2026 aparece al actualizar. |

### 5.2. Qué hay que cambiar a mano

| Elemento | Dónde | Qué hacer |
|---|---|---|
| Año por defecto de los segmentadores | `trabajo_en_curso/generadores/gen_pbir.py`, constante `ANIO_DEFECTO = ["2025L"]` | Cambiar a `["2026L"]` y regenerar el informe (apartado 7). Es un literal fijo en el filtro inicial de los tres segmentadores de año; si no se cambia, el informe seguirá abriéndose en 2025. |
| Reglas de calidad por año | `generadores/modelo/m_FactPuntuacion.m`, lista `ReglasCalidad` (R25–R28) | Añadir 2026 a las columnas afectadas si la nueva prueba presenta escalas anómalas, suelos artificiales o niveles no comparables. |
| Áreas territoriales | `generadores/modelo/m_stg.m`, registro `CodigosArea` y regla de `Barcelona Comarques` (R13, R14); `m_DimContextoCentro.m` | Si aparece un área nueva o cambia un perímetro, la actualización falla con «Área territorial desconocida»: hay que añadir el código y la fila de la dimensión (incluidas `AreaPerimetro2025` y `AreaSerieComparable`). |
| Códigos de categorías | `m_stg.m`, reglas R09 (género), R10 (naturaleza), R11 (hábitat) | Si la Generalitat cambia los literales, la actualización falla con el mensaje de la regla; añadir el nuevo literal al mapeo. |
| Estructura del fichero | `m_stg.m`, `ColumnasCsv` y `CamposPuntuacion`; `m_FactPuntuacion.m`, `ClaveCompetencia`; `m_DimCompetencia.m` | Una columna nueva o renombrada (por ejemplo, una nueva competencia) detiene la carga en la comprobación de cabecera. Requiere ampliar las listas, la dimensión de competencias (`AnioInicio`, `AnioFin`, `PeriodoDisenoInicio`) y las medidas si procede. |
| Rotaciones de columnas | `m_stg.m`, lista `Rotaciones` (R03, R04) | Solo si se detecta de nuevo un desorden de columnas en algún año. |
| Notas de convocatoria | `m_DimAnio.m`, registro `Notas` | Opcional, si 2026 requiere una nota (como 2020 y 2021). |
| Réplica Python y valores de control | `validacion/etl_referencia.py`, `test_modelo.py`, `kpis_referencia.py` | Replicar las mismas reglas, añadir la media oficial de 2026 del Quadern correspondiente y actualizar los recuentos esperados. Los CSV de `resultados/` están fijados en 2025 (`kpi_area_2025.csv`, etc.). |
| Este documento y los valores esperados | Apartado 3.2 | Actualizar los recuentos y los KPIs de control. |

Tras los cambios: regenerar (apartado 7), ejecutar la validación (apartado 6) y actualizar en Power BI Desktop.

---

## 6. Validación

### 6.1. Réplica Python (`validacion/`)

Es una réplica independiente de Power BI de la ETL y de las medidas, que sirve para contrastar cifra a cifra el modelo. Se ejecuta desde la raíz del repositorio, con `Datos.csv` en la raíz (solo se lee):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r validacion/requirements.txt

python validacion/etl_referencia.py      # 1. ETL -> validacion/salida/*.parquet (unos 10 s)
python validacion/test_modelo.py         # 2. tests de integridad (código 1 si alguno falla)
python validacion/kpis_referencia.py     # 3. KPIs de referencia -> validacion/resultados/*.csv
```

En Windows, la activación del entorno es `.venv\Scripts\activate`.

| Script | Resultado |
|---|---|
| `etl_referencia.py` | Las 8 tablas del modelo en estrella en `validacion/salida/` (carpeta no versionada), con las reglas R01–R29. |
| `test_modelo.py` | Comprobaciones del contrato §6: recuentos, claves huérfanas, rotaciones R03/R04 (con control negativo), códigos sin mapear, rango [0, 100], 2020 sin datos, `IndiceConvocatoria`, límites 55/70/85, máscara de `DimCalidadDato` y medias de Cataluña frente a los Quaderns (±0,2). Estado actual: 27/27 tests correctos. |
| `kpis_referencia.py` | Los 6 CSV de `validacion/resultados/` (versionados), usados en el apartado 3.2. |

### 6.2. Herramientas de validación del modelo (`trabajo_en_curso/herramientas`)

Validan los artefactos de Power BI sin necesidad de Power BI Desktop (se usaron en Linux).

| Herramienta | Qué comprueba | Requisitos y uso |
|---|---|---|
| `tmdlcheck` | Deserializa la carpeta `definition` con la librería oficial de Microsoft (TOM), lista el modelo y ejecuta `Model.Validate()`. No valida la semántica DAX. Estado actual: 0 errores. | .NET 8. `cd trabajo_en_curso/herramientas/tmdlcheck && ~/.dotnet/dotnet build -c Release -o out`; después `DOTNET_ROOT=~/.dotnet ./out/tmdlcheck ../../../PowerBI/CMI_Educacion_Primaria.SemanticModel/definition`. |
| `tmdldump` | Volcado de una tabla y reserialización del modelo (prueba de ida y vuelta). | .NET 8, igual que la anterior. |
| `mparser` + `validar_m.py` | Extrae todos los bloques M del TMDL (parámetros, `stg_Evaluaciones` y particiones) y los analiza con el parser oficial `@microsoft/powerquery-parser`. Solo detecta errores de sintaxis. Estado actual: 11/11 correctos. | Node.js. `cd trabajo_en_curso/herramientas/mparser && npm ci`; después `python trabajo_en_curso/herramientas/validar_m.py`. |
| `validar_pbir.py` | Valida los JSON del informe contra los esquemas oficiales, la estructura de carpetas, las posiciones de los visuales, las referencias a columnas y medidas del modelo y las proyecciones de cada visual. Estado actual: 0 errores. | Python con `jsonschema` y un clon disperso de `github.com/microsoft/json-schemas` (ver más abajo). `PBIR_SCHEMAS=~/json-schemas/fabric python trabajo_en_curso/herramientas/validar_pbir.py` o con `--schemas`. |
| `verificar_claves.py` | Reconstruye las dimensiones estáticas a partir del M y las compara con los parquet de la réplica; enumera todas las combinaciones posibles de claves de staging y comprueba que no hay huérfanas. Estado actual: 0 fallos. | Requiere haber ejecutado antes `validacion/etl_referencia.py` y el `npm ci` de `mparser`. `python trabajo_en_curso/herramientas/verificar_claves.py`. |

Instalación de .NET 8 en una carpeta local y obtención de los esquemas:

```bash
curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0 --install-dir ~/.dotnet

git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/json-schemas ~/json-schemas
git -C ~/json-schemas sparse-checkout set fabric/item/report fabric/item/semanticModel fabric/pbip
```

Si no se indica `--schemas` ni `PBIR_SCHEMAS`, `validar_pbir.py` busca los esquemas en una carpeta temporal de `/tmp` que se pierde al reiniciar el equipo; conviene pasarlos siempre explícitamente.

---

## 7. Regeneración de los artefactos

**Regla del proyecto:** la carpeta `PowerBI/` no se edita a mano. Todo cambio se hace en los generadores (o en los ficheros `m_*.m`) y después se regenera. Los generadores usan rutas relativas al repositorio y se ejecutan desde su raíz.

| Orden | Generador | Qué produce | Comando |
|---|---|---|---|
| 1 | `trabajo_en_curso/generadores/modelo/gen_modelo.py` | El modelo TMDL (salvo `_Medidas.tmdl`): `database`, `model`, `relationships`, `expressions` (parámetro `RutaDatos` y `stg_Evaluaciones`) y las 8 tablas, con el M tomado de `generadores/modelo/m_*.m`. También el `.pbip` y el `.gitignore` de `PowerBI/`. | `python trabajo_en_curso/generadores/modelo/gen_modelo.py PowerBI` |
| 2 | `trabajo_en_curso/generadores/gen_medidas.py` | `_Medidas.tmdl` con las 19 medidas, sus carpetas de visualización, formatos y descripciones. | `python trabajo_en_curso/generadores/gen_medidas.py PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl` |
| 3 | `trabajo_en_curso/generadores/gen_pbir.py` | El informe PBIR completo (3 páginas, 36 visuales) y `pbir_referencias.json` (campos del modelo que usa el informe, para `validar_pbir.py`). **Borra y recrea** la carpeta `CMI_Educacion_Primaria.Report`. Copia el tema base desde `trabajo_en_curso/referencias_pbir/`. | `python trabajo_en_curso/generadores/gen_pbir.py` |

`gen_stub.py` es un generador auxiliar de esqueletos de tablas TMDL usado en las primeras fases; no forma parte del flujo normal.

Después de regenerar:

1. si ha cambiado la ETL, ejecutar `validacion/etl_referencia.py` (y adaptar la réplica a la misma regla);
2. ejecutar `test_modelo.py` y `kpis_referencia.py`;
3. ejecutar `tmdlcheck`, `validar_m.py`, `validar_pbir.py` y `verificar_claves.py`;
4. abrir el `.pbip` en Power BI Desktop y actualizar.

Si se ha guardado el proyecto desde Power BI Desktop, conviene revisar con `git diff` qué ha cambiado antes de regenerar, porque la regeneración sobrescribe esos cambios.

---

## 8. Problemas conocidos

| Código | Problema | Situación y mitigación |
|---|---|---|
| INT-03 | **El M nunca se ha ejecutado en Power BI Desktop.** Toda la validación se ha hecho en Linux: sintaxis M con el parser oficial, modelo con TOM, informe con los esquemas oficiales y lógica con la réplica Python. Ninguna de estas herramientas ejecuta el M real. | Pendiente: primera apertura en Windows (apartado 3), lista de comprobación del apartado 3.2 y prueba negativa con una copia del CSV. Pueden aparecer errores de ejecución (tipos, nombres de columna, configuración regional) que el análisis sintáctico no detecta. |
| Rendimiento | La actualización puede ser lenta: `FactEvaluacion`, `FactPuntuacion` y `DimAnio` referencian `stg_Evaluaciones`, y cada consulta que la referencia **vuelve a leer y transformar** los 240 MB del CSV. `FactPuntuacion` además despivota 24 columnas hasta 17,7 millones de filas, y la validación de errores (`Table.SelectRowsWithErrors`) recorre todo el fichero. | Si tarda demasiado, `DimAnio` puede leer solo la columna `ANY` del CSV en lugar de `stg_Evaluaciones` (cambio en `m_DimAnio.m` y regeneración). **No** usar `Table.Buffer` sobre `stg_Evaluaciones`: cargaría el fichero entero en memoria en cada consulta. |
| Año por defecto | Los segmentadores de año arrancan en 2025 por un literal fijo. | Ver apartado 5.2 (`ANIO_DEFECTO`). |
| Parámetro y regeneración | El valor de `RutaDatos` cambiado en Power BI Desktop se pierde al regenerar el modelo. | Volver a fijarlo tras regenerar, o copiar el CSV a la ruta por defecto. |
| Decisiones abiertas | La versión actual aplica las opciones por defecto de las cuestiones pendientes con las directoras (informe de calidad, §7.2): umbrales 55/70/85; inglés 2015 y catalán 2018 marcados sin excluir; hábitat y edad de 2010 como «No fiable»; series territoriales agrupadas; francés solo informativo (n ≥ 30); KPIs temporales con la nota de no equiparación. | Si las directoras deciden otra cosa, cambiar los generadores y la réplica Python y regenerar. |
| Contraste oficial | Inglés 2016 se desvía 0,24 puntos de la media oficial (73,94 frente a 73,7), por encima de la tolerancia de ±0,2; está pendiente de documentar en el §4.6 del informe de calidad. | Convocatoria con nota (escalas comprimidas y % por nivel no comparable, R27/R28). |
