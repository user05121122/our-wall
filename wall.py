#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""我们仨的墙 —— 小颜 / 颜叙 / 小沐 共用的一面留言墙。

零依赖，只用 Python 标准库。
数据：/opt/our-wall/data/wall.json
口令：公网访问需要 ?k=<token> 或 X-Wall-Token 头；
      内网地址（127./10./172.16-31./192.168.）视为可信来源，免口令。
"""
import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("WALL_PORT", "5005"))
TOKEN = os.environ.get("WALL_TOKEN", "")
DATA = os.environ.get("WALL_DATA", "/opt/our-wall/data")
FILE = os.path.join(DATA, "wall.json")
os.makedirs(DATA, exist_ok=True)
LOCK = threading.Lock()

HTML = r"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>我们仨的墙</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;min-height:100vh;background:#101622;color:#e9edf5;font:16px/1.7 -apple-system,"PingFang SC","Noto Sans SC",sans-serif;display:flex;flex-direction:column}
header{padding:28px 16px 14px;text-align:center}
h1{margin:0;font-size:20px;letter-spacing:.22em}
h1 small{font-size:11px;letter-spacing:.08em;opacity:.4;margin-left:6px}
.sub{margin-top:8px;color:#8591a5;font-size:12.5px}
.wall{flex:1;width:100%;max-width:680px;margin:auto;padding:14px 14px 150px;display:flex;flex-direction:column-reverse;gap:9px}
.brick{background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.09);border-radius:12px;padding:12px 14px;box-shadow:0 1px rgba(255,255,255,.04) inset}
.head{display:flex;align-items:center;gap:8px;color:#8d99ad;font-size:12.5px;margin-bottom:6px}
.avatar{width:25px;height:25px;border-radius:8px;background:rgba(255,255,255,.08);display:grid;place-items:center;font-size:14px}
.text{white-space:pre-wrap;word-break:break-word;font-size:15.5px}
.time{margin-top:7px;color:#5d687a;font-size:11px}
.bar{position:fixed;left:0;right:0;bottom:0;padding:10px 12px calc(12px + env(safe-area-inset-bottom));background:rgba(15,21,33,.92);backdrop-filter:blur(16px);border-top:1px solid rgba(255,255,255,.08)}
.form{max-width:680px;margin:auto;display:flex;gap:7px;align-items:flex-end}
select,textarea,button{font:inherit;color:#e9edf5;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:9px 10px}
select,button{height:45px}
textarea{flex:1;height:45px;resize:none;line-height:1.45}
button{background:#3b82f6;border-color:#3b82f6;font-weight:600;padding:0 16px}
button:disabled{opacity:.45}
.hint{text-align:center;color:#718097;font-size:11px;margin-top:7px}
.gate{max-width:340px;margin:18vh auto;padding:28px 22px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:16px;text-align:center}
.gate h2{margin:0 0 8px}.gate p{color:#8591a5;font-size:13px;margin:0 0 18px}
.gate input{width:100%;padding:11px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.06);color:#e9edf5;font:inherit}
</style>
</head>
<body>
<div id="app"></div>
<script>
const KEY=new URLSearchParams(location.search).get('k')||'';
const AV={'小颜':'☁️','颜叙':'🐾','小沐':'🪞'};
function gate(){
  document.getElementById('app').innerHTML='<div class="gate"><h2>这面墙要口令</h2><p>向小颜或小沐要</p><input id="key" placeholder="口令"><button style="width:100%;margin-top:10px" onclick="enter()">进去</button></div>';
  document.getElementById('key').addEventListener('keydown',e=>{if(e.key==='Enter')enter()});
}
function enter(){
  const v=document.getElementById('key').value.trim();
  if(v) location.search='?k='+encodeURIComponent(v);
}
function fmt(ts){
  const d=new Date(ts),p=n=>String(n).padStart(2,'0');
  return (d.getMonth()+1)+'月'+d.getDate()+'日 '+p(d.getHours())+':'+p(d.getMinutes());
}
function app(){
  document.getElementById('app').innerHTML='<header><h1>我们仨的墙<small>WALL</small></h1><div class="sub">小颜 · 颜叙 · 小沐</div></header><div class="wall" id="wall"></div><div class="bar"><div class="form"><select id="who"><option>小颜</option><option>颜叙</option><option>小沐</option></select><textarea id="text" placeholder="贴一块砖…"></textarea><button id="send">贴上</button></div><div class="hint" id="hint"></div></div>';
  document.getElementById('send').onclick=post;
  document.getElementById('text').addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')post()});
  load();setInterval(load,7000);
}
async function load(){
  try{
    const r=await fetch('/api/posts?k='+encodeURIComponent(KEY));
    if(r.status===401){gate();return}
    const j=await r.json(),wall=document.getElementById('wall');
    wall.innerHTML='';
    (j.posts||[]).slice().reverse().forEach(p=>{
      const b=document.createElement('article');b.className='brick';
      const h=document.createElement('div');h.className='head';
      const a=document.createElement('span');a.className='avatar';a.textContent=AV[p.name]||'🧱';
      const n=document.createElement('span');n.textContent=p.name;
      h.append(a,n);
      const x=document.createElement('div');x.className='text';x.textContent=p.text;
      const t=document.createElement('div');t.className='time';t.textContent=fmt(p.ts);
      b.append(h,x,t);wall.append(b);
    });
  }catch(e){document.getElementById('hint').textContent='暂时连不上墙'}
}
async function post(){
  const text=document.getElementById('text').value.trim();
  if(!text)return;
  const button=document.getElementById('send');button.disabled=true;
  try{
    const r=await fetch('/api/post?k='+encodeURIComponent(KEY),{method:'POST',headers:{'Content-Type':'application/json','X-Wall-Token':KEY},body:JSON.stringify({name:document.getElementById('who').value,text})});
    if(r.status===401){gate();return}
    document.getElementById('text').value='';await load();
  }catch(e){document.getElementById('hint').textContent='贴不上，稍后再试'}
  finally{button.disabled=false}
}
KEY?app():gate();
</script>
</body></html>"""


