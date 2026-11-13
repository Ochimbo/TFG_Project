# Progreso del agente de datos e implementación (Week_2)

Encargo: auditoría de coherencia (documentos, implementación, memoria), cuestiones abiertas de datos, decidir, aplicar
y registrar en `DECISIONES.md` (D-01…). No edita `main.tex` (lo pendiente va en «Pendiente en la memoria»).
Quien retome: leer este fichero y `DECISIONES.md`, y comprobar el estado real con `git status` y `git diff`.

## Entorno de validación en este equipo (Windows)

- Python 3.12 global sin duckdb/pyarrow. Se instalan en una carpeta temporal y se usan con `PYTHONPATH`:
  `pip install --target <tmp>/pylibs duckdb pyarrow numpy pandas` y después
  `PYTHONPATH=<tmp>/pylibs PYTHONIOENCODING=utf-8 python validacion/etl_referencia.py` (ídem `test_modelo.py`, `kpis_referencia.py`).
- Analizador M: copiar `trabajo_en_curso/herramientas/mparser` a `<tmp>/mparser`, `npm ci` allí y
  `python trabajo_en_curso/herramientas/validar_m.py --mcheck <tmp>/mparser/mcheck.js` (Node 24 instalado).
- Esquemas PBIR: clon disperso de `github.com/microsoft/json-schemas` en `<tmp>/json-schemas` y
  `PBIR_SCHEMAS=<tmp>/json-schemas/fabric python trabajo_en_curso/herramientas/validar_pbir.py`.
- .NET: solo hay runtime 8.0.21, no SDK (`dotnet --list-sdks` vacío). `tmdlcheck` necesita compilarse: ver paso 9.
- Regenerar: `python trabajo_en_curso/generadores/modelo/gen_modelo.py PowerBI`;
  `python trabajo_en_curso/generadores/gen_medidas.py PowerBI/CMI_Educacion_Primaria.SemanticModel/definition/tables/_Medidas.tmdl`;
  `python trabajo_en_curso/generadores/gen_pbir.py`.

## Línea base (antes de cualquier cambio), ejecutada el 10/11/2026

- [x] `etl_referencia.py`: 1.102.324 evaluaciones y 17.728.085 puntuaciones. `test_modelo.py`: 27 de 27.
- [x] `kpis_referencia.py`: los 6 CSV salen idénticos a los versionados (git solo ve el cambio de fin de línea).
- [x] Evidencia sobre `Datos.csv`: `analisis/evidencia_cuestiones_abiertas.py` (resultados citados en DECISIONES.md).

## Pasos

- [x] 1. Lectura cruzada de ESTADO, contrato, 01–04, generadores, PBIR, validación y memoria (3.3–3.5, 4.3, cap. 7).
- [x] 2. Registrar en DECISIONES.md las decisiones tomadas (D-01…D-18), con «Estado de aplicación» en cada una.
- [x] 3. Modelo (M y réplica), hecho el 11/11/2026: D-05 «Barcelonès» en 2024 y `AreaOrden` 5 para el código 4
       (`m_DimContextoCentro.m`, `gen_modelo.py`, `etl_referencia.py`, `herramientas/verificar_claves.py`);
       D-10 `PeriodoDisenoInicio` 2017 en PANG y PFRAN (`m_DimCompetencia.m`, `etl_referencia.py`);
       D-08 quitar «provisionales» (`m_DimNivelLogro.m`, `gen_modelo.py`). Además D-19 (nueva): el `PowerBI/`
       versionado procede de un guardado desde Power BI Desktop (commit `6adfe70`, 15/10/2026): `gen_modelo.py`
       conserva ahora `cultures/`, `.platform`, `.pbi/`, el `ref cultureInfo es-ES`, el compat 1606 y el valor
       actual de `RutaDatos`. Regenerado con `gen_modelo.py`; `git diff` solo muestra los cambios previstos
       (más líneas en blanco finales y el espacio sobrante de la ruta). Los tests se adaptan en el paso 6.
- [x] 4. Medidas, hecho el 11/11/2026: D-12 `FMT_SEMAFORO` = `"▲ Favorable";"▼ Desfavorable";"● Neutro"` en los tres
       `Estado` (descripciones actualizadas); D-13 medida nueva `Puntuaciones por nivel de logro` (carpeta
       «1. Rendimiento académico», lineageTag `58ea587f-…`). `_Medidas.tmdl` regenerado: 20 medidas.
       Falta validar con TOM (`tmdlcheck`) que la cadena de formato con comillas se deserializa bien (paso 9).
