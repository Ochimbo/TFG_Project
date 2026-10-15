let
    // R29: niveles de logro de las puntuaciones globales. Umbrales 55 / 70 / 85 PROVISIONALES,
    // internos del TFG (no son los niveles oficiales). Las subcompetencias van al nivel 0.
    Resultado = #table(
        type table [
            NivelKey = Int64.Type,
            Nivel = text,
            LimiteInferior = number,
            LimiteSuperior = number,
            NivelOrden = Int64.Type
        ],
        {
            {0, "No aplica (subcompetencia)", null, null, 0},
            {1, "Bajo", 0, 55, 1},
            {2, "Medio-bajo", 55, 70, 2},
            {3, "Medio-alto", 70, 85, 3},
            {4, "Alto", 85, 100, 4}
        }
    )
in
    Resultado
