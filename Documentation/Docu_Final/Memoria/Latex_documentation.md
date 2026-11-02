# Documentación — Compilar LaTeX en local

Los documentos LaTeX de este proyecto se compilan con **Tectonic**, un compilador ligero (~30 MB) instalado en `~/.local/bin/tectonic`. Descarga automáticamente solo los paquetes que necesita cada documento y los guarda en caché (`~/.cache/Tectonic`). Por eso la primera compilación necesita Internet y las siguientes funcionan sin conexión.

Comprobar la instalación:

```bash
tectonic --version
```

## Compilar un documento

Desde la carpeta que contiene el `main.tex`:

```bash
cd Documentation/GEP/GEP4/Latex_GEP4
tectonic main.tex
```

- Genera `main.pdf` en la misma carpeta.
- Hace solo todas las pasadas necesarias (índice, referencias cruzadas y bibliografía con BibTeX).
- No deja ficheros auxiliares (`.aux`, `.log`, `.bbl`…).

Opciones útiles:

```bash
tectonic --keep-logs main.tex           # guarda main.log para depurar errores
tectonic --keep-intermediates main.tex  # conserva .aux, .bbl, etc.
```

## Exportar el PDF

Tectonic siempre genera `main.pdf`. Para entregarlo con el nombre habitual, cópialo a la carpeta del entregable:

```bash
cp main.pdf ../GEP4_Kiara_Rodriguez_Uribe.pdf
```

O genéralo directamente en otra carpeta con `-o`:

```bash
tectonic -o .. main.tex   # deja main.pdf en la carpeta superior
```

## Crear un documento nuevo

1. Crea una carpeta con la misma estructura que los GEP:

   ```bash
   mkdir -p Documentation/NuevoDoc/imagenes
   cd Documentation/NuevoDoc
   cp ../GEP/GEP4/Latex_GEP4/imagenes/logo_*.png imagenes/
   ```

2. Crea `main.tex` con una plantilla mínima:

   ```latex
   \documentclass[12pt, a4paper]{report}
   \usepackage[utf8]{inputenc}
   \usepackage[T1]{fontenc}
   \usepackage{lmodern}
   \usepackage{textcomp}
   \usepackage[spanish, es-tabla]{babel}
   \usepackage{graphicx}
   \usepackage{hyperref}
   \usepackage{cite}

   \title{Título del documento}
   \author{Kiara Kristin Rodríguez Uribe}
   \date{\today}

   \begin{document}
   \maketitle
   \tableofcontents

   \chapter{Introducción}
   Texto con una cita \cite{ejemplo}.

   \bibliographystyle{IEEEtran}
   \bibliography{bibliografia}
   \end{document}
   ```

3. Crea `bibliografia.bib` con las referencias:

   ```bibtex
   @book{ejemplo,
     author    = {Apellido, Nombre},
     title     = {Título del libro},
     publisher = {Editorial},
     year      = {2026}
   }
   ```

4. Compila con `tectonic main.tex`.

> Para empezar con el mismo formato que los entregables (portada, márgenes, encabezados, tablas), copia `GEP/GEP4/Latex_GEP4/main.tex` y borra el contenido de los capítulos.

## Consejos

- **Símbolo €:** escríbelo como `\texteuro{}`. El carácter `€` pegado directamente no se muestra con Tectonic.
- **Errores:** si la compilación falla, el mensaje indica la línea (`main.tex:123`). Usa `--keep-logs` para ver el detalle en `main.log`.
- **Overleaf:** los mismos `.tex` y `.bib` compilan también en Overleaf sin cambios.

## Desinstalar

```bash
rm ~/.local/bin/tectonic
rm -rf ~/.cache/Tectonic
```
