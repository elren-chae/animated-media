#!/usr/bin/env python3
"""
fetch_posters.py
Fetches movie & TV show posters for titles listed in index.html,
saving images into the `posters/` directory and updating `posters_map.json`.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTERS_DIR = os.path.join(BASE_DIR, "posters")
MAP_FILE = os.path.join(BASE_DIR, "posters_map.json")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")

os.makedirs(POSTERS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "MyAnimationWall/1.0 (https://github.com/user/animation-wall; contact@animationwall.local)"
}

# Specific overrides or aliases for titles that differ from standard search
ALIASES = {
    "The Magic Schoolbus (신나는 스쿨버스)": {"query": "The Magic School Bus", "tvmaze": "The Magic School Bus"},
    "Avatar 2": {"query": "Avatar: The Way of Water", "wiki": "Avatar: The Way of Water"},
    "Howl’s Moving Castle (하울의 움직이는 성)": {"query": "Howl's Moving Castle", "wiki": "Howl's Moving Castle (film)"},
    "Spirited Away 센과 치히로의 행방불명": {"query": "Spirited Away", "wiki": "Spirited Away"},
    "캐릭캐릭 체인지": {"query": "Shugo Chara!", "tvmaze": "Shugo Chara!"},
    "The Hunchback of Notre Dam": {"query": "The Hunchback of Notre Dame 1996", "wiki": "The Hunchback of Notre Dame (1996 film)"},
    "Tinkerbell: Secret of the Wings": {"query": "Secret of the Wings", "wiki": "Secret of the Wings"},
    "Tinker Bell and the Legend of the NeverBeast": {"query": "Legend of the NeverBeast", "wiki": "Legend of the NeverBeast"},
    "Kpop Demon Hunters": {"query": "K-Pop Demon Hunters", "wiki": "KPop Demon Hunters"},
    "Seabeast": {"query": "The Sea Beast", "wiki": "The Sea Beast (2022 film)"},
    "Monster University": {"query": "Monsters University", "wiki": "Monsters University"},
    "Monster Inc": {"query": "Monsters, Inc.", "wiki": "Monsters, Inc."}
}

def slugify(title):
    cleaned = re.sub(r'[\(\)]', '', title)
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '-', cleaned.strip().lower())
    slug = cleaned.strip('-')
    return slug or "poster-" + str(abs(hash(title)) % 100000)

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def download_image(url, target_path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        if len(content) < 1000:
            raise Exception("File too small")
        with open(target_path, "wb") as f:
            f.write(content)

def try_tvmaze(query):
    url = f"https://api.tvmaze.com/singlesearch/shows?q={urllib.parse.quote(query)}"
    data = fetch_json(url)
    if data and "image" in data and data["image"]:
        return data["image"].get("original") or data["image"].get("medium")
    return None

def try_itunes(query, entity=None):
    ent_param = f"&entity={entity}" if entity else ""
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}{ent_param}&limit=3"
    data = fetch_json(url)
    if data and data.get("resultCount", 0) > 0:
        for item in data["results"]:
            if "artworkUrl100" in item:
                return item["artworkUrl100"].replace("100x100bb.jpg", "600x900bb.jpg").replace("100x100", "600x900")
    return None

def try_wiki(title_or_query):
    safe = urllib.parse.quote(title_or_query.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe}"
    time.sleep(0.4)
    data = fetch_json(url)
    if not data:
        return None
    if "originalimage" in data and "source" in data["originalimage"]:
        return data["originalimage"]["source"]
    if "thumbnail" in data and "source" in data["thumbnail"]:
        return data["thumbnail"]["source"]
    return None

def parse_titles_from_index():
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"const RAW = \[(.*?)\]\.map", content, re.DOTALL)
    if not match:
        return []
    lines = [l.strip() for l in match.group(1).split("\n") if l.strip().startswith("[")]
    titles = []
    for line in lines:
        try:
            arr = json.loads(line.rstrip(",") if not line.endswith(",") else line[:-1])
            titles.append({"title": arr[0], "type": arr[1] if len(arr) > 1 else ""})
        except Exception:
            pass
    return titles

def main():
    titles = parse_titles_from_index()
    print(f"Found {len(titles)} titles in index.html.")

    mapping = {}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            mapping = json.load(f)

    for item in titles:
        raw = item["title"]
        mtype = item["type"]
        slug = slugify(raw)
        filename = f"{slug}.jpg"
        filepath = os.path.join(POSTERS_DIR, filename)
        rel_path = f"posters/{filename}"

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            mapping[raw] = rel_path
            continue

        alias = ALIASES.get(raw, {})
        query = alias.get("query", raw)
        wiki_title = alias.get("wiki", query)
        tvmaze_q = alias.get("tvmaze", query)

        print(f"Fetching poster for: {raw}...")
        img_url = None

        if mtype == "TV Series" or "tvmaze" in alias:
            img_url = try_tvmaze(tvmaze_q)

        if not img_url and wiki_title:
            img_url = try_wiki(wiki_title)

        if not img_url:
            img_url = try_itunes(query, entity="movie" if mtype == "Movie" else None)

        if not img_url and mtype != "Movie":
            img_url = try_tvmaze(query)

        if img_url:
            try:
                download_image(img_url, filepath)
                mapping[raw] = rel_path
                print(f"  -> Saved {filename} ({os.path.getsize(filepath)} bytes)")
            except Exception as e:
                print(f"  -> Download failed: {e}")
        else:
            print("  -> Could not find poster.")

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"Updated posters map: {len(mapping)} / {len(titles)} titles have posters.")

if __name__ == "__main__":
    main()

