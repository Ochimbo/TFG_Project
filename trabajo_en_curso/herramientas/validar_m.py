#!/usr/bin/env python3
"""Extrae el código Power Query (M) de un modelo TMDL y lo valida sintácticamente.

Recorre todos los .tmdl de una carpeta `definition` y extrae a ficheros .m:
  - cada `expression <Nombre> = ...` (parámetros y expresiones compartidas), y
  - cada `partition <Nombre> = m` (el bloque que sigue a `source =`).
Después ejecuta el analizador oficial de M (`mcheck.js`, basado en
@microsoft/powerquery-parser) sobre cada fichero e informa de OK / FAIL.

La extracción sigue las reglas de indentación de TMDL: el cuerpo de una expresión
multilínea son las líneas más indentadas que las propiedades del objeto (o en blanco),
hasta la primera línea no vacía con indentación igual o menor; se quita después la
indentación común. También admite expresiones en una sola línea y bloques delimitados
con ```.

Uso:
    python validar_m.py [carpeta_definition] [--salida CARPETA] [--mcheck RUTA_mcheck.js]

Por defecto: PowerBI/CMI_Educacion_Primaria.SemanticModel/definition, salida en una
carpeta temporal y mcheck.js en trabajo_en_curso/herramientas/mparser (requiere `npm ci`
en esa carpeta). Código de salida 0 si todo el M es sintácticamente correcto.
Solo detecta errores de sintaxis: no comprueba tipos, nombres de columna ni ejecución.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DEF_POR_DEFECTO = RAIZ / "PowerBI" / "CMI_Educacion_Primaria.SemanticModel" / "definition"
MCHECK_POR_DEFECTO = Path(__file__).resolve().parent / "mparser" / "mcheck.js"

RE_EXPRESION = re.compile(r"^(\t*)expression\s+('(?:[^']|'')+'|[^\s=]+)\s*=\s*(.*)$")
RE_PARTICION = re.compile(r"^(\t*)partition\s+('(?:[^']|'')+'|[^\s=]+)\s*=\s*(\w+)\s*$")
RE_SOURCE = re.compile(r"^(\t*)source\s*=\s*(.*)$")


def indentacion(linea: str) -> int:
    """Nivel de indentación TMDL (tabuladores iniciales)."""
    return len(linea) - len(linea.lstrip("\t"))


def nombre_limpio(nombre: str) -> str:
    if nombre.startswith("'") and nombre.endswith("'"):
        nombre = nombre[1:-1].replace("''", "'")
    return nombre


def desindentar(lineas: list[str]) -> str:
    while lineas and not lineas[-1].strip():
        lineas.pop()
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    no_vacias = [ln for ln in lineas if ln.strip()]
    comun = min((indentacion(ln) for ln in no_vacias), default=0)
    return "\n".join(ln[comun:] if ln.strip() else "" for ln in lineas) + "\n"


def leer_cuerpo(lineas: list[str], i: int, en_linea: str, nivel_propiedades: int) -> tuple[str, int]:
    """Devuelve (texto M, índice de la siguiente línea) a partir de la línea i+1.

    `en_linea` es lo que sigue a '=' en la propia línea de cabecera.
    `nivel_propiedades` es la indentación de las propiedades del objeto: el cuerpo
    multilínea va estrictamente más indentado.
    """
    j = i + 1
    if en_linea.strip() == "```":
        cuerpo = []
        while j < len(lineas) and lineas[j].strip() != "```":
            cuerpo.append(lineas[j])
            j += 1
        return desindentar(cuerpo), j + 1
    cuerpo = [en_linea] if en_linea.strip() else []
    while j < len(lineas):
        ln = lineas[j]
        if ln.strip() and indentacion(ln) <= nivel_propiedades:
            break
        cuerpo.append(ln)
        j += 1
    if en_linea.strip() and len(cuerpo) > 1:
        # Expresión que empieza en la línea de cabecera y continúa debajo
        return en_linea.strip() + "\n" + desindentar(cuerpo[1:]), j
    return desindentar(cuerpo), j


def extraer(fichero: Path) -> list[tuple[str, str]]:
    """Lista de (identificador, código M) de un fichero TMDL."""
    lineas = fichero.read_text(encoding="utf-8-sig").splitlines()
    resultado = []
    i = 0
    while i < len(lineas):
        ln = lineas[i]
        m_expr = RE_EXPRESION.match(ln)
        m_part = RE_PARTICION.match(ln)
        if m_expr:
            nivel = len(m_expr.group(1))
            codigo, i = leer_cuerpo(lineas, i, m_expr.group(3), nivel + 1)
            resultado.append((f"expression_{nombre_limpio(m_expr.group(2))}", codigo))
            continue
        if m_part:
            nivel = len(m_part.group(1))
            nombre = nombre_limpio(m_part.group(2))
            tipo = m_part.group(3).lower()
            j = i + 1
            while j < len(lineas) and (not lineas[j].strip() or indentacion(lineas[j]) > nivel):
                m_src = RE_SOURCE.match(lineas[j])
                if m_src and indentacion(lineas[j]) == nivel + 1:
                    if tipo == "m":
                        codigo, j = leer_cuerpo(lineas, j, m_src.group(2), nivel + 1)
                        resultado.append((f"partition_{nombre}", codigo))
                    break
                j += 1
            i += 1
            continue
        i += 1
    return resultado


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("definition", nargs="?", type=Path, default=DEF_POR_DEFECTO)
    ap.add_argument("--salida", type=Path, default=None, help="carpeta para los .m extraídos")
    ap.add_argument("--mcheck", type=Path, default=MCHECK_POR_DEFECTO, help="ruta de mcheck.js")
    args = ap.parse_args(argv)

    if not args.definition.is_dir():
        print(f"No existe la carpeta {args.definition}", file=sys.stderr)
        return 2
    salida = args.salida or Path(tempfile.mkdtemp(prefix="validar_m_"))
    salida.mkdir(parents=True, exist_ok=True)

    ficheros_m = []
    for tmdl in sorted(args.definition.rglob("*.tmdl")):
        for ident, codigo in extraer(tmdl):
            destino = salida / f"{tmdl.stem}__{re.sub(r'[^A-Za-z0-9_]+', '_', ident)}.m"
            destino.write_text(codigo, encoding="utf-8")
            ficheros_m.append(destino)
    print(f"Extraídos {len(ficheros_m)} bloques M en {salida}")
    if not ficheros_m:
        return 1
    if not args.mcheck.exists():
        print(f"No se encuentra {args.mcheck}", file=sys.stderr)
        return 2
    if not (args.mcheck.parent / "node_modules").exists():
        print(f"Falta node_modules: ejecuta `npm ci` en {args.mcheck.parent}", file=sys.stderr)
        return 2
    proceso = subprocess.run(["node", str(args.mcheck), *map(str, ficheros_m)],
                             capture_output=True, text=True)
    print(proceso.stdout, end="")
    if proceso.stderr:
        print(proceso.stderr, end="", file=sys.stderr)
    fallos = sum(1 for ln in proceso.stdout.splitlines() if ln.startswith("FAIL"))
    print(f"Resultado: {len(ficheros_m) - fallos} OK, {fallos} FAIL")
    return 0 if proceso.returncode == 0 and fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
