# Progreso del agente de diseño (capítulo 8, issues #11 y #13)

Fuente: `DECISIONES.md` (sección «Nombres» y «Datos para el capítulo 8»). Reglas: `GUIA_AGENTES.md`.
Solo se edita el capítulo 8 de `main.tex` (y `bibliografia.bib` si hace falta). Sin commits.

## Pasos

- [x] 1. Figura del esquema en estrella: `trabajo_en_curso/generadores/gen_esquema_estrella.py` →
      `Latex_Memoria/imagenes/diseno/esquema_estrella.png` (8 tablas, claves, 9 relaciones con cardinalidad).
- [x] 2. Introducción del capítulo y 8.1 (intro, 8.1.1 con tabla de correspondencia, figura y RI1–RI7).
- [x] 3. 8.1.2 Tablas de hechos, 8.1.3 Dimensiones (Barcelonès D-05, Girona D-06), 8.1.4 Diccionario (D-15).
- [x] 4. 8.2 Diseño de la ETL: 8.2.1 flujo, 8.2.2 reglas (D-03, D-07).
- [x] 5. 8.3 Lógica analítica: 8.3.1 fichas (longtable, DAX de 2–3 medidas; D-09, D-10, D-16), 8.3.2 semáforos (D-08, D-12, D-01).
- [x] 6. 8.4 Interfaz: 8.4.1 estructura común, 8.4.2 paneles y cambios respecto al prototipo.
- [x] 7. 8.5 Organización del repositorio.
- [x] 8. Repaso de estilo (13/11/2026, sesión principal tras cortarse el agente por el límite de uso): sin expresiones vetadas; cinco frases de más de 40 palabras partidas (8.1, 8.3.2, 8.4.1 y 8.5).
- [x] 9. Compilación sin errores (PDF de 91 páginas; capítulo 8 en las pp. 62-83). Revisadas las figuras y las páginas del capítulo; el .docx contiene las tablas 8.1-8.7, las cinco figuras y el DAX. Letra de las figuras de los paneles ampliada (`gen_paneles_diseno.py`), con los cuadros de texto dibujados debajo y el texto que no cabe recortado. PDF y .docx copiados al repositorio.

## Comprobaciones

- Compilación en copia temporal (13/11/2026): sin errores ni referencias sin definir; tres avisos Overfull de menos de 4 pt.
