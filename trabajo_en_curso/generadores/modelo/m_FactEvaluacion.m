let
    Origen = stg_Evaluaciones,
    // Número de competencias globales con puntuación en el registro
    ConCompetencias = Table.AddColumn(
        Origen,
        "CompetenciasEvaluadas",
        each List.Count(List.RemoveNulls({[PCAT], [PCAST], [PMAT], [PANG], [PFRAN], [PMED]})),
        Int64.Type
    ),
    // Una fila por registro (R01). CODI_ALUMNE no se carga: solo TieneCodigoAlumno.
    Resultado = Table.SelectColumns(
        ConCompetencias,
        {"EvaluacionID", "AnioKey", "ContextoKey", "PerfilKey", "TieneCodigoAlumno", "CompetenciasEvaluadas"}
    )
in
    Resultado
