# Validación del CMI (réplica de referencia en Python)

Réplica independiente de Power BI de la ETL y de las medidas del cuadro de mando. Sirve para
contrastar cifra a cifra el modelo `PowerBI/CMI_Educacion_Primaria.SemanticModel`
(contrato de diseño §2–§7, informe de calidad `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md`,
decisiones posteriores en `trabajo_en_curso/week2/DECISIONES.md`).

## Instalación

```bash
python -m venv .venv && source .venv/bin/activate     # desde la raíz del repositorio (Windows: .venv\Scripts\activate)
pip install -r validacion/requirements.txt
```

Sin entorno virtual (por ejemplo, en Windows con Git Bash): instalar las dependencias en una carpeta aparte
y ejecutar con `PYTHONPATH=<carpeta> PYTHONIOENCODING=utf-8 python ...` (`pip install --target <carpeta> duckdb pyarrow numpy pandas`).

`Datos.csv` debe estar en la raíz del repositorio (solo se lee).

## Orden de ejecución

```bash
python validacion/etl_referencia.py      # 1. ETL -> validacion/salida/*.parquet (unos 10 s)
python validacion/test_modelo.py         # 2. tests de integridad (sale con código 1 si alguno falla)
python validacion/kpis_referencia.py     # 3. KPIs de referencia -> validacion/resultados/*.csv
```

## Qué produce cada script

| Script | Salida |
|---|---|
| `etl_referencia.py` | Las 8 tablas del modelo en estrella (`DimAnio`, `DimContextoCentro`, `DimPerfilAlumno`, `DimCompetencia`, `DimNivelLogro`, `DimCalidadDato`, `FactEvaluacion`, `FactPuntuacion`) en `salida/` (git-ignorada), con las reglas R01–R29 del contrato. |
| `test_modelo.py` | 31 comprobaciones del contrato §6 y de las decisiones D-01, D-05, D-10, D-13 y D-17: recuentos, claves huérfanas, rotaciones R03/R04 (con control negativo sobre el CSV original), códigos sin mapear, área de 2024 («Barcelonès»), rango [0,100], 2020 sin datos, `IndiceConvocatoria`, límites de nivel 55/70/85, distribución por nivel frente a K03, vigencia de las competencias (RI2), periodos de diseño por materia, máscara de `DimCalidadDato` y medias de Cataluña frente a los Quaderns (criterio de aceptación de 0,5 y alerta de 0,2). |
| `kpis_referencia.py` | En `resultados/` (versionada): `kpi_cataluna_por_anio_materia.csv`, `kpi_area_2025.csv`, `kpi_global_por_anio.csv`, `kpi_subcompetencia_2025.csv` (K02 por materia y subcompetencia), `kpi_niveles_2025.csv` (medida `Puntuaciones por nivel de logro` y su % por competencia), `semaforos_2025.csv` y `contraste_oficial.csv`. |

Estado el 12/11/2026: ETL 1.102.324 evaluaciones y 17.728.085 puntuaciones; 31 de 31 tests correctos;
72 de 72 medias dentro de 0,5 puntos de la oficial (máximo 0,30) y 70 de 72 dentro de 0,2.

Notas para leer los CSV:

- Separador coma, punto decimal, 2 decimales. Celda vacía = `BLANK()` en DAX (mínimo muestral
  de 30, convocatoria sin anterior, periodo de diseño no comparable, francés en K09, etc.).
- K03 y K12 están en porcentaje (0–100), como los muestra el formato `0.0%`.
- `Alumnos evaluados` cuenta `FactEvaluacion`, que no se relaciona con `DimCompetencia`: por eso
  vale lo mismo para todas las materias de un año (igual que la medida DAX).
- `semaforos_2025.csv`: la fila `(Cataluña)` no tiene filtro de contexto de centro, así que
  `Estado K01` usa K10 (±0,5); en las áreas usa K07 (±1). Los semáforos figuran como 1, 0 y −1;
  el informe los muestra como «▲ Favorable», «● Neutro» y «▼ Desfavorable» (cadena de formato, D-12).
- `kpi_niveles_2025.csv`: la columna `% del nivel` del tramo Bajo coincide con `K03` por construcción (D-13).
- `contraste_oficial.csv`: `dentro_RNF06` es el criterio de aceptación de la memoria (0,5 puntos) y
  `dentro_tolerancia` la alerta interna de 0,2 (D-01). La columna `estado` vale «dentro de tolerancia»,
  «esperada fuera de tolerancia (informe §4.6)» (inglés 2016 y francés 2024, explicadas en el informe de calidad)
  o «FALLO: fuera de tolerancia sin explicar» (haría fallar `test_modelo.py`).
