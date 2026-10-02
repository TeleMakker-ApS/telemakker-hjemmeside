#!/usr/bin/env python3
"""
Bygger sitemap.xml ud fra de sider, der faktisk ligger i repoet.

Koeres automatisk af .github/workflows/sitemap.yml ved hvert push til main,
saa en ny side kommer med af sig selv, og en rettet side faar ny dato.
Kan ogsaa koeres i haanden:  python3 vaerktoej/byg-sitemap.py

Regler:
  - Hver .html-fil bliver en adresse. mappe/index.html -> /mappe/
  - lastmod er datoen for sidste commit, der aendrede netop den fil.
  - En side med <meta name="robots" content="noindex"> kommer IKKE med.
  - Mapper i UDELAD kommer ikke med (vaerktoej, skjulte mapper osv.).
  - priority og changefreq udelades med vilje: Google laeser dem ikke.
"""
import pathlib
import re
import subprocess
import sys
from datetime import date
from xml.sax.saxutils import escape

DOMAENE = "https://www.telemakker.dk"
ROD = pathlib.Path(__file__).resolve().parent.parent
UDELAD = {"vaerktoej", "skrift", "billeder", "node_modules"}
NOINDEX = re.compile(
    r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', re.I
)


def sidste_aendring(fil: pathlib.Path) -> str:
    try:
        ud = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(fil.relative_to(ROD))],
            cwd=ROD, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if ud:
            return ud
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return date.today().isoformat()  # ny fil, endnu ikke committet


def adresse(fil: pathlib.Path) -> str:
    sti = fil.relative_to(ROD).as_posix()
    if sti == "index.html":
        return DOMAENE + "/"
    if sti.endswith("/index.html"):
        return f"{DOMAENE}/{sti[: -len('index.html')]}"
    return f"{DOMAENE}/{sti}"


def sider():
    for fil in sorted(ROD.rglob("*.html")):
        dele = fil.relative_to(ROD).parts
        if any(d.startswith(".") or d in UDELAD for d in dele):
            continue
        if fil.name == "404.html":
            continue
        if NOINDEX.search(fil.read_text(encoding="utf-8", errors="ignore")):
            continue
        yield fil


def main() -> int:
    linjer = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- Bygget automatisk af vaerktoej/byg-sitemap.py. Ret ikke i haanden. -->",
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    # Forsiden foerst, resten alfabetisk
    alle = sorted(sider(), key=lambda f: (adresse(f) != DOMAENE + "/", adresse(f)))
    for fil in alle:
        linjer += [
            "  <url>",
            f"    <loc>{escape(adresse(fil))}</loc>",
            f"    <lastmod>{sidste_aendring(fil)}</lastmod>",
            "  </url>",
        ]
    linjer.append("</urlset>")
    (ROD / "sitemap.xml").write_text("\n".join(linjer) + "\n", encoding="utf-8")
    print(f"sitemap.xml: {len(alle)} sider")
    return 0


if __name__ == "__main__":
    sys.exit(main())
