#!/usr/bin/env bash
# Compila la memoria a PDF (Tectonic) y exporta a la vez la versión .docx (Pandoc) para que las directoras la comenten.
# Uso: ./compilar.sh   (desde cualquier carpeta)
set -euo pipefail

cd "$(dirname "$0")"
NOMBRE="Memoria_TFG_Kiara_Rodriguez_Uribe"
TECTONIC="${TECTONIC:-$(command -v tectonic || echo "$HOME/.local/bin/tectonic")}"

"$TECTONIC" main.tex
mv main.pdf "$NOMBRE.pdf"

# Pandoc no dibuja TikZ/pgfgantt: el diagrama de Gantt solo aparece en el PDF.
# Tampoco conoce algunos comandos de símbolos, así que se cambian por el carácter antes de exportar.
sed -e 's/\\texteuro{}/€/g' -e 's/\\textordmasculine{}/º/g' -e 's/\\textordfeminine{}/ª/g' \
    -e 's/\\guillemotleft{}/«/g' -e 's/\\guillemotright{}/»/g' main.tex \
| pandoc \
    --from=latex \
    --to=docx \
    --citeproc \
    --bibliography=bibliografia.bib \
    --csl=ieee.csl \
    --resource-path=. \
    --number-sections \
    --toc \
    --metadata lang=es-ES \
    --metadata toc-title="Índice" \
    -o "$NOMBRE.docx"

echo "Generados: $NOMBRE.pdf y $NOMBRE.docx"
