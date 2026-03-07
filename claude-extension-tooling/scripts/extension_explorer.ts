#!/usr/bin/env npx tsx

/**
 * extension_explorer — Interactive modal AST explorer for Chrome extensions.
 *
 * Usage:
 *   npx tsx extension_explorer.ts ~/ClaudeChromeExtension/latest
 *
 * Modes (vim-style):
 *   NAV mode    — single keypresses navigate results
 *   SEARCH mode — type a pattern, Enter to search
 *   INPUT mode  — type rewrite/command text, Enter to execute
 */

import { spawnSync } from "child_process";
import { readFileSync, writeFileSync, mkdirSync, statSync, realpathSync } from "fs";
import { relative, join } from "path";

// ─── ANSI ──────────────────────────────────────────────────────────────────────

const isColor = process.stdout.isTTY && !process.env.NO_COLOR;
const c = {
  reset:   isColor ? "\x1b[0m" : "",
  bold:    isColor ? "\x1b[1m" : "",
  dim:     isColor ? "\x1b[2m" : "",
  red:     isColor ? "\x1b[31m" : "",
  green:   isColor ? "\x1b[32m" : "",
  yellow:  isColor ? "\x1b[1;33m" : "",
  cyan:    isColor ? "\x1b[36m" : "",
  magenta: isColor ? "\x1b[35m" : "",
  inv:     isColor ? "\x1b[7m" : "",
};

const CLR_LINE = "\x1b[2K\r";

function write(s: string) { process.stdout.write(s); }

// ─── Types ─────────────────────────────────────────────────────────────────────

interface SgMatch {
  text: string;
  range: {
    byteOffset: { start: number; end: number };
    start: { line: number; column: number };
    end: { line: number; column: number };
  };
  file: string;
  lines: string;
  replacement?: string;
}

interface MatchView {
  match: SgMatch;
  fileContent: Buffer;
  relPath: string;
}

type Mode = "nav" | "search" | "rewrite" | "command";

// ─── State ─────────────────────────────────────────────────────────────────────
//
// Invariants (must hold after every user action):
//   1. matches.length === 0  =>  currentIdx === 0
//   2. matches.length > 0    =>  0 <= currentIdx < matches.length
//   3. lastPattern === ""    =>  rewrite/save/apply are no-ops
//   4. After :apply, matches are re-searched so byte offsets stay valid
//   5. mode transitions: {search,rewrite,command} → nav (submit/esc),
//                         nav → {search,rewrite,command} (keypress)
//

let targetDir = "";
let lang = "js";
let contextChars = 80;
let lastPattern = "";
let lastRewrite = "";
let matches: MatchView[] = [];
let currentIdx = 0;
const rulesDir = process.env.RULES_DIR || join(
  process.env.XDG_CONFIG_HOME || join(process.env.HOME!, ".config"),
  "extension_transformer",
  "rules"
);

// Enforce invariants 1+2: all match mutations go through here
function setMatches(next: MatchView[], idx = 0) {
  matches = next;
  currentIdx = next.length === 0 ? 0 : Math.min(Math.max(0, idx), next.length - 1);
}

let mode: Mode = "search";
let inputBuf = "";

// Per-mode history so search/rewrite/command don't pollute each other
const inputHistory: Record<Mode, string[]> = {
  nav: [], search: [], rewrite: [], command: [],
};
let historyIdx = -1;

function currentHistory(): string[] {
  return inputHistory[mode];
}

// ─── File cache ────────────────────────────────────────────────────────────────

const fileCache = new Map<string, Buffer>();
function readFileCached(path: string): Buffer {
  if (!fileCache.has(path)) {
    try {
      fileCache.set(path, readFileSync(path));
    } catch {
      fileCache.set(path, Buffer.alloc(0));
    }
  }
  return fileCache.get(path)!;
}

// ─── ast-grep wrapper ──────────────────────────────────────────────────────────

// sg (tree-sitter) hangs on very large single-line minified files.
// Per-file timeout keeps the UI responsive; we warn about skipped files.
const SG_PER_FILE_TIMEOUT = 10_000; // 10s per file
const SG_MAX_FILE_SIZE = 500_000;   // 500KB — skip files larger than this
let skippedFiles: string[] = [];

function runSg(args: string[]): SgMatch[] {
  const result = spawnSync("sg", args, {
    encoding: "utf-8",
    maxBuffer: 50 * 1024 * 1024,
    timeout: SG_PER_FILE_TIMEOUT,
  });
  if (result.signal === "SIGTERM") return [];
  const out = (result.stdout || "").trim();
  if (!out) return [];
  try { return JSON.parse(out); } catch { return []; }
}

