const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (o, n, tag) => {
  const i = s.indexOf(o);
  if (i === -1) { miss.push(tag); return; }
  if (s.indexOf(o, i + 1) !== -1) { miss.push(tag + " (NOT UNIQUE)"); return; }
  s = s.replace(o, n); ok++;
};

rep('.mrow .mv b{color:#fff;font-weight:600}',
  '.mrow .mv b{color:#fff;font-weight:600}.mrow .mv .seg{display:block;margin-top:7px}.mrow .mv .seg:first-child{margin-top:0}',
  "css-seg");

rep('<span class="mv"><b>Adopt the Unified Problem ID',
  '<span class="mv"><span class="seg"><b>Adopt the Unified Problem ID',
  "seg1-open");

rep('to a fresh UUID when absent (schema default). Plus coalescing on',
  'to a fresh UUID when absent (schema default).</span><span class="seg">Plus coalescing on',
  "seg2");

rep('prose pointer at a prior ticket (15133). Both are page planks',
  'prose pointer at a prior ticket (15133).</span><span class="seg">Both are page planks',
  "seg3");

rep('as open — resolution pending API review.</span></div>',
  'as open — resolution pending API review.</span></span></div>',
  "seg3-close");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
