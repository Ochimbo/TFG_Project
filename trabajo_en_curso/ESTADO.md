# Estado de la implementación del CMI (actualizado el 12/11/2026, Week_2)

Carpeta de trabajo para retomar la implementación con Claude Code. No es un entregable del TFG: cuando el
proyecto esté terminado se puede borrar, o mover lo útil a `validacion/` o a `Documentation/`.
Las decisiones tomadas después del contrato de diseño están en `trabajo_en_curso/week2/DECISIONES.md` (D-01 a D-19);
donde difieran del contrato o de los documentos 01–04, manda `DECISIONES.md`.

## Qué está hecho

| Fase | Estado | Dónde |
|---|---|---|
| Auditoría de calidad de datos (T7) | Terminada y verificada; cuestiones abiertas de §7.2 resueltas (D-05 a D-11, resumen en el propio §7.2) | `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md`, scripts en `validacion/perfilado/` |
| Contrato de diseño | Terminado y actualizado el 12/11/2026 (§0 rutas Windows, §1 compat 1606, §3 y §5.1 Barcelonès, §5.2 periodos de diseño, §7 20 medidas, §8 41 visuales) | `trabajo_en_curso/contrato_diseno.md` |
| Modelo semántico TMDL + ETL M + PBIP | Hecho. TOM `Model.Validate()` 0 errores (12/11/2026); parser M 11/11 OK | `PowerBI/` (generado por `trabajo_en_curso/generadores/modelo/gen_modelo.py PowerBI`; consultas M en `generadores/modelo/m_*.m`) |
| Medidas DAX (20) | Hechas y contrastadas con `kpis_referencia.py`; semáforos con formato «▲ Favorable / ● Neutro / ▼ Desfavorable» (D-12); medida nueva `Puntuaciones por nivel de logro` (D-13) | `.../tables/_Medidas.tmdl` (generado por `generadores/gen_medidas.py <ruta>`) |
| Informe PBIR (3 páginas, 41 visuales) | Validado contra los esquemas oficiales: 0 errores, 0 avisos | `PowerBI/CMI_Educacion_Primaria.Report/` (generado por `generadores/gen_pbir.py`) |
| Réplica Python de la ETL, tests y KPIs de referencia | Hechos: 31/31 tests OK; 7 CSV en `validacion/resultados/` | `validacion/etl_referencia.py`, `test_modelo.py`, `kpis_referencia.py` |
| Comprobación M frente a parquet | 0 fallos | `trabajo_en_curso/herramientas/verificar_claves.py` |
| Documentos 02, 03 y 04 | Hechos el 15/10/2026 y actualizados el 12/11/2026 con las decisiones D-01 a D-19 | `Documentation/Docu_Final/Docu_Parcial/` |

REGLA: no editar a mano `PowerBI/`. Cambiar el generador (o los `m_*.m`) y regenerar; después ejecutar
`validacion/etl_referencia.py` si cambia la ETL, `test_modelo.py`, `kpis_referencia.py` y los validadores.
Los generadores conservan lo que Power BI Desktop añade al guardar (`.platform`, `.pbi/`, `cultures/`, `RutaDatos`, compat 1606; D-19).

## Power BI Desktop

El proyecto se abrió y actualizó en Power BI Desktop (Windows) el 15/10/2026: el commit `6adfe70` contiene lo que Desktop
guarda (`cultures/es-ES.tmdl`, `.platform`, `.pbi/editorSettings.json`, compat 1606, `RutaDatos` con la ruta del repo),
así que el M se ejecutó. No quedó anotado el resultado de la lista de comprobación de `04_Guia_de_uso.md` §3.2.

## Qué falta

1. Repetir la actualización en Power BI Desktop con la versión actual y anotar aquí el resultado:
   - filas: FactEvaluacion 1.102.324, FactPuntuacion 17.728.085; K01 castellano 2017 = 73,51;
   - comparar los visuales con `validacion/resultados/*.csv` (incluidos `kpi_niveles_2025.csv` y `semaforos_2025.csv`);
   - comprobar que las tarjetas de estado muestran «▲ Favorable», «● Neutro» o «▼ Desfavorable» y no 1, 0, −1 (D-12);
   - comprobar que 2020 aparece como hueco en los tres gráficos de líneas, con la línea cortada entre 2019 y 2021 (D-14);
   - comprobar que los segmentadores de año arrancan en 2025 (filtro en `filterConfig`, D-19) y que el segmentador de
     género del panel táctico filtra todo salvo K04 (D-15);
   - comprobar que el Barcelonès tiene K10 y `Estado K10` en 2025 y que «Barcelona Comarques» solo aparece hasta 2023 (D-05);
   - prueba negativa: en una COPIA del CSV poner una puntuación inválida y comprobar que la actualización falla;
   - si la actualización tarda demasiado: DimAnio puede leer solo la columna ANY del CSV en vez de
     `stg_Evaluaciones` (cada consulta que referencia stg relee el CSV). No usar Table.Buffer sobre stg.
