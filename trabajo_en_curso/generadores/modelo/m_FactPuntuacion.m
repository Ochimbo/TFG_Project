let
    // Registro estático CampoOrigen -> CompetenciaKey (§5.2): búsqueda directa, sin combinar consultas
    ClaveCompetencia = [
        PCAT = 1, PCAT_CL = 2, PCAT_EE = 3, PCAT_CO = 4,
        PCAST = 5, PCAST_CL = 6, PCAST_EE = 7, PCAST_CO = 8,
        PMAT = 9, PMAT_NC = 10, PMAT_EFM = 11, PMAT_CR = 12,
        PANG = 13, PANG_CO = 14, PANG_CE = 15, PANG_EE = 16,
        PFRAN = 17, PFRAN_CO = 18, PFRAN_CE = 19, PFRAN_EE = 20,
        PMED = 21, PMED_COMP1 = 22, PMED_COMP2 = 23, PMED_COMP3 = 24
    ],
    CamposPuntuacion = Record.FieldNames(ClaveCompetencia),
    CamposGlobales = {"PCAT", "PCAST", "PMAT", "PANG", "PFRAN", "PMED"},
    // Reglas de calidad por (CampoOrigen, Anio): {bit, columnas, años}
    ReglasCalidad = {
        // R25 NoValida: expresión escrita de inglés 2015 (escala anómala)
        {1, {"PANG_EE"}, {2015}},
        // R26 Censurada: suelo artificial en toda la columna-año
        {2, {"PCAT_EE"}, {2018}},
        {2, {"PANG", "PANG_CO", "PANG_CE"}, {2015}},
        // R27 NoComparableSerie: escalas distintas del resto de la serie
        {4, {"PANG_CO", "PCAT_CL"}, {2011}},
        {4, {"PANG_EE"}, {2013, 2014, 2015, 2016}},
        {4, {"PANG_CO", "PANG_CE"}, {2015, 2016}},
        {4, {"PMAT_NC", "PMAT_EFM", "PMAT_CR"}, {2015}},
        // R28 NivelNoComparable (solo globales): el % por nivel de logro no es comparable
        {8, {"PANG"}, {2015, 2016}},
        {8, {"PMAT"}, {2015, 2019}},
        {8, {"PCAT"}, {2018}},
        {8, {"PFRAN"}, {2022}}
    },
    // Las reglas se expanden una sola vez a un registro "CAMPO|AÑO" -> máscara (OR de bits)
    ParesCalidad = List.Combine(
        List.Transform(
            ReglasCalidad,
            (regla) => List.Combine(
                List.Transform(
                    regla{1},
                    (campo) => List.Transform(regla{2}, (anio) => {campo & "|" & Text.From(anio), regla{0}})
                )
            )
        )
    ),
    MapaCalidad = List.Accumulate(
        ParesCalidad,
        [],
        (mapa, par) =>
            if Record.HasFields(mapa, par{0})
            then Record.TransformFields(mapa, {{par{0}, (bits) => Number.BitwiseOr(bits, par{1})}})
            else Record.AddField(mapa, par{0}, par{1})
    ),
    Origen = Table.SelectColumns(stg_Evaluaciones, {"AnioKey", "ContextoKey", "PerfilKey"} & CamposPuntuacion),
    // R33: despivotado de las 24 columnas; Table.UnpivotOtherColumns descarta las puntuaciones nulas
    Despivotado = Table.UnpivotOtherColumns(Origen, {"AnioKey", "ContextoKey", "PerfilKey"}, "CampoOrigen", "Puntuacion"),
    // Decimal fijo (Currency.Type, 4 decimales): las puntuaciones tienen 2 decimales exactos
    Tipado = Table.TransformColumnTypes(Despivotado, {{"CampoOrigen", type text}, {"Puntuacion", Currency.Type}}),
    ConCompetencia = Table.AddColumn(Tipado, "CompetenciaKey", each Record.Field(ClaveCompetencia, [CampoOrigen]), Int64.Type),
    // R29: nivel de logro solo para las globales (<55 -> 1; [55,70) -> 2; [70,85) -> 3; >=85 -> 4);
    // las subcompetencias -> 0 "No aplica"
    ConNivel = Table.AddColumn(
        ConCompetencia,
        "NivelKey",
        each
            if not List.Contains(CamposGlobales, [CampoOrigen]) then 0
            else if [Puntuacion] < 55 then 1
            else if [Puntuacion] < 70 then 2
            else if [Puntuacion] < 85 then 3
            else 4,
        Int64.Type
    ),
    // R25-R28: CalidadKey = máscara de la pareja (CampoOrigen, Anio); 0 = "Válido"
    ConCalidad = Table.AddColumn(
        ConNivel,
        "CalidadKey",
        each Record.FieldOrDefault(MapaCalidad, [CampoOrigen] & "|" & Text.From([AnioKey]), 0),
        Int64.Type
    ),
    Resultado = Table.SelectColumns(
        ConCalidad,
        {"AnioKey", "ContextoKey", "PerfilKey", "CompetenciaKey", "NivelKey", "CalidadKey", "Puntuacion"}
    )
in
    Resultado
