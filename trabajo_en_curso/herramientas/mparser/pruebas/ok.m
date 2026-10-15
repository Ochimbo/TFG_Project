let
    a = {"0".."9"},
    b = Text.Remove("12,3", a),
    f = (x as nullable text) as nullable number => if x = null then null else Number.FromText(x, "es-ES"),
    t = #table(type table [A = Int64.Type, B = text], {{1, "x"}}),
    #"Paso con espacios" = Table.AddColumn(t, "C", each [A] * 2, Int64.Type),
    e = try 1 otherwise error Error.Record("R", "m", [d = 1])
in
    #"Paso con espacios"