function findJsFiles(dir: string): string[] {
  const result = spawnSync("find", [dir, "-type", "f", "-name", "*.js"], {
    encoding: "utf-8",
    timeout: 5000,
  });
  return (result.stdout || "").trim().split("\n").filter(Boolean);
}

// Returns true if pattern is a literal identifier (no AST wildcards)
function isLiteralPattern(pattern: string): boolean {
  return /^[a-zA-Z_$][a-zA-Z0-9_$.]*$/.test(pattern);
}

// Grep-based fallback for files too large for tree-sitter.
// Produces SgMatch-shaped results using byte offsets from grep -bo.
function grepFallback(pattern: string, file: string): SgMatch[] {
  if (!isLiteralPattern(pattern)) return []; // Can't grep AST patterns
  const result = spawnSync("grep", ["-bo", pattern, file], {
    encoding: "utf-8",
    timeout: 5000,
  });
  const out = (result.stdout || "").trim();
  if (!out) return [];
  const content = readFileCached(file);
  return out.split("\n").filter(Boolean).map((line) => {
    const sep = line.indexOf(":");
    const byteStart = parseInt(line.slice(0, sep), 10);
    const byteEnd = byteStart + Buffer.byteLength(pattern, "utf-8");
    // Compute line/col from byte offset
    const before = content.subarray(0, byteStart).toString("utf-8");
    const lastNl = before.lastIndexOf("\n");
    const lineNum = (before.match(/\n/g) || []).length;
    const col = lastNl === -1 ? byteStart : byteStart - Buffer.byteLength(before.slice(0, lastNl + 1), "utf-8");
    return {
      text: pattern,
      range: {
        byteOffset: { start: byteStart, end: byteEnd },
        start: { line: lineNum, column: col },
        end: { line: lineNum, column: col + pattern.length },
      },
      file,
      lines: pattern,
    };
  });
}

function doSearch(pattern: string, rewrite?: string): MatchView[] {
  const files = findJsFiles(targetDir);
  const all: MatchView[] = [];
  skippedFiles = [];
  const sgFoundIn = new Set<string>(); // files where sg found matches

  for (const file of files) {
    let isLarge = false;
    try {
      const size = statSync(file).size;
      if (size > SG_MAX_FILE_SIZE) isLarge = true;
    } catch { continue; }

    if (isLarge) {
      skippedFiles.push(relative(targetDir, file));
    }

    if (!isLarge) {
      const args = ["run", "--pattern", pattern, "--lang", lang, "--json"];
      if (rewrite) args.push("--rewrite", rewrite);
      args.push(file);

      const sgMatches = runSg(args);
      if (sgMatches.length > 0) sgFoundIn.add(file);
      for (const m of sgMatches) {
        all.push({
          match: m,
          fileContent: readFileCached(m.file),
          relPath: relative(targetDir, m.file),
        });
      }
    }
  }

  // Grep fallback: for literal patterns, search files where sg found nothing
  // (catches property_identifier vs identifier mismatches + large files)
  if (isLiteralPattern(pattern) && !rewrite) {
    for (const file of files) {
      if (sgFoundIn.has(file)) continue; // sg already covered this file
      for (const m of grepFallback(pattern, file)) {
        all.push({
          match: m,
          fileContent: readFileCached(m.file),
          relPath: relative(targetDir, m.file),
        });
      }
    }
  }

  return all;
}

// ─── Display ───────────────────────────────────────────────────────────────────

function extractContext(view: MatchView, chars: number) {
  const { fileContent, match } = view;
  const { start, end } = match.range.byteOffset;
  const cs = Math.max(0, start - chars);
  const ce = Math.min(fileContent.length, end + chars);
  return {
    before: fileContent.subarray(cs, start).toString("utf-8").replace(/\n/g, "↵"),
    after:  fileContent.subarray(end, ce).toString("utf-8").replace(/\n/g, "↵"),
    hasMore: [cs > 0, ce < fileContent.length] as [boolean, boolean],
  };
}

