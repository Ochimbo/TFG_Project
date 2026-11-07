"""Crea docx/plantilla.docx, la plantilla de estilos que usa Pandoc para exportar la memoria a Word.

Parte de la plantilla por defecto de Pandoc y ajusta fuentes, márgenes (los mismos que el PDF), títulos, tablas,
leyendas, estilos de la portada, número de página en el pie y actualización del índice al abrir el documento.
Uso: python3 docx/crear_plantilla.py   (solo hace falta volver a ejecutarlo si se cambian los estilos)
"""

import re
import subprocess
import zipfile
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
DESTINO = CARPETA / "plantilla.docx"
FUENTE = "Cambria"

FUENTES = f'<w:rFonts w:ascii="{FUENTE}" w:hAnsi="{FUENTE}" w:eastAsia="{FUENTE}" w:cs="{FUENTE}"/>'


def estilo(id_, nombre, ppr="", rpr="", basado="Normal", siguiente=None, tipo="paragraph", extra=""):
    sig = f'<w:next w:val="{siguiente}"/>' if siguiente else ""
    return (f'<w:style w:type="{tipo}" w:customStyle="1" w:styleId="{id_}"><w:name w:val="{nombre}"/>'
            f'<w:basedOn w:val="{basado}"/>{sig}<w:qFormat/>{extra}<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


def titulo(nivel, tam, antes, despues):
    return (f'<w:style w:type="paragraph" w:styleId="Heading{nivel}"><w:name w:val="heading {nivel}"/>'
            f'<w:basedOn w:val="Normal"/><w:next w:val="BodyText"/><w:uiPriority w:val="9"/><w:qFormat/>'
            f'<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="{antes}" w:after="{despues}"/>'
            f'<w:outlineLvl w:val="{nivel - 1}"/></w:pPr>'
            f'<w:rPr>{FUENTES}<w:b/><w:bCs/><w:color w:val="000000"/><w:sz w:val="{tam}"/><w:szCs w:val="{tam}"/></w:rPr></w:style>')


ESTILOS = {
    "BodyText": ('<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:basedOn w:val="Normal"/>'
                 '<w:qFormat/><w:pPr><w:spacing w:before="0" w:after="140" w:line="300" w:lineRule="auto"/><w:jc w:val="both"/>'
                 '</w:pPr></w:style>'),
    "Compact": ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="Compact"><w:name w:val="Compact"/>'
                '<w:basedOn w:val="BodyText"/><w:qFormat/><w:pPr><w:spacing w:before="20" w:after="20" w:line="264" '
                'w:lineRule="auto"/><w:jc w:val="left"/></w:pPr></w:style>'),
    "Heading1": titulo(1, 32, 0, 280),
    "Heading2": titulo(2, 26, 300, 120),
    "Heading3": titulo(3, 23, 240, 100),
    "Table": ('<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/>'
              '<w:qFormat/><w:rPr><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr><w:tblPr><w:tblInd w:w="0" w:type="dxa"/>'
              '<w:tblBorders><w:top w:val="single" w:sz="10" w:space="0" w:color="000000"/>'
              '<w:bottom w:val="single" w:sz="10" w:space="0" w:color="000000"/>'
              '<w:insideH w:val="single" w:sz="2" w:space="0" w:color="D9D9D9"/></w:tblBorders>'
              '<w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/>'
              '<w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
              '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/></w:rPr><w:tcPr><w:tcBorders>'
              '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/></w:tcBorders><w:vAlign w:val="bottom"/>'
              '</w:tcPr></w:tblStylePr></w:style>'),
    "Caption": ('<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:basedOn w:val="Normal"/>'
                '<w:qFormat/><w:pPr><w:spacing w:before="80" w:after="280"/><w:jc w:val="center"/></w:pPr>'
                '<w:rPr><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr></w:style>'),
    "TableCaption": ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="TableCaption"><w:name w:val="Table Caption"/>'
                     '<w:basedOn w:val="Caption"/></w:style>'),
}

