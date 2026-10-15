using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using Microsoft.AnalysisServices.Tabular;
using Microsoft.AnalysisServices.Tabular.Tmdl;

var db = TmdlSerializer.DeserializeDatabaseFromFolder(args[0]);
var t = db.Model.Tables["_Medidas"];
var list = t.Measures.Select(m => new { name = m.Name, folder = m.DisplayFolder, fmt = m.FormatString, desc = m.Description, expr = m.Expression, tag = m.LineageTag }).ToList();
File.WriteAllText(args[1], System.Text.Json.JsonSerializer.Serialize(new { table = t.Name, tableTag = t.LineageTag, cols = t.Columns.Select(c => new { c.Name, c.IsHidden, c.LineageTag }).ToList(), part = ((MPartitionSource)t.Partitions[0].Source).Expression, measures = list }, new JsonSerializerOptions { WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping }));
if (args.Length > 2) { if (Directory.Exists(args[2])) Directory.Delete(args[2], true); TmdlSerializer.SerializeDatabaseToFolder(db, args[2]); }
Console.WriteLine($"dump OK: {list.Count} medidas");
