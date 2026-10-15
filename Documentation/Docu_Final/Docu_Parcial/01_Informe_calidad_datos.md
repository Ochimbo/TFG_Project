# Informe de calidad de datos del dataset «Avaluació de sisè d'educació primària»

**Proyecto:** Diseño e implementación de un Cuadro de Mando Integral (CMI) en Power BI para el soporte a la toma de decisiones en la educación primaria de Cataluña (TFG, FIB-UPC).
**Autora:** Kiara Rodríguez Uribe.
**Tarea de la planificación:** T7 — Perfilado y auditoría del dataset.
**Fecha:** 14 de octubre de 2026.
**Estado:** versión para revisar con las directoras. Las cuestiones abiertas están en la sección 7.2.

---

## Resumen

El fichero publicado por la Generalitat está bien formado: 1.102.324 registros, 32 columnas en todas las líneas, sin caracteres extraños y con todas las puntuaciones en un formato numérico homogéneo. Los problemas no están en la estructura, sino en el contenido, y se agrupan en cuatro familias:

1. **Codificaciones inconsistentes entre años**, fáciles de normalizar: `GENERE` (H/D y, solo en 2021, Home/Dona), `NATURALESA` (Públic/Privat hasta 2023 y Pública/Privada desde 2024) y la etiqueta de la categoría grande de `HÀBITAT` (Més de 100000 / Més de 100001).
2. **Errores de datos localizados**, que se pueden corregir o neutralizar: columnas de castellano rotadas en 2017 y de francés rotadas en 2016, 13.357 valores de `HÀBITAT` de 2024 autoincrementados («Fins a 10001»… «Fins a 23357»), y dos columnas de 2010 (`HÀBITAT` y `ANY_NAIXEMENT`) desalineadas respecto al resto del registro.
3. **Rupturas de comparabilidad temporal**, que no son errores, pero condicionan los KPIs de evolución: no hay convocatoria en 2020, el mapa de servicios territoriales cambia en 2024, la composición de las pruebas y los pesos de las subcompetencias cambian varias veces, y las puntuaciones no están equiparadas entre años.
4. **Incompletitud estructural**: `CODI_ALUMNE` no existe antes de 2016 (40,72 % de las filas) y la fecha de nacimiento falta o es de relleno en algunos años.

Las reglas de limpieza (sección 5) no eliminan ningún registro. Corrigen lo que es demostrablemente un error (rotaciones y codificaciones) y, en todo lo demás, conservan el valor publicado y añaden un indicador de calidad que las medidas DAX usan para filtrar o anotar.

---

## 1. Objetivo y alcance de la auditoría

El objetivo de la tarea T7 es conocer con detalle el dataset antes de diseñar el modelo dimensional (T10) y la ETL (T12–T13), para:

- detectar los valores nulos, inválidos, inconsistentes o duplicados y medir su alcance;
- decidir, con evidencia, qué se corrige, qué se marca y qué se deja como está;
- identificar las rupturas que afectan a los 12 KPIs del CMI, en especial a los temporales;
- fijar las cifras de control que la ETL debe reproducir (número de filas, recuentos por año, etc.).

