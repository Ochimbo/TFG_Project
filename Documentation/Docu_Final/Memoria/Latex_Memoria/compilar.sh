#!/usr/bin/env bash
# Compila la memoria a PDF (Tectonic) y exporta a la vez la versión .docx (Pandoc) para que las directoras la comenten.
# Uso: ./compilar.sh   (desde cualquier carpeta)
#      DRIVE_DOCX=<.docx descargado del Drive> ./compilar.sh
#        genera además Memoria_..._Drive.docx con los comentarios de las directoras copiados del Drive, para subirlo
#        como nueva versión del mismo archivo (Gestionar versiones) sin perder los hilos. Si un título comentado ha
#        cambiado, pasar DRIVE_RENOMBRA="texto antiguo=texto nuevo"; para añadir un comentario propio,
#        DRIVE_NUEVO="texto del párrafo=comentario".
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

if [ -n "${DRIVE_DOCX:-}" ]; then
    # En Windows, «python3» puede ser el acceso directo vacío de la Microsoft Store: se usa el primero que funcione
    PY=""
    for c in python3 python; do
        if command -v "$c" >/dev/null && "$c" -c "" 2>/dev/null; then PY="$c"; break; fi
    done
    [ -n "$PY" ] || { echo "No se encuentra Python para copiar los comentarios del Drive" >&2; exit 1; }
    ARGS=()
    [ -n "${DRIVE_RENOMBRA:-}" ] && ARGS+=(--renombra "$DRIVE_RENOMBRA")
    # DRIVE_NUEVO="texto del párrafo=comentario": añade un comentario nuevo de la estudiante (una sola vez)
    [ -n "${DRIVE_NUEVO:-}" ] && ARGS+=(--nuevo "$DRIVE_NUEVO")
    "$PY" -I -X utf8 docx/copiar_comentarios.py "$DRIVE_DOCX" "$NOMBRE.docx" "${NOMBRE}_Drive.docx" "${ARGS[@]}"
fi
