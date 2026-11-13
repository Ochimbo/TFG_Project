let
    // §5.1 Áreas: {AreaCodigo, AreaTerritorial, AreaPerimetro2025, AreaSerieComparable,
    // AreaConRupturaSerie, RupturaHabitat2024}. R13: 99 = área vacía. R14: el código 3 es
    // "Barcelona Comarques" hasta 2023; el código 4 es el área que el CSV llama "Barcelona Comarques"
    // en 2024, que tiene el perímetro del Barcelonès y se muestra con ese nombre, el del informe
    // oficial de 2024 (DECISIONES.md, D-05). Así "Barcelonès" cubre 2024 y 2025 con un perímetro único.
    Areas = {
        {1, "Alt Pirineu i Aran", "Alt Pirineu i Aran", "Lleida + Alt Pirineu i Aran", true, false},
        {2, "Baix Llobregat", "Baix Llobregat", "Baix Llobregat", false, false},
        {3, "Barcelona Comarques", "Barcelona Comarques (perímetro hasta 2023)", "Barcelonès-Penedès y áreas afectadas", true, false},
        {4, "Barcelonès", "Barcelonès", "Barcelonès-Penedès y áreas afectadas", true, false},
        {5, "Barcelonès", "Barcelonès", "Barcelonès-Penedès y áreas afectadas", true, false},
        {6, "Catalunya Central", "Catalunya Central", "Barcelonès-Penedès y áreas afectadas", true, false},
        {7, "Consorci d'Educació de Barcelona", "Consorci d'Educació de Barcelona", "Consorci d'Educació de Barcelona", false, false},
        {8, "Girona", "Girona", "Girona", false, true},
        {9, "Lleida", "Lleida", "Lleida + Alt Pirineu i Aran", true, false},
        {10, "Maresme - Vallès Oriental", "Maresme - Vallès Oriental", "Maresme - Vallès Oriental", false, true},
        {11, "Penedès", "Penedès", "Barcelonès-Penedès y áreas afectadas", true, false},
        {12, "Tarragona", "Tarragona", "Barcelonès-Penedès y áreas afectadas", true, false},
        {13, "Terres de l'Ebre", "Terres de l'Ebre", "Terres de l'Ebre", false, false},
        {14, "Vallès Occidental", "Vallès Occidental", "Vallès Occidental", false, false},
        {99, "Desconocida", "Desconocida", "Desconocida", false, false}
    },
    // R10: {NaturalezaCodigo, Naturaleza}; "Privada" incluye la concertada
    Naturalezas = {{1, "Pública"}, {2, "Privada"}},
    // R11 y R12: {HabitatCodigo, Habitat}; 0 = no fiable (2010 y bloque incoherente de 2014)
    Habitats = {{0, "No fiable"}, {1, "Hasta 10.000 hab."}, {2, "De 10.001 a 100.000 hab."}, {3, "Más de 100.000 hab."}},
    // Producto cartesiano 15 x 2 x 4 = 120 filas. ContextoKey usa la misma fórmula que
    // stg_Evaluaciones: AreaCodigo * 100 + NaturalezaCodigo * 10 + HabitatCodigo. AreaOrden = AreaCodigo,
    // salvo el código 4, que toma el orden 5: así cada texto de AreaTerritorial ("Barcelonès" en los
    // códigos 4 y 5) tiene un único valor de orden y AreaOrden puede ser su sortByColumn.
    Filas = List.Combine(
        List.Transform(
            Areas,
            (area) => List.Combine(
                List.Transform(
                    Naturalezas,
                    (naturaleza) => List.Transform(
                        Habitats,
                        (habitat) => {
                            area{0} * 100 + naturaleza{0} * 10 + habitat{0},
                            area{0},
                            area{1},
                            area{2},
                            area{3},
                            area{4},
                            area{5},
                            naturaleza{1},
                            naturaleza{0},
                            habitat{1},
                            habitat{0},
                            if area{0} = 4 then 5 else area{0}
                        }
                    )
                )
            )
        )
    ),
    Resultado = #table(
        type table [
            ContextoKey = Int64.Type,
            AreaCodigo = Int64.Type,
            AreaTerritorial = text,
            AreaPerimetro2025 = text,
            AreaSerieComparable = text,
            AreaConRupturaSerie = logical,
            RupturaHabitat2024 = logical,
            Naturaleza = text,
            NaturalezaCodigo = Int64.Type,
            Habitat = text,
            HabitatCodigo = Int64.Type,
            AreaOrden = Int64.Type
        ],
        Filas
    )
in
    Resultado
