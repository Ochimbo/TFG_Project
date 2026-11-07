#!/usr/bin/env bash
# Compila la memoria a PDF (Tectonic) y exporta a la vez la versión .docx (Pandoc) para que las directoras la comenten.
# Uso: ./compilar.sh   (desde cualquier carpeta)
set -euo pipefail

cd "$(dirname "$0")"
NOMBRE="Memoria_TFG_Kiara_Rodriguez_Uribe"
TECTONIC="${TECTONIC:-$(command -v tectonic || echo "$HOME/.local/bin/tectonic")}"

"$TECTONIC" main.tex
mv main.pdf "$NOMBRE.pdf"

# Marcas de apartados terminados: Pandoc no entiende la macro, así que se sustituye por una marca que
# docx/memoria.lua convierte en la franja verde (o se elimina si \mostrarterminados vale 0).
if grep -q '^\\newcommand{\\mostrarterminados}{1}' main.tex; then MARCA='\\par MARCATERMINADO\\par'; else MARCA=''; fi

# Pandoc no dibuja TikZ/pgfgantt: el diagrama de Gantt solo aparece en el PDF.
# Tampoco conoce algunos comandos de símbolos ni las columnas @{} dentro de \multicolumn, así que se adaptan antes.
# El aspecto del .docx lo dan docx/plantilla.docx (estilos, márgenes, pie) y docx/memoria.lua (portada, índice,
# saltos de página, numeración de tablas y figuras, ancho de columnas).
sed -e '/^\\newcommand/!s/\\terminado\b/'"$MARCA"'/g' -e 's/\\texteuro{}/€/g' -e 's/\\textordmasculine{}/º/g' -e 's/\\textordfeminine{}/ª/g' \
    -e 's/\\guillemotleft{}/«/g' -e 's/\\guillemotright{}/»/g' \
    -e 's/\\textquestiondown{}/¿/g' -e 's/\\textexclamdown{}/¡/g' \
    -e 's/\\multicolumn{\([0-9]*\)}{@{}l}/\\multicolumn{\1}{l}/g' -e 's/\\addlinespace//g' main.tex \
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
