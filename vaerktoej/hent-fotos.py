#!/usr/bin/env python3
"""
Henter materialefotoene til forsiden og goer dem lette.

Koeres af .github/workflows/fotos.yml (eller i haanden med Pillow
installeret):  python3 vaerktoej/hent-fotos.py

HVAD DEN GOER med hvert foto:
  1. Henter det fra Unsplash. Unsplash-licensen tillader kommerciel brug
     uden kreditering; fotografen staar alligevel herunder.
  2. Lægger det moerke sloer ind I selve billedet. Saa skal browseren
     ikke tegne et lag ovenpaa, og et moerkt billede fylder langt mindre.
  3. Gemmer det som WebP i to bredder: 1600 px til computer og 800 px
     til mobil. Telefonen henter kun den lille.

Vil I skifte et foto, saa ret id'et herunder og koer den igen.
Navnene maa ikke aendres uden at rette dem i index.html ogsaa.
"""
import io
import pathlib
import urllib.request

from PIL import Image

ROD = pathlib.Path(__file__).resolve().parent.parent
UD = ROD / "billeder"

# navn, Unsplash-id, hvor moerkt sloeret er (0 = intet, 1 = sort)
FOTOS = [
    ("rundsav",      "photo-1683115099860-5379ac101bce", 0.76),  # toppen
    ("mursten",      "photo-1495578942200-c5f5d2137def", 0.57),  # regnestykket
    ("trae",         "photo-1620671716215-b2c6609996fe", 0.75),  # det, kunden faar
    ("vaerktoej",    "photo-1683115099191-51e617fc5ff1", 0.71),  # det vi ikke goer
    ("haandvaerker", "photo-1687422810663-c316494f725a", 0.72),  # stadig dit tilbud
    ("planker",      "photo-1644925757334-d0397c01518c", 0.68),  # vi ringer til dig
]
SLOER = (18, 18, 18)
BREDDER = {1600: 58, 800: 60}  # bredde: WebP-kvalitet


def hent(foto_id: str) -> Image.Image:
    url = f"https://images.unsplash.com/{foto_id}?fm=jpg&w=1600&q=85"
    req = urllib.request.Request(url, headers={"User-Agent": "telemakker.dk-byg"})
    with urllib.request.urlopen(req, timeout=60) as svar:
        return Image.open(io.BytesIO(svar.read())).convert("RGB")


def main() -> None:
    for navn, foto_id, styrke in FOTOS:
        billede = hent(foto_id)
        sloer = Image.new("RGB", billede.size, SLOER)
        billede = Image.blend(billede, sloer, styrke)
        for bredde, kvalitet in BREDDER.items():
            hoejde = round(billede.height * bredde / billede.width)
            lille = billede.resize((bredde, hoejde), Image.LANCZOS)
            fil = UD / f"foto-{navn}-{bredde}.webp"
            lille.save(fil, "WEBP", quality=kvalitet, method=6)
            print(f"{fil.name}: {bredde}x{hoejde}, {fil.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main()
