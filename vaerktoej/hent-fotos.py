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
  3. Gemmer det som WebP i to bredder: en til computer og en
     til mobil (2400 og 1200 px). Telefonen henter kun den lille.

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
# Kun toppen har et foto; resten af siden er i headerens farver.
FOTOS = [
    ("rundsav", "photo-1683115099860-5379ac101bce", 0.72),  # toppen
]
SLOER = (18, 18, 18)
# 2400 til computer og 1200 til mobil, saa fotoet er skarpt paa skaerme
# med dobbelt pixeltaethed. Hoejere kvalitet end foer: det var for uskarpt.
BREDDER = {2400: 75, 1200: 72}  # bredde: WebP-kvalitet


def hent(foto_id: str) -> Image.Image:
    url = f"https://images.unsplash.com/{foto_id}?fm=jpg&w=2400&q=90"
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
