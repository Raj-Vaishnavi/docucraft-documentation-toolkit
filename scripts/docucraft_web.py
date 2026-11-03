#!/usr/bin/env python3
"""Run DocuCraft's local browser interface using only Python's standard library."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from docucraft import check_markdown, load_config  # noqa: E402

HOST, PORT = "127.0.0.1", 8765
HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DocuCraft · Documentation checker</title>
<style>
:root{color-scheme:light;--ink:#172b3a;--muted:#607383;--line:#dce5e8;--teal:#087e78;--pale:#eff8f7;--bg:#f5f8f8;--red:#b43b48;--amber:#956500}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif}.top{background:#fff;border-bottom:1px solid var(--line);padding:18px max(calc((100vw - 1100px)/2),24px);display:flex;align-items:center;gap:12px}.logo{width:38px;height:38px;border-radius:12px;background:var(--teal);color:white;display:grid;place-items:center;font-weight:800;font-size:20px}.brand{font-weight:750;font-size:18px;letter-spacing:-.3px}.tag{color:var(--muted);font-size:13px}.wrap{max-width:1100px;margin:38px auto;padding:0 24px}.intro{margin-bottom:26px}.eyebrow{color:var(--teal);text-transform:uppercase;letter-spacing:1.5px;font-size:11px;font-weight:800}.intro h1{font-size:30px;letter-spacing:-.8px;margin:5px 0}.intro p{color:var(--muted);margin:0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:19px;box-shadow:0 4px 14px #183b4510}.labelrow{display:flex;align-items:center;justify-content:space-between;margin-bottom:9px}.labelrow label{font-weight:700}.hint{font-size:12px;color:var(--muted)}select,textarea{width:100%;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);font:inherit}select{padding:10px}textarea{height:400px;padding:14px;resize:vertical;font:13px/1.6 Consolas,monospace}textarea:focus,select:focus{outline:3px solid #087e7824;border-color:var(--teal)}.actions{display:flex;gap:10px;margin-top:12px}.button{border:0;border-radius:9px;padding:10px 16px;background:var(--teal);color:white;font-weight:700;font-size:14px;cursor:pointer}.button.secondary{background:#edf3f4;color:var(--ink)}.button:disabled{opacity:.6;cursor:wait}.status{min-height:24px;color:var(--muted);font-size:13px;margin-top:8px}.result{margin-top:18px}.empty{padding:28px 10px;text-align:center;color:var(--muted)}.summary{padding:12px 14px;border-radius:9px;background:var(--pale);color:var(--teal);font-weight:750;margin-bottom:10px}.summary.fail{background:#fff1f1;color:var(--red)}.finding{padding:11px 12px;border:1px solid var(--line);border-radius:9px;margin:8px 0;font-size:13px}.finding strong{margin-right:5px}.finding.error strong{color:var(--red)}.finding.warning strong{color:var(--amber)}.code{font:11px Consolas,monospace;color:var(--muted);padding:2px 6px;background:#f0f4f4;border-radius:5px}.footer{margin:22px 2px;color:var(--muted);font-size:12px}.footer b{color:var(--ink)}@media(max-width:760px){.grid{grid-template-columns:1fr}.wrap{margin:24px auto}textarea{height:300px}}
</style></head><body><header class="top"><div class="logo">D</div><div><div class="brand">DocuCraft</div><div class="tag">Documentation quality checker</div></div></header>
<main class="wrap"><section class="intro"><div class="eyebrow">Local writing workspace</div><h1>Check a Markdown document</h1><p>Choose a sample, review or edit its text, then run the checks.</p></section>
<div class="grid"><section class="card"><div class="labelrow"><label for="file">Document</label><span class="hint">Sample project files</span></div><select id="file"></select><div class="labelrow" style="margin-top:16px"><label for="source">Markdown text</label><span class="hint" id="chars">0 characters</span></div><textarea id="source" spellcheck="false" aria-label="Markdown document text" placeholder="Loading document…"></textarea><div class="actions"><button class="button" id="check">Run quality check</button><button class="button secondary" id="reload">Reload original</button></div><div class="status" id="status" aria-live="polite"></div></section>
<section class="card"><div class="labelrow"><label>Results</label><span class="hint">Structure · links · terminology</span></div><div id="result" class="result"><div class="empty">Your report will appear here after you run a check.</div></div></section></div>
<div class="footer"><b>Note:</b> SafeRestore is a fictional product used for examples. DocuCraft checks document structure and consistency; a human must verify product facts.</div></main>
<script>
const file=document.querySelector('#file'),source=document.querySelector('#source'),result=document.querySelector('#result'),status=document.querySelector('#status'),button=document.querySelector('#check'),chars=document.querySelector('#chars');
function count(){chars.textContent=source.value.length.toLocaleString()+' characters'}
async function loadDoc(){status.textContent='Loading document…';try{const r=await fetch('/api/file?path='+encodeURIComponent(file.value));if(!r.ok)throw Error(await r.text());source.value=(await r.json()).text;count();status.textContent='Original sample loaded.'}catch(e){status.textContent='Could not load document: '+e.message}}
source.addEventListener('input',count);file.addEventListener('change',loadDoc);document.querySelector('#reload').addEventListener('click',loadDoc);
function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(data){const fs=data.findings||[],errors=fs.filter(x=>x.severity==='error').length,warnings=fs.filter(x=>x.severity==='warning').length;result.innerHTML='';const summary=document.createElement('div');summary.className='summary'+(errors?' fail':'');summary.textContent=(errors?'Needs attention':'Looks good')+' · '+errors+' errors · '+warnings+' warnings';result.append(summary);if(!fs.length){const p=document.createElement('div');p.className='empty';p.textContent='No issues found. Your document passed all configured checks.';result.append(p);return}for(const f of fs){const row=document.createElement('div');row.className='finding '+f.severity;row.innerHTML='<strong>'+escapeHtml(f.severity.toUpperCase())+'</strong> Line '+f.line+' <span class="code">'+escapeHtml(f.code)+'</span><br>'+escapeHtml(f.message);result.append(row)}}
button.addEventListener('click',async()=>{button.disabled=true;status.textContent='Checking…';try{const r=await fetch('/api/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:file.value,text:source.value})});const data=await r.json();if(!r.ok)throw Error(data.error||'Check failed');render(data);status.textContent='Check complete.'}catch(e){status.textContent='Could not check document: '+e.message}finally{button.disabled=false}});
(async()=>{try{const r=await fetch('/api/files');const files=await r.json();for(const name of files){const option=document.createElement('option');option.value=name;option.textContent=name;file.append(option)}await loadDoc()}catch(e){status.textContent='Could not load project documents.'}})();
</script></body></html>'''


def safe_markdown_path(value: str) -> Path:
    candidate = (ROOT / value).resolve()
    if ROOT.resolve() not in candidate.parents or candidate.suffix.lower() != ".md" or not candidate.is_file():
        raise ValueError("Choose a Markdown file inside this project.")
    return candidate


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: object) -> None:
        self._send(status, json.dumps(data).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
        elif parsed.path == "/api/files":
            files = sorted(p.relative_to(ROOT).as_posix() for folder in ("docs", "examples") for p in (ROOT / folder).rglob("*.md"))
            self._json(200, files)
        elif parsed.path == "/api/file":
            from urllib.parse import parse_qs
            try:
                path = safe_markdown_path(parse_qs(parsed.query).get("path", [""])[0])
                self._json(200, {"text": path.read_text(encoding="utf-8")})
            except (ValueError, OSError) as exc:
                self._json(400, {"error": str(exc)})
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/check":
            self._json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                raise ValueError("Document is too large (maximum 1 MB).")
            payload = json.loads(self.rfile.read(length))
            path = safe_markdown_path(payload.get("path", ""))
            text = payload.get("text", "")
            if not isinstance(text, str):
                raise ValueError("Document content must be text.")
            sections, terms = load_config(ROOT / "docucraft.toml")
            findings = check_markdown(path, sections, terms, text=text)
            self._json(200, {"file": path.relative_to(ROOT).as_posix(), "findings": [f.__dict__ for f in findings]})
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, fmt: str, *args: object) -> None:
        print("[DocuCraft] " + fmt % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"DocuCraft is ready at http://{HOST}:{PORT}")
    print("Keep this terminal open while using the page. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDocuCraft stopped.")
        server.server_close()
