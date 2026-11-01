#!/usr/bin/env python3
"""Local OCR (Unlimited-OCR-2-4bit, in-process mlx_vlm) over archived MWPVL facility table images.
run: <venv with mlx_vlm>/bin/python -I scripts/mwpvl_local_ocr.py [--limit N] [--only substr]
Whole image first; if token cap hit or output loops, tile into overlapping horizontal strips and concatenate.
Outputs data/raw/mwpvl_wayback/ocr_local/<model>/<basename>.md + timing.jsonl (resumable)."""
import argparse, csv, json, os, re, time
from PIL import Image
import base64, urllib.request, urllib.error
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "mwpvl_wayback")
TMP = os.environ.get("MWPVL_TMP", "/tmp/mwpvl_tiles")
MAXTOK = 8192
URL = "http://127.0.0.1:8000/v1/chat/completions"; KEY = os.environ.get("OMLX_KEY", ""); STRIP_H = 1000; OVERLAP = 80
ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int); ap.add_argument("--only"); ap.add_argument("--force-tile", action="store_true")
ap.add_argument("--model", default="Unlimited-OCR-2-4bit", choices=["Unlimited-OCR-2-4bit", "DeepSeek-OCR-8bit"]); a = ap.parse_args()
MODEL = a.model; MP = os.environ.get("MWPVL_OCR_MODEL", MODEL)
OD = f"{ROOT}/ocr_local/{MODEL}"; os.makedirs(OD, exist_ok=True); os.makedirs(TMP, exist_ok=True)
rows = [r for r in csv.DictReader(open(f"{ROOT}/images/index.csv")) if r["table_type"] not in ("summary", "rest of world")]
if a.only: rows = [r for r in rows if a.only in r["local_path"]]
if a.limit: rows = rows[:a.limit]
if MODEL == "Unlimited-OCR-2-4bit":
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config
    model, proc = load(MP); cfg = load_config(MP)
def looped(t):
    ls = [l for l in t.splitlines() if l.strip()]
    if len(ls) < 30: return False
    return len(set(ls[-30:])) <= 5
def run(path):
    if MODEL == "DeepSeek-OCR-8bit":  # oMLX OpenAI-compatible server (see dean_thesis/scripts/ocr_eval_run.py)
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        body = {"model": MODEL, "temperature": 0, "max_tokens": MAXTOK, "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
            {"type": "text", "text": "<|grounding|>Convert the document to markdown."}]}]}
        req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
        for attempt in range(4):  # oMLX memory guard / transient 400s: the server's resident memory creeps up between calls,
            try: j = json.load(urllib.request.urlopen(req, timeout=1500)); break   # so unload our (idle) model to reset it, then retry
            except urllib.error.HTTPError as e:
                body_e = e.read()[:200]
                if attempt == 3: raise RuntimeError(f"{e} {body_e}")
                try: urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:8000/v1/models/{MODEL}/unload", b"{}", {"Content-Type": "application/json", "Authorization": "Bearer " + KEY}), timeout=60)
                except Exception: pass
                time.sleep(5 * (attempt + 1))
        return j["choices"][0]["message"]["content"], j.get("usage", {}).get("completion_tokens", 0) or 0
    r = generate(model, proc, apply_chat_template(proc, cfg, "Multi page parsing.", num_images=1), path, max_tokens=MAXTOK, temperature=0.0, verbose=False)
    return (r.text if hasattr(r, "text") else str(r)), getattr(r, "generation_tokens", 0) or 0
for r in rows:
    base = os.path.splitext(os.path.basename(r["local_path"]))[0]; out = f"{OD}/{base}.md"
    if os.path.exists(out) and os.path.getsize(out) > 0: continue  # empty file = earlier failed call, redo
    t0 = time.time(); mode = "whole"; ntok = 0; err = None; nstrips = 1
    try:
        try: txt, ntok = ("", 0) if a.force_tile else run(r["local_path"])
        except RuntimeError as e0:
            if "memory guard" not in str(e0): raise
            txt, ntok = "", 0  # whole-page prefill too big for oMLX memory guard: fall through to strips
        if a.force_tile or ntok >= MAXTOK - 8 or looped(txt) or not txt.strip():
            mode = "tiled"; im = Image.open(r["local_path"]).convert("RGB"); W, H = im.size; parts = []; y = 0; ntok = 0
            while y < H:
                y2 = min(H, y + STRIP_H); tp = f"{TMP}/{base}_{y}.png"; im.crop((0, y, W, y2)).save(tp)
                t, n = run(tp); parts.append(f"<!-- strip y={y}-{y2} -->\n{t}"); ntok += n
                if y2 >= H: break
                y = y2 - OVERLAP
            nstrips = len(parts); txt = "\n".join(parts)
    except Exception as e: txt, err = "", str(e)[:300]
    if not err: open(out, "w").write(txt)  # never leave an empty file for a failed call
    open(f"{OD}/timing.jsonl", "a").write(json.dumps(dict(image=base, model=MODEL, mode=mode, strips=nstrips, sec=round(time.time() - t0, 1), completion_tokens=ntok, error=err)) + "\n")
    print(base, mode, round(time.time() - t0, 1), ntok, err, flush=True)
