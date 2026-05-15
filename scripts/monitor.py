#!/usr/bin/env python3
"""
腳本進度監控伺服器
用法：
  python scripts/monitor.py

電腦與手機連同一個 WiFi，手機開啟 http://<顯示的IP>:8765
即可即時看到腳本執行進度
"""

import http.server
import json
import socket
import time
from pathlib import Path

PORT = 8765
PROGRESS_FILE = Path(__file__).parent / "progress.json"

HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>腳本進度監控</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue","PingFang TC",sans-serif;
  background:#0a0a0a;color:#f5f5f7;min-height:100vh;padding:1.5rem}
h1{font-size:18px;font-weight:600;color:#86868b;letter-spacing:.04em;text-transform:uppercase;margin-bottom:1.5rem}
.card{background:#1c1c1e;border-radius:16px;padding:1.5rem;margin-bottom:1rem}
.script-name{font-size:22px;font-weight:700;margin-bottom:.25rem}
.task{font-size:14px;color:#86868b;margin-bottom:1.25rem}
.bar-wrap{background:#2c2c2e;border-radius:99px;height:10px;overflow:hidden;margin-bottom:.75rem}
.bar{height:100%;border-radius:99px;background:linear-gradient(90deg,#0071e3,#34aadc);
  transition:width .4s ease;width:0%}
.bar.done{background:linear-gradient(90deg,#30d158,#34c759)}
.bar.error{background:linear-gradient(90deg,#ff453a,#ff6961)}
.pct{font-size:40px;font-weight:700;letter-spacing:-.02em}
.pct-label{font-size:13px;color:#86868b;margin-top:.25rem}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-top:1rem}
.stat{background:#2c2c2e;border-radius:12px;padding:.875rem 1rem}
.stat-label{font-size:11px;color:#86868b;margin-bottom:.25rem}
.stat-value{font-size:15px;font-weight:600}
.message{font-size:14px;color:#f5f5f7;margin-top:1rem;padding:.75rem 1rem;
  background:#2c2c2e;border-radius:10px;line-height:1.5}
.error-msg{color:#ff6961}
.log{background:#1c1c1e;border-radius:16px;padding:1.25rem 1.5rem}
.log h2{font-size:13px;color:#86868b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.875rem}
.log-list{list-style:none;max-height:280px;overflow-y:auto}
.log-item{font-size:12px;color:#aeaeb2;padding:.3rem 0;border-bottom:.5px solid #2c2c2e;line-height:1.5}
.log-item:last-child{border-bottom:none;color:#f5f5f7}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#0071e3;
  margin-right:.5rem;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.dot.done{background:#30d158;animation:none}
.dot.idle{background:#86868b;animation:none}
.dot.error{background:#ff453a;animation:none}
.updated{font-size:11px;color:#48484a;text-align:right;margin-top:.75rem}
</style>
</head>
<body>
<h1>&#9654; 腳本進度監控</h1>
<div class="card" id="main-card">
  <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem">
    <span class="dot idle" id="dot"></span>
    <span class="script-name" id="script">等待腳本啟動…</span>
  </div>
  <div class="task" id="task"></div>
  <div class="bar-wrap"><div class="bar" id="bar"></div></div>
  <div class="pct" id="pct">—</div>
  <div class="pct-label" id="count"></div>
  <div class="stats">
    <div class="stat"><div class="stat-label">開始時間</div><div class="stat-value" id="started">—</div></div>
    <div class="stat"><div class="stat-label">最後更新</div><div class="stat-value" id="updated-val">—</div></div>
  </div>
  <div class="message" id="message" style="display:none"></div>
</div>
<div class="log">
  <h2>執行紀錄</h2>
  <ul class="log-list" id="log-list"><li class="log-item" style="color:#48484a">尚無記錄</li></ul>
</div>
<div class="updated" id="poll-status">連線中…</div>

<script>
const dot = document.getElementById('dot')
const scriptEl = document.getElementById('script')
const taskEl = document.getElementById('task')
const bar = document.getElementById('bar')
const pct = document.getElementById('pct')
const count = document.getElementById('count')
const started = document.getElementById('started')
const updatedVal = document.getElementById('updated-val')
const message = document.getElementById('message')
const logList = document.getElementById('log-list')
const pollStatus = document.getElementById('poll-status')

function render(d) {
  if (!d.script) return
  scriptEl.textContent = d.script
  taskEl.textContent = d.task || ''
  bar.style.width = d.percent + '%'
  pct.textContent = d.percent + '%'
  count.textContent = d.total > 0 ? d.current + ' / ' + d.total : ''
  started.textContent = d.started || '—'
  updatedVal.textContent = d.updated || '—'

  if (d.message) {
    message.textContent = d.message
    message.style.display = 'block'
    message.className = 'message' + (d.error ? ' error-msg' : '')
  } else {
    message.style.display = 'none'
  }

  if (d.error) {
    dot.className = 'dot error'
    bar.className = 'bar error'
  } else if (d.done) {
    dot.className = 'dot done'
    bar.className = 'bar done'
  } else {
    dot.className = 'dot'
    bar.className = 'bar'
  }

  if (d.log && d.log.length) {
    logList.innerHTML = d.log.slice().reverse().map(
      l => '<li class="log-item">' + l.replace(/</g,'&lt;') + '</li>'
    ).join('')
  }
}

async function poll() {
  try {
    const r = await fetch('/progress?t=' + Date.now())
    if (r.ok) {
      const d = await r.json()
      render(d)
      pollStatus.textContent = '已連線・每 2 秒更新'
    }
  } catch(e) {
    pollStatus.textContent = '連線中斷，重試…'
  }
}

poll()
setInterval(poll, 2000)
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve(200, "text/html; charset=utf-8", HTML.encode())
        elif self.path.startswith("/progress"):
            data = self._read_progress()
            body = json.dumps(data, ensure_ascii=False).encode()
            self._serve(200, "application/json", body)
        else:
            self._serve(404, "text/plain", b"Not found")

    def _serve(self, status, ctype, body):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _read_progress(self):
        if PROGRESS_FILE.exists():
            try:
                return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def log_message(self, format, *args):
        pass  # 不輸出 HTTP 請求 log


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 45)
    print(f"  進度監控已啟動")
    print(f"  手機開啟：http://{ip}:{PORT}")
    print(f"  電腦開啟：http://localhost:{PORT}")
    print("=" * 45)
    print("  按 Ctrl+C 停止")
    print()
    with http.server.HTTPServer(("", PORT), Handler) as server:
        server.serve_forever()