function showMatch(view: MatchView, idx: number, total: number) {
  const { match, relPath } = view;
  const { before, after, hasMore } = extractContext(view, contextChars);
  const line = match.range.start.line + 1;
  const col = match.range.start.column + 1;
  const el = hasMore[0] ? "…" : "";
  const er = hasMore[1] ? "…" : "";

  console.log();
  console.log(
    `${c.cyan}${relPath}${c.reset} ${c.dim}:${line}:${col}${c.reset}  ${c.dim}[${idx + 1}/${total}]${c.reset}`
  );
  console.log();

  if (match.replacement !== undefined) {
    console.log(`  ${c.dim}${el}${before}${c.reset}${c.red}${match.text}${c.reset}${c.dim}${after}${er}${c.reset}`);
    console.log(`  ${c.dim}${el}${before}${c.reset}${c.green}${match.replacement}${c.reset}${c.dim}${after}${er}${c.reset}`);
  } else {
    console.log(`  ${c.dim}${el}${before}${c.reset}${c.yellow}${match.text}${c.reset}${c.dim}${after}${er}${c.reset}`);
  }
  console.log();
}

function showAllMatches() {
  if (skippedFiles.length > 0) {
    console.log(`${c.dim}Large files (>${Math.round(SG_MAX_FILE_SIZE / 1024)}KB) — grep fallback, no AST:${c.reset}`);
    for (const f of skippedFiles.slice(0, 5)) console.log(`  ${c.dim}${f}${c.reset}`);
    if (skippedFiles.length > 5) console.log(`  ${c.dim}… and ${skippedFiles.length - 5} more${c.reset}`);
  }
  if (matches.length === 0) {
    console.log(`${c.dim}No matches.${c.reset}`);
    return;
  }
  const byFile = new Map<string, number>();
  for (const m of matches) byFile.set(m.relPath, (byFile.get(m.relPath) || 0) + 1);
  console.log(`\n${c.bold}${matches.length} match${matches.length !== 1 ? "es" : ""}${c.reset} in ${byFile.size} file${byFile.size !== 1 ? "s" : ""}:`);
  for (const [file, count] of byFile) console.log(`  ${c.cyan}${file}${c.reset} ${c.dim}(${count})${c.reset}`);
  showMatch(matches[currentIdx], currentIdx, matches.length);
}

function showCurrent() {
  if (matches.length > 0) showMatch(matches[currentIdx], currentIdx, matches.length);
}

// ─── AST navigation ───────────────────────────────────────────────────────────

function showEnclosingScope() {
  if (matches.length === 0) { console.log(`${c.dim}No match selected.${c.reset}`); return; }
  const view = matches[currentIdx];
  const byteStart = view.match.range.byteOffset.start;
  const byteEnd = view.match.range.byteOffset.end;

  const scopePatterns = [
    "function $NAME($$$) { $$$ }",
    "async function $NAME($$$) { $$$ }",
    "($$$) => { $$$ }",
    "async ($$$) => { $$$ }",
    "$NAME($$$) { $$$ }",
    "static $NAME($$$) { $$$ }",
    "static async $NAME($$$) { $$$ }",
    "class $NAME { $$$ }",
  ];

  console.log(`\n${c.bold}Enclosing scope${c.reset}`);
  for (const pattern of scopePatterns) {
    const sm = runSg(["run", "--pattern", pattern, "--lang", lang, "--json", view.match.file]);
    let best: SgMatch | null = null;
    for (const s of sm) {
      const ss = s.range.byteOffset.start, se = s.range.byteOffset.end;
      if (ss <= byteStart && se >= byteEnd && ss !== byteStart) {
        if (!best || (se - ss) < (best.range.byteOffset.end - best.range.byteOffset.start)) best = s;
      }
    }
    if (best) {
      const txt = best.text.length > 400 ? best.text.slice(0, 400) + "…" : best.text;
      const hl = txt.replace(view.match.text, `${c.yellow}${view.match.text}${c.reset}${c.dim}`);
      console.log(`  ${c.magenta}${pattern}${c.reset}`);
      console.log(`  ${c.dim}${hl}${c.reset}\n`);
      return;
    }
  }
  console.log(`  ${c.dim}No enclosing scope found. Try${c.reset} ${c.cyan}w${c.reset} ${c.dim}to widen context.${c.reset}\n`);
}

