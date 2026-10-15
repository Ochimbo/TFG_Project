let
    // R09: {GeneroCodigo, Genero}
    Generos = {{1, "Niña"}, {2, "Niño"}},
    // R21: {SituacionEdadCodigo, SituacionEdad, SituacionEdadOrden}; orden de presentación 4, 1, 2, 3, 8, 9
    Situaciones = {
        {4, "Adelantado", 1},
        {1, "Edad teórica (12 años)", 2},
        {2, "Retraso de 1 año", 3},
        {3, "Retraso de 2 años", 4},
        {8, "No fiable (2010)", 5},
        {9, "Desconocida", 6}
    },
    // R16-R19, R21: combinaciones válidas {EdadAnioNatural (0 = sin edad), SituacionEdadCodigo}
    Combinaciones = {{10, 4}, {11, 4}, {12, 1}, {13, 2}, {14, 3}, {0, 8}, {0, 9}},
    // 2 géneros x 7 combinaciones x 13 meses (0 = no informado) = 182 filas. PerfilKey usa la
    // misma fórmula que stg_Evaluaciones: Genero * 100000 + Situacion * 10000 + Edad * 100 + Mes.
    Filas = List.Combine(
        List.Transform(
            Generos,
            (genero) => List.Combine(
                List.Transform(
                    Combinaciones,
                    (combinacion) =>
                        let
                            Situacion = List.First(List.Select(Situaciones, (s) => s{0} = combinacion{1}))
                        in
                            List.Transform(
                                {0..12},
                                (mes) => {
                                    genero{0} * 100000 + combinacion{1} * 10000 + combinacion{0} * 100 + mes,
                                    genero{1},
                                    genero{0},
                                    if combinacion{0} = 0 then null else combinacion{0},
                                    Situacion{1},
                                    Situacion{0},
                                    Situacion{2},
                                    if mes = 0 then null else mes,
                                    if mes = 0 then "No informado" else "T" & Text.From(Number.IntegerDivide(mes - 1, 3) + 1)
                                }
                            )
                )
            )
        )
    ),
    Resultado = #table(
        type table [
            PerfilKey = Int64.Type,
            Genero = text,
            GeneroCodigo = Int64.Type,
            EdadAnioNatural = Int64.Type,
            SituacionEdad = text,
            SituacionEdadCodigo = Int64.Type,
            SituacionEdadOrden = Int64.Type,
            MesNacimiento = Int64.Type,
            TrimestreNacimiento = text
        ],
        Filas
    )
in
    Resultado