2. Memoria: aplicar lo que cada entrada D-NN deja en «Pendiente en la memoria» y escribir el capítulo 8 con la
   sección «Datos para el capítulo 8» de `DECISIONES.md`.
3. Contrastar la n oficial de inglés 2016 y francés 2024 en los Quaderns (informe de calidad §4.6).
4. Comunicar al titular del dataset las incidencias objetivas (texto en `DECISIONES.md`, D-07): acción de la estudiante.

## Decisiones que antes estaban pendientes con las directoras

Resueltas como decisiones de ingeniería el 10/11/2026 (D-05 a D-11; resumen en el informe de calidad §7.2): cortes
55/70/85 definitivos; inglés 2015 y catalán 2018 marcados sin excluir; hábitat y edad de 2010 «No fiable»; series
territoriales agrupadas y Girona como serie propia; el área de 2024 publicada como «Barcelona Comarques» se muestra como
«Barcelonès»; francés informativo; KPIs temporales con aviso de no equiparación y periodo de diseño desde 2017 en inglés y
francés; global de ciencias sin recalcular. Las directoras las revisan en la memoria.

## Herramientas de validación (Windows, 12/11/2026)

Todo en una carpeta del directorio temporal, nunca en el repositorio:

- Python: `pip install --target <tmp>/pylibs duckdb pyarrow numpy pandas jsonschema referencing` y
  `PYTHONPATH=<tmp>/pylibs PYTHONIOENCODING=utf-8 python validacion/etl_referencia.py` (ídem `test_modelo.py`, `kpis_referencia.py`,
  `trabajo_en_curso/herramientas/verificar_claves.py`).
- **Validador TMDL** (`herramientas/tmdlcheck`, librería oficial TOM): SDK de .NET 8 en una carpeta temporal
  (`dotnet-install.ps1 -Channel 8.0 -InstallDir <tmp>/dotnet`), copiar la carpeta a `<tmp>/tmdlcheck`, `dotnet build -c Release -o out`
  y `DOTNET_ROOT=<tmp>/dotnet out/tmdlcheck <repo>/PowerBI/CMI_Educacion_Primaria.SemanticModel/definition`. Deserializa el modelo,
  lo lista y ejecuta `Model.Validate()`. No valida la semántica DAX. `herramientas/tmdldump` hace un volcado y una reserialización.
- **Analizador sintáctico de Power Query M** (`herramientas/mparser`, `@microsoft/powerquery-parser`, Node 24): copiar a
  `<tmp>/mparser`, `npm ci` y `python trabajo_en_curso/herramientas/validar_m.py --mcheck <tmp>/mparser/mcheck.js`.
- **Esquemas JSON de PBIR/PBIP**: `git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/json-schemas <tmp>/json-schemas`,
  `git -C <tmp>/json-schemas sparse-checkout set fabric/item/report fabric/item/semanticModel fabric/pbip` y
  `PBIR_SCHEMAS=<tmp>/json-schemas/fabric python trabajo_en_curso/herramientas/validar_pbir.py`.
- Documentación y ejemplos de PBIR descargados: `referencias_pbir/`.

En Linux valen las mismas instrucciones con `dotnet-install.sh`. Los generadores usan rutas relativas al repo.

## Cómo retomar con Claude Code

Leer `trabajo_en_curso/week2/DECISIONES.md` y `PROGRESO_datos.md`. Con los errores o capturas de la próxima actualización
en Power BI Desktop, pedir: «corrige el CMI con estos errores de Power BI». Las correcciones se hacen en los generadores
(`trabajo_en_curso/generadores/`) y se revalidan con las herramientas de arriba.
Los scripts de los workflows usados están en `trabajo_en_curso/workflows/` (1 auditoría, 2 construcción interrumpida,
3 reanudación completada).

## Comprobaciones clave (contrato §6)

FactEvaluacion = 1.102.324 filas; FactPuntuacion = 17.728.085 (4.769.851 globales); media de castellano 2017
corregida = 73,51 (oficial 73,4); las 72 medias de Cataluña dentro de 0,5 puntos de los Quaderns d'avaluació 2009–2025
(criterio RNF06; máximo 0,30) y 70 de 72 dentro de la alerta interna de 0,2 (D-01).
