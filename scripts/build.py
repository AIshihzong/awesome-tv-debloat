#!/usr/bin/env python3
"""Render the project tables in README.md and README.zh-CN.md from data/projects.json.

Usage:
  python3 scripts/build.py            # rebuild tables from data/
  python3 scripts/build.py --refresh  # also refresh star counts from the GitHub API
                                      # (uses GITHUB_TOKEN if set)
  python3 scripts/build.py --check    # exit 1 if README tables are out of date
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, timezone, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "projects.json"
STARS = ROOT / "data" / "stars.json"

LABELS = {
    "en": {
        "head": "| Project | ★ | Root | Set up from | Undo | What it does |\n| --- | ---: | --- | --- | :---: | --- |",
        "root": {"no": "No", "dev": "Dev Mode", "yes": "**Yes**", "-": "–"},
        "setup": {"pc": "💻 Computer", "phone": "📱 Phone", "tv": "📺 TV only", "router": "🌐 Router / DNS", "-": "–"},
        "undo": {"yes": "✅", "partial": "⚠️", "n/a": "–", "-": "–"},
        "agent": " 🤖",
    },
    "zh": {
        "head": "| 项目 | ★ | 需 root | 在哪操作 | 可还原 | 说明 |\n| --- | ---: | --- | --- | :---: | --- |",
        "root": {"no": "不用", "dev": "开发者模式", "yes": "**要**", "-": "–"},
        "setup": {"pc": "💻 电脑", "phone": "📱 手机", "tv": "📺 只用电视", "router": "🌐 路由器 / DNS", "-": "–"},
        "undo": {"yes": "✅", "partial": "⚠️", "n/a": "–", "-": "–"},
        "agent": " 🤖",
    },
}


def fmt_stars(n):
    if n is None:
        return "–"
    if n >= 10000:
        return f"{n / 1000:.1f}k"
    return f"{n:,}"


def load():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    stars = json.loads(STARS.read_text(encoding="utf-8")) if STARS.exists() else {"stars": {}}
    return data, stars


def refresh_stars(data, stars):
    token = os.environ.get("GITHUB_TOKEN")
    for p in data["projects"]:
        req = urllib.request.Request(f"https://api.github.com/repos/{p['repo']}")
        req.add_header("Accept", "application/vnd.github+json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                info = json.load(r)
            stars["stars"][p["repo"]] = info["stargazers_count"]
            if info.get("archived"):
                print(f"note: {p['repo']} is archived", file=sys.stderr)
        except Exception as e:  # keep the old number on errors
            print(f"warn: {p['repo']}: {e}", file=sys.stderr)
    stars["updated"] = datetime.now(timezone.utc).date().isoformat()
    STARS.write_text(json.dumps(stars, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def render_section(sec, projects, stars, lang):
    L = LABELS[lang]
    rows = [p for p in projects if p["s"] == sec["id"]]
    rows.sort(key=lambda p: -(stars["stars"].get(p["repo"]) or 0))
    out = []
    intro = sec.get(f"intro_{lang}")
    if intro:
        out.append(intro)
        out.append("")
    if sec["id"] == "related":
        for p in rows:
            out.append(f"- [{p['name']}](https://github.com/{p['repo']}) ({fmt_stars(stars['stars'].get(p['repo']))} ★): {p[lang]}")
        return "\n".join(out)
    out.append(L["head"])
    for p in rows:
        name = f"[{p['name']}](https://github.com/{p['repo']})" + (L["agent"] if p.get("agent") else "")
        setup = " · ".join(L["setup"][s] for s in p["setup"].split(","))
        out.append(
            f"| {name} | {fmt_stars(stars['stars'].get(p['repo']))} | {L['root'][p['root']]} | {setup} | {L['undo'][p['undo']]} | {p[lang]} |"
        )
    return "\n".join(out)


def render_file(path, data, stars, lang):
    text = path.read_text(encoding="utf-8")
    for sec in data["sections"]:
        body = render_section(sec, data["projects"], stars, lang)
        pat = re.compile(rf"(<!-- BEGIN {sec['id']} -->\n).*?(<!-- END {sec['id']} -->)", re.S)
        if not pat.search(text):
            sys.exit(f"{path.name}: missing markers for {sec['id']}")
        text = pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)
    count = sum(1 for p in data["projects"] if p["s"] != "related")
    text = re.sub(r"<!-- COUNT -->\d+<!-- /COUNT -->", f"<!-- COUNT -->{count}<!-- /COUNT -->", text)
    text = re.sub(r"<!-- DATE -->[\d-]+<!-- /DATE -->", f"<!-- DATE -->{stars.get('updated', data['checked'])}<!-- /DATE -->", text)
    return text


def main():
    data, stars = load()
    repos = [p["repo"] for p in data["projects"]]
    dupes = {r for r in repos if repos.count(r) > 1}
    if dupes:
        sys.exit(f"duplicate entries: {sorted(dupes)}")
    ids = {s["id"] for s in data["sections"]}
    for p in data["projects"]:
        if p["s"] not in ids:
            sys.exit(f"{p['repo']}: unknown section {p['s']}")
    if "--refresh" in sys.argv:
        refresh_stars(data, stars)
    stale = False
    for name, lang in (("README.md", "en"), ("README.zh-CN.md", "zh")):
        path = ROOT / name
        new = render_file(path, data, stars, lang)
        if new != path.read_text(encoding="utf-8"):
            stale = True
            if "--check" not in sys.argv:
                path.write_text(new, encoding="utf-8")
    if "--check" in sys.argv and stale:
        sys.exit("README tables are out of date: run python3 scripts/build.py")


if __name__ == "__main__":
    main()