function showCallers() {
  if (matches.length === 0) { console.log(`${c.dim}No match selected.${c.reset}`); return; }
  const text = matches[currentIdx].match.text;
  const ids = text.match(/[a-zA-Z_$][a-zA-Z0-9_$]*/g) || [];
  const noise = new Set(["this","const","let","var","if","else","return","await","async","new","function","class","static","try","catch","finally","throw","typeof","instanceof","true","false","null","undefined","void","delete","in","of","for","while","do","switch","case","break","continue","default","export","import","from","get","set","Map","Set","Array","Object","Date","Math","JSON","console","log","Error","Promise"]);
  const meaningful = ids.filter((id) => !noise.has(id) && id.length > 1);
  if (!meaningful.length) { console.log(`${c.dim}No identifiers to search.${c.reset}`); return; }

  const symbol = meaningful[meaningful.length - 1];
  console.log(`\n${c.bold}References to: ${c.cyan}${symbol}${c.reset}`);

  const refs: MatchView[] = [];
  const seen = new Set<string>();
  for (const pat of [`this.${symbol}`, `$_.${symbol}`, symbol]) {
    for (const r of doSearch(pat)) {
      const key = `${r.match.file}:${r.match.range.byteOffset.start}`;
      if (!seen.has(key)) { seen.add(key); refs.push(r); }
    }
  }

  if (!refs.length) { console.log(`  ${c.dim}No references found.${c.reset}`); return; }
  for (const ref of refs.slice(0, 15)) {
    const ctx = extractContext(ref, 60);
    const el = ctx.hasMore[0] ? "…" : "", er = ctx.hasMore[1] ? "…" : "";
    console.log(`  ${c.cyan}${ref.relPath}${c.reset} ${c.dim}:${ref.match.range.start.line + 1}:${ref.match.range.start.column + 1}${c.reset}`);
    console.log(`    ${c.dim}${el}${ctx.before}${c.reset}${c.yellow}${ref.match.text}${c.reset}${c.dim}${ctx.after}${er}${c.reset}`);
  }
  if (refs.length > 15) console.log(`  ${c.dim}… and ${refs.length - 15} more${c.reset}`);
  console.log(`\n${c.dim}${refs.length} total${c.reset}`);
}