- [x] 5. Informe (`gen_pbir.py`), hecho el 11-12/11/2026: D-12 tarjeta `Estado K10` y columna en la tabla (p1), tarjetas
       `Estado K01` y `Estado K03` en p2 y `Estado K03` en p3 (7, 6 y 5 tarjetas por fila, `fila_tarjetas`);
       D-13 barras 100 % con `Puntuaciones por nivel de logro` y solo el filtro «No aplica»; D-14 `showAll` en el
       eje de los tres gráficos de líneas; D-15 etiquetas «Competencia»/«Titularidad» y segmentador de género
       (`p2_seg_genero`, grupo `Genero`); D-11 aviso con «2021 se compara con 2019»; D-08 aviso sin «provisionales»;
       D-19 selección por defecto 2025 como filtro `Categorical` en `filterConfig` y conservación de `.platform`/`.pbi`.
       Informe regenerado: 3 páginas, 41 visuales (13 + 14 + 14), `pbir_referencias.json` con 27 campos.
       `tmdlcheck` (TOM, SDK .NET 8.0.428 en carpeta temporal): deserializa, 20 medidas, `Model.Validate()` 0 errores;
       la cadena de formato de los semáforos exige en TMDL la forma `"""▲ Favorable"";…"""` (`tmdl_value` en `gen_medidas.py`).
- [x] 6. Réplica y tests, hecho el 12/11/2026: D-01 `TOLERANCIA_RNF06 = 0.5`, columna `dentro_RNF06` en
       `contraste_oficial.csv` y `test_criterio_aceptacion_rnf06`; D-13 `Modelo.puntuaciones_por_nivel`, CSV nuevo
       `kpi_niveles_2025.csv` (24 filas) y `test_distribucion_por_nivel_coincide_con_k03`; D-17
       `test_vigencia_competencias_ri2`; D-05 ampliación de `test_area_barcelona_comarques_por_anio`; D-10
       `test_periodo_diseno_coherente_por_materia`. Resultados reales (ver «Comprobaciones ejecutadas»): ETL
       1.102.324 / 17.728.085; 31 de 31 tests; 72 de 72 dentro de ±0,5 (máx. 0,30), 70 de 72 dentro de ±0,2.
       Cambios en los CSV frente a los versionados: K10 de 2017 (inglés +6,03, francés +4,62) y K12 de 2017 (100 %)
       pasan a vacío; K11 de 2021 (inglés −0,19, francés +0,90; global −0,19) pasa a vacío (D-10); el Barcelonès
       tiene K10 y `Estado K10` en 2025 (catalán −1,03, castellano +2,20, matemáticas −4,05, inglés +1,76,
       ciencias −8,27) (D-05). `kpi_area_2025.csv` y `kpi_subcompetencia_2025.csv` no cambian.
- [x] 7. Documentos, hecho el 12/11/2026: `01` (§4.5 tabla de periodos y nota D-10; §4.6 dos umbrales D-01; §5 «Cómo aplica
       la ETL estas reglas» D-03; §6 nota con tabla de diferencias D-04; §6.3 cortes definitivos D-08; §7.1 Desktop D-19;
       §7.2 resolución de las diez cuestiones), `02` (recuentos 20/41/31/7, nota de nombres D-15, diccionario D-05/D-10/D-08,
       medidas D-12/D-13, §7.2 criterio D-09, §7.3 Barcelonès y Girona D-05/D-06, §7.4 ciencias y umbrales D-07/D-01/D-02,
       §8.1), `03` (§1.2 y §1.4 paneles de cada semáforo, §2 periodos, K03/K06/K07/K10/K11/K12 y semáforos, ficha nueva de
       `Puntuaciones por nivel de logro`, §5.2), `04` (aviso, 2.3, 3.2 con nuevos valores de control, 4.x, 5.2, 6.x, 7, 8),
       `contrato_diseno.md` (§0, §1, §3, §5.1, §5.2, §6, §7, §8), `ESTADO.md` (reescrito) y `validacion/README.md` (reescrito).
- [x] 8. Sección «Datos para el capítulo 8» al final de DECISIONES.md (12-13/11/2026): correspondencia modelo conceptual →
       tablas con cómo se garantiza cada RI, relaciones, tablas de hechos, dimensiones (columnas, tipos, claves, filas),
       flujo de consultas M y reglas de cada una con las comprobaciones que detienen la carga, las 20 medidas con fórmula
       y carpeta (extraídas de `gen_medidas.py` con un script), semáforos y referencias, estructura común de la interfaz,
       los 41 visuales con posición, campos y filtros (extraídos de los `visual.json`), estructura del repositorio y
       cifras de validación. Además la sección «Incidencias para comunicar al titular del dataset (D-07)» y la
       corrección de los «Cambios aplicados» de D-01, D-05, D-07, D-08, D-10, D-11, D-12, D-13, D-14, D-15, D-17 y D-18.
- [x] 9. Validadores ejecutados el 12/11/2026 (resultados abajo). `tmdlcheck` compilado con el SDK .NET 8.0.428 instalado
       en el directorio temporal.
- [x] 10. Informe final: el agente se cortó (error de API) tras el paso 9; el informe lo resume la sesión principal el 13/11/2026.

