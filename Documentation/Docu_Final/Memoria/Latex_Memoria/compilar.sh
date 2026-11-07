#!/usr/bin/env bash
# Compila la memoria a PDF (Tectonic) y exporta a la vez la versión .docx (Pandoc) para que las directoras la comenten.
# Uso: ./compilar.sh   (desde cualquier carpeta)
set -euo pipefail

cd "$(dirname "$0")"
NOMBRE="Memoria_TFG_Kiara_Rodriguez_Uribe"
TECTONIC="${TECTONIC:-$(command -v tectonic || echo "$HOME/.local/bin/tectonic")}"

"$TECTONIC" main.tex
mv main.pdf "$NOMBRE.pdf"

# Apartados revisados: Pandoc no entiende el entorno, así que su inicio y su final se sustituyen por marcas que
# docx/memoria.lua convierte en la franja y el fondo verdes (o se eliminan si \mostrarterminados vale 0).
if grep -q '^\\newcommand{\\mostrarterminados}{1}' main.tex; then
    INICIO='\\par MARCATERMINADO\\par'; FIN='\\par FINREVISADO\\par'
else
    INICIO=''; FIN=''
fi

# Pandoc no dibuja TikZ/pgfgantt: el diagrama de Gantt solo aparece en el PDF.
# Tampoco conoce algunos comandos de símbolos ni las columnas @{} dentro de \multicolumn, así que se adaptan antes.
# El aspecto del .docx lo dan docx/plantilla.docx (estilos, márgenes, pie) y docx/memoria.lua (portada, índice,
# saltos de página, numeración de tablas y figuras, ancho de columnas).
sed -e 's/^\\begin{revisado}/'"$INICIO"'/' -e 's/^\\end{revisado}/'"$FIN"'/' -e 's/\\texteuro{}/€/g' -e 's/\\textordmasculine{}/º/g' -e 's/\\textordfeminine{}/ª/g' \
    -e 's/\\guillemotleft{}/«/g' -e 's/\\guillemotright{}/»/g' \
    -e 's/\\textquestiondown{}/¿/g' -e 's/\\textexclamdown{}/¡/g' \
    -e 's/\\multicolumn{\([0-9]*\)}{@{}l}/\\multicolumn{\1}{l}/g' -e 's/\\addlinespace//g' -e 's/m\$\^2\$/m²/g' -e 's/CO\$_2\$/CO₂/g' main.tex \
| pandoc \
    --from=latex \
    --to=docx \
    --citeproc \
    --bibliography=bibliografia.bib \
    --csl=ieee.csl \
    --lua-filter=docx/memoria.lua \
    --reference-doc=docx/plantilla.docx \
    --resource-path=. \
    --number-sections \
    --table-caption-position=below \
    --metadata lang=es-ES \
    --metadata reference-section-title="Bibliografía" \
    -o "$NOMBRE.docx"

echo "Generados: $NOMBRE.pdf y $NOMBRE.docx"
