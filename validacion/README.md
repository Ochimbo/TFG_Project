# Validación del CMI (réplica de referencia en Python)

Réplica independiente de Power BI de la ETL y de las medidas del cuadro de mando. Sirve para
contrastar cifra a cifra el modelo `PowerBI/CMI_Educacion_Primaria.SemanticModel`
(contrato de diseño §2–§7, informe de calidad `Documentation/Docu_Final/Docu_Parcial/01_Informe_calidad_datos.md`).

## Instalación

```bash
python -m venv .venv && source .venv/bin/activate     # desde la raíz del repositorio
pip install -r validacion/requirements.txt
```

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
| `test_modelo.py` | Comprobaciones del contrato §6: recuentos, claves huérfanas, rotaciones R03/R04 (con control negativo sobre el CSV original), códigos sin mapear, rango [0,100], 2020 sin datos, `IndiceConvocatoria`, límites de nivel 55/70/85, máscara de `DimCalidadDato` y medias de Cataluña frente a los Quaderns (±0,2). |
| `kpis_referencia.py` | En `resultados/` (versionada): `kpi_cataluna_por_anio_materia.csv`, `kpi_area_2025.csv`, `kpi_global_por_anio.csv`, `kpi_subcompetencia_2025.csv` (K02 por materia y subcompetencia), `semaforos_2025.csv` y `contraste_oficial.csv`. |

Notas para leer los CSV:

- Separador coma, punto decimal, 2 decimales. Celda vacía = `BLANK()` en DAX (mínimo muestral
  de 30, convocatoria sin anterior, periodo de diseño no comparable, francés en K09, etc.).
- K03 y K12 están en porcentaje (0–100), como los muestra el formato `0.0%`.
- `Alumnos evaluados` cuenta `FactEvaluacion`, que no se relaciona con `DimCompetencia`: por eso
  vale lo mismo para todas las materias de un año (igual que la medida DAX).
- `semaforos_2025.csv`: la fila `(Cataluña)` no tiene filtro de contexto de centro, así que
  `Estado K01` usa K10 (±0,5); en las áreas usa K07 (±1).
- `contraste_oficial.csv`, columna `estado`: dentro de tolerancia, esperada fuera de tolerancia
  (excepción del informe §4.6) o pendiente de documentar en §4.6.
