# Estado de la implementación del CMI (actualizado el 15/10/2026: versión mínima completa)

Carpeta de trabajo para retomar la implementación con Claude Code. No es un entregable del TFG: cuando el
proyecto esté terminado se puede borrar, o mover lo útil a `validacion/` o a `Documentation/`.

## Qué está hecho (actualizado el 15/10/2026, integración final)

| Fase | Estado | Dónde |
|---|---|---|
| Auditoría de calidad de datos (T7) | Terminada y verificada | `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md`, scripts en `validacion/perfilado/` |
| Contrato de diseño | Terminado (con los cambios de integración de §5.1 AreaOrden y §5.2 SubcompetenciaOrden) | `trabajo_en_curso/contrato_diseno.md` |
| Modelo semántico TMDL + ETL M + PBIP | Hecho. TOM Validate 0 errores; parser M 11/11 OK | `PowerBI/` (generado por `trabajo_en_curso/generadores/modelo/gen_modelo.py PowerBI`; consultas M en `generadores/modelo/m_*.m`) |
| Medidas DAX (19) | Hechas y contrastadas con `kpis_referencia.py` | `.../tables/_Medidas.tmdl` (generado por `generadores/gen_medidas.py <ruta>`) |
| Informe PBIR (3 páginas, 36 visuales) | Validado contra los esquemas oficiales: 0 errores | `PowerBI/CMI_Educacion_Primaria.Report/` (generado por `generadores/gen_pbir.py`) |
| Réplica Python de la ETL, tests y KPIs de referencia | Hechos: 27/27 tests OK; 6 CSV en `validacion/resultados/` | `validacion/etl_referencia.py`, `test_modelo.py`, `kpis_referencia.py` |
| Comprobación M frente a parquet | 0 fallos | `trabajo_en_curso/herramientas/verificar_claves.py` |

REGLA: no editar a mano `PowerBI/`. Cambiar el generador (o los `m_*.m`) y regenerar; después ejecutar
`validacion/etl_referencia.py` si cambia la ETL, `test_modelo.py`, `kpis_referencia.py` y los validadores.

## Qué falta

1. Documentación: HECHA el 15/10/2026: `02_Modelo_y_diccionario.md`, `03_Fichas_KPI.md` y `04_Guia_de_uso.md` en
   `Documentation/Docu_Final/Docu_Parcial/`. En el §4.6 del informe de calidad se han documentado inglés 2016 y francés 2024.
2. Primera apertura en Power BI Desktop (Windows), que nadie ha hecho todavía (el M nunca se ha ejecutado):
   - abrir `PowerBI/CMI_Educacion_Primaria.pbip`, fijar `RutaDatos` y actualizar;
   - comprobar filas: FactEvaluacion 1.102.324, FactPuntuacion 17.728.085; K01 castellano 2017 = 73,51;
     comparar visuales con `validacion/resultados/*.csv` (incluido `kpi_subcompetencia_2025.csv` para K02);
   - prueba negativa: en una COPIA del CSV poner una puntuación inválida y comprobar que la actualización falla;
   - si la actualización tarda demasiado: DimAnio puede leer solo la columna ANY del CSV en vez de
     `stg_Evaluaciones` (cada consulta que referencia stg relee el CSV). No usar Table.Buffer sobre stg.

## Decisiones pendientes con las directoras

Están en el informe de calidad, §7.2. Esta versión aplica las opciones por defecto: umbrales de nivel 55/70/85;
marcar sin excluir inglés 2015 y catalán 2018; hábitat y edad de 2010 como «No fiable»; series territoriales
agrupadas (`AreaSerieComparable`); francés solo informativo (n >= 30); KPIs temporales con la nota «no equiparada».

## Herramientas de validación (Linux)

Estaban en `/tmp` (se pierden al reiniciar). Aquí está su código fuente para reconstruirlas:

- **Validador TMDL** (`herramientas/tmdlcheck`): usa la librería oficial de Microsoft (TOM). Deserializa la carpeta
  `definition`, lista el modelo y ejecuta `Model.Validate()`. No valida la semántica DAX.
  ```bash
  # .NET 8 en una carpeta local (unos 600 MB)
  curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0 --install-dir ~/.dotnet
  cd trabajo_en_curso/herramientas/tmdlcheck && ~/.dotnet/dotnet build -c Release -o out
  DOTNET_ROOT=~/.dotnet ./out/tmdlcheck ../../../PowerBI/CMI_Educacion_Primaria.SemanticModel/definition
  ```
  `herramientas/tmdldump` hace un volcado y una reserialización (round-trip) del modelo.
- **Analizador sintáctico de Power Query M** (`herramientas/mparser`): usa el parser oficial `@microsoft/powerquery-parser`.
  ```bash
  cd trabajo_en_curso/herramientas/mparser && npm ci && node mcheck.js pruebas/ok.m pruebas/bad.m
  ```
  `python trabajo_en_curso/herramientas/validar_m.py` extrae los bloques M del TMDL y los analiza (necesita el `npm ci`
  anterior; `package-lock.json` está versionado y `node_modules/` está en .gitignore).
- **Esquemas JSON de PBIR/PBIP**: `git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/json-schemas`
  y después `git sparse-checkout set fabric/item/report fabric/item/semanticModel fabric/pbip`.
  `validar_pbir.py` los toma de `--schemas` o de la variable `PBIR_SCHEMAS` (p. ej. `PBIR_SCHEMAS=~/json-schemas/fabric`).
- Documentación y ejemplos de PBIR descargados: `referencias_pbir/`.

Los generadores ya no dependen de `/tmp`: `gen_pbir.py` y `gen_modelo.py` usan rutas relativas al repo.

## Cómo retomar con Claude Code

La versión mínima está completa en Linux. El siguiente paso lo tiene que hacer la estudiante: abrir el proyecto en
Power BI Desktop (Windows) siguiendo `Documentation/Docu_Final/Docu_Parcial/04_Guia_de_uso.md` (punto 2 de «Qué falta»).
Con los errores o capturas de esa primera actualización, pídele a Claude Code: «corrige el CMI con estos errores de
Power BI». Las correcciones se hacen en los generadores (`trabajo_en_curso/generadores/`) y se revalidan con las herramientas.
Los scripts de los workflows usados están en `trabajo_en_curso/workflows/` (1 auditoría, 2 construcción interrumpida,
3 reanudación completada).

## Comprobaciones clave (contrato §6)

FactEvaluacion = 1.102.324 filas; FactPuntuacion = 17.728.085 (4.769.851 globales); media de castellano 2017
corregida = 73,51 (oficial 73,4); medias de Cataluña dentro de ±0,2 de los Quaderns d'avaluació 2009–2025.
