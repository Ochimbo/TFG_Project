# Progreso del agente de especificación (issues #12, #10 y #9)

Quien retome: leer también `DECISIONES.md` (sección «Nombres» y D-E01 a D-E05) y comprobar el estado real de los ficheros.

## Issue #12: títulos de los capítulos 7 y 8

- [x] Estructura, títulos, labels y comentarios guía del capítulo 8 en `main.tex`.
- [x] 7.2 y 7.3: «modelo dimensional» e «interfaz» en lugar de «modelo en estrella» y «presentación».
- [x] `gen_arquitectura.py` (rótulos y ruta de Lato) y `arquitectura.png` regenerado.
- [x] Glosario y lista de títulos en «Nombres» de `DECISIONES.md`; D-E01.

## Issue #10: fichas Volere

- [x] Nuevo 7.4 «Especificación de los requisitos no funcionales» con 11 fichas (`tab:rnf01`–`tab:rnf11`).
- [x] 3.4.3: columna «Criterio de aceptación» y remisión al 7.4; introducción del capítulo 7.
- [x] `bibliografia.bib`: `robertson2012mastering` (comprobada en la web).
- [x] D-E02 y D-E03.
- [x] Paginación revisada el 11/11/2026: la primera ficha fija ([H]) y las demás flotantes ([!htbp]) con FloatBarrier antes del 7.5; tres fichas por página sin huecos. El .docx sale bien.

## Issue #9: OCL

- [x] Nuevo 7.2.1 «Restricciones de integridad»: tabla con RI4 precisada y RI7 nueva; RI2, RI3 y RI5 en OCL (`verbatim`).
- [x] `gen_modelo_conceptual.py` (`valor: Real`, ruta de Lato) y `modelo_conceptual.png` regenerado.
- [x] `bibliografia.bib`: `omg_ocl24` (comprobada en omg.org).
- [x] D-E04 y D-E05.
- [x] OCL revisado el 11/11/2026: tildes y «ñ» correctas, sin desbordes. Se añadió espacio vertical (2ex / 2,5ex) alrededor de cada bloque, que salía pegado al texto.

## Comprobaciones

- [x] Compilación en una copia fuera del repo (`compilar.sh`, Tectonic + Pandoc): sin errores, PDF de 73 páginas y .docx generados.
- [x] Revisión visual del PDF (7.2.1, 7.3, 7.4, capítulo 8) y del .docx hecha el 11/11/2026. PDF de 71 páginas. PDF y .docx regenerados y copiados al repositorio.
