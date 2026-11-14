"""Copia los comentarios del .docx del Drive (el que comentan las directoras) al .docx recién generado.

El .docx se genera de nuevo en cada compilación y no trae los comentarios. Este script los lee del fichero
descargado del Drive y los ancla en el nuevo, en el párrafo que tiene el mismo texto, para subirlo como nueva
versión del mismo archivo sin perder los hilos.

Uso: python docx/copiar_comentarios.py <docx del Drive> <docx generado> <docx de salida>
     [--renombra "texto antiguo=texto nuevo" ...]   para anclas cuyo título ha cambiado en la memoria.

Cada comentario se ancla en el primer párrafo, fuera del índice, cuyo texto empieza por los primeros caracteres
del primer párrafo que comentaba (sin espacios ni numeración). Si no lo encuentra, lo ancla al título y lo dice.
"""
import argparse
import html
import re
import zipfile
from datetime import datetime, timezone

AUTORA = "Kiara Kristin Rodríguez Uribe"

NS_COMMENTS = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
NS_COMMENTS_EX = "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"
REL_COMMENTS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
REL_COMMENTS_EX = "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"


def texto(xml):
    return html.unescape("".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", xml)))


def clave(s, n=40):
    """Texto normalizado para comparar anclas: sin numeración inicial ni espacios."""
    s = re.sub(r"^[\d.\s]+", "", s)
    return re.sub(r"\s+", "", s)[:n].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drive")
    ap.add_argument("generado")
    ap.add_argument("salida")
    ap.add_argument("--renombra", action="append", default=[])
    ap.add_argument("--nuevo", action="append", default=[],
                    help='comentario nuevo de la estudiante: "texto del párrafo=texto del comentario". '
                         "Solo una vez: después ya viene en el .docx del Drive.")
    a = ap.parse_args()
    renombra = dict(r.split("=", 1) for r in a.renombra)

    zd = zipfile.ZipFile(a.drive)
    comments = zd.read("word/comments.xml").decode("utf-8")
    comments_ex = zd.read("word/commentsExtended.xml").decode("utf-8") if "word/commentsExtended.xml" in zd.namelist() else None
    doc_d = zd.read("word/document.xml").decode("utf-8")

    # Ancla de cada comentario en el .docx del Drive
    ids = re.findall(r'<w:comment [^>]*w:id="(\d+)"', comments)
    anclas = {}
    for cid in ids:
        m = re.search(r'<w:commentRangeStart w:id="%s"/>(.*?)<w:commentRangeEnd w:id="%s"/>' % (cid, cid), doc_d, re.S)
        # Solo el primer párrafo del rango: un comentario sobre «Resumen» abarca el título y el texto
        t = texto(m.group(1).split("</w:p>")[0]) if m else ""
        for viejo, nuevo in renombra.items():
            if viejo in t:
                t = t.replace(viejo, nuevo)
        anclas[cid] = t

    # Comentarios nuevos de la estudiante, con el mismo formato mínimo que los de Google Docs
    siguiente = max((int(i) for i in ids), default=-1) + 1
    for k, nuevo in enumerate(a.nuevo):
        ancla, cuerpo = nuevo.split("=", 1)
        cid = str(siguiente + k)
        para_id = f"{0x7E000000 + int(cid):08X}"
        fecha = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        comments = comments.replace(
            "</w:comments>",
            f'<w:comment w:author="{AUTORA}" w:id="{cid}" w:date="{fecha}" w:initials="KR">'
            f'<w:p w14:paraId="{para_id}"><w:r><w:t xml:space="preserve">{html.escape(cuerpo)}</w:t></w:r></w:p>'
            f"</w:comment></w:comments>")
        if comments_ex:
            comments_ex = comments_ex.replace(
                "</w15:commentsEx>", f'<w15:commentEx w15:paraId="{para_id}" w15:done="0"/></w15:commentsEx>')
        ids.append(cid)
        anclas[cid] = ancla

    zg = zipfile.ZipFile(a.generado)
    doc = zg.read("word/document.xml").decode("utf-8")
    parrafos = list(re.finditer(r"<w:p[ >].*?</w:p>", doc, re.S))
    # Las entradas del índice (estilos TOC1-TOC3) repiten los títulos: no son anclas válidas
    claves_p = ["" if re.search(r'<w:pStyle w:val="TOC\d"', p.group(0)) else clave(texto(p.group(0)))
                for p in parrafos]

    # Párrafo de destino de cada comentario
    destino = {}
    for cid, t in anclas.items():
        k = clave(t, 25)
        idx = next((i for i, kp in enumerate(claves_p) if k and kp.startswith(k)), None)
        if idx is None:
            idx = next(i for i, kp in enumerate(claves_p) if kp)
            print(f"AVISO: comentario {cid} sin ancla ({t[:50]!r}); se ancla al título")
        destino.setdefault(idx, []).append(cid)
        print(f"comentario {cid} -> párrafo {idx}: {texto(parrafos[idx].group(0))[:60]!r}")

    # Insertar marcas, del último párrafo al primero para no mover posiciones
    for idx in sorted(destino, reverse=True):
        p = parrafos[idx]
        xml = p.group(0)
        inicio = "".join(f'<w:commentRangeStart w:id="{c}"/>' for c in destino[idx])
        fin = "".join(f'<w:commentRangeEnd w:id="{c}"/><w:r><w:commentReference w:id="{c}"/></w:r>'
                      for c in destino[idx])
        m = re.match(r"(<w:p[^>]*>(?:<w:pPr>.*?</w:pPr>)?)", xml, re.S)
        nuevo = m.group(1) + inicio + xml[m.end():-len("</w:p>")] + fin + "</w:p>"
        doc = doc[:p.start()] + nuevo + doc[p.end():]

    # Partes del paquete: comentarios, relaciones y tipos de contenido
    rels = zg.read("word/_rels/document.xml.rels").decode("utf-8")
    tipos = zg.read("[Content_Types].xml").decode("utf-8")
    if REL_COMMENTS not in rels:
        rels = rels.replace("</Relationships>",
                            f'<Relationship Id="rIdComentarios" Type="{REL_COMMENTS}" Target="comments.xml"/></Relationships>')
    if comments_ex and REL_COMMENTS_EX not in rels:
        rels = rels.replace("</Relationships>",
                            f'<Relationship Id="rIdComentariosEx" Type="{REL_COMMENTS_EX}" Target="commentsExtended.xml"/></Relationships>')
    if "/word/comments.xml" not in tipos:
        tipos = tipos.replace("</Types>", f'<Override PartName="/word/comments.xml" ContentType="{NS_COMMENTS}"/></Types>')
    if comments_ex and "/word/commentsExtended.xml" not in tipos:
        tipos = tipos.replace("</Types>",
                              f'<Override PartName="/word/commentsExtended.xml" ContentType="{NS_COMMENTS_EX}"/></Types>')

    reemplazos = {"word/document.xml": doc, "word/comments.xml": comments,
                  "word/_rels/document.xml.rels": rels, "[Content_Types].xml": tipos}
    if comments_ex:
        reemplazos["word/commentsExtended.xml"] = comments_ex
    with zipfile.ZipFile(a.salida, "w", zipfile.ZIP_DEFLATED) as zs:
        for item in zg.infolist():
            if item.filename in reemplazos:
                zs.writestr(item, reemplazos.pop(item.filename).encode("utf-8"))
            else:
                zs.writestr(item, zg.read(item.filename))
        for nombre, contenido in reemplazos.items():
            zs.writestr(nombre, contenido.encode("utf-8"))
    print(f"{len(ids)} comentarios copiados en {a.salida}")


if __name__ == "__main__":
    main()
