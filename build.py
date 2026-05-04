#!/usr/bin/env python3
"""SOC Scanner PWA assembly script.
Downloads Dexie + html5-qrcode from CDN and assembles final index.html with all libs inlined.
Run: python build.py
Output: index.html, manifest.json, sw.js, README.md
"""
import urllib.request, urllib.error, zlib, struct, base64, json, os, sys, time

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def download(url: str, retries: int = 3) -> str:
    print(f'  Downloading {url} ...')
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; SOC-Build/1.0)'}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                content = r.read().decode('utf-8')
            print(f'    OK ({len(content):,} chars)')
            return content
        except Exception as e:
            if attempt < retries - 1:
                print(f'    Retry {attempt+1}/{retries-1}: {e}')
                time.sleep(2)
            else:
                raise RuntimeError(f'Failed to download {url}: {e}')
    raise RuntimeError(f'Failed to download {url}')  # unreachable, satisfies type checker

def make_png(size, r, g, b):
    """Generate solid-color PNG, return base64 string (stdlib only)."""
    def chunk(tag, data):
        payload = tag + data
        return struct.pack('>I', len(data)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xFFFFFFFF)
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    row = bytes([0]) + bytes([r, g, b] * size)
    raw = row * size
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    return base64.b64encode(png).decode('ascii')

# ---------------------------------------------------------------------------
# HTML parts (assembled around inlined libs)
# ---------------------------------------------------------------------------
PART1 = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0a0a0a">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="SOC">
<link rel="manifest" href="./manifest.json">
<link rel="apple-touch-icon" href="ICON180_DATA">
<title>SOC Scanner</title>
<style>
:root{
  --bg:#0a0a0a;--surface:#1a1a1a;--text:#f5f5f5;
  --accent:#ff6b35;--success:#00ff88;--error:#ff3b3b;
  --border:#2a2a2a;--font-base:18px;--font-soc:28px;
  --btn-min:56px;--tap-radius:12px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font:var(--font-base)/1.4 system-ui,-apple-system,sans-serif;-webkit-text-size-adjust:100%;overflow-x:hidden}
