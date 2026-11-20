"""Clean scraped detail records, group by post office, geocode with GSI, write data/tokyo.json."""
import json, re, time, sys, os, urllib.request, urllib.parse, unicodedata
from datetime import date
detail = json.load(open(sys.argv[1])); out = sys.argv[2]
cache_f = "raw/geocode_cache.json"
cache = json.load(open(cache_f)) if os.path.exists(cache_f) else {}
BASE = "https://www.post.japanpost.jp"
def geocode(addr):
    if addr in cache: return cache[addr]
    url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + urllib.parse.quote(addr)
    for i in range(4):
        try:
            res = json.load(urllib.request.urlopen(url, timeout=30)); break
        except Exception as e:
            print("retry", addr, e, file=sys.stderr); time.sleep(2 * (i + 1))
    else: return None
    time.sleep(0.5)
    cache[addr] = res[0]["geometry"]["coordinates"] + [res[0]["properties"]["title"]] if res else None
    return cache[addr]
def ymd(s):
    m = s and re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", s)
    return m and f"{int(m[1]):04d}-{int(m[2]):02d}-{int(m[3]):02d}"
# Typos / ambiguous forms in the official addresses that confuse the geocoder
ADDR_FIX = {"東京都千代区": "東京都千代田区", "東京都西多摩郡日原": "東京都西多摩郡奥多摩町日原",
            "東京都三宅村": "東京都三宅島三宅村", "伊ヶ谷": "伊ケ谷"}
offices = {}
for r in detail.values():
    addr_full = (r.get("address") or "").strip()
    m = re.match(r"〒?\s*(\d{3}-\d{4})?\s*(.*)", addr_full)
    zipc, addr = m[1], unicodedata.normalize("NFKC", m[2]).replace("東京都東京都", "東京都")
    addr = re.sub(r"(?<=\d)[ー－―‐](?=\d)", "-", addr)
    for a, b in ADDR_FIX.items(): addr = addr.replace(a, b)
    designer, note = r.get("designer"), None
    if designer and "備考" in designer:
        designer, note = [s.strip() for s in designer.split("備考", 1)]
    desc = r.get("desc")
    if desc and "備考" in desc and not note:
        desc, note = [x.strip() for x in desc.split("備考", 1)]
    upcoming = ymd(r.get("posting")); ending = ymd(r.get("obsolete"))
    d = {"id": r["id"], "start": ymd(r.get("start")) or ymd(r.get("date")), "desc": desc,
         "designer": designer or None, "note": note, "endsOn": ending, "startsOn": upcoming,
         "url": f"{BASE}/enjoy/culture/stamp/fuke/detail.php?id={r['id']}",
         "thumb": BASE + r["thumb"].replace("/./", "/") if r.get("thumb") else None}
    key = (r["name"], addr)
    o = offices.setdefault(key, {"name": r["name"], "zip": zipc, "address": addr, "designs": []})
    o["designs"].append(d)
res, fails = [], []
for n, o in enumerate(offices.values()):
    g = geocode(o["address"])
    if n % 50 == 0:
        json.dump(cache, open(cache_f, "w"), ensure_ascii=False); print(n, len(offices), flush=True)
    if not g: fails.append(o["address"]); continue
    o["lng"], o["lat"] = round(g[0], 6), round(g[1], 6)
    o["approx"] = not re.search(r"番|号|地$", g[2])
    m = re.match(r"東京都(.+?[区市町村])", o["address"]); o["area"] = m and m[1]
    o["id"] = min(d["id"] for d in o["designs"])
    o["designs"].sort(key=lambda d: d["start"] or "")
    res.append(o)
json.dump(cache, open(cache_f, "w"), ensure_ascii=False)
res.sort(key=lambda o: (o["area"] or "", o["name"]))
json.dump({"source": "日本郵便 風景印 (www.post.japanpost.jp/enjoy/culture/stamp/fuke/)",
           "updated": date.today().isoformat(), "pref": "東京都", "offices": res},
          open(out, "w"), ensure_ascii=False, separators=(",", ":"))
print("approx", sum(o["approx"] for o in res), [o["address"] for o in res if o["approx"]])
print("offices", len(res), "designs", sum(len(o["designs"]) for o in res), "geocode fails", len(fails), fails[:10])
