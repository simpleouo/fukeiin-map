import re, json, time, sys, html, os

from urllib.request import urlopen, Request
BASE = "https://www.post.japanpost.jp/enjoy/culture/stamp/fuke/"
src, dst = sys.argv[1], sys.argv[2]
items = list({i["id"]: i for i in json.load(open(src))}.values())
done = json.load(open(dst)) if os.path.exists(dst) else {}
def get(url):
    for i in range(4):
        try:
            with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0 (personal stamp map)"}), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            print("retry", url, e, file=sys.stderr, flush=True); time.sleep(3 * (i + 1))
    return None
def text(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
for n, it in enumerate(items):
    k = str(it["id"])
    if k in done: continue
    p = get(f"{BASE}detail.php?id={k}")
    if p is None: continue
    t = text(p)
    def between(a, b):
        m = re.search(re.escape(a) + r"\s*(.*?)\s*" + b, t); return m.group(1) if m else None
    rec = dict(it)
    rec.update(start=between("使用開始日", "(?:意匠図案説明|廃止|図案作成者名)"),
               desc=between("意匠図案説明", "(?:図案作成者名|郵便局情報)"),
               designer=between("図案作成者名", "郵便局情報"),
               address=between("開設場所", "※"),
               abolish=between("廃止日", "(?:意匠図案説明|図案作成者名|郵便局情報)"))
    m = re.search(r'<img src="(/kitte_hagaki/stamp/preview/img/fuke/[^"]+)"', p); rec["image"] = m and m.group(1)
    done[k] = rec
    if n % 25 == 0:
        json.dump(done, open(dst, "w"), ensure_ascii=False); print(n, "/", len(items), flush=True)
    time.sleep(1)
json.dump(done, open(dst, "w"), ensure_ascii=False, indent=1); print("done", len(done))
