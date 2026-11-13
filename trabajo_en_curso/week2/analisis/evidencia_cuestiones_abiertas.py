# Evidencia sobre Datos.csv para las decisiones D-05 a D-10 y D-17 (DECISIONES.md).
# Uso (desde la raiz del repo, con duckdb y pandas instalados): python trabajo_en_curso/week2/analisis/evidencia_cuestiones_abiertas.py
# Solo lee Datos.csv. La columna ANY se renombra a ANIO porque ANY es palabra reservada en DuckDB.
import duckdb, sys
con = duckdb.connect()
con.execute("""CREATE TABLE c AS SELECT * RENAME ("ANY" AS ANIO) FROM read_csv('Datos.csv', all_varchar=true, header=true)""")
def q(t, sql):
    print("\n##", t); print(con.execute(sql).df().to_string(index=False))
n = lambda c: f"CAST(replace(\"{c}\", ',', '.') AS DOUBLE)"
q("areas n por año 2022-2025", """SELECT AREA_TERRITORIAL a, sum((ANIO='2022')::int) n22, sum((ANIO='2023')::int) n23, sum((ANIO='2024')::int) n24, sum((ANIO='2025')::int) n25 FROM c WHERE ANIO>='2022' GROUP BY 1 ORDER BY 1""")
q("ciencias: global = media simple vs 42/25/33 (tolerancia 0.01 y 0.115)", f"""SELECT ANIO, count(*) n,
 avg((abs({n('PMED')} - round(({n('PMED_COMP1')}+{n('PMED_COMP2')}+{n('PMED_COMP3')})/3,2))<=0.0101)::int)*100 pct_simple_001,
 avg((abs({n('PMED')} - ({n('PMED_COMP1')}+{n('PMED_COMP2')}+{n('PMED_COMP3')})/3)<=0.115)::int)*100 pct_simple_0115,
 avg((abs({n('PMED')} - (0.42*{n('PMED_COMP1')}+0.25*{n('PMED_COMP2')}+0.33*{n('PMED_COMP3')}))<=0.115)::int)*100 pct_422533,
 avg(abs({n('PMED')} - (0.42*{n('PMED_COMP1')}+0.25*{n('PMED_COMP2')}+0.33*{n('PMED_COMP3')}))) err_medio_422533,
 avg({n('PMED')}) media_pub, avg(0.42*{n('PMED_COMP1')}+0.25*{n('PMED_COMP2')}+0.33*{n('PMED_COMP3')}) media_422533
 FROM c WHERE PMED IS NOT NULL AND PMED_COMP1 IS NOT NULL AND PMED_COMP2 IS NOT NULL AND PMED_COMP3 IS NOT NULL GROUP BY 1 ORDER BY 1""")
q("ciencias otras permutaciones de pesos 42/25/33", f"""SELECT 
 avg((abs({n('PMED')} - (0.42*{n('PMED_COMP1')}+0.33*{n('PMED_COMP2')}+0.25*{n('PMED_COMP3')}))<=0.115)::int)*100 p_42_33_25,
 avg((abs({n('PMED')} - (0.25*{n('PMED_COMP1')}+0.42*{n('PMED_COMP2')}+0.33*{n('PMED_COMP3')}))<=0.115)::int)*100 p_25_42_33,
 avg((abs({n('PMED')} - (0.33*{n('PMED_COMP1')}+0.42*{n('PMED_COMP2')}+0.25*{n('PMED_COMP3')}))<=0.115)::int)*100 p_33_42_25,
 avg((abs({n('PMED')} - (0.33*{n('PMED_COMP1')}+0.25*{n('PMED_COMP2')}+0.42*{n('PMED_COMP3')}))<=0.115)::int)*100 p_33_25_42,
 avg((abs({n('PMED')} - (0.25*{n('PMED_COMP1')}+0.33*{n('PMED_COMP2')}+0.42*{n('PMED_COMP3')}))<=0.115)::int)*100 p_25_33_42
 FROM c WHERE PMED IS NOT NULL AND PMED_COMP1 IS NOT NULL AND PMED_COMP2 IS NOT NULL AND PMED_COMP3 IS NOT NULL""")