function yamlQuote(s: string): string {
  // If it contains chars that YAML would interpret, use block scalar
  if (/[:{}\[\]#&*!|>'"@`,%]/.test(s) || s.includes("\n")) return `|-\n  ${s.replace(/\n/g, "\n  ")}`;
  return s;
}

function saveRule(name: string) {
  if (!lastPattern) { console.log(`${c.red}No pattern to save.${c.reset}`); return; }
  mkdirSync(rulesDir, { recursive: true });
  const safeName = name.replace(/[^a-zA-Z0-9_-]/g, "-");
  const fp = join(rulesDir, safeName + ".yml");
  let yaml = `id: ${safeName}\nlanguage: JavaScript\nrule:\n  pattern: ${yamlQuote(lastPattern)}\n`;
  if (lastRewrite) yaml += `fix: ${yamlQuote(lastRewrite)}\n`;
  writeFileSync(fp, yaml);
  console.log(`${c.green}Saved:${c.reset} ${fp}`);
}

function applyRewrite() {
  if (!lastPattern || !lastRewrite) { console.log(`${c.red}Need pattern + rewrite first.${c.reset}`); return; }
  // Apply per-file to avoid hanging on large files
  const files = findJsFiles(targetDir);
  let applied = 0;
  for (const file of files) {
    try { if (statSync(file).size > SG_MAX_FILE_SIZE) continue; } catch { continue; }
    const r = spawnSync("sg", ["run", "--pattern", lastPattern, "--rewrite", lastRewrite, "--lang", lang, "--update-all", file], {
      encoding: "utf-8",
      timeout: SG_PER_FILE_TIMEOUT,
    });
    if (r.status === 0) applied++;
  }
  // Invariant 4: refresh everything after file mutation
  fileCache.clear();
  const remaining = doSearch(lastPattern);
  setMatches(remaining);
  const still = remaining.length;
  console.log(`${c.green}Applied to ${applied} file${applied !== 1 ? "s" : ""}.${c.reset}${still ? ` ${c.dim}${still} remaining match${still !== 1 ? "es" : ""}.${c.reset}` : ""}`);
}

// ─── Prompt ────────────────────────────────────────────────────────────────────

function modeLabel(): string {
  switch (mode) {
    case "nav":     return `${c.inv}${c.cyan} NAV ${c.reset}`;
    case "search":  return `${c.inv}${c.green} / ${c.reset}`;
    case "rewrite": return `${c.inv}${c.yellow} REWRITE ${c.reset}`;
    case "command": return `${c.inv}${c.magenta} : ${c.reset}`;
  }
}

function drawPrompt() {
  if (mode === "nav") {
    write(`${CLR_LINE}${modeLabel()} ${c.dim}n/p u c w s r / : q ?${c.reset}`);
  } else {
    write(`${CLR_LINE}${modeLabel()} ${inputBuf}`);
  }
}

function showNavHelp() {
  console.log(`
${c.bold}NAV mode${c.reset} ${c.dim}(single keypresses)${c.reset}
  ${c.cyan}n${c.reset}  next match        ${c.cyan}p${c.reset}  prev match
  ${c.cyan}u${c.reset}  enclosing scope   ${c.cyan}c${c.reset}  callers/references
  ${c.cyan}w${c.reset}  widen context     ${c.cyan}s${c.reset}  shrink context
  ${c.cyan}/${c.reset}  search pattern    ${c.cyan}r${c.reset}  enter rewrite
  ${c.cyan}:${c.reset}  command mode      ${c.cyan}?${c.reset}  this help
  ${c.cyan}q${c.reset}  quit

${c.bold}Search mode${c.reset} ${c.dim}(type pattern, Enter to run, Esc for NAV)${c.reset}
${c.bold}Rewrite mode${c.reset} ${c.dim}(type replacement, Enter to preview, Esc for NAV)${c.reset}
${c.bold}Command mode${c.reset} ${c.dim}(commands below, Esc for NAV)${c.reset}
  ${c.cyan}:save <name>${c.reset}     save pattern+rewrite as rule
  ${c.cyan}:apply${c.reset}           apply rewrite to files ${c.red}(destructive)${c.reset}
  ${c.cyan}:lang <lang>${c.reset}     change language (current: ${lang})

${c.bold}Pattern tips${c.reset}
  ${c.dim}\$NAME${c.reset}  single node   ${c.dim}\$\$\$${c.reset}  zero or more   ${c.dim}\$_${c.reset}  wildcard
`);
}

// ─── Input handling ────────────────────────────────────────────────────────────

function enterMode(m: Mode) {
  mode = m;
  inputBuf = "";
  historyIdx = -1;
  drawPrompt();
}

function submitInput() {
  const val = inputBuf.trim();
  inputBuf = "";
  write(CLR_LINE);

  if (!val) { enterMode("nav"); return; }

  // Save to per-mode history
  const hist = currentHistory();
  if (hist[0] !== val) hist.unshift(val);
  if (hist.length > 50) hist.pop();

  switch (mode) {
    case "search":
      lastPattern = val;
      lastRewrite = "";
      console.log(`\n${c.bold}Pattern:${c.reset} ${val}`);
      setMatches(doSearch(val));
      showAllMatches();
      enterMode("nav");
      break;

    case "rewrite":
      lastRewrite = val;
      if (!lastPattern) {
        console.log(`${c.red}Search first.${c.reset}`);
      } else {
        console.log(`\n${c.bold}Rewrite:${c.reset} ${val}`);
        setMatches(doSearch(lastPattern, val));
        showAllMatches();
      }
      enterMode("nav");
      break;

    case "command":
      if (val.startsWith("save ")) {
        saveRule(val.slice(5).trim());
      } else if (val === "apply") {
        applyRewrite();
      } else if (val.startsWith("lang ")) {
        lang = val.slice(5).trim();
        console.log(`${c.dim}Language: ${lang}${c.reset}`);
      } else if (val === "q" || val === "quit") {
        cleanup();
      } else {
        console.log(`${c.red}Unknown command: :${val}${c.reset}`);
      }
      enterMode("nav");
      break;
  }
}

function handleNavKey(key: string, raw: Buffer) {
  switch (key) {
    case "n": case "j":
      if (matches.length) { setMatches(matches, (currentIdx + 1) % matches.length); showCurrent(); }
      else console.log(`\n${c.dim}No matches. Press / to search.${c.reset}`);
      drawPrompt();
      break;
    case "p": case "k":
      if (matches.length) { setMatches(matches, (currentIdx - 1 + matches.length) % matches.length); showCurrent(); }
      drawPrompt();
      break;
    case "w":
      contextChars += 40;
      console.log(`\n${c.dim}Context: ${contextChars} chars${c.reset}`);
      showCurrent();
      drawPrompt();
      break;
    case "s":
      contextChars = Math.max(20, contextChars - 40);
      console.log(`\n${c.dim}Context: ${contextChars} chars${c.reset}`);
      showCurrent();
      drawPrompt();
      break;
    case "u":
      showEnclosingScope();
      drawPrompt();
      break;
    case "c":
      showCallers();
      drawPrompt();
      break;
    case "/": case "i":
      enterMode("search");
      break;
    case "r":
      enterMode("rewrite");
      break;
    case ":":
      enterMode("command");
      break;
    case "?":
      showNavHelp();
      drawPrompt();
      break;
    case "q":
      cleanup();
      break;
    default:
      // Ignore unknown keys
      break;
  }
}

function handleInputKey(key: string, raw: Buffer) {
  // Escape → back to nav
  if (raw[0] === 0x1b && raw.length === 1) {
    write(CLR_LINE);
    enterMode("nav");
    return;
  }

  // Enter → submit
  if (key === "\r" || key === "\n") {
    submitInput();
    return;
  }

  // Backspace
  if (raw[0] === 0x7f || raw[0] === 0x08) {
    inputBuf = inputBuf.slice(0, -1);
    drawPrompt();
    return;
  }

  // Ctrl+C
  if (raw[0] === 0x03) {
    write(CLR_LINE);
    enterMode("nav");
    return;
  }

  // Ctrl+U — clear line
  if (raw[0] === 0x15) {
    inputBuf = "";
    drawPrompt();
    return;
  }

  // Up arrow — per-mode history
  if (raw[0] === 0x1b && raw[1] === 0x5b && raw[2] === 0x41) {
    const hist = currentHistory();
    if (historyIdx < hist.length - 1) {
      historyIdx++;
      inputBuf = hist[historyIdx];
      drawPrompt();
    }
    return;
  }

  // Down arrow — per-mode history
  if (raw[0] === 0x1b && raw[1] === 0x5b && raw[2] === 0x42) {
    const hist = currentHistory();
    if (historyIdx > 0) {
      historyIdx--;
      inputBuf = hist[historyIdx];
    } else {
      historyIdx = -1;
      inputBuf = "";
    }
    drawPrompt();
    return;
  }

  // Ignore other control/escape sequences
  if (raw[0] < 0x20 || (raw[0] === 0x1b && raw.length > 1)) return;

  // Regular character
  inputBuf += key;
  drawPrompt();
}

// ─── Main loop ─────────────────────────────────────────────────────────────────

function cleanup() {
  if (process.stdin.isTTY) process.stdin.setRawMode(false);
  console.log(`\n${c.dim}bye${c.reset}`);
  process.exit(0);
}

function main() {
  targetDir = process.argv[2];

  if (!targetDir || targetDir === "--help" || targetDir === "-h") {
    console.log("Usage: extension_explorer.ts <extension-dir>");
    console.log("       npx tsx extension_explorer.ts ~/ClaudeChromeExtension/latest");
    process.exit(targetDir ? 0 : 1);
  }

  // Resolve symlinks so sg/find can traverse the real directory
  try {
    targetDir = realpathSync(targetDir);
    const stat = statSync(targetDir);
    if (!stat.isDirectory()) {
      console.error(`Not a directory: ${targetDir}`);
      process.exit(1);
    }
  } catch {
    console.error(`Directory not found: ${targetDir}`);
    process.exit(1);
  }

  const sgCheck = spawnSync("sg", ["--version"], { encoding: "utf-8" });
  if (sgCheck.error) {
    console.error("ast-grep (sg) not found. Install: brew install ast-grep");
    process.exit(1);
  }

  if (!process.stdin.isTTY) {
    console.error("Not a TTY. Run this in an interactive terminal.");
    process.exit(1);
  }

  console.log(`\n${c.bold}extension_explorer${c.reset} ${c.dim}— interactive AST search${c.reset}`);
  console.log(`${c.dim}Target: ${targetDir}${c.reset}`);
  console.log(`${c.dim}Press ${c.reset}?${c.dim} for help, ${c.reset}/${c.dim} to search, ${c.reset}q${c.dim} to quit${c.reset}\n`);

  // Start in search mode so you can type a pattern immediately
  mode = "search";

  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding("utf-8");

  drawPrompt();

  process.stdin.on("data", (data: string) => {
    const raw = Buffer.from(data, "utf-8");
    const key = data;

    // Ctrl+C always exits from nav, cancels from input
    if (raw[0] === 0x03 && mode === "nav") cleanup();

    if (mode === "nav") {
      handleNavKey(key, raw);
    } else {
      handleInputKey(key, raw);
    }
  });
}

main();
