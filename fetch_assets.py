#!/usr/bin/env python3
"""从 Wikimedia Commons 抓取 CC 授权素材（走 curl 通道，规避 urllib 限流）。"""
import json
import os
import re
import subprocess
import time
import urllib.parse

ASSETS = "/workspace/mooncake/assets"
UA = "ResumelessBot/1.0"

# (输出文件名, 检索词, 标题必须包含的关键字)
PICKS = [
    ("shot01_crack.jpg", "salted egg yolk mooncake", "quarter"),
    ("shot02_pattern.jpg", "mooncake", "WING WAH"),
    ("shot03_cross.jpg", "salted egg yolk mooncake", "double yolk"),
    ("shot04_festival.jpg", "mid-autumn festival", "Victoria Park"),
    ("shot05_bite.jpg", "salted egg yolk mooncake", "lotus paste and salted egg yolk fill"),
    ("shot06_tea.jpg", "oolong tea cup chinese", "zhong"),
    ("shot07_hero.jpg", "mooncake", "Mooncake.jpg"),
]


def curl(url, dest=None, timeout=90):
    cmd = ["curl", "-sL", "-A", UA, "--max-time", str(timeout)]
    if dest:
        cmd += ["-o", dest]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True)
    return out.stdout if dest is None else None


def api(query, limit=25):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": 1600, "format": "json",
    })
    for attempt in range(4):
        raw = curl(url)
        try:
            return json.loads(raw)
        except Exception:
            print(f"    api retry {attempt+1}/4")
            time.sleep(4)
    return {"query": {}}


credits = []
for fname, query, keyword in PICKS:
    d = api(query)
    pages = d.get("query", {}).get("pages", {})
    hit = None
    for p in pages.values():
        if keyword.lower() in p["title"].lower():
            hit = p
            break
    if hit is None:
        print(f"[MISS] {fname} (query={query!r} keyword={keyword!r})")
        time.sleep(3)
        continue
    ii = hit["imageinfo"][0]
    em = ii.get("extmetadata", {})
    url = ii.get("thumburl") or ii["url"]
    dest = os.path.join(ASSETS, fname)
    curl(url, dest=dest)
    size = os.path.getsize(dest) if os.path.exists(dest) else 0
    if size < 5000:
        print(f"[FAIL] {fname} 下载异常 size={size}")
        time.sleep(3)
        continue
    artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "")).strip()
    credits.append({
        "file": fname,
        "title": hit["title"],
        "author": artist,
        "license": em.get("LicenseShortName", {}).get("value", "?"),
        "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(hit["title"].replace(" ", "_")),
        "bytes": size,
    })
    print(f"[OK] {fname} <- {hit['title'][:52]} | {credits[-1]['license']} | {size}B")
    time.sleep(3)

with open(os.path.join(ASSETS, "credits.json"), "w") as f:
    json.dump(credits, f, ensure_ascii=False, indent=2)
print(f"\n下载完成 {len(credits)}/{len(PICKS)}")
