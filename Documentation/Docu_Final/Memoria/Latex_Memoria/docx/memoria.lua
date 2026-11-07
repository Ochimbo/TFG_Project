-- Filtro de Pandoc para exportar la memoria a .docx con un aspecto parecido al PDF.
-- Rehace la portada, inserta el índice tras los resúmenes, añade saltos de página antes de cada capítulo,
-- numera tablas y figuras por capítulo (Tabla 3.2), reparte el ancho de las columnas según su contenido
-- y convierte las marcas de apartado terminado en una franja verde.

local capitulo = 0
local n_tabla, n_figura = 0, 0
local indice_puesto = false

local function salto_pagina()
  return pandoc.RawBlock("openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
end

local function con_estilo(estilo, inlines)
  return pandoc.Div({ pandoc.Para(inlines) }, { ["custom-style"] = estilo })
end

local entradas = {}

local function escapar(texto)
  return (texto:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

-- El índice es un campo TOC de Word con las entradas ya escritas: Word añade los números de página al
-- actualizarlo y Google Docs, que no actualiza campos, muestra igualmente la lista de apartados.
local function indice()
  local partes = {}
  for i, e in ipairs(entradas) do
    local inicio, fin = "", ""
    if i == 1 then
      inicio = '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        .. '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
        .. '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    end
    if i == #entradas then fin = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' end
    table.insert(partes, string.format('<w:p><w:pPr><w:pStyle w:val="TOC%d"/></w:pPr>%s<w:r><w:t xml:space="preserve">%s</w:t></w:r>%s</w:p>',
      e.nivel, inicio, escapar(e.texto), fin))
  end
  return {
    con_estilo("IndiceTitulo", { pandoc.Str("Índice") }),
    pandoc.RawBlock("openxml", table.concat(partes)),
  }
end

-- Primera pasada: lista de apartados con la misma numeración que aplica --number-sections
local function recoger(doc)
  local c = { 0, 0, 0 }
  local empezado = false
  doc:walk({
    Header = function(h)
      if h.level > 3 then return nil end
      local titulo = pandoc.utils.stringify(h.content)
      if h.classes:includes("unnumbered") then
        if empezado and h.level == 1 then table.insert(entradas, { nivel = 1, texto = titulo }) end
        return nil
      end
      empezado = true
      c[h.level] = c[h.level] + 1
      for k = h.level + 1, 3 do c[k] = 0 end
      local numero = tostring(c[1])
      for k = 2, h.level do numero = numero .. "." .. c[k] end
      table.insert(entradas, { nivel = h.level, texto = numero .. "   " .. titulo })
    end,
  })
end

-- Divide una lista de inlines por los saltos de línea y devuelve el texto de cada trozo no vacío
local function lineas(inlines)
  local resultado, actual = {}, {}
  local function cerrar()
    local texto = pandoc.utils.stringify(actual):gsub("^%s+", ""):gsub("%s+$", "")
    if texto ~= "" then table.insert(resultado, texto) end
    actual = {}
  end
  for _, el in ipairs(inlines) do
    if el.t == "LineBreak" then cerrar() else table.insert(actual, el) end
  end
  cerrar()
  return resultado
end

local function portada(div)
  local bloques, textos, datos = {}, {}, {}
  div:walk({
    Para = function(p)
      local tiene_imagen = false
      for _, el in ipairs(p.content) do
        if el.t == "Image" then tiene_imagen = true end
      end
      if tiene_imagen then
        local imagenes = {}
        for _, el in ipairs(p.content) do
          if el.t == "Image" then
            table.insert(imagenes, el)
            table.insert(imagenes, pandoc.Space())
            table.insert(imagenes, pandoc.Space())
          end
        end
        table.insert(bloques, con_estilo("PortadaCentro", imagenes))
      end
    end,
  })
  for _, bloque in ipairs(div.content) do
    if bloque.t == "Div" and bloque.classes:includes("center") then
      for _, interior in ipairs(bloque.content) do
        if interior.t == "Para" then
          for _, linea in ipairs(lineas(interior.content)) do table.insert(textos, linea) end
        end
      end
    end
  end
  div:walk({
    Table = function(tbl)
      for _, cuerpo in ipairs(tbl.bodies) do
        for _, fila in ipairs(cuerpo.body) do
          local etiqueta = pandoc.utils.stringify(fila.cells[1].contents)
          local valor = pandoc.utils.stringify(fila.cells[2].contents)
          table.insert(datos, { etiqueta, valor })
        end
      end
    end,
  })
  if #textos > 0 then
    table.insert(bloques, con_estilo("PortadaTitulo", { pandoc.Str(textos[1]) }))
    for i = 2, #textos do
      local estilo = (i <= 3) and "PortadaSubtitulo" or "PortadaTexto"
      table.insert(bloques, con_estilo(estilo, { pandoc.Str(textos[i]) }))
    end
  end
  table.insert(bloques, con_estilo("PortadaEspacio", { pandoc.Str("") }))
  for _, par in ipairs(datos) do
    table.insert(bloques, con_estilo("PortadaDatos", { pandoc.Strong(pandoc.Str(par[1])), pandoc.Space(), pandoc.Str(par[2]) }))
  end
  return bloques
end

local function anteponer(caption_blocks, prefijo)
  if #caption_blocks == 0 then return caption_blocks end
  local primero = caption_blocks[1]
  if primero.content then
    table.insert(primero.content, 1, pandoc.Space())
    table.insert(primero.content, 1, pandoc.Strong(pandoc.Str(prefijo)))
  end
  return caption_blocks
end

local function anchos(tbl)
  local n = #tbl.colspecs
  local puntos = {}
  for i = 1, n do puntos[i] = 4 end
  local function medir(fila)
    local col = 1
    for _, celda in ipairs(fila.cells) do
      if celda.col_span == 1 and col <= n then
        local texto = pandoc.utils.stringify(celda.contents)
        local palabra = 0
        for p in texto:gmatch("%S+") do palabra = math.max(palabra, utf8.len(p) or #p) end
        local largo = math.max(palabra + 2, math.min(utf8.len(texto) or #texto, 70) * 0.5)
        if largo > puntos[col] then puntos[col] = largo end
      end
      col = col + celda.col_span
    end
  end
  for _, fila in ipairs(tbl.head.rows) do medir(fila) end
  for _, cuerpo in ipairs(tbl.bodies) do
    for _, fila in ipairs(cuerpo.body) do medir(fila) end
  end
  local total = 0
  for i = 1, n do total = total + puntos[i] end
  for i = 1, n do
    tbl.colspecs[i] = { pandoc.AlignLeft, puntos[i] / total }
  end
end

local principal = {
  traverse = "topdown",
  Para = function(p)
    if pandoc.utils.stringify(p) == "MARCATERMINADO" then
      return con_estilo("Terminado", { pandoc.Str("✓"), pandoc.Space(), pandoc.Strong(pandoc.Str("Apartado terminado:")),
        pandoc.Space(), pandoc.Str("no hace falta revisarlo.") })
    end
  end,
  Div = function(div)
    if div.classes:includes("titlepage") then
      return portada(div), false
    end
  end,
  Header = function(h)
    if h.level ~= 1 then return nil end
    local bloques = { salto_pagina() }
    if not h.classes:includes("unnumbered") then
      if not indice_puesto then
        for _, b in ipairs(indice()) do table.insert(bloques, b) end
        table.insert(bloques, salto_pagina())
        indice_puesto = true
      end
      capitulo = capitulo + 1
      n_tabla, n_figura = 0, 0
    end
    table.insert(bloques, h)
    return bloques
  end,
  Table = function(tbl)
    anchos(tbl)
    if #tbl.caption.long > 0 then
      n_tabla = n_tabla + 1
      tbl.caption.long = anteponer(tbl.caption.long, string.format("Tabla %d.%d.", capitulo, n_tabla))
    end
    return tbl
  end,
  Figure = function(fig)
    if #fig.caption.long > 0 then
      n_figura = n_figura + 1
      fig.caption.long = anteponer(fig.caption.long, string.format("Figura %d.%d.", capitulo, n_figura))
    end
    return fig
  end,
}

return { { Pandoc = function(doc) recoger(doc) end }, principal }
