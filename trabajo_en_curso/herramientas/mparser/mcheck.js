// Uso: node mcheck.js fichero.m [...]  -> analiza sintácticamente expresiones M
const PQP = require("@microsoft/powerquery-parser");
const fs = require("fs");
(async () => {
  let fallos = 0;
  for (const f of process.argv.slice(2)) {
    const text = fs.readFileSync(f, "utf8");
    const task = await PQP.TaskUtils.tryLexParse(PQP.DefaultSettings, text);
    if (PQP.TaskUtils.isOk(task)) {
      console.log("OK   " + f);
    } else {
      fallos++;
      const err = task.error;
      let msg = err && err.message ? err.message : String(err);
      let pos = "";
      try { const inner = err.innerError; if (inner && inner.foundToken) pos = JSON.stringify(inner.foundToken.token.positionStart); else if (inner && inner.graphemePosition) pos = JSON.stringify(inner.graphemePosition);} catch(e) {}
      console.log("FAIL " + f + ": " + msg + " " + pos);
    }
  }
  process.exit(fallos ? 1 : 0);
})();