q("PANG por año: n, media, sd, min, p01, p99, max, distintos", f"""SELECT ANIO, count(PANG) n, round(avg({n('PANG')}),2) media, round(stddev_pop({n('PANG')}),2) sd, min({n('PANG')}) mn, quantile_cont({n('PANG')},0.01) p01, quantile_cont({n('PANG')},0.99) p99, max({n('PANG')}) mx, count(DISTINCT PANG) dist, round(avg(({n('PANG')}>=95)::int)*100,2) pct95 FROM c WHERE PANG IS NOT NULL GROUP BY 1 ORDER BY 1""")
q("PCAT por año: sd, moda y % en la moda, min", f"""WITH m AS (SELECT ANIO, PCAT, count(*) k FROM c WHERE PCAT IS NOT NULL GROUP BY 1,2), t AS (SELECT ANIO, count(PCAT) n, round(stddev_pop({n('PCAT')}),2) sd, min({n('PCAT')}) mn, round(avg(({n('PCAT')}<55)::int)*100,2) pbajo FROM c WHERE PCAT IS NOT NULL GROUP BY 1)
 SELECT t.*, (SELECT PCAT FROM m WHERE m.ANIO=t.ANIO ORDER BY k DESC LIMIT 1) moda, round((SELECT max(k) FROM m WHERE m.ANIO=t.ANIO)*100.0/n,2) pct_moda FROM t ORDER BY 1""")
q("PCAT 2018: valores mas frecuentes por debajo de 60", """SELECT PCAT, count(*) k FROM c WHERE ANIO='2018' AND CAST(replace(PCAT, ',', '.') AS DOUBLE)<60 GROUP BY 1 ORDER BY k DESC LIMIT 8""")
q("PCAT 2018 y 2019: percentiles bajos", f"""SELECT ANIO, quantile_cont({n('PCAT')},[0.01,0.05,0.10,0.25]) q FROM c WHERE ANIO IN ('2017','2018','2019') AND PCAT IS NOT NULL GROUP BY 1 ORDER BY 1""")
q("Barcelona Comarques 2024 vs Barcelonès 2025: composición", """SELECT ANIO, AREA_TERRITORIAL, left(NATURALESA,4) nat, CASE WHEN "HÀBITAT" LIKE 'Fins a%' THEN 1 WHEN "HÀBITAT" LIKE 'De %' THEN 2 ELSE 3 END hab, count(*) n FROM c WHERE (ANIO='2024' AND AREA_TERRITORIAL='Barcelona Comarques') OR (ANIO='2025' AND AREA_TERRITORIAL='Barcelonès') OR (ANIO='2023' AND AREA_TERRITORIAL='Barcelona Comarques') GROUP BY ALL ORDER BY 2,1,3,4""")
q("puntuaciones fuera de vigencia (RI2): no nulos por columna antes del año de inicio", """SELECT 'PANG<2010' k, count(*) FROM c WHERE ANIO<'2010' AND (PANG IS NOT NULL OR PANG_CO IS NOT NULL OR PANG_CE IS NOT NULL OR PFRAN IS NOT NULL OR PFRAN_CO IS NOT NULL OR PFRAN_CE IS NOT NULL)
 UNION ALL SELECT 'EE ext<2013', count(*) FROM c WHERE ANIO<'2013' AND (PANG_EE IS NOT NULL OR PFRAN_EE IS NOT NULL)
 UNION ALL SELECT 'CO/PMED<2018', count(*) FROM c WHERE ANIO<'2018' AND (PCAT_CO IS NOT NULL OR PCAST_CO IS NOT NULL OR PMED IS NOT NULL OR PMED_COMP1 IS NOT NULL OR PMED_COMP2 IS NOT NULL OR PMED_COMP3 IS NOT NULL)""")
q("formatos con punto o sin patron en puntuaciones (control R02)", """SELECT count(*) FROM c WHERE PCAT LIKE '%.%' OR PMAT LIKE '%.%' OR PANG LIKE '%.%'""")
