// Limpieza de las columnas categóricas de Datos.csv (Avaluació de sisè, rk5x-gny6)
// Power Query (M). Reglas derivadas de validacion/perfilado/perfil_categoricas.py;
// su equivalente en pandas es la función limpiar_categoricas() de ese script, que
// se ejecuta y verifica sobre el fichero completo (sección 8 de la salida).
// Parámetro requerido: RutaDatos (texto) = ruta completa de Datos.csv.
// Las columnas de puntuación se conservan sin tocar (se tratan en otra consulta).
let
    Origen = Csv.Document(
        File.Contents(RutaDatos),
        [Delimiter = ",", Columns = 32, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    ConEncabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),

    // R0 Clave sustituta: línea física del CSV (cabecera = línea 1). CODI_ALUMNE no sirve como clave.
    ConLinea = Table.AddIndexColumn(ConEncabezados, "EvaluacionID", 2, 1, Int64.Type),

    // R0 Csv.Document lee el campo vacío como "": recortar y convertir "" en null.
    ColsCategoricas = {"ANY", "CODI_ALUMNE", "GENERE", "MES_NAIXEMENT", "ANY_NAIXEMENT",
                       "AREA_TERRITORIAL", "NATURALESA", "HÀBITAT"},
    Normalizado = Table.TransformColumns(
        ConLinea,
        List.Transform(
            ColsCategoricas,
            (c) => {c, (v) => let t = if v = null then null else Text.Trim(v) in if t = "" then null else t,
                    type nullable text}
        )
    ),

    // R1 Tipos. CODI_ALUMNE se mantiene como texto (identificador, 6-11 dígitos).
    Tipado = Table.TransformColumnTypes(
        Normalizado,
        {{"ANY", Int64.Type}, {"MES_NAIXEMENT", Int64.Type}, {"ANY_NAIXEMENT", Int64.Type}}
    ),

    // R3 Género: H/Home -> H ; D/Dona -> D (2021 usa Home/Dona).
    GeneroCod = Table.AddColumn(Tipado, "GeneroCod", each
        if List.Contains({"H", "Home"}, [GENERE]) then "H"
        else if List.Contains({"D", "Dona"}, [GENERE]) then "D"
        else null, type nullable text),
    Genero = Table.AddColumn(GeneroCod, "Genero", each
        if [GeneroCod] = "H" then "Niño" else if [GeneroCod] = "D" then "Niña" else "Desconocido", type text),

    // R4 Naturaleza: Públic/Pública -> Pública ; Privat/Privada -> Privada (cambio de etiqueta en 2024).
    Naturaleza = Table.AddColumn(Genero, "Naturaleza", each
        if List.Contains({"Públic", "Pública"}, [NATURALESA]) then "Pública"
        else if List.Contains({"Privat", "Privada"}, [NATURALESA]) then "Privada"
        else "Desconocida", type text),

    // R5 Hábitat a 3 categorías por prefijo; absorbe 'Fins a 10001'..'Fins a 23357' (2024)
    //    y 'Més de 100001' (2024-2025).
    HabitatCod = Table.AddColumn(Naturaleza, "HabitatCod", each
        let h = [#"HÀBITAT"] in
            if h = null then null
            else if Text.StartsWith(h, "Fins a ") then 1
            else if h = "De 10001 a 100000" then 2
            else if Text.StartsWith(h, "Més de ") then 3
            else null, Int64.Type),
    Habitat = Table.AddColumn(HabitatCod, "Habitat", each
        if [HabitatCod] = 1 then "Hasta 10.000 hab."
        else if [HabitatCod] = 2 then "De 10.001 a 100.000 hab."
        else if [HabitatCod] = 3 then "Más de 100.000 hab."
        else "Desconocido", type text),
    FlagHabitatTexto = Table.AddColumn(Habitat, "FlagHabitatTextoAnomalo", each
        [#"HÀBITAT"] <> null and Text.StartsWith([#"HÀBITAT"], "Fins a ") and [#"HÀBITAT"] <> "Fins a 10000",
        type logical),

    // R6 Área: vacío -> "Desconocida" (1 fila en 2024).
    Area = Table.AddColumn(FlagHabitatTexto, "AreaTerritorial", each
        if [AREA_TERRITORIAL] = null then "Desconocida" else [AREA_TERRITORIAL], type text),

    // R5b Coherencia área x hábitat: combinaciones que solo aparecen en 2010 (y 29 filas de 2014).
    CombosIncoherentes = {"Consorci d'Educació de Barcelona|1", "Consorci d'Educació de Barcelona|2",
                          "Catalunya Central|3", "Terres de l'Ebre|3", "Baix Llobregat|3"},
    FlagHabitatIncoh = Table.AddColumn(Area, "FlagHabitatIncoherenteArea", each
        [HabitatCod] <> null and List.Contains(CombosIncoherentes, [AreaTerritorial] & "|" & Text.From([HabitatCod])),
        type logical),
    HabitatFiable = Table.AddColumn(FlagHabitatIncoh, "HabitatFiable", each
        [ANY] <> 2010 and not [FlagHabitatIncoherenteArea], type logical),

    // R6b Ruptura territorial 2024-2025.
    AreaPerimetro = Table.AddColumn(HabitatFiable, "AreaPerimetro2025", each
        if [AREA_TERRITORIAL] = "Barcelona Comarques" and [ANY] = 2024 then "Barcelonès"
        else if [AREA_TERRITORIAL] = "Barcelona Comarques" then "Barcelona Comarques (perímetro hasta 2023)"
        else [AreaTerritorial], type text),
    AreaSerie = Table.AddColumn(AreaPerimetro, "AreaSerieComparable", each
        if List.Contains({"Lleida", "Alt Pirineu i Aran"}, [AREA_TERRITORIAL]) then "Lleida + Alt Pirineu i Aran"
        else if List.Contains({"Barcelona Comarques", "Barcelonès", "Penedès", "Tarragona", "Catalunya Central"},
                              [AREA_TERRITORIAL])
            then "Barcelona Comarques/Barcelonès + Penedès + Tarragona + Catalunya Central"
        else [AreaTerritorial], type text),
    AreaRuptura = Table.AddColumn(AreaSerie, "AreaConRupturaSerie", each
        List.Contains({"Lleida", "Alt Pirineu i Aran", "Barcelona Comarques", "Barcelonès", "Penedès",
                       "Tarragona", "Catalunya Central"}, [AREA_TERRITORIAL]), type logical),

    // R7 Fecha de nacimiento y edad en la prueba.
    Mes = Table.AddColumn(AreaRuptura, "MesNacimiento", each
        if [MES_NAIXEMENT] <> null and [MES_NAIXEMENT] >= 1 and [MES_NAIXEMENT] <= 12
        then [MES_NAIXEMENT] else null, Int64.Type),
    EdadBruta = Table.AddColumn(Mes, "EdadBruta", each
        if [ANY_NAIXEMENT] = null then null else [ANY] - [ANY_NAIXEMENT], Int64.Type),
    FlagEdad = Table.AddColumn(EdadBruta, "FlagEdadFueraRango", each
        [EdadBruta] <> null and ([EdadBruta] < 10 or [EdadBruta] > 14), type logical),
    EdadPrueba = Table.AddColumn(FlagEdad, "EdadPrueba", each
        if [ANY] = 2010 or [EdadBruta] = null or [FlagEdadFueraRango] then null else [EdadBruta], Int64.Type),
    SituacionEdad = Table.AddColumn(EdadPrueba, "SituacionEdad", each
        if [ANY] = 2010 then "No fiable (2010)"
        else if [EdadPrueba] = null then "Desconocida"
        else if [EdadPrueba] < 12 then "Adelantado"
        else if [EdadPrueba] = 12 then "Edad teórica"
        else if [EdadPrueba] = 13 then "Retraso de 1 año"
        else "Retraso de 2 años", type text),

    // R2 CODI_ALUMNE: marca de ausencia, duplicado en el año y aparición en la convocatoria anterior.
    TieneCodigo = Table.AddColumn(SituacionEdad, "TieneCodigo", each [CODI_ALUMNE] <> null, type logical),
    ConCodigo = Table.Buffer(Table.SelectRows(TieneCodigo, each [CODI_ALUMNE] <> null)),
    ConteoCodigo = Table.Group(ConCodigo, {"ANY", "CODI_ALUMNE"},
        {{"FilasMismoAnio", each Table.RowCount(_), Int64.Type}}),
    ConConteo = Table.NestedJoin(TieneCodigo, {"ANY", "CODI_ALUMNE"}, ConteoCodigo, {"ANY", "CODI_ALUMNE"},
        "Conteo", JoinKind.LeftOuter),
    ExpConteo = Table.ExpandTableColumn(ConConteo, "Conteo", {"FilasMismoAnio"}),
    FlagDup = Table.AddColumn(ExpConteo, "FlagCodigoDuplicadoAnio", each
        [FilasMismoAnio] <> null and [FilasMismoAnio] > 1, type logical),
    Anterior = Table.AddColumn(
        Table.Distinct(
            Table.RenameColumns(
                Table.SelectColumns(
                    Table.TransformColumns(ConCodigo, {{"ANY", each _ + 1, Int64.Type}}),
                    {"CODI_ALUMNE", "ANY", "GeneroCod", "ANY_NAIXEMENT", "MesNacimiento"}),
                {{"GeneroCod", "GeneroAnt"}, {"ANY_NAIXEMENT", "AnioNacAnt"}, {"MesNacimiento", "MesNacAnt"}}),
            {"CODI_ALUMNE", "ANY"}),
        "EnAnterior", each true, type logical),
    ConAnterior = Table.NestedJoin(FlagDup, {"CODI_ALUMNE", "ANY"}, Anterior, {"CODI_ALUMNE", "ANY"},
        "Ant", JoinKind.LeftOuter),
    ExpAnterior = Table.ExpandTableColumn(ConAnterior, "Ant", {"GeneroAnt", "AnioNacAnt", "MesNacAnt", "EnAnterior"}),
    FlagAnterior = Table.AddColumn(ExpAnterior, "CodigoEnConvocatoriaAnterior", each [EnAnterior] = true, type logical),
    Repeticion = Table.AddColumn(FlagAnterior, "RepeticionProbable", each
        [CodigoEnConvocatoriaAnterior] and [GeneroAnt] = [GeneroCod]
        and [AnioNacAnt] = [ANY_NAIXEMENT] and [MesNacAnt] = [MesNacimiento], type logical),

    // Salida: se eliminan columnas auxiliares y las categóricas en bruto ya normalizadas.
    SinAuxiliares = Table.RemoveColumns(Repeticion,
        {"FilasMismoAnio", "GeneroAnt", "AnioNacAnt", "MesNacAnt", "EnAnterior",
         "GENERE", "NATURALESA", "HÀBITAT", "AREA_TERRITORIAL", "MES_NAIXEMENT"}),
    Final = Table.RenameColumns(SinAuxiliares,
        {{"ANY", "Anio"}, {"CODI_ALUMNE", "CodiAlumne"}, {"ANY_NAIXEMENT", "AnioNacimiento"}})
in
    Final
