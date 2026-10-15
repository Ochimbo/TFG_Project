using System;
using System.Linq;
using Microsoft.AnalysisServices.Tabular;
using Microsoft.AnalysisServices.Tabular.Tmdl;

if (args.Length < 1) { Console.Error.WriteLine("uso: tmdlcheck <carpeta definition>"); return 2; }
try
{
    var db = TmdlSerializer.DeserializeDatabaseFromFolder(args[0]);
    var m = db.Model;
    Console.WriteLine($"OK: database '{db.Name}' compat {db.CompatibilityLevel} culture {m.Culture}");
    foreach (var t in m.Tables)
    {
        Console.WriteLine($"TABLE {t.Name}: cols={t.Columns.Count} measures={t.Measures.Count} partitions={t.Partitions.Count} hidden={t.IsHidden}");
        foreach (var c in t.Columns) Console.WriteLine($"   col {c.Name} [{c.DataType}] {(c is CalculatedColumn ? "calc" : "")}");
        foreach (var me in t.Measures) Console.WriteLine($"   measure {me.Name} folder='{me.DisplayFolder}' fmt='{me.FormatString}'");
        foreach (var p in t.Partitions) Console.WriteLine($"   partition {p.Name} source={p.SourceType} mode={p.Mode}");
    }
    foreach (SingleColumnRelationship r in m.Relationships)
        Console.WriteLine($"REL {r.FromTable.Name}[{r.FromColumn.Name}] -> {r.ToTable.Name}[{r.ToColumn.Name}] {r.FromCardinality}:{r.ToCardinality} {r.CrossFilteringBehavior} active={r.IsActive}");
    foreach (var e in m.Expressions) Console.WriteLine($"EXPR {e.Name} kind={e.Kind}");
    var res = m.Validate();
    var errs = res.Errors.ToList();
    Console.WriteLine($"VALIDATE: {errs.Count} errores");
    foreach (var e in errs) Console.WriteLine($"   ERR {e.Message}");
    return errs.Count == 0 ? 0 : 1;
}
catch (Exception ex)
{
    Console.WriteLine("FALLO: " + ex.GetType().Name + ": " + ex.Message);
    if (ex.InnerException != null) Console.WriteLine("   inner: " + ex.InnerException.Message);
    return 1;
}
