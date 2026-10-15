let
    // Años con datos, tal como quedan en stg_Evaluaciones (Anio = entero de ANY)
    AniosConDatos = List.Sort(List.Distinct(Table.Column(stg_Evaluaciones, "Anio"))),
    UltimoAnio = List.Max(AniosConDatos),
    // Notas de las convocatorias especiales (2020 no tuvo prueba por la COVID-19)
    Notas = [
        #"2020" = "Sin prueba por la COVID-19",
        #"2021" = "Primera convocatoria tras la COVID-19 (se compara con 2019)"
    ],
    // Una fila por año de 2009 al último con datos, 2020 incluido. IndiceConvocatoria numera
    // 1..N solo los años con prueba: las comparaciones temporales usan este índice, no Anio - 1.
    Filas = List.Transform(
        {2009..UltimoAnio},
        (anio) =>
            let
                Posicion = List.PositionOf(AniosConDatos, anio),
                TieneDatos = Posicion >= 0
            in
                {
                    anio,
                    anio,
                    Text.From(anio - 1) & "-" & Text.From(anio),
                    TieneDatos,
                    if TieneDatos then Posicion + 1 else null,
                    anio = UltimoAnio,
                    Record.FieldOrDefault(Notas, Text.From(anio), "")
                }
    ),
    Resultado = #table(
        type table [
            AnioKey = Int64.Type,
            Anio = Int64.Type,
            Curso = text,
            TieneConvocatoria = logical,
            IndiceConvocatoria = Int64.Type,
            EsUltimaConvocatoria = logical,
            NotaConvocatoria = text
        ],
        Filas
    )
in
    Resultado