NUEVOS = [
    estilo("PortadaCentro", "Portada Centro", '<w:spacing w:after="0"/><w:jc w:val="center"/>'),
    estilo("PortadaTitulo", "Portada Titulo", '<w:spacing w:before="1600" w:after="900" w:line="300" w:lineRule="auto"/>'
           '<w:jc w:val="center"/><w:pBdr><w:top w:val="single" w:sz="12" w:space="12" w:color="000000"/>'
           '<w:bottom w:val="single" w:sz="12" w:space="12" w:color="000000"/></w:pBdr>',
           '<w:b/><w:bCs/><w:sz w:val="30"/><w:szCs w:val="30"/>'),
    estilo("PortadaSubtitulo", "Portada Subtitulo", '<w:spacing w:after="80"/><w:jc w:val="center"/>',
           '<w:b/><w:sz w:val="26"/><w:szCs w:val="26"/>'),
    estilo("PortadaTexto", "Portada Texto", '<w:spacing w:after="80"/><w:jc w:val="center"/>',
           '<w:sz w:val="24"/><w:szCs w:val="24"/>'),
    estilo("PortadaDatos", "Portada Datos", '<w:spacing w:after="40"/>', '<w:sz w:val="22"/><w:szCs w:val="22"/>'),
    estilo("PortadaEspacio", "Portada Espacio", '<w:spacing w:before="2400" w:after="0"/>'),
    estilo("TOC1", "toc 1", '<w:spacing w:before="120" w:after="20"/>', '<w:b/><w:bCs/>'),
    estilo("TOC2", "toc 2", '<w:spacing w:after="20"/><w:ind w:left="300"/>'),
    estilo("TOC3", "toc 3", '<w:spacing w:after="20"/><w:ind w:left="600"/>', '<w:sz w:val="20"/><w:szCs w:val="20"/>'),
    estilo("IndiceTitulo", "Indice Titulo", '<w:spacing w:after="280"/>',
           f'{FUENTES}<w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/>'),
]

DEFAULTS = (f'<w:docDefaults><w:rPrDefault><w:rPr>{FUENTES}<w:sz w:val="22"/><w:szCs w:val="22"/>'
            '<w:lang w:val="es-ES" w:eastAsia="es-ES" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:after="120"/></w:pPr></w:pPrDefault></w:docDefaults>')

# A4 con los márgenes del PDF (3 cm arriba, abajo e izquierda; 2,5 cm a la derecha) y pie con el número de página
SECCION = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdPie"/><w:pgSz w:w="11906" w:h="16838"/>'
           '<w:pgMar w:top="1701" w:right="1418" w:bottom="1701" w:left="1701" w:header="709" w:footer="709" w:gutter="0"/>'
           '</w:sectPr>')

PIE = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
       'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
       '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:fldChar w:fldCharType="begin"/></w:r>'
       '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
       '<w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')


def reemplazar_estilo(xml, id_, nuevo):
    patron = re.compile(r'<w:style [^>]*w:styleId="' + id_ + r'"[^>]*>.*?</w:style>', re.S)
    assert patron.search(xml), id_
    return patron.sub(lambda _: nuevo, xml, count=1)


def main():
    base = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    origen = CARPETA / "_base.docx"
    origen.write_bytes(base)
    with zipfile.ZipFile(origen) as zin, zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            datos = zin.read(item.filename).decode("utf-8") if item.filename.endswith((".xml", ".rels")) else zin.read(item.filename)
            if item.filename == "word/styles.xml":
                datos = re.sub(r"<w:docDefaults>.*?</w:docDefaults>", DEFAULTS, datos, flags=re.S)
                for id_, xml in ESTILOS.items():
                    datos = reemplazar_estilo(datos, id_, xml)
                datos = datos.replace("</w:styles>", "".join(NUEVOS) + "</w:styles>")
            elif item.filename == "word/document.xml":
                datos = re.sub(r"<w:sectPr\b.*?</w:sectPr>", SECCION, datos, flags=re.S)
            elif item.filename == "word/_rels/document.xml.rels":
                datos = datos.replace("</Relationships>", '<Relationship Id="rIdPie" Type="http://schemas.openxmlformats.org/'
                                      'officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
            elif item.filename == "[Content_Types].xml":
                datos = datos.replace("</Types>", '<Override PartName="/word/footer1.xml" ContentType="application/'
                                      'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
            elif item.filename == "word/settings.xml":
                datos = re.sub(r"(<w:settings\b[^>]*>)", r'\1<w:updateFields w:val="true"/>', datos, count=1)
            zout.writestr(item, datos)
        zout.writestr("word/footer1.xml", PIE)
    origen.unlink()
    print(f"Plantilla creada: {DESTINO}")


if __name__ == "__main__":
    main()
