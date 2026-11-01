#!/usr/bin/env python3
"""Rebuild index.html from the issue files in issues/.

Issue files are named NNN-YYYY-MM-DD.html. The headline blurb for each
entry is taken from the issue's masthead dek (<p class="dek">...</p>).
Run from the repo root:  python3 scripts/build_index.py
"""
import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ISSUES = ROOT / "issues"
NAME_RE = re.compile(r"^(\d{3})-(\d{4})-(\d{2})-(\d{2})\.html$")
DEK_RE = re.compile(r'<p class="dek">(.*?)</p>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def dek_of(path: Path) -> str:
    m = DEK_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return ""
    text = html.unescape(TAG_RE.sub("", m.group(1))).strip()
    return " ".join(text.split())


def entries():
    out = []
    for p in ISSUES.glob("*.html"):
        m = NAME_RE.match(p.name)
        if not m:
            continue
        num, y, mo, d = m.groups()
        out.append((int(num), date(int(y), int(mo), int(d)), p))
    return sorted(out, reverse=True)


def render(items) -> str:
    rows = []
    for num, d, p in items:
        label = d.strftime("%b %-d, %Y")
        rows.append(
            f'<li><a href="issues/{p.name}"><span class="num">No. {num:03d}</span>'
            f'<span class="date">{label}</span></a>'
            f'<p>{html.escape(dek_of(p))}</p></li>'
        )
    latest = f'issues/{items[0][2].name}' if items else "#"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Harness Log · Archive</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--paper:#F4F5F0;--ink:#1B2027;--soft:#4A5159;--rule:#D9DAD2;--card:#FFFFFF;--blue:#2B5EA8;--blue-soft:#EAF0F8}}
@media (prefers-color-scheme: dark){{:root{{--paper:#12161C;--ink:#E8E6DE;--soft:#A3A9AF;--rule:#2A313A;--card:#171C23;--blue:#7BAEE8;--blue-soft:#1B2A3C;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 'IBM Plex Sans',-apple-system,sans-serif;padding:2.5rem 16px 3rem}}
.wrap{{max-width:46rem;margin:0 auto}}
.kicker{{font:600 .72rem 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--soft)}}
h1{{font:700 2.6rem 'Spectral',Georgia,serif;margin:.3rem 0 .5rem}}
.masthead{{border-bottom:3px solid var(--ink);padding-bottom:1.25rem;margin-bottom:2rem}}
.latest{{display:inline-block;font:.82rem 'IBM Plex Mono',monospace;color:var(--blue)}}
ul{{list-style:none;margin:0;padding:0}}
li{{border-bottom:1px solid var(--rule);padding:1rem 0}}
li a{{display:flex;gap:1rem;text-decoration:none;color:var(--blue);font:600 .85rem 'IBM Plex Mono',monospace}}
li .date{{color:var(--soft);font-weight:400}}
li p{{margin:.35rem 0 0;font-family:'Spectral',Georgia,serif;font-size:1.02rem;color:var(--ink)}}
footer{{margin-top:2.5rem;font:.72rem 'IBM Plex Mono',monospace;color:var(--soft)}}
@media (max-width:480px){{h1{{font-size:2.05rem}}}}
</style></head>
<body><div class="wrap">
<div class="masthead">
<div class="kicker">Prompt Engineering · Harness Engineering · Daily</div>
<h1>The Harness Log</h1>
<a class="latest" href="{latest}">Read the latest issue →</a>
</div>
<ul>
{chr(10).join(rows)}
</ul>
<footer>{len(items)} issue{'s' if len(items) != 1 else ''} archived</footer>
</div></body></html>
"""


if __name__ == "__main__":
    items = entries()
    (ROOT / "index.html").write_text(render(items), encoding="utf-8")
    print(f"index.html: {len(items)} issues")
