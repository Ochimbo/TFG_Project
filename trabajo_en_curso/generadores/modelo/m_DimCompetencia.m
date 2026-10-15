let
    // Tabla de códigos §5.2: las 24 columnas de puntuación de Datos.csv. CompetenciaKey es la
    // misma que asigna FactPuntuacion. AnioFin = null: competencia vigente. EsInformativa: francés
    // (muestra pequeña, solo informativo). PeriodoDisenoInicio: primer año del diseño actual de la prueba.
    // SubcompetenciaOrden es global por texto (0 Global, 1 CL, 2 CO, 3 EE, 4-6 matemáticas, 7-9 ciencias):
    // un único valor por texto de Subcompetencia, para poder usarlo como su sortByColumn.
    Resultado = #table(
        type table [
            CompetenciaKey = Int64.Type,
            CampoOrigen = text,
            CodigoMateria = text,
            Materia = text,
            MateriaOrden = Int64.Type,
            Subcompetencia = text,
            SubcompetenciaOrden = Int64.Type,
            EsGlobal = logical,
            AnioInicio = Int64.Type,
            AnioFin = Int64.Type,
            PeriodoDisenoInicio = Int64.Type,
            EsInformativa = logical
        ],
        {
            {1, "PCAT", "PCAT", "Lengua catalana", 1, "Global", 0, true, 2009, null, 2018, false},
            {2, "PCAT_CL", "PCAT", "Lengua catalana", 1, "Comprensión lectora", 1, false, 2009, null, 2018, false},
            {3, "PCAT_EE", "PCAT", "Lengua catalana", 1, "Expresión escrita", 3, false, 2009, null, 2018, false},
            {4, "PCAT_CO", "PCAT", "Lengua catalana", 1, "Comprensión oral", 2, false, 2018, null, 2018, false},
            {5, "PCAST", "PCAST", "Lengua castellana", 2, "Global", 0, true, 2009, null, 2018, false},
            {6, "PCAST_CL", "PCAST", "Lengua castellana", 2, "Comprensión lectora", 1, false, 2009, null, 2018, false},
            {7, "PCAST_EE", "PCAST", "Lengua castellana", 2, "Expresión escrita", 3, false, 2009, null, 2018, false},
            {8, "PCAST_CO", "PCAST", "Lengua castellana", 2, "Comprensión oral", 2, false, 2018, null, 2018, false},
            {9, "PMAT", "PMAT", "Matemáticas", 3, "Global", 0, true, 2009, null, 2017, false},
            {10, "PMAT_NC", "PMAT", "Matemáticas", 3, "Numeración y cálculo", 4, false, 2009, null, 2017, false},
            {11, "PMAT_EFM", "PMAT", "Matemáticas", 3, "Espacio, medida y datos", 5, false, 2009, null, 2017, false},
            {12, "PMAT_CR", "PMAT", "Matemáticas", 3, "Relaciones y cambio", 6, false, 2009, null, 2017, false},
            {13, "PANG", "PANG", "Lengua inglesa", 4, "Global", 0, true, 2010, null, 2016, false},
            {14, "PANG_CO", "PANG", "Lengua inglesa", 4, "Comprensión oral", 2, false, 2010, null, 2017, false},
            {15, "PANG_CE", "PANG", "Lengua inglesa", 4, "Comprensión lectora", 1, false, 2010, null, 2017, false},
            {16, "PANG_EE", "PANG", "Lengua inglesa", 4, "Expresión escrita", 3, false, 2013, null, 2017, false},
            {17, "PFRAN", "PFRAN", "Lengua francesa", 5, "Global", 0, true, 2010, null, 2016, true},
            {18, "PFRAN_CO", "PFRAN", "Lengua francesa", 5, "Comprensión oral", 2, false, 2010, null, 2017, true},
            {19, "PFRAN_CE", "PFRAN", "Lengua francesa", 5, "Comprensión lectora", 1, false, 2010, null, 2017, true},
            {20, "PFRAN_EE", "PFRAN", "Lengua francesa", 5, "Expresión escrita", 3, false, 2013, null, 2017, true},
            {21, "PMED", "PMED", "Ciencias", 6, "Global", 0, true, 2018, null, 2018, false},
            {22, "PMED_COMP1", "PMED", "Ciencias", 6, "Explicar fenómenos naturales y tecnológicos", 7, false, 2018, null, 2018, false},
            {23, "PMED_COMP2", "PMED", "Ciencias", 6, "Reconocer la investigación científica", 8, false, 2018, null, 2018, false},
            {24, "PMED_COMP3", "PMED", "Ciencias", 6, "Interpretar datos y pruebas científicas", 9, false, 2018, null, 2018, false}
        }
    )
in
    Resultado