## Comprobaciones ejecutadas tras los cambios (12/11/2026, Windows, Git Bash)

| Comprobación | Resultado |
|---|---|
| `validacion/etl_referencia.py` | 8 tablas en 9,3 s: DimAnio 17, DimContextoCentro 120, DimPerfilAlumno 182, DimCompetencia 24, DimNivelLogro 5, DimCalidadDato 16, FactEvaluacion 1.102.324, FactPuntuacion 17.728.085 |
| `validacion/test_modelo.py` | 31 de 31 tests correctos (10,0 s); 4 tests nuevos: distribución por nivel = K03, vigencia RI2, periodo de diseño por materia, criterio RNF06 |
| `validacion/kpis_referencia.py` | 7 CSV (85, 63, 17, 18, 24, 69 y 72 filas); 72 de 72 medias dentro de ±0,5 (máximo 0,30); 70 de 72 dentro de ±0,2 |
| `tmdlcheck` (TOM, Microsoft.AnalysisServices 19.84.1, SDK .NET 8.0.428 en carpeta temporal) | Deserializa el modelo (compat 1606, cultura es-ES), 9 tablas, 20 medidas, 9 relaciones Many:One OneDirection, `Model.Validate()` 0 errores. Primera ejecución falló con `InvalidValueFormat` por las comillas del formato de los semáforos; corregido en `gen_medidas.py` (`tmdl_value`) |
| `validar_m.py` (parser oficial de M, Node 24) | 11 de 11 bloques M correctos |
| `validar_pbir.py` (esquemas oficiales, clon disperso) | 49 ficheros validados, 7 esquemas, 270 expresiones, 3 páginas, 41 visuales, 27 campos referenciados (9 columnas, 18 medidas), coinciden con `pbir_referencias.json`: 0 errores, 0 avisos |
| `verificar_claves.py` | 0 fallos: dimensiones reconstruidas desde el M idénticas al parquet (120, 182, 24, 5, 16, 17 filas), 0 combinaciones huérfanas en el dominio de staging, 0 claves huérfanas en los hechos (85 contextos y 169 perfiles observados) |
| `git diff` de `PowerBI/` | Solo los cambios previstos (D-05, D-08, D-10, D-12, D-13, D-14, D-15, D-19) más ruido de Desktop: líneas en blanco finales, orden de claves de los JSON y versión del esquema de los `visual.json` (Desktop había escrito 2.13.0; el generador escribe 2.4.0, validado) |

## Pendiente de comprobar en Power BI Desktop

Nadie ha anotado todavía los resultados de la lista de comprobación de `04_Guia_de_uso.md` §3.2 (el proyecto se abrió en
Desktop el 15/10/2026, commit `6adfe70`, pero sin registro). Con la versión actual hay que comprobar:

1. Actualización completa sin errores con `RutaDatos` apuntando al CSV de la raíz del repositorio; filas FactEvaluacion
   1.102.324 y FactPuntuacion 17.728.085; K01 castellano 2017 = 73,51.
2. Semáforos (D-12): las tarjetas `Estado K10` (estratégico), `Estado K01` y `Estado K03` (táctico y operativo) y la
   columna `Estado K10` de la tabla muestran «▲ Favorable», «● Neutro» o «▼ Desfavorable», no 1, 0, −1. Valores en
   `semaforos_2025.csv`.
3. Distribución por nivel (D-13): barras 100 % por competencia con la medida `Puntuaciones por nivel de logro`; matemáticas
   2025 = 22,7 / 21,4 / 27,8 / 28,2 %; la leyenda no muestra «No aplica»; con un contexto de menos de 30 puntuaciones el
   gráfico queda vacío.
4. Hueco de 2020 (D-14): en los tres gráficos de líneas 2020 aparece en el eje sin punto y la línea se corta entre 2019 y 2021.
5. Año por defecto (D-19): los tres segmentadores de año arrancan en 2025 con el filtro en `filterConfig`; si Desktop lo
   descarta también así, habrá que fijarlo desde Desktop y registrar cómo lo guarda.
6. Segmentador de género del táctico (D-15): filtra todos los visuales de la página salvo K04; etiquetas «Competencia» y
   «Titularidad» visibles.
7. Barcelonès (D-05): en 2025 tiene K10 y `Estado K10`; «Barcelona Comarques» solo aparece con años hasta 2023; el
   segmentador de área muestra 15 valores sin duplicados.
8. Prueba negativa: en una COPIA del CSV poner `150,00` o `abc` en una puntuación y comprobar que la actualización falla
   con «R02 Puntuación no válida» y el `EvaluacionID`.
9. Tras guardar desde Desktop, revisar con `git diff` qué reescribe (esquema 2.13.0, orden de claves) y confirmar que
   `.platform`, `.pbi/` y `cultures/` siguen intactos tras regenerar.
