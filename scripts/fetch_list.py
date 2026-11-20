import re, json, time, sys, urllib.request, html
BASE = "https://www.post.japanpost.jp/enjoy/culture/stamp/fuke/"
def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (personal stamp map)"}), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            print("retry", url, e, file=sys.stderr); time.sleep(2 * (i + 1))
    raise SystemExit("failed " + url)
POST = re.compile(r'<div class="post">(.*?)</div><!-- /.post -->', re.S)
def parse(page):
    out = []
    for b in POST.findall(page):
        g = lambda p: (m := re.search(p, b, re.S)) and html.unescape(m.group(1).strip())
        out.append({"id": int(g(r'detail\.php\?id=(\d+)')), "date": g(r'class="date">([^<]*)'),
                    "name": g(r'class="title">([^<]*)'), "thumb": g(r'<img src="([^"]*)"'),
                    "obsolete": g(r'class="obsolescent">([^<]*)'), "posting": g(r'class="posting">([^<]*)'),
                    "pref": g(r'class="pre">([^<]*)')})
    return out
items = parse(get(BASE + "result_pre.php?pref_id=13"))
page = 1
while True:
    time.sleep(1)
    got = parse(get(f"{BASE}item.php?pref_id=13&page={page}"))
    print("page", page, len(got), file=sys.stderr)
    if not got: break
    items += got; page += 1
    if page > 40: break
json.dump(items, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(len(items), "items,", len({i['id'] for i in items}), "unique ids,", len({i['name'] for i in items}), "unique names")
