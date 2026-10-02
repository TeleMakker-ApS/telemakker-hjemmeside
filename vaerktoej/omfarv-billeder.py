#!/usr/bin/env python3
"""
Farver de groenne billeder om til de nye brand-farver.

Koeres af .github/workflows/omfarv.yml (eller i haanden med Pillow):
    python3 vaerktoej/omfarv-billeder.py

HVORFOR: siden skiftede 2. oktober 2026 fra groen til antracit og birk.
Skaermbillederne af tilbuddet og sagslisten, logoet og delingsbilledet
var stadig groenne.

HVORDAN: kun pixels, der ER groenne (farvetone mellem gul-groen og
blaa-groen, og tydeligt farvede), aendres. De faar en farve paa skalaen
fra antracit til lys sandtone med samme lyshed som foer, saa en moerk
groen bjaelke bliver antracit, og en lysegroen etiket bliver lys sand.
Tekst, hvidt, sort og priser roeres ikke. Kanterne blandes efter hvor
groen pixlen var, saa skriften ikke faar takker.

Koeres den igen, sker der intet: der er ikke mere groent at finde.
"""
import colorsys
import pathlib

from PIL import Image

ROD = pathlib.Path(__file__).resolve().parent.parent
FILER = ["billeder/tilbud-1.png", "billeder/tilbud-2.png", "billeder/sagsliste.png",
         "billeder/deling.png", "billeder/logo.png"]

MOERK = (0x24, 0x28, 0x2C)   # antracit
LYS = (0xF2, 0xEE, 0xE7)     # lys sandtone
BIRK = (0xE3, 0xC9, 0x9F)    # accent, som "Makker" i headeren
L_MOERK, L_LYS = 0.24, 0.95  # lyshed, der svarer til hver ende af skalaen


def er_groen(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return 80 / 360 < h < 190 / 360 and s > 0.08, l, s


def ny_farve(r, g, b):
    groen, l, s = er_groen(r, g, b)
    if not groen:
        return None
    if s > 0.30 and 0.55 < l < 0.85:
        maal = BIRK  # den lyse mynte-accent bliver birk
    else:
        t = min(1.0, max(0.0, (l - L_MOERK) / (L_LYS - L_MOERK)))
        maal = tuple(round(m + (y - m) * t) for m, y in zip(MOERK, LYS))
    vaegt = min(1.0, (s - 0.08) / 0.17)  # kanterne blandes, saa skriften ikke faar takker
    ny = tuple(round(o + (n - o) * vaegt) for o, n in zip((r, g, b), maal))
    # Er blandingen stadig groen, tages maalfarven helt; saa er en
    # ny koersel altid uden virkning.
    return maal if er_groen(*ny)[0] else ny


def main() -> None:
    for navn in FILER:
        fil = ROD / navn
        im = Image.open(fil)
        alfa = im.getchannel("A") if im.mode in ("RGBA", "LA") else None
        rgb = im.convert("RGB")
        px = rgb.load()
        cache, aendret = {}, 0
        for y in range(rgb.height):
            for x in range(rgb.width):
                p = px[x, y]
                if p not in cache:
                    cache[p] = ny_farve(*p)
                n = cache[p]
                if n is not None and n != p:
                    px[x, y] = n
                    aendret += 1
        if aendret:
            ud = rgb.convert("RGBA") if alfa else rgb
            if alfa:
                ud.putalpha(alfa)
            ud.save(fil, optimize=True)
        print(f"{navn}: {aendret} pixels omfarvet")


if __name__ == "__main__":
    main()