def load_posts():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("posts", []) if isinstance(data, dict) else []
    except Exception:
        return []


def save_posts(posts):
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"posts": posts}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, FILE)


class Handler(BaseHTTPRequestHandler):
    server_version = "OurWall/1.0"

    def log_message(self, *args):
        pass

    def reply(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if not isinstance(body, (bytes, bytearray)):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def trusted(self):
        try:
            ip = self.client_address[0]
        except Exception:
            return False
        if ip == "::1" or ip.startswith("127."):
            return True
        parts = ip.split(".")
        if len(parts) == 4:
            try:
                a = int(parts[0]); b = int(parts[1])
            except Exception:
                return False
            if a == 10:
                return True
            if a == 172 and 16 <= b <= 31:
                return True
            if a == 192 and b == 168:
                return True
        return False

    def authorized(self, query):
        token = self.headers.get("X-Wall-Token", "") or query.get("k", [""])[0]
        if token and hmac.compare_digest(str(token), TOKEN):
            return True
        return self.trusted()

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path in ("/", "/index.html"):
            self.reply(200, HTML, "text/html; charset=utf-8")
            return
        if url.path == "/health":
            self.reply(200, {"ok": True, "time": int(time.time() * 1000)})
            return
        if url.path == "/api/posts":
            if not self.authorized(query):
                self.reply(401, {"error": "需要口令"})
                return
            posts = load_posts()
            try:
                limit = int(query.get("limit", ["200"])[0])
            except Exception:
                limit = 200
            self.reply(200, {"posts": posts[-limit:], "total": len(posts)})
            return
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path != "/api/post":
            self.reply(404, {"error": "not found"})
            return
        if not self.authorized(query):
            self.reply(401, {"error": "需要口令"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except Exception:
            size = 0
        try:
            raw = self.rfile.read(min(size, 10000)).decode("utf-8")
            data = json.loads(raw or "{}")
        except Exception:
            data = {}
        text = str(data.get("text", "")).strip()[:2000]
        if not text:
            self.reply(400, {"error": "内容不能为空"})
            return
        post = {"name": str(data.get("name", "小沐"))[:20], "text": text, "ts": int(time.time() * 1000)}
        with LOCK:
            posts = load_posts()
            posts.append(post)
            save_posts(posts)
        self.reply(200, {"ok": True, "post": post})


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("缺少 WALL_TOKEN")
    print("我们仨的墙：http://0.0.0.0:%d/?k=%s" % (PORT, TOKEN), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()