/* Flash overlay */
#flash-overlay{position:fixed;inset:0;pointer-events:none;z-index:9999;transition:opacity .2s;display:none;opacity:0}
/* Toast */
.toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--surface);color:var(--text);padding:14px 24px;border-radius:12px;font-size:16px;font-weight:500;box-shadow:0 4px 20px rgba(0,0,0,.5);z-index:2000;opacity:0;transition:opacity .2s,transform .2s;max-width:90vw;text-align:center;pointer-events:none;border:1px solid var(--border)}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.toast.success{background:#0d2a1a;color:var(--success);border-color:var(--success)}
.toast.error{background:#2a0d0d;color:var(--error);border-color:var(--error)}
/* Header */
#app-header{position:sticky;top:0;height:56px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 16px;z-index:100}
#app-header .title{font-size:18px;font-weight:700}
/* Tab content */
.tab-content{min-height:calc(100vh - 56px - 64px);padding-bottom:80px}
/* Bottom nav */
#bottom-nav{position:fixed;bottom:0;left:0;right:0;height:64px;background:var(--surface);border-top:1px solid var(--border);display:flex;z-index:100;padding-bottom:env(safe-area-inset-bottom,0)}
.nav-btn{flex:1;background:transparent;border:none;color:#555;font-size:11px;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:var(--btn-min);transition:color .2s;-webkit-tap-highlight-color:transparent;border-top:3px solid transparent}
.nav-btn .ico{font-size:22px;line-height:1}
.nav-btn.active{color:var(--accent);border-top-color:var(--accent)}
/* Scanner */
.scanner-area{padding:16px;display:flex;flex-direction:column;align-items:center;gap:16px}
#scanner-container{width:100%;max-width:400px;border-radius:12px;overflow:hidden;background:var(--surface);min-height:180px;position:relative}
#scanner-container video{width:100%;height:auto;display:block}
.scan-status{font-size:16px;color:#888;text-align:center;min-height:24px;padding:0 16px}
/* Buttons */
.btn-primary{background:var(--accent);color:#fff;font-weight:700;border:none;border-radius:var(--tap-radius);cursor:pointer;min-height:var(--btn-min);-webkit-tap-highlight-color:transparent}
.btn-secondary{background:var(--border);color:var(--text);border:none;border-radius:var(--tap-radius);cursor:pointer;min-height:var(--btn-min);-webkit-tap-highlight-color:transparent}
.btn-danger{background:var(--error);color:#fff;font-weight:700;border:none;border-radius:var(--tap-radius);cursor:pointer;min-height:var(--btn-min);-webkit-tap-highlight-color:transparent}
.btn-block{width:100%;padding:14px;font-size:18px}
.btn-scan{font-size:20px;padding:16px 20px}
/* History header */
.history-header{padding:12px 16px;background:var(--surface);position:sticky;top:56px;z-index:10;border-bottom:1px solid var(--border)}
#history-summary{margin:0 0 8px;font-size:15px;color:#aaa}
.history-toolbar{display:flex;gap:8px;align-items:center}
#search-input{flex:1;padding:10px 12px;min-height:44px;background:var(--bg);color:var(--text);border:2px solid var(--border);border-radius:var(--tap-radius);font-size:16px;outline:none;-webkit-appearance:none}
#search-input:focus{border-color:var(--accent)}
.btn-export{padding:10px 12px;min-height:44px;font-size:14px;white-space:nowrap}
/* History list (card layout) */
.rec-item{display:flex;align-items:center;gap:8px;padding:12px 16px;border-bottom:1px solid var(--border)}
.rec-body{flex:1;min-width:0}
.rec-row1{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:3px}
.rec-soc{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-weight:700;font-size:14px;color:var(--text)}
.rec-qty{font-weight:700;font-size:15px;color:var(--accent);white-space:nowrap}
.rec-row2{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.rec-meta{font-size:12px;color:#888}
.rec-note{font-size:12px;color:#666;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:130px}
.btn-delete-row{min-width:44px;min-height:44px;background:transparent;border:none;color:var(--error);font-size:20px;cursor:pointer;padding:8px;-webkit-tap-highlight-color:transparent}
/* Empty state */
.empty-state{text-align:center;padding:60px 20px;color:#555;font-size:16px;line-height:1.8}
/* Settings */
.settings-section{padding:20px 16px;border-bottom:1px solid var(--border)}
.settings-section h3{margin:0 0 12px;font-size:18px}
.hint{margin:8px 0 0;font-size:14px;color:#555;line-height:1.5}
details{margin-top:12px}
details summary{cursor:pointer;padding:8px 0;color:var(--accent);font-size:16px;list-style:none;-webkit-tap-highlight-color:transparent}
details summary::-webkit-details-marker{display:none}
details summary::before{content:'\25B6  '}
details[open] summary::before{content:'\25BC  '}
details ol{padding:12px 0 0 24px;color:#aaa}
details li{margin-bottom:6px;font-size:15px;line-height:1.5}
/* Bottom sheet */
#sheet-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.65);opacity:0;transition:opacity .2s;z-index:1000}
#sheet-backdrop:not([hidden]){opacity:1}
.sheet{position:fixed;left:0;right:0;bottom:0;background:var(--surface);border-radius:20px 20px 0 0;padding:20px 16px;padding-bottom:max(32px,env(safe-area-inset-bottom,16px));z-index:1001;transform:translateY(100%);transition:transform .25s ease-out;max-height:85vh;overflow-y:auto}
.sheet:not([hidden]){transform:translateY(0)}
.sheet-handle{width:40px;height:4px;background:var(--border);border-radius:2px;margin:0 auto 16px}
.soc-display{font:bold var(--font-soc)/1.2 ui-monospace,'SF Mono',monospace;color:var(--accent);text-align:center;margin:0 0 20px;letter-spacing:.05em;word-break:break-all}
.date-display{font-size:14px;color:#888;text-align:center;margin:-10px 0 16px}
label{display:block;font-size:14px;color:#777;margin-bottom:6px}
#qty-input{width:100%;font-size:24px;padding:14px;background:var(--bg);color:var(--text);border:2px solid var(--border);border-radius:var(--tap-radius);min-height:var(--btn-min);outline:none;-webkit-appearance:none}
#qty-input:focus{border-color:var(--accent)}
.link-note{display:inline-block;margin:14px 0 6px;color:var(--accent);text-decoration:none;padding:8px 0;font-size:16px}
#note-input{width:100%;padding:12px;resize:vertical;background:var(--bg);color:var(--text);border:2px solid var(--border);border-radius:var(--tap-radius);font-size:16px;font-family:inherit;outline:none;min-height:80px}
#note-input:focus{border-color:var(--accent)}
.sheet-actions{display:flex;gap:12px;margin-top:20px}
.sheet-actions button{flex:1;font-size:18px}
</style>
</head>
<body>
<div id="flash-overlay"></div>
<div id="toast" class="toast" role="alert" aria-live="polite"></div>

<header id="app-header">
  <span class="title">SOC Scanner</span>
</header>

<!-- Tab: Scanner -->
<section id="tab-scanner" class="tab-content">
  <div class="scanner-area">
    <div id="scanner-container"></div>
    <p id="scan-status" class="scan-status">Bấm <strong>Bắt đầu quét</strong> để mở camera</p>
    <button id="btn-start-scan" class="btn-primary btn-block btn-scan">📷 Bắt đầu quét</button>
  </div>
</section>

<!-- Tab: History -->
<section id="tab-history" class="tab-content" hidden>
  <div class="history-header">
    <p id="history-summary">0 dòng &bull; Tổng 0 sản phẩm</p>
    <div class="history-toolbar">
      <input id="search-input" type="search" placeholder="Tìm SOC..." inputmode="search" autocomplete="off">
      <button id="btn-export-history" class="btn-secondary btn-export">📥 CSV</button>
    </div>
  </div>
  <div id="history-empty" class="empty-state">
    <p>Chưa có dữ liệu.<br>Bấm tab <strong>Quét</strong> để bắt đầu.</p>
  </div>
  <div id="history-table-wrap" hidden>
    <div id="history-list"></div>
  </div>
</section>

<!-- Tab: Settings -->
<section id="tab-settings" class="tab-content" hidden>
  <div class="settings-section">
    <h3>📥 Export</h3>
    <button id="btn-export-settings" class="btn-primary btn-block">Export CSV</button>
    <p class="hint">Tải file CSV chứa tất cả records hiện tại.</p>
  </div>
  <div class="settings-section">
    <h3>🗑️ Xóa dữ liệu</h3>
    <button id="btn-delete-all" class="btn-danger btn-block">Xóa toàn bộ</button>
    <p class="hint">Cẩn thận: hành động này không thể hoàn tác. Hãy export CSV trước.</p>
  </div>
  <div class="settings-section">
    <h3>📱 Cài đặt vào màn hình chính</h3>
    <details>
      <summary>iOS (Safari)</summary>
      <ol>
        <li>Mở URL trong Safari (không phải Chrome)</li>
        <li>Bấm nút Share <strong>□↑</strong> ở thanh dưới</li>
        <li>Cuộn xuống chọn <strong>Add to Home Screen</strong></li>
        <li>Đặt tên rồi bấm <strong>Add</strong></li>
      </ol>
    </details>
    <details>
      <summary>Android (Chrome)</summary>
      <ol>
        <li>Mở URL trong Chrome</li>
        <li>Bấm menu <strong>⋮</strong> góc trên phải</li>
        <li>Chọn <strong>Install app</strong> hoặc <strong>Add to Home Screen</strong></li>
        <li>Bấm <strong>Install</strong></li>
      </ol>
    </details>
  </div>
</section>

<!-- Bottom nav -->
<nav id="bottom-nav">
  <button class="nav-btn active" data-tab="scanner"><span class="ico">📷</span>Quét</button>
  <button class="nav-btn" data-tab="history"><span class="ico">📋</span>Lịch sử</button>
  <button class="nav-btn" data-tab="settings"><span class="ico">⚙️</span>Cài đặt</button>
</nav>

<!-- Bottom sheet backdrop + form -->
<div id="sheet-backdrop" hidden></div>
<div id="sheet-qty" class="sheet" hidden role="dialog" aria-modal="true" aria-labelledby="sheet-soc">
  <div class="sheet-handle"></div>
  <h2 id="sheet-soc" class="soc-display"></h2>
  <p id="sheet-date" class="date-display" hidden></p>
  <form id="form-qty" novalidate>
    <label for="qty-input">Số lượng</label>
    <input id="qty-input" type="number" inputmode="numeric" min="1" max="99999" required placeholder="1" autocomplete="off">
    <a href="#" id="toggle-note" class="link-note">+ Thêm ghi chú</a>
    <div id="note-wrapper" hidden>
      <label for="note-input">Ghi chú</label>
      <textarea id="note-input" rows="3" maxlength="500" placeholder="Ghi chú tùy chọn..."></textarea>
    </div>
    <div class="sheet-actions">
      <button type="button" id="btn-cancel" class="btn-secondary">Hủy</button>
      <button type="submit" id="btn-save" class="btn-primary">Lưu</button>
    </div>
  </form>
</div>

<!-- Dexie (IndexedDB wrapper) -->
<script>
"""

PART2 = r"""
</script>
<!-- html5-qrcode (QR/barcode scanner) -->
<script>
"""

PART3 = r"""
</script>
<!-- App logic -->
<script>
'use strict';

// ── CONFIG ──────────────────────────────────────────────────────────────────
const SOC_REGEX = /^\d-26\d{5,6}-\d{3}$/;
const DATE_REGEX = /^(\d{2})\/(\d{2})\/(\d{4})$/;

// ── SERVICE WORKER ───────────────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () =>
    navigator.serviceWorker.register('./sw.js').catch(e => console.error('SW:', e))
  );
}

// ── TAB SYSTEM ───────────────────────────────────────────────────────────────
function showTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(s => { s.hidden = true; });
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const tab = document.getElementById('tab-' + tabId);
  if (tab) tab.hidden = false;
  const btn = document.querySelector('.nav-btn[data-tab="' + tabId + '"]');
  if (btn) btn.classList.add('active');
  if (tabId === 'history') refreshHistory();
}
document.querySelectorAll('.nav-btn').forEach(btn =>
  btn.addEventListener('click', () => showTab(btn.dataset.tab))
);

// ── TOAST ────────────────────────────────────────────────────────────────────
let _toastTimer = null;
function toast(msg, type) {
  clearTimeout(_toastTimer);
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show ' + (type || 'info');
  _toastTimer = setTimeout(() => el.classList.remove('show'), 2500);
}

// ── AUDIO ────────────────────────────────────────────────────────────────────
let _audioCtx = null;
function _initAudio() {
  if (!_audioCtx) {
    try { _audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch(e) {}
  }
}
function _tone(freq, dur, t) {
  if (!_audioCtx) return;
  try {
    const o = _audioCtx.createOscillator(), g = _audioCtx.createGain();
    o.connect(g); g.connect(_audioCtx.destination);
    o.type = 'sine';
    o.frequency.setValueAtTime(freq, _audioCtx.currentTime + t);
    g.gain.setValueAtTime(0.25, _audioCtx.currentTime + t);
    g.gain.exponentialRampToValueAtTime(0.001, _audioCtx.currentTime + t + dur);
    o.start(_audioCtx.currentTime + t);
    o.stop(_audioCtx.currentTime + t + dur + 0.01);
  } catch(e) {}
}
function beepSuccess() { _initAudio(); _tone(800, 0.1, 0); }
function beepError() { _initAudio(); _tone(200, 0.08, 0); _tone(200, 0.08, 0.13); _tone(200, 0.08, 0.26); }

// ── HAPTIC ───────────────────────────────────────────────────────────────────
function vibrate(p) { try { if (navigator.vibrate) navigator.vibrate(p); } catch(e) {} }
function flashScreen(color, ms) {
  const ov = document.getElementById('flash-overlay');
  ov.style.cssText = 'display:block;background:' + color + ';opacity:0.35;transition:none';
  requestAnimationFrame(() => {
    ov.style.transition = 'opacity 0.25s';
    setTimeout(() => {
      ov.style.opacity = '0';
      setTimeout(() => { ov.style.display = 'none'; }, 260);
    }, ms);
  });
}

// ── DATABASE (Dexie) ─────────────────────────────────────────────────────────
const db = new Dexie('soc_db');
db.version(1).stores({ records: '++id, timestamp, soc' });
db.version(2).stores({ records: '++id, timestamp, soc, productionDate' });

async function addRecord(data) {
  try {
    return await db.records.add({
      timestamp: new Date().toISOString(),
      soc: data.soc,
      productionDate: data.productionDate || null,
      quantity: parseInt(data.quantity, 10),
      note: data.note ? String(data.note).trim() || null : null
    });
  } catch (err) {
    if (err.name === 'QuotaExceededError') throw new Error('Hết dung lượng. Vui l\xf2ng export CSV v\xe0 x\xf3a bớt records.');
    throw err;
  }
}
async function getAllRecords() { return db.records.orderBy('timestamp').reverse().toArray(); }
async function searchRecords(q) {
  if (!q) return getAllRecords();
  const lq = q.toLowerCase();
  return (await getAllRecords()).filter(r => r.soc.toLowerCase().includes(lq));
}
async function deleteRecord(id) { await db.records.delete(id); }
async function deleteAll() {
  return db.transaction('rw', db.records, async () => {
    const n = await db.records.count();
    await db.records.clear();
    return n;
  });
}

// ── SCANNER ───────────────────────────────────────────────────────────────────
let _qr = null, _qrRunning = false;

function _parseQR(text) {
  const s = text.trim().replace(/[\r\n\t]/g, '');
  const parts = s.split(':');
  if (parts.length === 1) {
    return SOC_REGEX.test(parts[0]) ? { soc: parts[0], productionDate: null } : null;
  }
  if (parts.length === 2) {
    const [soc, dateStr] = parts;
    if (!SOC_REGEX.test(soc)) return null;
    const m = DATE_REGEX.exec(dateStr);
    if (!m) return null;
    const [, dd, mm, yyyy] = m;
    const d = new Date(`${yyyy}-${mm}-${dd}T00:00:00`);
    if (isNaN(d.getTime()) || d.getDate() !== +dd || d.getMonth() + 1 !== +mm) return null;
    return { soc, productionDate: dateStr };
  }
  return null;
}

async function _startScanner() {
  const box = document.getElementById('scanner-container');
  box.innerHTML = '';
  const startBtn = document.getElementById('btn-start-scan');
  const statusEl = document.getElementById('scan-status');
  startBtn.hidden = true;
  statusEl.textContent = 'Đang khởi động camera…';
  _qr = new Html5Qrcode('scanner-container', {
    formatsToSupport: [
      Html5QrcodeSupportedFormats.QR_CODE,
      Html5QrcodeSupportedFormats.CODE_128
    ]
  });
  try {
    await _qr.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 260, height: 180 } },
      txt => _onScan(txt),
      () => {}
    );
    _qrRunning = true;
    statusEl.textContent = 'Đang qu\xe9t…';
  } catch (err) {
    startBtn.hidden = false;
    const m = (err.message || '').toLowerCase();
    if (m.includes('ermission') || m.includes('denied')) {
      statusEl.textContent = '🚫 Bị từ chối quyền camera. Cấp quyền rồi thử lại.';
    } else {
      statusEl.textContent = '❌ Lỗi: ' + (err.message || '').slice(0, 80);
    }
  }
}

async function stopScanner() {
  if (_qr) { try { if (_qrRunning) await _qr.stop(); _qr.clear(); } catch(e) {} _qr = null; }
  _qrRunning = false;
  document.getElementById('btn-start-scan').hidden = false;
  document.getElementById('scan-status').textContent = 'Bấm Bắt đầu qu\xe9t để mở camera';
  document.getElementById('scanner-container').innerHTML = '';
}

function _onScan(text) {
  const parsed = _parseQR(text);
  const st = document.getElementById('scan-status');
  if (!parsed) {
    beepError(); vibrate([80,50,80,50,80]); flashScreen('#ff3b3b', 180);
    st.textContent = '⚠️ Kh\xf4ng hợp lệ: ' + text.trim().slice(0, 40);
    return;
  }
  const { soc, productionDate } = parsed;
  stopScanner(); beepSuccess(); vibrate(200); flashScreen('#00ff88', 150);
  st.textContent = '✓ ' + soc;
  document.dispatchEvent(new CustomEvent('soc-scanned', { detail: { soc, productionDate } }));
}

document.getElementById('btn-start-scan').addEventListener('click', () => { _initAudio(); _startScanner(); });

// ── BOTTOM SHEET ─────────────────────────────────────────────────────────────
const _sht = document.getElementById('sheet-qty');
const _bkd = document.getElementById('sheet-backdrop');
const _socDisp = document.getElementById('sheet-soc');
const _dateDisp = document.getElementById('sheet-date');
const _qtyIn = document.getElementById('qty-input');
const _noteIn = document.getElementById('note-input');
const _noteWrap = document.getElementById('note-wrapper');
const _togNote = document.getElementById('toggle-note');
const _frmQty = document.getElementById('form-qty');
let _curSoc = null, _curProdDate = null;

function _openSht(soc, productionDate) {
  _curSoc = soc; _curProdDate = productionDate || null;
  _socDisp.textContent = soc;
  if (_curProdDate) { _dateDisp.textContent = 'Ng\xe0y SX: ' + _curProdDate; _dateDisp.hidden = false; }
  else { _dateDisp.hidden = true; }
  _qtyIn.value = ''; _noteIn.value = '';
  _noteWrap.hidden = true; _togNote.textContent = '+ Th\xeam ghi ch\xfa';
  _bkd.hidden = false; _sht.hidden = false;
  setTimeout(() => _qtyIn.focus(), 100);
}
function _closeSht() { _sht.hidden = true; _bkd.hidden = true; _curSoc = null; _curProdDate = null; }

_togNote.addEventListener('click', e => {
  e.preventDefault();
  const exp = !_noteWrap.hidden;
  _noteWrap.hidden = exp;
  _togNote.textContent = exp ? '+ Th\xeam ghi ch\xfa' : '− Ẩn ghi ch\xfa';
  if (!exp) setTimeout(() => _noteIn.focus(), 50);
});

_frmQty.addEventListener('submit', async e => {
  e.preventDefault();
  const qty = parseInt(_qtyIn.value, 10);
  if (!qty || qty < 1) { toast('Số lượng kh\xf4ng hợp lệ', 'error'); return; }
  const sv = document.getElementById('btn-save'); sv.disabled = true;
  try {
    await addRecord({ soc: _curSoc, productionDate: _curProdDate, quantity: qty, note: _noteIn.value || null });
    toast('Đ\xe3 lưu ' + _curSoc + ' \xd7 ' + qty, 'success');
    _closeSht();
    document.dispatchEvent(new CustomEvent('record-added'));
  } catch (err) {
    toast('Lỗi: ' + err.message, 'error');
  } finally { sv.disabled = false; }
});

document.getElementById('btn-cancel').addEventListener('click', () => { _closeSht(); });
_bkd.addEventListener('click', () => { _closeSht(); });
document.addEventListener('soc-scanned', e => {
  if (_curSoc !== null) return;
  _openSht(e.detail.soc, e.detail.productionDate);
});

// ── HISTORY ───────────────────────────────────────────────────────────────────
function _fmtTime(iso) {
  const d = new Date(iso), p = n => String(n).padStart(2,'0');
  return p(d.getDate())+'/'+p(d.getMonth()+1)+' '+p(d.getHours())+':'+p(d.getMinutes());
}
function _esc(s) {
  return String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function _trunc(s, n) { n=n||30; if(!s)return''; return s.length>n?s.slice(0,n)+'…':s; }

async function refreshHistory(q) {
  try {
    const recs = q ? await searchRecords(q) : await getAllRecords();
    const list=document.getElementById('history-list'), empty=document.getElementById('history-empty'), wrap=document.getElementById('history-table-wrap');
    if (!recs.length) { empty.hidden=false; wrap.hidden=true; }
    else {
      empty.hidden=true; wrap.hidden=false;
      list.innerHTML = recs.map(r => {
        const datePart = r.productionDate ? '<span class="rec-meta">'+_esc(r.productionDate)+'</span>' : '';
        const notePart = r.note ? '<span class="rec-note" title="'+_esc(r.note)+'">'+_esc(_trunc(r.note))+'</span>' : '';
        return '<div class="rec-item">'+
          '<div class="rec-body">'+
            '<div class="rec-row1"><span class="rec-soc">'+_esc(r.soc)+'</span><span class="rec-qty">\xd7'+_esc(String(r.quantity))+'</span></div>'+
            '<div class="rec-row2"><span class="rec-meta">'+_fmtTime(r.timestamp)+'</span>'+datePart+notePart+'</div>'+
          '</div>'+
          '<button class="btn-delete-row" data-id="'+_esc(String(r.id))+'" aria-label="X\xf3a">🗑️</button>'+
        '</div>';
      }).join('');
    }
    const dispQty = recs.reduce((s, r) => s + (r.quantity || 0), 0);
    const label = q ? 'kết quả' : 'd\xf2ng';
    document.getElementById('history-summary').textContent =
      recs.length+' '+label+' • Tổng '+dispQty+' sản phẩm';
  } catch(err) {
    document.getElementById('history-empty').hidden = false;
    document.getElementById('history-table-wrap').hidden = true;
    document.getElementById('history-summary').textContent = 'Lỗi tải dữ liệu';
    console.error('refreshHistory:', err);
  }
}

let _srchT = null;
document.getElementById('search-input').addEventListener('input', e => {
  clearTimeout(_srchT);
  _srchT = setTimeout(() => refreshHistory(e.target.value.trim()), 200);
});

document.getElementById('history-list').addEventListener('click', async e => {
  const btn = e.target.closest('.btn-delete-row');
  if (!btn) return;
  if (!confirm('X\xf3a record n\xe0y?')) return;
  try {
    await deleteRecord(parseInt(btn.dataset.id, 10));
    toast('Đ\xe3 x\xf3a', 'success');
    refreshHistory(document.getElementById('search-input').value.trim());
  } catch(err) { toast('Lỗi x\xf3a: '+err.message, 'error'); }
});

document.addEventListener('record-added', () => refreshHistory());

// ── CSV EXPORT ────────────────────────────────────────────────────────────────
function _csvFld(v) {
  const s = String(v??'');
  return /[",\r\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s;
}
async function exportCurrentRecords() {
  try {
    const recs = await getAllRecords();
    if (!recs.length) { toast('Chưa c\xf3 dữ liệu để export', 'error'); return; }
    const BOM = '﻿', HDR = 'time,SOC,production_date,Qty,Note\r\n';
    const rows = recs.map(r => [_fmtTime(r.timestamp),r.soc,r.productionDate??'',r.quantity,r.note??''].map(_csvFld).join(',')).join('\r\n') + '\r\n';
    const d=new Date(), p=n=>String(n).padStart(2,'0');
    const fn='SOC_records_'+d.getFullYear()+p(d.getMonth()+1)+p(d.getDate())+'_'+p(d.getHours())+p(d.getMinutes())+p(d.getSeconds())+'.csv';
    const blob = new Blob([BOM+HDR+rows], {type:'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href=url; a.download=fn; document.body.appendChild(a); a.click();
    setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
    toast('Đ\xe3 export '+recs.length+' d\xf2ng', 'success');
  } catch(err) { toast('Lỗi export: '+err.message, 'error'); }
}
document.getElementById('btn-export-history').addEventListener('click', exportCurrentRecords);
document.getElementById('btn-export-settings').addEventListener('click', exportCurrentRecords);

// ── SETTINGS ─────────────────────────────────────────────────────────────────
document.getElementById('btn-delete-all').addEventListener('click', async () => {
  if (!confirm('Bạn c\xf3 chắc muốn x\xf3a TẤT CẢ records?\n\nH\xe0nh động n\xe0y KH\xd4NG THỂ ho\xe0n t\xe1c.')) return;
  const typed = prompt('G\xf5 ch\xednh x\xe1c chữ “X\xd3A” (đ\xfa c\xf3 dấu) để x\xe1c nhận:');
  if (typed !== 'X\xd3A') { toast('Kh\xf4ng khớp. Đ\xe3 hủy.', 'info'); return; }
  try {
    const n = await deleteAll();
    toast('Đ\xe3 x\xf3a '+n+' d\xf2ng', 'success');
    if (!document.getElementById('tab-history').hidden) refreshHistory();
  } catch(err) { toast('Lỗi: '+err.message, 'error'); }
});
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Service Worker
# ---------------------------------------------------------------------------
SW_JS = """const CACHE = 'soc-v1.0.0';
const FILES = ['./index.html', './manifest.json'];
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
"""

# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------
README_MD = """# SOC Scanner PWA

PWA quét QR/barcode mã SOC, lưu local (IndexedDB), export CSV. Chạy 100% offline sau lần load đầu.

## Deploy lên GitHub Pages (5 bước)

1. Tạo repo mới trên GitHub (ví dụ: `soc-scanner`)
2. Upload 3 files: `index.html`, `manifest.json`, `sw.js`
3. Vào **Settings → Pages**
4. Source: chọn branch `main`, folder `/` (root) → Save
5. Sau 1–2 phút, URL `https://<username>.github.io/<repo>/` sẽ live

## Add to Home Screen

### iPhone/iPad (Safari, iOS 16.4+)
1. Mở URL trong **Safari** (không phải Chrome)
2. Bấm nút **Share** (□↑) ở thanh dưới
3. Cuộn xuống → **Add to Home Screen**
4. Đặt tên → **Add**

### Android (Chrome 100+)
1. Mở URL trong **Chrome**
2. Menu **⋮** → **Install app** (hoặc **Add to Home Screen**)
3. **Install**

## Sử dụng

| Tab | Chức năng |
|-----|-----------|
| 📷 Quét | Bấm "Bắt đầu quét" → chĩa camera vào QR/barcode SOC → nhập số lượng → Lưu |
| 📋 Lịch sử | Xem records, tìm kiếm, xóa từng dòng, export CSV |
| ⚙️ Cài đặt | Export tất cả, xóa toàn bộ, hướng dẫn cài đặt |

## Format SOC

Regex: `^\\d-\\d{7,8}-\\d{3}$`
Ví dụ: `1-1234567-001`, `1-12345678-002`

## Offline

Lần đầu cần internet để load app + cache libs (~500KB).
Sau đó chạy hoàn toàn offline qua Service Worker.

## Tech

- Vanilla JS, không framework, không build step
- [html5-qrcode](https://github.com/mebjas/html5-qrcode) — quét QR/barcode
- [Dexie.js](https://dexie.org) — IndexedDB wrapper
- Service Worker cache-first — offline PWA
- Không backend, không tracking, không đăng nhập

## Generate icons tốt hơn

Để có icon với chữ "SOC", chạy lệnh này trong DevTools Console (sau khi app đang chạy):

```js
function genIcon(size) {
  const c=document.createElement('canvas'); c.width=c.height=size;
  const x=c.getContext('2d');
  x.fillStyle='#0a0a0a'; x.fillRect(0,0,size,size);
  x.fillStyle='#ff6b35'; x.font='bold '+Math.round(size*.35)+'px sans-serif';
  x.textAlign='center'; x.textBaseline='middle';
  x.fillText('SOC',size/2,size/2);
  return c.toDataURL('image/png');
}
console.log('192:', genIcon(192));
console.log('512:', genIcon(512));
```

Copy base64 strings và paste vào `manifest.json` icons.src + `<link rel="apple-touch-icon">` trong `index.html`.
"""

# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------
def main():
    print('=== SOC Scanner PWA Build ===\n')

    # Generate icons (solid #ff6b35 orange = 255,107,53)
    print('Generating icons...')
    icon192 = make_png(192, 255, 107, 53)
    icon512 = make_png(512, 255, 107, 53)
    icon180 = make_png(180, 255, 107, 53)
    print(f'  192x192: {len(icon192)} chars')
    print(f'  512x512: {len(icon512)} chars')

    # Download libraries
    print('\nDownloading libraries...')
    try:
        dexie_js = download('https://unpkg.com/dexie@4.0.8/dist/dexie.min.js')
        html5qr_js = download('https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js')
    except RuntimeError as e:
        print(f'\nERROR: {e}')
        print('Check internet connection and try again.')
        sys.exit(1)

    # Assemble index.html
    print('\nAssembling index.html...')
    icon180_data = 'data:image/png;base64,' + icon180
    html = (PART1.replace('ICON180_DATA', icon180_data)
            + dexie_js + PART2 + html5qr_js + PART3)
    print(f'  Total size: {len(html):,} bytes ({len(html)//1024} KB)')

    # Build manifest
    manifest = {
        'name': 'SOC Scanner',
        'short_name': 'SOC',
        'description': 'Quét QR/barcode mã SOC, ghi nhận số lượng, export CSV',
        'start_url': './',
        'scope': './',
        'display': 'standalone',
        'orientation': 'portrait',
        'theme_color': '#0a0a0a',
        'background_color': '#0a0a0a',
        'icons': [
            {'src': 'data:image/png;base64,' + icon192, 'sizes': '192x192', 'type': 'image/png'},
            {'src': 'data:image/png;base64,' + icon512, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
        {'src': 'data:image/png;base64,' + icon512, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}
        ]
    }

    # Write output files
    print('\nWriting output files...')
    out = OUTPUT_DIR
    files = [
        ('index.html',    html,                     'utf-8'),
        ('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2), 'utf-8'),
        ('sw.js',         SW_JS,                    'utf-8'),
        ('README.md',     README_MD,                'utf-8'),
    ]
    for fname, content, enc in files:
        path = os.path.join(out, fname)
        with open(path, 'w', encoding=enc) as f:
            f.write(content)
        print(f'  {fname}: {len(content):,} bytes')

    print('\nBuild complete!')
    print(f'  Output: {out}')
    print('\nDeploy index.html + manifest.json + sw.js to GitHub Pages.')
    print('Or serve locally: python -m http.server 8080')

if __name__ == '__main__':
    main()
