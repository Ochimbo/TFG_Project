let
    // R25-R28: máscara de 4 bits {bit, descripción}. CalidadKey 0..15 = suma de los bits activos.
    // 1 NoValida (R25), 2 Censurada (R26), 4 NoComparableSerie (R27), 8 NivelNoComparable (R28).
    Bits = {{1, "No válida"}, {2, "Censurada"}, {4, "No comparable en la serie"}, {8, "Nivel no comparable"}},
    Filas = List.Transform(
        {0..15},
        (clave) => {
            clave,
            Number.BitwiseAnd(clave, 1) <> 0,
            Number.BitwiseAnd(clave, 2) <> 0,
            Number.BitwiseAnd(clave, 4) <> 0,
            Number.BitwiseAnd(clave, 8) <> 0,
            if clave = 0 then "Válido"
            else Text.Combine(
                List.Transform(List.Select(Bits, (bit) => Number.BitwiseAnd(clave, bit{0}) <> 0), (bit) => bit{1}),
                "; "
            )
        }
    ),
    Resultado = #table(
        type table [
            CalidadKey = Int64.Type,
            NoValida = logical,
            Censurada = logical,
            NoComparableSerie = logical,
            NivelNoComparable = logical,
            DescripcionCalidad = text
        ],
        Filas
    )
in
    Resultado