**Alcance.** Se han auditado las 32 columnas y los 1.102.324 registros de las 16 convocatorias disponibles (2009–2019 y 2021–2025). Se han contrastado las cifras agregadas con los informes oficiales publicados (Quaderns d'avaluació). Quedan fuera del alcance la calidad psicométrica de las pruebas y la verificación de los datos en origen, a los que no hay acceso.

---

## 2. Descripción del dataset y de la fuente

### 2.1. Fuente y metadatos oficiales

| Atributo | Valor |
|---|---|
| Título | *Avaluació de sisè d'educació primària* |
| Identificador | `rk5x-gny6` (plataforma Socrata) |
| Portal | Portal de Dades Obertes de la Generalitat de Catalunya |
| Página del dataset | https://analisi.transparenciacatalunya.cat/Educaci-/Avaluaci-de-sis-d-educaci-prim-ria/rk5x-gny6/about_data |
| Metadatos (API) | https://analisi.transparenciacatalunya.cat/api/views/rk5x-gny6.json |
| Titular | Departament d'Educació i Formació Professional |
| Licencia | «See Terms of Use», con enlace a las licencias de datos abiertos de la Generalitat: https://administraciodigital.gencat.cat/ca/dades/dades-obertes/informacio-practica/llicencies/ |
| Categoría y frecuencia | Educació; actualización anual |
| Creación / publicación | 4 y 6 de abril de 2022 |
| Última actualización de filas | 10 de febrero de 2026 |
| Fichero local | `Datos.csv`: 240.120.178 bytes, SHA-256 `20632aac414363b6dbe951cd384d11e541e9338a15a04327aa6fddf610d83c63` |

La descripción oficial dice que el dataset contiene los resultados del alumnado de 6.º de primaria en la evaluación de las competencias básicas desde 2009, y que el código de alumno anonimizado, pensado para enlazar con la evaluación de 4.º de ESO, «només està disponible a partir de l'any 2016».

### 2.2. Estructura

El CSV está en UTF-8, sin BOM, con separador coma y todos los valores no vacíos entre comillas dobles. Los decimales usan coma (`"87,70"`) y un valor vacío es un campo sin comillas (no aparece ni una vez la cadena `""`). Los registros están ordenados por año descendente, en bloques contiguos: 2025 ocupa las líneas 2–68.912 y 2009 las líneas 1.043.263–1.102.325.

| Grupo | Columnas | Descripción oficial (resumida) |
|---|---|---|
| Convocatoria | `ANY` | Año en que tuvo lugar la evaluación. Coincide con el año en que termina el curso: 2025 = curso 2024-2025. |
| Alumno | `CODI_ALUMNE` | Código anonimizado del alumno; solo desde 2016. |
| Puntuaciones globales (6) | `PCAT`, `PCAST`, `PMAT`, `PANG`, `PFRAN`, `PMED` | Puntuación global ponderada de cada competencia, de 0 a 100. |
| Subcompetencias (18) | `PCAT_CL`, `PCAT_EE`, `PCAT_CO`, `PCAST_CL`, `PCAST_EE`, `PCAST_CO`, `PMAT_NC`, `PMAT_EFM`, `PMAT_CR`, `PANG_CO`, `PANG_CE`, `PANG_EE`, `PFRAN_CO`, `PFRAN_CE`, `PFRAN_EE`, `PMED_COMP1`, `PMED_COMP2`, `PMED_COMP3` | Puntuación de cada dimensión de la competencia, de 0 a 100. |
| Perfil del alumno | `GENERE`, `MES_NAIXEMENT`, `ANY_NAIXEMENT` | Género, mes y año de nacimiento. |
| Contexto del centro | `AREA_TERRITORIAL`, `NATURALESA`, `HÀBITAT` | Servicio territorial o Consorci d'Educació de Barcelona; titularidad (pública/privada, donde «privada» incluye la concertada); tramo de población del municipio. |

Las columnas `PCAT_CO` y `PCAST_CO` ocupan las posiciones 21–22, detrás de las de francés, porque se añadieron en 2018. Los nombres legibles de las 24 columnas de puntuación están en la sección 6.6.

### 2.3. Documentación oficial complementaria

Los resultados agregados de cada convocatoria se publican en los *Quaderns d'avaluació* del Consell Superior d'Avaluació del Sistema Educatiu (CSASE) y, en 2025, de la Agència d'Avaluació i Prospectiva de l'Educació. Se han usado como referencia externa:

| Año | Informe | Año | Informe |
|---|---|---|---|
| 2009 | https://hdl.handle.net/20.500.12694/390 | 2018 | https://hdl.handle.net/20.500.12694/441 |
| 2010 | https://hdl.handle.net/20.500.12694/397 | 2019 | https://hdl.handle.net/20.500.12694/444 (Q44) |
| 2011 | https://hdl.handle.net/20.500.12694/399 | 2021 | https://hdl.handle.net/20.500.12694/2098 (Q50) |
| 2012 | https://hdl.handle.net/20.500.12694/402 (Q23) | 2022 | https://hdl.handle.net/20.500.12694/3555 (Q54) |
| 2013 | https://hdl.handle.net/20.500.12694/406 (Q26) | 2023 | https://hdl.handle.net/20.500.12694/4245 (Q59) |
| 2014 | https://hdl.handle.net/20.500.12694/414 | 2024 | https://hdl.handle.net/20.500.12694/7364 (Q62) |
| 2015 | https://hdl.handle.net/20.500.12694/420 | 2025 | https://hdl.handle.net/20.500.12694/7383 (Q68) |
| 2016 | https://hdl.handle.net/20.500.12694/435 | 2017 | https://hdl.handle.net/20.500.12694/438 |

Tres afirmaciones de estos informes condicionan el análisis:

- **No hubo prueba en 2020.** «A causa del confinament i de la interrupció de l'activitat lectiva presencial […] no es va poder dur a terme l'avaluació de sisè de primària programada per al mes de maig del 2020» (Quadern 50, presentación).
- **Las puntuaciones no están equiparadas entre años.** «El model vigent de disseny de les proves no disposa d'ítems d'ancoratge […]. Qualsevol comparació longitudinal que es realitzi s'ha d'interpretar com orientativa» (Quadern 68, p. 8).
- **Los niveles de logro oficiales no tienen cortes fijos.** «El llindar del nivell alt, entre els 80 i els 90 punts, i el llindar del nivell mínim, entre els 50 i els 60 punts. El llindar òptim d'assoliment de la competència es fixa en els 70 punts. Per obtenir els punts de tall […] es prenen, com a referència, la puntuació mitjana i les estadístiques de dispersió» (Quadern 68, p. 9).

---

## 3. Metodología

### 3.1. Herramientas

La auditoría se ha hecho con Python 3.14.4 y DuckDB 1.5.6, con pandas 3.0.6, pyarrow 26.0.0 y NumPy 2.5.4 (entorno virtual del proyecto). DuckDB lee el CSV completo como texto (`read_csv(..., all_varchar=true)`), de modo que ninguna conversión de tipos oculta un valor anómalo. Las puntuaciones se convierten a centésimas enteras (`"87,70"` → 8770) para comparar sin errores de coma flotante. `Datos.csv` y `Datos.zip` se han usado solo en modo lectura.

### 3.2. Proceso en tres pasos

1. **Perfilado.** Dos scripts recorren las columnas categóricas y de puntuación y documentan cada hallazgo con su consulta, su impacto y una regla propuesta.
2. **Verificación independiente.** Otros dos scripts, escritos desde cero y con otra vía de carga (pyarrow y lectura línea a línea con el número de línea real), reproducen cada cifra, revisan cada regla y buscan lo que se escapó. Este paso confirmó 38 de los 41 hallazgos; corrigió 3 recuentos (PUN-13, PUN-21 y PUN-23) y añadió hallazgos nuevos, como los suelos artificiales de inglés 2015 y la verdadera magnitud del problema de 2010.
3. **Síntesis y complemento.** Este informe usa solo cifras confirmadas por la verificación, o la cifra corregida cuando no se confirmó. Las cifras que faltaban (pesos reales de ciencias, comparación de umbrales con los niveles oficiales, recuento final de indicadores y cardinalidad de las dimensiones) se han calculado con un script adicional.

### 3.3. Dimensiones de calidad evaluadas

Se usan las dimensiones habituales de los modelos de calidad de datos (por ejemplo, ISO/IEC 25012), más una específica de series temporales:

- **Completitud:** presencia de valor donde debería haberlo.
- **Validez:** el valor pertenece al dominio y al rango esperados.
- **Consistencia:** el mismo hecho se codifica igual en todo el fichero, y los valores relacionados entre sí (global y subcompetencias, área y hábitat) son coherentes.
- **Unicidad:** ausencia de registros duplicados.
- **Comparabilidad temporal:** los valores de distintas convocatorias miden lo mismo.

### 3.4. Trazabilidad

| Fichero (en `validacion/perfilado/`) | Contenido |
|---|---|
| `perfil_categoricas.py` | Perfilado de las 8 columnas no numéricas, con la función pandas `limpiar_categoricas()` verificada sobre el fichero completo. Salida en `salidas_categoricas/` (texto completo y CSV de cada tabla). |
| `limpieza_categoricas.pq` | Traducción a Power Query (M) de `limpiar_categoricas()`. No se ha podido ejecutar en este entorno porque no hay Power BI. |
| `perfil_puntuaciones.py` | Perfilado de las 24 columnas de puntuación. Salida en `salidas_puntuaciones/` (registro `perfil_puntuaciones.log` y CSV). |
| `verificacion_categoricas.py` | Verificación independiente de los hallazgos de las columnas categóricas (101 consultas). Registro en `salidas_verificacion/verificacion_categoricas.log`. |
| `verificacion_puntuaciones.py` | Verificación independiente de los hallazgos PUN-01…PUN-23 (una función por hallazgo). |
| `complemento_informe_calidad.py` | Cifras nuevas de este informe (secciones A–H). Registro en `salidas_complemento/complemento_informe_calidad.log`. |

Los identificadores de hallazgo (ANY-01, COD-01…, PUN-01…) se usan en todo el informe y en la columna «Hallazgos» de las reglas de limpieza. Las cifras siguen la notación española: punto de miles y coma decimal.

---

## 4. Resultados por dimensión de calidad

### 4.0. Contraste con los hechos conocidos antes de la auditoría

| Hecho previo | Resultado | Evidencia |
|---|---|---|
| No existe 2020 (COVID-19) | Confirmado. Hay 16 convocatorias: 2009–2019 y 2021–2025. | ANY-01; Quaderns 50, 62 y 68 |
| `CODI_ALUMNE` vacío en 2009–2015 | Confirmado (448.758 filas), y además 47 vacíos en 2016 y 11 en 2018. | COD-01 |
| 914 códigos en 2 años | Confirmado. Siempre en dos convocatorias consecutivas. | COD-03 |
| Duplicados dentro de un año en 2016–2018 | **Corregido.** Solo hay un código repetido en un mismo año (2017). Los «duplicados» de 2016 y 2018 eran el código vacío. | COD-02, PUN-20 |
| `GENERE` H/D salvo 2021 (Home/Dona) | Confirmado. | GEN-01 |
| `NATURALESA` Públic/Privat hasta 2023 y Pública/Privada en 2024–2025 | Confirmado. | NAT-01 |
| `HÀBITAT` «Més de 100000» → «Més de 100001» en 2024–2025 | Confirmado. | HAB-02 |
| 13.357 filas de 2024 con «Fins a 100xx» autoincrementado | Confirmado: de «Fins a 10001» a «Fins a 23357», sin huecos ni repeticiones. | HAB-01 |
| 1 fila de 2024 sin `AREA_TERRITORIAL` | Confirmado (línea 82.995). | ARE-01 |
| Áreas nuevas desde 2024–2025 | Confirmado. Además, Barcelona Comarques de 2024 es el mismo perímetro que Barcelonès de 2025. | ARE-02 |

### 4.1. Completitud

**Código de alumno.** `CODI_ALUMNE` está vacío en el 100 % de las filas de 2009–2015, en 47 filas de 2016 y en 11 de 2018: en total, 448.816 filas (40,72 %). Por tanto, no puede ser la clave del registro, y no se puede seguir a ningún alumno antes de 2016. Los códigos presentes son solo dígitos, de 6 a 11 caracteres y sin ceros a la izquierda; hay 652.593 códigos distintos. En 2025 cambia la forma del código: el 98,86 % tiene 11 dígitos, frente al 19,40 % de 2024 (COD-04).

**Fecha de nacimiento.** `ANY_NAIXEMENT` falta en 1.835 filas y `MES_NAIXEMENT` en 1.335, todas de 2009–2014 (FEC-01). En 500 filas falta el año pero hay mes. Desde 2015 no hay vacíos.

**Área territorial.** Solo una fila no tiene área: la línea 82.995, de 2024. Su código no aparece en ningún otro año, así que el área no se puede imputar (ARE-01).

**Puntuaciones.** No hay ningún registro sin puntuaciones: ninguna fila tiene vacías las 24 columnas ni todas las globales. La cobertura de cada global vigente va del 95,99 % (catalán 2025) al 100 %. Un nulo significa que el alumno no hizo esa prueba (PUN-15). La coherencia de nulos entre la global y sus subcompetencias es casi perfecta: solo hay 11 filas de matemáticas 2014 con la global y sin `PMAT_EFM`, y 22 de inglés 2013 con CE y EE pero sin global ni CO (PUN-14).

**Cobertura atípica en 2017 y 2024.** El castellano de 2024 y las matemáticas de 2017 no tienen ningún nulo, y en esos años también es máxima la cobertura de otras materias (catalán 2017, 99,49 %; matemáticas 2024, 99,23 %). Esto apunta a un filtro de población en origen, y no a una imputación. La participación de esos dos años no es comparable con la de los demás (PUN-16).

**Cobertura por columna.** Las columnas aparecen de forma escalonada. Por eso, la mayoría de los vacíos estructurales no son datos perdidos, sino competencias que no se evaluaban ese año:

| Columnas | Convocatorias con datos |
|---|---|
| `PCAT`, `PCAST`, `PMAT` y sus CL, EE, NC, EFM, CR | 2009–2025 |
| `PANG`, `PANG_CO`, `PANG_CE`, `PFRAN`, `PFRAN_CO`, `PFRAN_CE` | 2010–2025 |
| `PANG_EE`, `PFRAN_EE` | 2013–2025 |
| `PCAT_CO`, `PCAST_CO`, `PMED`, `PMED_COMP1`…`COMP3` | 2018–2025 |

El francés es una prueba alternativa al inglés: solo la hace entre el 0,35 % y el 0,81 % del alumnado (243–505 alumnos al año; 5.130 en total).

### 4.2. Validez

**Formato numérico.** Los 17.728.085 valores de puntuación no nulos cumplen el patrón `ddd,dd` (coma decimal y siempre dos decimales). No hay ninguno con punto, ninguno que no se pueda convertir a número, ninguno negativo ni ninguno mayor que 100 (PUN-01).

**`HÀBITAT` en 2024.** La columna tiene 13.361 valores distintos en bruto, cuando debería tener 3. En 2024 hay una fila «Fins a 10000» y 13.357 filas con «Fins a N», donde N va de 10.001 a 23.357; cada N aparece una sola vez y la secuencia no tiene huecos. Es el patrón típico de arrastrar una celda en una hoja de cálculo (HAB-01). Solo se alteró el texto, no la categoría: el peso de la categoría pequeña en 2024 (18,98 %) está entre el de 2023 (19,42 %) y el de 2025 (18,76 %), y el % por área es casi igual al de 2025. Además, los repetidores que siguen en la misma área y naturaleza conservan la categoría (36 de 36 entre 2024 y 2025). Mapear por prefijo recupera, por tanto, la categoría correcta.

**Edad imposible.** La edad calculada `ANY − ANY_NAIXEMENT` toma 95 valores fuera del rango plausible en 6.º de primaria (10–14 años): 9 por debajo y 86 por encima, con casos de 2 y de 48 años (FEC-02). De ellos, 41 son de 2016 y todos tienen el nacimiento en enero de 2001: es un valor de relleno.

**Fechas de relleno.** Las 58 filas sin código de 2016 y 2018 tienen siempre el mes 1 (enero), con años como 2001, 2004 o 2011. Su fecha de nacimiento es, por tanto, un relleno, aunque la edad resultante caiga entre 10 y 14 años. En total, las fechas dudosas son 83 filas: las 58 sin código más las 25 con código y el relleno 1/2001. Además, en 2009 y 2012–2015 hay más nacidos en enero de lo esperado: entre un 8,2 % y un 18,1 % más que la media de los otros seis meses de 31 días, unas 3.331 filas de exceso. No se pueden identificar una a una (FEC-04).

**Suelos artificiales y escalas anómalas.** En varias convocatorias, la parte baja de la escala está censurada o comprimida:

| Caso | Evidencia | Hallazgo |
|---|---|---|
| `PCAT_EE` 2018 | 10.093 de 72.464 valores (13,93 %) son exactamente 49,40, que es el mínimo. No hay ceros, y en 2019 hay 13.721 valores ≤ 50. La global de 2018 se calculó con ese suelo: tiene la desviación típica más baja de la serie (13,01). | PUN-08 |
| `PANG` 2015 | 8.801 globales (12,9 %) valen exactamente 48,79, y son el 87 % de las 10.106 que están por debajo de 50. `PANG_CO` tiene un suelo en 53,19 (8.655 filas) y `PANG_CE` en 45,00 (7.554), sin ningún valor positivo por debajo. | Verificación PUN-06 y PUN-18 |
| `PANG_EE` 2015 | Toma 9 valores no estándar (20,00; 53,00; 56,67…). Con EE = 53 la global no cuadra en ningún caso; en total, la global de inglés 2015 solo cuadra en el 65,72 % de las filas. | PUN-06 |
| `PMAT` 2015 | Las subcompetencias usan otra escala: 515, 259 y 167 valores distintos (15–40 en otros años) y ningún valor positivo por debajo de unos 38–40 puntos. | Verificación PUN-09 |
| `PMAT` 2016 | 251 globales valen exactamente 59,20, frente a 6–19 en los valores vecinos. Las 248 que no cuadran con sus subcompetencias tienen una media ponderada entre 49,38 y 59,20: la global se elevó artificialmente hasta 59,20. | Verificación PUN-23 |
| `PANG_CO` 2011 y `PCAT_CL` 2011 | Techo en 99,73: el 53,66 % de `PANG_CO` (32.737 de 61.013) vale exactamente 99,73, y la media de `PANG_CO` sube a 91,70, frente a 69,58 en 2010 y 78,98 en 2012. | PUN-10 |

### 4.3. Consistencia

**Codificaciones que cambian según el año.** Sin normalizar, cada una de estas columnas tendría el doble de miembros y los KPIs de brecha quedarían vacíos en los años afectados:

| Columna | Valores en bruto | Años | Filas con la codificación minoritaria |
|---|---|---|---|
| `GENERE` | H, D / Home, Dona | Home/Dona solo en 2021 | 73.674 (37.502 Home y 36.172 Dona) |
| `NATURALESA` | Públic, Privat / Pública, Privada | Pública/Privada en 2024–2025 | 139.291 |
| `HÀBITAT` (categoría grande) | Més de 100000 / Més de 100001 | Més de 100001 en 2024–2025 | 53.512 |

En las 8 columnas de texto no hay espacios al inicio o al final, ni espacios dobles, ni caracteres de control (OTR-01).

**Columnas rotadas.** En dos convocatorias, las columnas de una materia están cambiadas de sitio:

- **Castellano 2017 (PUN-02).** La regresión de `PCAST` sobre sus subcompetencias da pesos imposibles (−0,67 y 1,67). En cambio, `PCAST_EE` = 0,6·`PCAST` + 0,4·`PCAST_CL` en el 99,07 % de las 71.036 filas, que son justo los pesos de 2016. La rotación correcta es: global real = `PCAST_EE`, CL real = `PCAST`, EE real = `PCAST_CL`. La correlación con las subcompetencias de catalán del mismo año lo confirma de forma independiente. Tras corregir, la media global de castellano 2017 pasa de 74,30 a 73,51 (oficial 73,4) y la desviación típica de 19,63 a 16,55.
- **Francés 2016 (PUN-03).** `PFRAN_EE` = 0,35·`PFRAN` + 0,50·`PFRAN_CO` + 0,15·`PFRAN_CE` en las 389 filas (100 %). La rotación correcta es: global = `PFRAN_EE`, CO = `PFRAN`, CE = `PFRAN_CO`, EE = `PFRAN_CE`.

**La global es una media ponderada de sus subcompetencias, con pesos que cambian (PUN-04).** Los pesos se han estimado por mínimos cuadrados sin intercepto sobre los datos corregidos, y coinciden con los oficiales cuando están publicados (Quadern 44, Taula 1; Quadern 68, Taula 3):

| Materia | Subcompetencias | 2009–2010 | 2011–2012 | 2013–2015 | 2016–2017 | 2018–2025 |
|---|---|---|---|---|---|---|
| Catalán | CL / EE (/ CO) | ≈0,53/0,47 y ≈0,58/0,42 (estimados) | 0,50/0,50 (2011); 0,60/0,40 (2012) | 0,50/0,50 | 0,60/0,40 | 0,50/0,35/0,15 |
| Castellano | CL / EE (/ CO) | ≈0,52/0,48 y ≈0,54/0,46 (estimados) | 0,50/0,50 (2011); 0,60/0,40 (2012) | 0,50/0,50 | 0,60/0,40 | 0,50/0,35/0,15 |
| Matemáticas | NC / EFM / CR | ≈0,40/0,31/0,29 y ≈0,35/0,37/0,28 | ≈0,36/0,35/0,29 y ≈0,35/0,33/0,32 | 0,35/0,35/0,30; 2015: 0,40/0,36/0,24 | 2016: 0,35/0,35/0,30; 2017: 0,30/0,35/0,35 | 0,30/0,35/0,35 |
| Inglés y francés | CO / CE (/ EE) | 2010: ≈0,39/0,61 (inglés) y ≈0,40/0,58 (francés) | 0,50/0,50 | 1/3 cada una | 0,35/0,50/0,15 | 0,35/0,50/0,15 |
| Ciencias | COMP1 / COMP2 / COMP3 | – | – | – | – | 1/3 cada una |

En ciencias, el Quadern 68 publica unos pesos de 42 % / 25 % / 33 %, pero los datos no los siguen. La media simple de las tres subcompetencias reproduce la global en el 100 % de las filas de las 7 convocatorias, mientras que los pesos 42/25/33 solo la reproducen en el 4,7 %–8,7 %, con un error medio de 1,32 a 1,62 puntos (complemento, sección A). Recalcular la global como media simple en otras materias daría errores de hasta 19 puntos. Por tanto, **la global nunca se recalcula**: se carga el valor publicado.

**Globales que no cuadran con sus subcompetencias.** Con una tolerancia única de 0,115 puntos (cubre el redondeo a un decimal de algunas convocatorias y el desfase de +0,07 de inglés 2011) y los pesos de la tabla anterior, hay 49.740 globales incoherentes de 4.359.515 evaluables en 2011–2025 (1,14 %). En 2009–2010 no se aplica la comprobación, porque allí los pesos son estimados y en catalán y castellano 2009 una misma combinación (CL, EE) puede tener varias globales distintas, lo que indica que hubo varias versiones de la prueba.

| Materia y año | Globales | Fuera de tolerancia | Explicación |
|---|---|---|---|
| Inglés 2015 | 68.342 | 23.427 | `PANG_EE` 2015 anómala (PUN-06) |
| Inglés 2022 | 72.913 | 13.228 | Exactamente un ítem de diferencia en CE. Sesgo neto: la global queda de media 0,206 puntos por debajo (PUN-05). |
| Castellano 2022 | 73.024 | 12.000 | Exactamente un ítem de diferencia en EE; residuo simétrico (PUN-05). |
| Castellano 2017 | 71.036 | 658 | Una sola combinación (CL 72,73; EE 68,18) con global 72,10, en lugar de 70,91 (PUN-02). |
| Matemáticas 2016 | 70.426 | 248 | Global elevada hasta 59,20 (PUN-23). |
| Francés 2022 | 319 | 145 | Las globales parecen desalineadas entre alumnos: 143 de las 145 coinciden con la ponderada de otra fila errónea. La media anual apenas cambia: 82,32 frente a 82,21 (PUN-07). |
| Francés 2011 | 505 | 30 | Residuo (PUN-23). |
| Catalán 2011 y 2022, castellano 2016, matemáticas 2011 | – | 1 en cada caso | Casos sueltos. |

**Desalineamiento de `HÀBITAT` y `ANY_NAIXEMENT` en 2010.** Es el problema más grave del dataset, porque no se ve en los totales del año:

- En 2010 aparecen combinaciones de área y hábitat que no existen en ningún otro año. Por ejemplo, el Consorci d'Educació de Barcelona (la ciudad de Barcelona) tiene 744 alumnos en municipios de hasta 10.000 habitantes, y Terres de l'Ebre tiene 505 en municipios de más de 100.000. Esas combinaciones imposibles suman 7.252 filas (12,22 % del año). Comparando la distribución área × hábitat de 2010 con la esperada a partir de 2009 y 2011, se obtiene una cota inferior de al menos 15.186 filas mal asignadas (25,6 %). El cruce naturaleza × hábitat también está roto: el 35,2 % de los alumnos de centros privados están en municipios pequeños, frente al 9,9 %–13,2 % del resto de años.
- Siguiendo el orden del fichero, `HÀBITAT` cambia de valor 198 veces en 2010, frente a 448 en 2009 y 490 en 2011, mientras que el área cambia un número de veces parecido (531, 534 y 546). Es un desplazamiento por bloques: el valor no corresponde al alumno de esa fila.
- `ANY_NAIXEMENT` de 2010 muestra el mismo mecanismo. La diferencia de puntuación en matemáticas entre los alumnos de 12 y de 13 años es de −0,05 puntos en 2010, frente a 10,37–16,86 en los otros 15 años, y se mantiene casi en 0 en todos los tramos del fichero (FEC-03).
- En cambio, área, naturaleza, género y mes de nacimiento de 2010 son coherentes. El % de privada por área se mantiene, la correlación de la media de matemáticas por área entre 2009 y 2010 es 0,945, y el mes de nacimiento conserva el efecto de la edad relativa.

En 2014 hay además un bloque contiguo de 29 filas (líneas 786.241–786.269, todas de centro privado y sin código) en Baix Llobregat con hábitat «Més de 100000», una combinación que no aparece en ningún otro año salvo en 2010 (HAB-03).

**Repetidores.** Los 914 códigos que aparecen en dos convocatorias siempre lo hacen en años consecutivos, con una fila en cada uno (COD-03). Casi todos tienen un año más de edad en la segunda aparición: de 12 a 13 años en 906 casos y de 13 a 14 en 7; solo uno pasa de 15 a 13. Encaja con alumnado que repite 6.º. Si el mes de enero de 2016 y el relleno 1/2001 se tratan como desconocidos al comparar, 910 pares coinciden en género y fecha de nacimiento, y solo quedan 4 posibles colisiones de código: 3 cambios de género y 1 cambio de mes (complemento, sección H).

### 4.4. Unicidad

- Solo un código se repite dentro del mismo año: el 2483875190 en 2017, en las líneas 525.396 y 525.397. Las dos filas difieren en 17 columnas (14 puntuaciones, área, naturaleza y hábitat). No se deduplican, porque no hay criterio para elegir una (COD-02).
- Hay 11 grupos de filas idénticas en las 32 columnas (2009: 3; 2011: 2; 2012: 2; 2014: 4), con 11 filas sobrantes, todas sin código. Por su perfil (puntuaciones en el máximo, todo a 0,00 o una sola prueba informada) pueden ser coincidencias reales. No se deduplican (OTR-01, PUN-20).
- El número de línea del CSV identifica cada registro de forma única y se usa como clave sustituta `EvaluacionID`.

### 4.5. Comparabilidad temporal

**Hueco de 2020.** La variación interanual de 2021 se compara con 2019. Un eje continuo de años mostraría un hueco o un falso cero en 2020 (ANY-01).

**Reorganización territorial de 2024.** El Decret 120/2023 consolida dos servicios territoriales nuevos, operativos desde el 1 de octubre de 2023, y renombra Barcelona Comarques como Barcelonès. Los datos reflejan el cambio a partir de la convocatoria de 2024 (ARE-02):

| Área | 2023 | 2024 | 2025 | Origen según la documentación oficial |
|---|---|---|---|---|
| Alt Pirineu i Aran | – | 514 | 556 | Alt Urgell, Alta Ribagorça, Pallars Jussà, Pallars Sobirà y Aran (antes en Lleida) y la Cerdanya (antes repartida entre Girona y Lleida) |
| Penedès | – | 4.739 | 4.641 | Alt Penedès y Garraf (Barcelona Comarques), Baix Penedès (Tarragona) y Anoia (Catalunya Central, salvo 4 centros) |
| Barcelona Comarques | 8.211 | 5.386 | – | Pasa a llamarse Barcelonès; sin Alt Penedès ni Garraf |
| Barcelonès | – | – | 5.408 | Mismo perímetro que Barcelona Comarques de 2024 |
| Tarragona | 6.485 | 5.164 | 5.100 | Pierde el Baix Penedès |
| Catalunya Central | 5.565 | 4.106 | 3.999 | Pierde la Anoia |
| Lleida | 4.066 | 3.466 | 3.381 | Pierde el Pirineo |

Fuentes: resumen del Decret 120/2023 (https://laadministracionaldia.inap.es/noticia.asp?id=1234838), Acords de Govern de 27/06/2023 (https://govern.cat/govern/docs/2023/06/27/15/19/4262d160-a91a-4708-a7ea-87c8868f25c0.pdf) y Directori de centres docents (https://analisi.transparenciacatalunya.cat/resource/kvmv-ahh4.json).

Los volúmenes del CSV son coherentes con esta reorganización. Las 6 áreas que no cambian de nombre caen un 4,28 % de 2023 a 2024 (factor 0,9572). Con ese mismo factor, a Barcelona Comarques, Tarragona y Catalunya Central les faltan 2.474 + 1.044 + 1.221 = 4.739 alumnos, exactamente los 4.739 de Penedès. A Lleida le faltan 426, frente a los 514 de Alt Pirineu i Aran; la diferencia es compatible con la aportación de la Cerdanya gironina, aunque el dataset no permite comprobarlo. Barcelonès 2025 y Barcelona Comarques 2024 tienen el mismo tamaño (5.408 y 5.386) y la misma composición por naturaleza y hábitat, y los 7 códigos de Barcelona Comarques 2024 que reaparecen en 2025 están todos en Barcelonès. El Quadern 62 ya publica el área de 2024 como «Barcelonès», con la misma n.

La agrupación «Barcelona Comarques/Barcelonès + Penedès + Tarragona + Catalunya Central» tiene una serie continua: 20.261, 19.395 y 19.148 alumnos en 2023–2025, con factores (0,9573 y 0,9873) iguales a los de las áreas estables. Es un grupo grande, alrededor del 27 % de Cataluña.

**Reclasificación del hábitat en 2024.** Desde 2024, Girona pasa del 35,7 % al 49,0 % de alumnado en municipios pequeños y Maresme - Vallès Oriental del 25,4 % al 17,2 %, sin cambio de volumen y manteniéndose en 2025 (HAB-04). Tarragona, Lleida y Barcelona Comarques también cambian de reparto, pero eso se explica por la reorganización territorial. En el total de Cataluña el reparto es estable (19,42 %, 18,98 % y 18,76 % en municipios pequeños en 2023–2025). Los datos no permiten saber la causa de la reclasificación de Girona y Maresme.

**Cambios en el diseño de las pruebas (PUN-11, PUN-21).** Hay subcompetencias nuevas (EE de lenguas extranjeras en 2013; comprensión oral de catalán y castellano y ciencias en 2018), los pesos cambian (tabla de la sección 4.3) y cambian también los techos y la granularidad. Por ejemplo, el catalán tiene 5.859 valores distintos en 2011 y 105 en 2017; `PANG_EE` usa 9 valores en 2013, una escala no estándar en 2015 y 2016, y 7 valores desde 2017; y en 2016 `PANG_CO` y `PANG_CE` están comprimidas. Los periodos de diseño estable son:

| Materia | Periodo de diseño estable |
|---|---|
| Catalán y castellano (global y subcompetencias) | 2018–2025 |
| Matemáticas | 2017–2025 |
| Inglés y francés: global | 2016–2025 (2016 con nota) |
| Inglés y francés: subcompetencias | 2017–2025 |
| Ciencias | 2018–2025 |

**Puntuaciones no equiparadas (PUN-12).** Hay 35 pares columna-año con saltos de la media de 8 puntos o más (18 de ellos en francés). Por ejemplo, ciencias baja 8,16 puntos de 2024 a 2025, y matemáticas pasa de 76,02 en 2021 a 71,12 en 2022. El % de alumnado con menos de 50 puntos en matemáticas varía entre el 0,7 % y el 17,2 % según el año. Como el propio Departament advierte, estas variaciones mezclan la dificultad de cada prueba con el rendimiento real.

**Matemáticas 2015 y 2019 (PUN-09).** Las dos convocatorias tienen un 0,7 % de alumnado por debajo de 50, pero por motivos distintos. En 2015 las subcompetencias usan otra escala (sección 4.2). En 2019 la distribución está comprimida por los dos extremos: la media baja (78,18 frente a 79,23 en 2018), la desviación típica pasa de 16,46 a 12,56, y el % con 95 puntos o más baja del 15,10 % al 8,08 %. No es una «prueba más fácil». En los dos años, el % en nivel bajo, la dispersión y el % en nivel alto no son comparables.

**Francés (PUN-19).** Con 243–505 alumnos al año, los segmentos por área, naturaleza o hábitat son demasiado pequeños, y la serie tiene saltos de hasta 22 puntos. Los propios informes excluyen el francés de las series temporales.

### 4.6. Contraste externo con los informes oficiales

La media y el número de alumnos del CSV reproducen los informes oficiales con una diferencia de 0,1 puntos o menos en casi todos los casos. Esto valida la lectura y la interpretación de las columnas. Las discrepancias que quedan también se han documentado.

| Año | Competencia | Oficial: media (n) | CSV: media (n) | Observación |
|---|---|---|---|---|
| 2009 | Catalán | 76,9 (58.955) | 76,84 (58.955) | n idéntico |
| 2012 | Catalán | 79,6 (64.207) | 79,67 (64.207) | n idéntico |
| 2017 | Castellano | 73,4 (71.792) | 74,30 sin corregir; **73,51 corregido** (71.036) | La rotación PUN-02 explica la mayor parte de la diferencia; el CSV tiene 756 alumnos menos. |
| 2017 | Inglés | 79,9 (71.420) | 79,97 (70.629) | El CSV tiene 791 alumnos menos. |
| 2016 | Inglés | 73,7 (no contrastada) | 73,94 (69.985) | **Fuera de ±0,2** (+0,24). Convocatoria con escalas de CO y CE comprimidas (R27, R28); véase el detalle a continuación. |
| 2018 | Ciencias | 70,2 (72.649) | 70,20 (72.648) | – |
| 2023 | Inglés | 77,8 (71.323) | 77,96 (71.323) | n idéntico; la media difiere en 0,16. |
| 2024 | Catalán | 74,7 (69.753) | 74,85 (68.729) | El CSV tiene 1.024 alumnos menos. |
| 2024 | Matemáticas | 74,3 (70.231) | 74,37 (69.836) | El CSV tiene 395 alumnos menos. |
| 2024 | Francés | 62,5 (no contrastada) | 62,80 (266) | **Fuera de ±0,2** (+0,30). Población muy pequeña (PUN-19); véase el detalle a continuación. |
| 2025 | Catalán | 73,5 (66.151) | 73,53 (66.151) | n idéntico |
| 2025 | Matemáticas | 70,4 (66.954) | 70,42 (66.995) | El CSV tiene 41 alumnos más. |
| 2025 | Ciencias | 66,3 (66.509) | 66,32 (66.509) | n idéntico |

Las cifras oficiales están tomadas de los Quaderns de la sección 2.3, y las del CSV del script complementario (sección G). El CSV solo incluye al alumnado con corrección externa. Por ejemplo, las 70.380 filas de 2024 coinciden con la cifra oficial de alumnos que «han realitzat la prova amb correcció externa».

**Combinaciones fuera de la tolerancia de ±0,2.** El contraste automático de la réplica Python (`validacion/resultados/contraste_oficial.csv`) compara las 72 medias oficiales del contrato de diseño (§6) con las del CSV. Solo dos quedan fuera de ±0,2 puntos. En ambas, la n oficial no figura entre las cifras recogidas de los Quaderns, de modo que la causa se ha acotado con los datos del CSV (consultas DuckDB sobre `Datos.csv`):

| Comprobación | Inglés 2016 | Francés 2024 |
|---|---|---|
| Filas del año / puntuaciones globales no nulas | 71.244 / 69.985 | 70.380 / 266 |
| Media del CSV (oficial) | 73,938 (73,7) | 62,801 (62,5) |
| Intervalo que redondea a la cifra oficial | [73,65; 73,75) | [62,45; 62,55) |
| Exceso sobre el límite superior del intervalo | 0,19 | 0,25 |
| Desviación típica / error típico de la media | 15,88 / 0,06 | 13,77 / 0,85 |
| Diferencia en puntos totales (dif. × n) | 16.678 | 80 |
| Globales que cuadran con 0,35·CO + 0,50·CE + 0,15·EE (±0,115) | 98,23 % | 100 % |
| Valores atípicos | 9 ceros; sin ellos, 73,95 | mínimo 27,08; ningún cero |

- **El redondeo queda descartado.** Las cifras oficiales se publican con un decimal, pero las dos medias del CSV superan en 0,19 y 0,25 puntos el valor más alto que todavía redondearía a la cifra oficial.
- **No es un error de carga.** La global del CSV es coherente con sus subcompetencias y los pesos de la sección 4.3 en el 98,23 % y el 100 % de las filas, y no hay filas con subcompetencias y global vacía.
- **Inglés 2016: escala y población.** Con n = 69.985, el error típico de la media es de 0,06 puntos, así que una diferencia de 0,24 (unas 4 veces el error típico) no se explica por unas decenas de alumnos más o menos. Para bajar a 73,7 sin cambiar ninguna puntuación harían falta 226 alumnos más con 0 puntos, o unos 790 alumnos más (la diferencia de n documentada en 2017) con una media de 52,6, muy por debajo de la del año. La causa más probable es la escala: 2016 es la única convocatoria del periodo 2015–2017 en que la global no llega a 100 (máximo 95,55, con CO hasta 96,33 y CE hasta 93,67, frente a 100 en 2015 y 2017). Esta compresión de CO y CE (R27) ya hace que el % por nivel de 2016 se marque como no comparable (R28). Es compatible con que el informe oficial calculara la media sobre una versión de las puntuaciones distinta de la publicada en el CSV, pero el dataset no permite confirmarlo.
- **Francés 2024: tamaño de la población.** Los 266 alumnos se reparten en solo tres áreas (Girona 180, Alt Pirineu i Aran 62 y Vallès Occidental 24), y cada alumno pesa un 0,38 % en la media. La diferencia equivale a 80 puntos en total y a 0,35 errores típicos. Basta una diferencia de pocos alumnos en la n: con 4 alumnos más con una media de 42,5 puntos, la media sería exactamente 62,50, mientras que con 2 alumnos más con 0 puntos bajaría a 62,33. Es coherente con las diferencias de n de entre 41 y 1.024 alumnos de la tabla anterior. Además, el francés es informativo en el CMI (R30), por lo que la discrepancia no afecta a ninguna posición relativa ni al % de competencias que mejoran.

En los dos casos, el valor que muestra el CMI es el del CSV. Queda pendiente contrastar la n oficial en los Quaderns de 2016 y 2024 (Q62) para confirmar la explicación.

---

## 5. Reglas de limpieza

Las reglas están ordenadas tal como se aplicarán en la ETL (T12–T13). Ninguna elimina registros, y todas se aplican sobre las columnas originales, nunca sobre una columna ya transformada. «Filas» son registros del CSV; «celdas» son valores de puntuación, que en FactPuntuacion son filas.

| ID | Columna(s) | Problema | Regla (condición → acción) | Filas afectadas | Hallazgos |
|---|---|---|---|---|---|
| R01 | Todas | Hace falta una clave estable y una comprobación de la carga. | Leer en UTF-8 con separador coma y todas las columnas como texto. Añadir `EvaluacionID` = número de línea del CSV (2…1.102.325) **antes** de filtrar u ordenar. Comprobar 32 columnas y 1.102.324 filas, y que `EvaluacionID` no se repite. | 1.102.324 | OTR-01, COD-01 |
| R02 | Las 24 puntuaciones | Coma decimal; vacío = no presentado. | Validar sobre el texto original el patrón `^\d{1,3},\d{2}$` y el rango [0, 100]. Si falla, la carga debe fallar. Convertir con cultura es-ES directamente sobre el texto original, o bien sustituir la coma por punto y convertir con en-US, sin mezclar las dos vías. Tipo decimal fijo. Vacío → null, nunca 0. | 17.728.085 celdas | PUN-01 |
| R03 | `PCAST`, `PCAST_CL`, `PCAST_EE` | Columnas rotadas en 2017. | Si `ANY` = 2017, asignar a la vez y desde las originales: `PCAST` := `PCAST_EE`; `PCAST_CL` := `PCAST`; `PCAST_EE` := `PCAST_CL`. Prueba de regresión: global ≈ 0,6·CL + 0,4·EE en el 99 % de las filas o más. | 71.036 | PUN-02 |
| R04 | `PFRAN`, `PFRAN_CO`, `PFRAN_CE`, `PFRAN_EE` | Columnas rotadas en 2016. | Si `ANY` = 2016, asignar a la vez y desde las originales: `PFRAN` := `PFRAN_EE`; `PFRAN_CO` := `PFRAN`; `PFRAN_CE` := `PFRAN_CO`; `PFRAN_EE` := `PFRAN_CE`. Prueba: global = 0,35·CO + 0,50·CE + 0,15·EE en el 100 % de las filas. | 389 | PUN-03 |
| R05 | Columnas de texto | Salvaguarda (hoy no hay ningún caso). | Aplicar `Text.Trim` y convertir la cadena vacía en null antes de cualquier mapeo. | 0 | OTR-01 |
| R06 | `CODI_ALUMNE` | Vacío en 2009–2015, en 47 filas de 2016 y en 11 de 2018. | Guardarlo como texto, nunca como número ni como clave. Vacío → null. Añadir `TieneCodigo` = `CODI_ALUMNE` no nulo. Para contar evaluaciones, usar `COUNTROWS(FactEvaluacion)`, no un recuento de códigos distintos. | 448.816 | COD-01, COD-04, PUN-20 |
| R07 | `CODI_ALUMNE` | Un código repetido en el mismo año (2017) y 11 filas idénticas. | No deduplicar. `FlagCodigoDuplicadoAnio` = el código tiene más de una fila en el mismo año. Documentar las 11 filas idénticas. | 2 marcadas (+ 11 documentadas) | COD-02, PUN-20 |
| R08 | `CODI_ALUMNE`, `GENERE`, fecha | Alumnado repetidor. | Con `IndiceConvocatoria` − 1 (no `ANY` − 1) y sin claves duplicadas en la tabla de la convocatoria anterior: `CodigoEnConvocatoriaAnterior` = el código existe en la convocatoria anterior. `RepeticionProbable` = además coinciden el género normalizado y la fecha de nacimiento; el mes 1 de 2016 y la fecha 1/2001 se consideran desconocidos. No fusionar filas. | 914 marcadas, de ellas 910 repeticiones probables (1.828 filas implicadas) | COD-03 |
| R09 | `GENERE` | Dos codificaciones. | H o Home → `GeneroCod` H, `Genero` «Niño». D o Dona → D, «Niña». Cualquier otro valor → null, «Desconocido» (hoy 0 filas). | 73.674 recodificadas | GEN-01 |
| R10 | `NATURALESA` | Dos etiquetados. | Públic o Pública → «Pública». Privat o Privada → «Privada». Cualquier otro valor → «Desconocida» (hoy 0 filas; comprobar en la carga que sigue en 0). | 139.291 recodificadas | NAT-01 |
| R11 | `HÀBITAT` | Texto autoincrementado en 2024 y nueva etiqueta en 2024–2025. | Mapear por prefijo: «Fins a %» → 1 «Hasta 10.000 hab.»; «De 10001 a 100000» → 2 «De 10.001 a 100.000 hab.»; «Més de %» → 3 «Más de 100.000 hab.». Cualquier otro valor → null, y la carga falla si hay alguno (en pandas, `np.select` con default nulo, no 0). `FlagHabitatTextoAnomalo` = el texto es «Fins a N» con N ≠ 10000. | 13.357 marcadas; 53.512 recodificadas | HAB-01, HAB-02 |
| R12 | `HÀBITAT` | Desalineado en 2010; bloque incoherente en 2014. | Si `ANY` = 2010 → `HabitatCod` = 0, «No fiable (2010)», y `HabitatFiable` = false. Si `ANY` = 2014, el área es Baix Llobregat y el hábitat «Més de 100000» → `FlagHabitatIncoherenteArea` = true y `HabitatFiable` = false. En el resto, `HabitatFiable` = true. | 59.358 (59.329 + 29) | HAB-03 |
| R13 | `AREA_TERRITORIAL` | Una fila vacía. | Null → «Desconocida». Se aplica antes de R14. La fila cuenta en los totales de Cataluña y se excluye de los KPIs por área. | 1 | ARE-01 |
| R14 | `AREA_TERRITORIAL` | Reorganización territorial de 2024. | Derivar: `AreaPerimetro2025`: Barcelona Comarques de 2024 → «Barcelonès»; Barcelona Comarques hasta 2023 → «Barcelona Comarques (perímetro hasta 2023)»; el resto, sin cambio. `AreaSerieComparable`: Lleida y Alt Pirineu i Aran → «Lleida + Alt Pirineu i Aran»; Barcelona Comarques, Barcelonès, Penedès, Tarragona y Catalunya Central → «Barcelona Comarques/Barcelonès + Penedès + Tarragona + Catalunya Central»; el resto, sin cambio. `AreaConRupturaSerie` = el área está en uno de los dos grupos. | 358.593 | ARE-02 |
| R15 | `HÀBITAT` × área | Reclasificación del hábitat en Girona y Maresme - Vallès Oriental desde 2024. | No corregir los valores. `RupturaHabitat2024` = el área es Girona o Maresme - Vallès Oriental (atributo del área; la ruptura empieza en 2024). Los visuales área × hábitat a lo largo del tiempo usan `AreaSerieComparable` y llevan una nota en esas dos áreas. | 31.234 (filas de 2024–2025 de esas áreas) | HAB-04 |
| R16 | `ANY_NAIXEMENT`, `MES_NAIXEMENT` | Vacíos en 2009–2014. | `EdadAnioNatural` = `ANY` − `ANY_NAIXEMENT`; si falta el año → null. `MesNacimiento` = null si falta o está fuera de 1–12. | 1.835 sin año; 1.335 sin mes | FEC-01 |
| R17 | Edad | Edades imposibles. | Si `EdadAnioNatural` no está entre 10 y 14 → `EdadAnioNatural` = null y `FlagEdadFueraRango` = true. | 95 | FEC-02 |
| R18 | `ANY_NAIXEMENT` | Desalineado en 2010. | Si `ANY` = 2010 → `EdadAnioNatural` = null y `SituacionEdad` = «No fiable (2010)». El año de nacimiento de 2010 no se expone en DimPerfilAlumno. El mes de 2010 sí es utilizable. | 59.329 | FEC-03 |
| R19 | Fecha de nacimiento | Fechas de relleno. | `FechaNacimientoDudosa` = sin código en 2016 o 2018, o nacimiento 1/2001 en 2016. Si es true → `EdadAnioNatural` = null y `SituacionEdad` = «Desconocida». | 83 | COD-01 y FEC-02 (verificación) |
| R20 | `MES_NAIXEMENT` | Exceso de nacidos en enero. | Indicador informativo `MesNacimientoDudoso` = mes 1 y `ANY` en {2009, 2012, 2013, 2014, 2015}. El mes no se usa para analizar la edad relativa en esos años, o se muestra con nota. | 30.812 marcadas (exceso estimado: 3.331) | FEC-04 |
| R21 | Edad | Situación de edad. | `SituacionEdad` (por este orden): 2010 → «No fiable (2010)»; edad nula → «Desconocida»; menor de 12 → «Adelantado»; 12 → «Edad teórica»; 13 → «Retraso de 1 año»; 14 → «Retraso de 2 años». | 1.102.324 (resultado en la sección 6.2) | FEC-02, FEC-03 |
| R22 | `ANY` | No hay convocatoria en 2020. | DimAnio de 2009 a 2025 con `TieneConvocatoria` (2020 = false, motivo «COVID-19») e `IndiceConvocatoria` 1…16 solo en los años con datos. Las comparaciones temporales usan el índice, nunca `ANY` − 1. | 73.674 (2021 se compara con 2019) | ANY-01 |
| R23 | Globales | Global incoherente con sus subcompetencias. | No recalcular nunca la global. `FlagGlobalIncoherente` = \|global − Σ peso·subcompetencia\| > 0,115, con los pesos de la tabla de la sección 4.3, solo en 2011–2025. En 2009–2010 queda null (no evaluable). | 49.740 de 4.359.515 globales | PUN-04, PUN-05, PUN-07, PUN-13, PUN-23 |
| R24 | `PMAT` 2016 | Global elevada hasta 59,20. | `FlagGlobalRecortada` = `ANY` = 2016, `PMAT` = 59,20 y la global no cuadra (R23). Se mantiene el valor publicado. | 248 | PUN-23 |
| R25 | `PANG_EE` 2015 | Escala anómala, no coherente con la global. | Cargar con `FlagValida` = 0. Las medidas de subcompetencia filtran `FlagValida` = 1. Se mantiene la global de inglés 2015 (ver R26). | 68.342 celdas | PUN-06 |
| R26 | `PCAT_EE` 2018; `PANG`, `PANG_CO`, `PANG_CE` 2015 | Suelos artificiales. | `FlagCensurada` = 1 en esas celdas. Ni imputar ni recortar. Las medidas de % en nivel bajo y de dispersión las excluyen o las anotan. | 72.464 + 3 × 68.342 = 277.490 celdas | PUN-08; PUN-06 y PUN-18 (verificación) |
| R27 | Subcompetencias | Escalas no comparables. | `FlagComparableSerie` = 0 en: `PANG_CO` y `PCAT_CL` de 2011 (techo 99,73); `PANG_EE` de 2013–2016; `PANG_CO` y `PANG_CE` de 2015–2016; subcompetencias de matemáticas de 2015. Las tendencias de subcompetencias las excluyen. | Calculable en la ETL: por ejemplo, `PANG_EE` 2013–2016 = 268.554 celdas | PUN-10, PUN-11, PUN-21 y PUN-09 (verificación) |
| R28 | Globales | % por nivel no comparable. | `NivelComparable` = false en inglés 2015, matemáticas 2015, matemáticas 2019, catalán 2018, inglés 2016 y francés 2022 (sin ningún valor por debajo de 52,90). Esas convocatorias salen de la serie del % en nivel bajo, o aparecen con nota. | 6 combinaciones materia-año | PUN-09, PUN-18, PUN-19 (verificación) |
| R29 | Globales | Nivel de logro. | `IdNivelLogro`: < 55 → 1 Bajo; [55, 70) → 2 Medio-bajo; [70, 85) → 3 Medio-alto; ≥ 85 → 4 Alto. Solo para filas globales; en las subcompetencias, 0 «No aplica». | 4.769.851 globales | PUN-18 y sección 6.3 |
| R30 | Francés | Población pequeña y serie inestable. | `EsInformativa` = true en DimCompetencia. Ocultar o atenuar el valor si el segmento tiene menos de 30 alumnos. Excluir el francés de las posiciones relativas y del % de competencias que mejoran. | 5.130 filas; 19.256 celdas | PUN-19, PUN-07 |
| R31 | Todas las globales | Participación atípica en 2017 y 2024. | Nota de calidad: la tasa de participación de esos años no se compara con la de los demás. | 142.416 (72.036 + 70.380) | PUN-16 |
| R32 | Globales y subcompetencias | Cambios de diseño. | `PeriodoDiseno` por competencia (tabla de la sección 4.5). La variación interanual solo se calcula entre convocatorias del mismo periodo; en los demás casos se muestra «ruptura de serie». Hace falta \|Δ\| ≥ 1 punto para contar una mejora. | Afecta a los KPIs temporales | PUN-11, PUN-12 |
| R33 | Puntuaciones → FactPuntuacion | Despivotado. | Despivotar las 24 columnas y conservar solo los valores no nulos (los 33 nulos parciales de PUN-14 desaparecen sin imputar). Se conservan todas las celdas y se filtra con los indicadores, en lugar de borrar. | 17.728.085 celdas | PUN-14, PUN-17 |
| R34 | Todas | Comprobaciones de la carga. | La carga falla si: no hay 1.102.324 filas; hay algún género, naturaleza o hábitat sin mapear; se repite algún `EvaluacionID`; alguna puntuación incumple el patrón; o la prueba de regresión de R03 o R04 no se cumple. | – | OTR-01 |

El script `perfil_categoricas.py` y su versión M (`limpieza_categoricas.pq`) implementan las reglas tal como las propuso el perfilado. Hay que actualizarlos en T12 en cuatro puntos que la verificación ha cambiado: `HabitatCod` de 2010 pasa a «No fiable (2010)» (R12), se añade `FechaNacimientoDudosa` (R19), la edad pasa a llamarse `EdadAnioNatural` (R16), y `RepeticionProbable` usa la comparación relajada y el índice de convocatoria (R08).

---

## 6. Decisiones de modelado derivadas

### 6.1. Granularidad y tablas de hechos

| Tabla | Grano | Filas | Clave y atributos |
|---|---|---|---|
| FactEvaluacion | Un alumno evaluado en una convocatoria (un registro del CSV) | 1.102.324 | `EvaluacionID` (clave sustituta). Claves de DimAnio, DimContextoCentro y DimPerfilAlumno. `CodiAlumne` como atributo degenerado. Indicadores por fila: `TieneCodigo`, `FlagCodigoDuplicadoAnio`, `CodigoEnConvocatoriaAnterior`, `RepeticionProbable`, `FechaNacimientoDudosa`, `MesNacimientoDudoso`, `FlagEdadFueraRango`, `FlagHabitatTextoAnomalo`. |
| FactPuntuacion | Una evaluación × una competencia o subcompetencia con puntuación no nula | 17.728.085 (4.769.851 globales y 12.958.234 de subcompetencias) | `EvaluacionID`, `IdCompetencia`, y las mismas claves de dimensión que FactEvaluacion, para no relacionar hechos entre sí. `IdNivelLogro` (0 en las subcompetencias). `Puntuacion` (decimal fijo). Indicadores: `FlagValida`, `FlagCensurada`, `FlagComparableSerie`, `FlagGlobalIncoherente` y `FlagGlobalRecortada`. |

Por convocatoria, FactPuntuacion va de 589.644 filas (2009) a 1.466.352 (2019): en media hay 16,08 puntuaciones por alumno, 9,98 en 2009 y entre 19,38 y 19,70 en 2018–2025. Si se decidiera borrar físicamente `PANG_EE` 2015 en lugar de marcarla, quedarían 17.659.743 filas. Se recomienda marcar, para conservar la conciliación con el CSV.

### 6.2. Dimensiones

| Dimensión | Filas | Atributos principales | Observaciones |
|---|---|---|---|
| DimAnio | 17 (2009–2025) | `Anio`, `Curso` («2024-2025»), `TieneConvocatoria`, `IndiceConvocatoria` (1…16), `MotivoSinConvocatoria` | 2020 existe como miembro, sin hechos, para que el eje sea continuo. |
| DimContextoCentro | 86 combinaciones observadas | `AreaTerritorial` (original, con «Desconocida»), `AreaPerimetro2025`, `AreaSerieComparable`, `AreaConRupturaSerie`, `RupturaHabitat2024`, `Naturaleza`, `HabitatCod`, `Habitat` (incluido «No fiable (2010)»), `HabitatFiable` | Dimensión de combinaciones (*junk dimension*). Como `AreaPerimetro2025` depende del año en Barcelona Comarques, la combinación incluye ese atributo. |
| DimPerfilAlumno | 169 combinaciones observadas | `GeneroCod`, `Genero`, `MesNacimiento`, `EdadAnioNatural`, `SituacionEdad` | El año de nacimiento no se expone, porque en 2010 no es fiable. |
| DimCompetencia | 24 | `CodigoOrigen`, `Materia`, `Subcompetencia`, `NombreLegible`, `EsGlobal`, `Orden`, `AnioInicio`, `AnioFin`, `PeriodoDisenoInicio`, `EsInformativa` | Más una tabla documental `PesoCompetenciaAnio`, con los pesos de la sección 4.3; los de 2009–2012 se marcan como «estimados». |
| DimNivelLogro | 5 | `IdNivelLogro` (0–4), `Nivel`, `LimiteInferior`, `LimiteSuperior`, `Orden` | 0 = «No aplica (subcompetencia)». |

La situación de edad que resulta de R16–R21 es: edad teórica, 987.151 filas; retraso de 1 año, 52.240; retraso de 2 años, 471; adelantado, 1.573; desconocida, 1.560; y «No fiable (2010)», 59.329.

**Edad.** `ANY − ANY_NAIXEMENT` es la edad que se cumple durante el año natural de la prueba, no la edad el día de la prueba. Las pruebas se hacen en abril o mayo, y los nacidos después de esa fecha todavía tienen 11 años ese día. Por eso el campo se llama `EdadAnioNatural`. `SituacionEdad` es una clasificación por cohorte de nacimiento: 12 = cohorte regular, como el criterio de idoneidad habitual.

### 6.3. Niveles de logro

El CSV no incluye el nivel oficial de cada alumno, y los informes no publican puntos de corte fijos: los calculan cada año a partir de la media y la dispersión (sección 2.3). Para tener un nivel estable y explicable, se han comparado varios cortes fijos con los % oficiales por nivel de las 35 combinaciones materia-año de 2018–2025 (catalán, castellano, inglés, matemáticas y ciencias):

| Cortes (bajo / medio / alto) | Error medio % Bajo | Sesgo % Bajo | Error medio % Medio-bajo | Error medio % Medio-alto | Error medio % Alto | Sesgo % Alto |
|---|---|---|---|---|---|---|
| 50 / 70 / 85 | 4,39 | −4,39 | 2,97 | 4,18 | 4,75 | +4,09 |
| **55 / 70 / 85** | **2,70** | **−0,14** | **2,29** | **4,18** | **4,75** | **+4,09** |
| 60 / 70 / 85 | 5,57 | +5,22 | 7,17 | 4,18 | 4,75 | +4,09 |
| 55 / 70 / 90 | 2,70 | −0,14 | 2,29 | 10,80 | 8,91 | −8,85 |

Errores en puntos porcentuales (complemento, sección B). En la misma muestra, los cortes que reproducen exactamente los % oficiales tienen una mediana de 55,98 / 70,70 / 85,69, con rangos de 50,08–63,59, 67,86–75,55 y 83,93–90,50.

**Propuesta: cortes fijos 55 / 70 / 85, comunes a todas las materias y años y aplicados a la puntuación global.**

- Cada corte cae en la horquilla oficial: 55 es el centro de la horquilla del nivel mínimo (50–60), 70 es el «llindar òptim» oficial y 85 es el centro de la horquilla del nivel alto (80–90).
- Son los cortes fijos que mejor reproducen el % oficial en nivel bajo: error medio de 2,70 puntos porcentuales y sesgo prácticamente nulo. Con 50 se infravalora sistemáticamente el nivel bajo (−4,39 puntos), y con 60 se sobrevalora (+5,22).
- Un corte común mantiene la comparación entre materias y años con la misma regla. No hace falta un umbral por materia: la escala es la misma (porcentaje de puntuación) y el % en nivel bajo varía más entre años que entre materias.

Distribución resultante en 2009–2025, con las rotaciones corregidas:

| Materia | Bajo (< 55) | Medio-bajo (55–70) | Medio-alto (70–85) | Alto (≥ 85) |
|---|---|---|---|---|
| Catalán | 11,4 % | 20,6 % | 38,6 % | 29,4 % |
| Castellano | 11,6 % | 21,0 % | 40,4 % | 27,1 % |
| Matemáticas | 11,6 % | 18,0 % | 31,6 % | 38,9 % |
| Inglés | 15,8 % | 18,1 % | 26,5 % | 39,5 % |
| Ciencias (2018–2025) | 18,6 % | 22,8 % | 33,2 % | 25,3 % |
| Francés | 14,7 % | 26,5 % | 35,0 % | 23,9 % |
| **Total** | **13,2 %** | **19,8 %** | **34,3 %** | **32,8 %** |

% en nivel bajo (< 55) por materia y convocatoria:

| Materia | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Catalán | 9,0 | 13,2 | 7,7 | 7,5 | 15,2 | 8,7 | 10,9 | 11,2 | 11,2 | 9,6* | 9,9 | 9,8 | 14,9 | 15,9 | 13,1 | 14,2 |
| Castellano | 12,4 | 16,5 | 12,1 | 9,1 | 11,7 | 8,6 | 7,9 | 10,0 | 14,9 | 6,6 | 13,6 | 11,3 | 11,5 | 16,1 | 13,3 | 9,8 |
| Matemáticas | 8,4 | 9,3 | 6,7 | 10,6 | 13,6 | 8,0 | 2,8* | 11,2 | 11,9 | 9,7 | 4,4* | 14,3 | 17,9 | 16,4 | 16,0 | 22,7 |
| Inglés | – | 23,6 | 6,7 | 14,0 | 19,1 | 16,3 | 21,6* | 15,7* | 9,7 | 14,1 | 15,1 | 21,7 | 15,2 | 12,6 | 17,2 | 15,4 |
| Ciencias | – | – | – | – | – | – | – | – | – | 20,2 | 21,9 | 11,1 | 16,9 | 20,1 | 13,2 | 26,9 |
| Francés | – | 7,0 | 9,9 | 13,4 | 17,4 | 24,8 | 26,1 | 16,5 | 7,7 | 18,6 | 15,6 | 9,6 | 0,6* | 8,7 | 29,7 | 21,8 |

\* `NivelComparable` = false (R28). En inglés 2015, 8.801 de los 14.733 alumnos en nivel bajo están en el suelo artificial de 48,79.

**Limitaciones del nivel propuesto.** Los cortes fijos no reproducen los cortes oficiales de cada año, que se ajustan con la media y la dispersión. Las desviaciones más grandes en el % en nivel bajo son catalán y castellano 2018 (−5,7 y −7,3 puntos), matemáticas 2019 (−8,6), ciencias 2019 (+6,2) y matemáticas 2025 (+5,2). El CMI debe indicar que son **niveles internos del TFG, no los niveles oficiales**. Como medida complementaria, se puede ofrecer un nivel relativo por cuartil dentro de cada materia y año.

### 6.4. Restricciones que la calidad de los datos impone a los 12 KPIs

| Perspectiva | KPI | Restricciones derivadas de la auditoría |
|---|---|---|
| Rendimiento | Puntuación media por competencia | Solo `EsGlobal` = 1, con la global publicada (R23), con R03 y R04 aplicadas. Nota en inglés y castellano 2022 (PUN-05). |
| Rendimiento | Puntuación por subcompetencia | Solo `EsGlobal` = 0 y `FlagValida` = 1 (excluye `PANG_EE` 2015). Las series usan `FlagComparableSerie` = 1. No mezclar nunca filas globales y de subcompetencia en una misma medida. |
| Rendimiento | % de alumnado en nivel bajo | `IdNivelLogro` = 1 sobre las globales. `NivelComparable` (R28). Indicar que el nivel es interno. |
| Equidad | Brecha de género | Usar `GeneroCod` normalizado (sin R09, 2021 no tendría datos). Se puede ofrecer también la brecha estandarizada (diferencia dividida por la desviación típica del año). |
| Equidad | Brecha pública-privada | Usar `Naturaleza` normalizada (R10). «Privada» incluye la concertada. |
| Equidad | Dispersión | No comparable en catalán 2018, inglés 2015 (suelos), matemáticas 2015 y 2019 (escala y compresión) ni inglés 2011 (techo en la comprensión oral). |
| Territorio | Desviación del área respecto a Cataluña | Válida dentro de cada año con `AreaTerritorial`. Excluir «Desconocida» de las áreas, pero no del total de Cataluña. |
| Territorio | Diferencia por hábitat | Solo con `HabitatFiable` = true: 2010 queda en blanco con nota. Nota de ruptura en Girona y Maresme - Vallès Oriental desde 2024. |
| Territorio | Posición relativa del área | Ranking dentro de cada año con `AreaTerritorial`. Sin francés. |
| Progreso | Variación interanual | Por `IndiceConvocatoria` (2021 frente a 2019) y solo dentro del mismo `PeriodoDiseno`. Por área, con `AreaSerieComparable`. Etiqueta «puntuación no equiparada entre convocatorias». |
| Progreso | Tendencia de 5 convocatorias | Índices i−4…i. La ventana 2021–2025 cae dentro de periodos de diseño estables, pero incluye inglés y castellano 2022 y la granularidad distinta de 2024 (PUN-22). |
| Progreso | % de competencias que mejoran | Hace falta \|Δ\| ≥ 1 punto. Sin francés. Solo competencias comparables en los dos años. |

### 6.5. Patrones DAX y Power Query

La medida propuesta por el perfilado para la convocatoria anterior devolvía un blanco cuando el eje del visual era `DimAnio[Anio]`, porque el filtro del año se mantenía. La versión correcta elimina los filtros de DimAnio:

```DAX
Media global :=
CALCULATE ( AVERAGE ( FactPuntuacion[Puntuacion] ), DimCompetencia[EsGlobal] = TRUE () )

Media convocatoria anterior :=
VAR i = MAX ( DimAnio[IndiceConvocatoria] )
RETURN
    IF (
        NOT ISBLANK ( i ) && i > 1,
        CALCULATE ( [Media global], REMOVEFILTERS ( DimAnio ), DimAnio[IndiceConvocatoria] = i - 1 )
    )
```

La tendencia de 5 convocatorias usa el mismo patrón, con `DimAnio[IndiceConvocatoria] >= i - 4 && DimAnio[IndiceConvocatoria] <= i`.

En Power Query, las rotaciones (R03 y R04) se implementan creando columnas nuevas a partir de las originales y renombrándolas al final, nunca con sustituciones encadenadas: si se sobrescribe `PCAST` antes de usarlo, se corrompe `PCAST_CL`. La conversión numérica (R02) se hace con `Table.TransformColumnTypes(…, "es-ES")` sobre el texto original. Si primero se cambia la coma por punto y luego se convierte con es-ES, «87.70» se lee como 8770.

### 6.6. Nombres legibles de las 24 columnas de puntuación

| Campo | Materia | Subcompetencia | Global | Convocatorias |
|---|---|---|---|---|
| `PCAT` | Lengua catalana | Puntuación global | Sí | 2009–2025 (sin 2020) |
| `PCAT_CL` | Lengua catalana | Comprensión lectora | No | 2009–2025 |
| `PCAT_EE` | Lengua catalana | Expresión escrita | No | 2009–2025 |
| `PCAT_CO` | Lengua catalana | Comprensión oral | No | 2018–2025 |
| `PCAST` | Lengua castellana | Puntuación global | Sí | 2009–2025 |
| `PCAST_CL` | Lengua castellana | Comprensión lectora | No | 2009–2025 |
| `PCAST_EE` | Lengua castellana | Expresión escrita | No | 2009–2025 |
| `PCAST_CO` | Lengua castellana | Comprensión oral | No | 2018–2025 |
| `PMAT` | Matemáticas | Puntuación global | Sí | 2009–2025 |
| `PMAT_NC` | Matemáticas | Numeración y cálculo | No | 2009–2025 |
| `PMAT_EFM` | Matemáticas | Espacio, medida y representación gráfica de datos («Espacio, forma y medida» hasta 2012) | No | 2009–2025 |
| `PMAT_CR` | Matemáticas | Relaciones y cambio | No | 2009–2025 |
| `PANG` | Lengua inglesa | Puntuación global | Sí | 2010–2025 |
| `PANG_CO` | Lengua inglesa | Comprensión oral | No | 2010–2025 |
| `PANG_CE` | Lengua inglesa | Comprensión lectora (escrita) | No | 2010–2025 |
| `PANG_EE` | Lengua inglesa | Expresión escrita | No | 2013–2025 |
| `PFRAN` | Lengua francesa | Puntuación global | Sí | 2010–2025 |
| `PFRAN_CO` | Lengua francesa | Comprensión oral | No | 2010–2025 |
| `PFRAN_CE` | Lengua francesa | Comprensión lectora (escrita) | No | 2010–2025 |
| `PFRAN_EE` | Lengua francesa | Expresión escrita | No | 2013–2025 |
| `PMED` | Ciencias (medio natural; «Ciencia, tecnología e ingeniería» desde 2024) | Puntuación global | Sí | 2018–2025 |
| `PMED_COMP1` | Ciencias | Explicar fenómenos naturales y aplicaciones tecnológicas | No | 2018–2025 |
| `PMED_COMP2` | Ciencias | Reconocer los aspectos principales de la investigación científica | No | 2018–2025 |
| `PMED_COMP3` | Ciencias | Interpretar información científico-tecnológica (datos y pruebas) | No | 2018–2025 |

Ninguna columna tiene datos en 2020. Las descripciones originales en catalán están en los metadatos de la API (sección 2.1).

---

## 7. Limitaciones y cuestiones abiertas

### 7.1. Limitaciones

- **Sin acceso al origen.** No hay código de centro ni de municipio. Por eso no se puede saber qué municipios cambian de área en 2024, por qué se reclasifica el hábitat de Girona y Maresme, ni cuál es el hábitat real de 2010. Las reglas neutralizan esos problemas, pero no los corrigen.
- **Pesos estimados.** Los pesos de 2009–2012 se han estimado con los datos y no hay fuente oficial que los confirme. En ciencias, los pesos observados (media simple) contradicen los publicados (42/25/33).
- **Niveles no oficiales.** Los cortes 55/70/85 aproximan los % oficiales, pero no los reproducen en cada año.
- **Normativa territorial.** El detalle del Decret 120/2023 procede de un resumen del INAP y de documentos del Govern, no del texto del DOGC. El antecedente del nombre «Barcelona Comarques» (2008–2009) no se ha verificado.
- **Power Query sin ejecutar.** Las reglas se han verificado en pandas y DuckDB. El código M no se ha podido ejecutar en este entorno, y no está comprobado que Power Query lea el campo vacío sin comillas como null o como cadena vacía (por eso R05 trata ambos casos).
- **Clave dependiente del fichero.** `EvaluacionID` es el número de línea de esta versión del CSV (SHA-256 de la sección 2.1). Si la Generalitat publica una nueva versión, las claves cambian.
- **Población.** El CSV contiene solo al alumnado con corrección externa, y en 2017 y 2024 parece filtrado. Los recuentos de alumnado pueden diferir hasta en unos 1.000 alumnos de los informes.

### 7.2. Cuestiones para validar con las directoras

1. **Umbrales de nivel.** ¿Se aceptan los cortes fijos 55/70/85 (sección 6.3)? Las alternativas son 50/70/85, la propuesta inicial, más simple pero con el nivel bajo infravalorado en 4,4 puntos, o cortes calibrados por materia y año, que reproducen los oficiales pero solo existen para los años con informe.
2. **Inglés 2015 y catalán 2018.** ¿Basta con marcar los suelos artificiales y la escala anómala (R25, R26 y R28), o se excluyen esas convocatorias del CMI?
3. **2010.** ¿Se acepta perder el hábitat y la edad de 2010 (R12 y R18), con una nota, en lugar de usar valores que se sabe que están desalineados?
4. **Series territoriales.** El grupo «Barcelona Comarques/Barcelonès + Penedès + Tarragona + Catalunya Central» reúne cerca del 27 % de Cataluña. ¿Se usa para los KPIs temporales por área, o se limitan esos KPIs a las áreas estables y a la comparación 2024–2025? ¿Se incluye Girona en el grupo de Lleida por la Cerdanya, o se deja con una nota?
5. **KPIs temporales sin equiparación.** ¿Se mantienen la variación interanual, la tendencia y el % de competencias que mejoran con la etiqueta «puntuación no equiparada», el umbral \|Δ\| ≥ 1 y las rupturas de diseño? ¿Se añade una puntuación estandarizada por año (z)?
6. **Comparación 2021 frente a 2019.** ¿Se muestra como variación interanual, con nota de la COVID-19, o se rompe la serie, como hace el Quadern 68 en su gráfico 3?
7. **Francés.** ¿Se mantiene solo como competencia informativa (R30), o se excluye del CMI?
8. **Pesos de ciencias.** ¿Cómo se documenta en la memoria la contradicción entre los pesos publicados (42/25/33) y los datos (media simple)? ¿Se comunica al titular del dataset, junto con las rotaciones de 2016 y 2017 y el error de `HÀBITAT` de 2024?
9. **Grano de FactPuntuacion.** ¿Se confirma conservar las 17.728.085 celdas con indicadores, en lugar de borrar las inválidas (17.659.743)?
10. **Edad.** ¿Se acepta presentar `EdadAnioNatural` y una situación de edad por cohorte, en lugar de la «edad en la prueba» prevista en el diseño inicial?

---

## Referencias

- Generalitat de Catalunya, Departament d'Educació i Formació Professional. *Avaluació de sisè d'educació primària* (`rk5x-gny6`). Portal de Dades Obertes. https://analisi.transparenciacatalunya.cat/Educaci-/Avaluaci-de-sis-d-educaci-prim-ria/rk5x-gny6/about_data (metadatos: https://analisi.transparenciacatalunya.cat/api/views/rk5x-gny6.json).
- Generalitat de Catalunya. Licencias de datos abiertos. https://administraciodigital.gencat.cat/ca/dades/dades-obertes/informacio-practica/llicencies/
- Consell Superior d'Avaluació del Sistema Educatiu / Agència d'Avaluació i Prospectiva de l'Educació. *Quaderns d'avaluació* de sexto de primaria, 2009–2025 (handles en la sección 2.3), en particular el Quadern 44 (2019, https://hdl.handle.net/20.500.12694/444), el Quadern 50 (2021, https://hdl.handle.net/20.500.12694/2098), el Quadern 62 (2024, https://hdl.handle.net/20.500.12694/7364) y el Quadern 68 (2025, https://hdl.handle.net/20.500.12694/7383).
- Resumen del Decret 120/2023, de 27 de junio, de reestructuración del Departament d'Educació. https://laadministracionaldia.inap.es/noticia.asp?id=1234838
- Govern de la Generalitat. Acords de Govern de 27/06/2023. https://govern.cat/govern/docs/2023/06/27/15/19/4262d160-a91a-4708-a7ea-87c8868f25c0.pdf
- Govern de la Generalitat. Acords de Govern (setembre de 2022), creación de los Serveis Territorials a l'Alt Pirineu i Aran. https://govern.cat/govern/docs/2022/09/05/17/53/4c60bfbd-fbb8-4ed9-922a-9da09d8c57da.pdf
- Generalitat de Catalunya. Directori de centres docents (`kvmv-ahh4`). https://analisi.transparenciacatalunya.cat/resource/kvmv-ahh4.json
- ISO/IEC 25012:2008. *Software engineering — Software product Quality Requirements and Evaluation (SQuaRE) — Data quality model*.
- Kimball, R. y Ross, M. (2013). *The Data Warehouse Toolkit* (3.ª ed.). Wiley.
