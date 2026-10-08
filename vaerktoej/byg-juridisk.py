#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BYGGER DE TRE JURIDISKE SIDER UD FRA ADVOKATENS WORD-FILER

HVORFOR VÆRKTØJET FINDES, og hvorfor siderne ikke bare er skrevet i
hånden: teksten er ikke vores. Den kommer fra advokaten, og den bliver
rettet igen. Var siderne skrevet i hånden, skulle en ny udgave klippes
ind tre steder, og så ville hjemmesiden og aftalen skride fra hinanden,
uden at nogen opdagede det. Det er præcis den fejl, der er alvorlig på
en juridisk side: den ser rigtig ud.

Reglen er derfor: advokaten sender en ny fil, filen lægges i mappen
med kilderne, og værktøjet køres. Siderne er en AFLEDNING af
kilden, aldrig en kopi, nogen har rettet i.

HVORFOR PYTHON OG IKKE NODE, når resten af TeleMakker er Node: en
.docx-fil er en zip med XML indeni. Python har både zip og XML med fra
fabrikken. Node skulle have en pakke hentet ned, og hjemmesiden har i
dag ikke én eneste afhængighed. Det skal den blive ved med at have.

KØRES SÅDAN, fra roden af hjemmesidens mappe:

    python vaerktoej/byg-juridisk.py

Den skriver, hvad den lavede, og den STOPPER MED EN FEJL, hvis kilden
ikke ser ud som forventet. En stille byggefejl på en juridisk side er
værre end ingen side.
"""

import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

ROD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# KILDERNE LIGGER I DET PRIVATE REPO, OG DET ER IKKE til pynt.
#
# Hjemmesidens repo er OFFENTLIGT, fordi siden ligger paa GitHub Pages.
# Alt i det kan hentes af hvem som helst, ogsaa filer der ikke er en del
# af siden. Foerste udgave af vaerktoejet lagde advokatens Word-filer i
# juridisk/kilder/, og saa kunne hele databehandleraftalen hentes paa
# telemakker.dk/juridisk/kilder/databehandleraftale.docx, ogsaa de dele
# der med vilje var holdt ude af HTML-siden. Den laa aabent i 40
# minutter den 30. september 2026. Hele historien staar i STATUS.md i
# det private repo.
#
# Derfor: kilderne bor i Telemakker-repoet, som er privat. Vaerktoejet
# koeres fra hjemmesidens mappe og laeser en mappe op og over. Ligger de
# to mapper ikke ved siden af hinanden, siger den det.
KILDER = os.path.join(os.path.dirname(ROD), "Telemakker", "dokumenter",
                      "juridiske-kilder")
if not os.path.isdir(KILDER):
    sys.exit("STOP: kilderne skal ligge i det PRIVATE repo, her: " + KILDER
             + ". De to mapper skal ligge ved siden af hinanden, og kilderne"
               " maa IKKE laegges i hjemmesidens repo: det er offentligt.")
# VORES EGNE AFSNIT. Se vaerktoej/egne-afsnit.py for, hvorfor de ligger
# i deres egen fil og ikke i advokatens.
import importlib.util as _iu
_sp = _iu.spec_from_file_location(
    "egne_afsnit", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "egne-afsnit.py"))
EGNE = _iu.module_from_spec(_sp)
_sp.loader.exec_module(EGNE)

# EN DATO PR. SIDE, OG IKKE ÉN FOR ALLE TRE.
#
# Før stod her én DATO, og den gjaldt alle tre sider. Det betyder, at en
# kørsel ville slå privatlivspolitikkens dato TILBAGE fra 7. oktober til
# 30. september, selv om teksten var nyere. En juridisk side, der lyver
# om sin egen dato, bliver ikke læst som andet end en side, der ikke
# passer.
#
# NÅR DER RETTES I EN SIDE, SKAL DATOEN HER MED I SAMME ÆNDRING.
DATOER = {
    "privatlivspolitik": "7. oktober 2026",
    "handelsbetingelser": "7. oktober 2026",
    "databehandleraftale": "5. oktober 2026",
}

# OVERSIGTSSIDEN FAAR DEN NYESTE AF DE TRE, og den regnes ud.
#
# Skrev vi en dato i haanden ogsaa her, ville den drive fra de tre, og
# oversigten ville staa med en aeldre dato end de sider, den peger paa.
MAANEDER = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
            "august", "september", "oktober", "november", "december"]


def som_tal(dato):
    m = re.match(r"^(\d{1,2})\.\s+(\w+)\s+(\d{4})$", dato)
    if not m or m.group(2).lower() not in MAANEDER:
        sys.exit("STOP: datoen \"%s\" kan ikke laeses. Den skal se ud som "
                 "\"7. oktober 2026\"." % dato)
    return (int(m.group(3)), MAANEDER.index(m.group(2).lower()) + 1,
            int(m.group(1)))


DATOER[""] = max(DATOER.values(), key=som_tal)
DATO = "30. september 2026"   # bruges ikke laengere, staar for en sikkerheds skyld


# ----------------------------------------------------------------------
# AT LÆSE EN WORD-FIL
# ----------------------------------------------------------------------

def flugt(t):
    """HTML-flugt. Kildeteksten er ikke vores, så den skal IKKE kunne
    smide markup ind på siden, heller ikke ved et uheld."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Afsnit:
    """Ét afsnit fra Word, med den struktur Word selv har på det.

    HVORFOR DET ER VIGTIGT. Første udgave af værktøjet skrabede kun
    teksten ud og gættede sig til resten: et kort afsnit uden punktum
    var en overskrift, et afsnit efter et kolon var et listepunkt. Det
    gik galt i bilag C. "Fakta om det konstaterede brud (tid, sted,
    årsag)" blev en overskrift, fordi den er kort, og selskabets egen
    adresse blev det også.

    Men Word VED det. Filen indeholder både typografien (Heading1) og
    nummereringen med niveau: niveau 0 er en bestemmelse, niveau 1 er et
    listepunkt under den. Nu læses det i stedet for at gættes, og så er
    der ikke noget at gætte forkert.
    """

    __slots__ = ("html", "tekst", "stil", "niveau", "nummereret")

    def __init__(self, html, stil, niveau, nummereret):
        self.html = html
        self.tekst = re.sub("<[^>]+>", "", html)
        self.stil = stil
        self.niveau = niveau
        self.nummereret = nummereret

    def er_overskrift(self):
        return (self.stil or "").startswith(("Heading", "Overskrift", "Title"))

    def __repr__(self):
        return "Afsnit(%r, %s, %s)" % (self.tekst[:40], self.stil, self.niveau)


def laes(navn):
    """Returnerer afsnittene som Afsnit, med links bevaret.

    LINKENE ER GRUNDEN TIL, AT DEN HER ER MERE END ET regex. I
    privatlivspolitikken står der "Facebooks privatlivspolitik er
    tilgængelig her", hvor "her" ER et link. Skrabede vi kun teksten,
    ville der stå "her" uden noget at trykke på, og så er der en
    oplysningspligt, der ikke bliver opfyldt.
    """
    sti = os.path.join(KILDER, navn)
    if not os.path.exists(sti):
        sys.exit("STOP: kilden mangler: " + sti)
    z = zipfile.ZipFile(sti)
    rels = {}
    try:
        for r in ET.fromstring(z.read("word/_rels/document.xml.rels")):
            rels[r.get("Id")] = r.get("Target")
    except KeyError:
        pass

    doc = ET.fromstring(z.read("word/document.xml"))
    ud = []
    for p in doc.iter(W + "p"):
        dele = []
        for barn in p:
            if barn.tag == W + "hyperlink":
                maal = rels.get(barn.get(R + "id"), "")
                tekst = "".join(t.text or "" for t in barn.iter(W + "t"))
                if tekst.strip() and maal:
                    dele.append('<a href="%s" rel="noopener" target="_blank">%s</a>'
                                % (flugt(maal), flugt(tekst)))
                elif tekst.strip():
                    dele.append(flugt(tekst))
            else:
                dele.append(flugt("".join(t.text or "" for t in barn.iter(W + "t"))))
        # Word deler et ord op i flere stykker, når man har rettet i det.
        # Det giver dobbelte mellemrum, som skal væk igen.
        linje = re.sub(r"\s+", " ", "".join(dele)).strip()
        if not linje:
            continue
        stil = p.find(W + "pPr/" + W + "pStyle")
        num = p.find(W + "pPr/" + W + "numPr")
        niveau = None
        if num is not None:
            ilvl = num.find(W + "ilvl")
            niveau = int(ilvl.get(W + "val")) if ilvl is not None else 0
        ud.append(Afsnit(linje, stil.get(W + "val") if stil is not None else None,
                         niveau, num is not None))
    return ud


def find(afsnit, tekst, fra=0):
    """Finder det afsnit, der ER den her tekst. Fejler, hvis det ikke
    findes, så en ændret kilde ikke bliver bygget på et gæt."""
    for i in range(fra, len(afsnit)):
        if afsnit[i].tekst.strip().rstrip(":") == tekst:
            return i
    sys.exit("STOP: kunne ikke finde afsnittet %r i kilden." % tekst)


# ----------------------------------------------------------------------
# SIDENS RAMME
# ----------------------------------------------------------------------

SIDE = """<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titel)s: TeleMakker</title>
<meta name="description" content="%(beskrivelse)s">
<link rel="canonical" href="https://www.telemakker.dk/juridisk/%(mappe)s">
<link rel="icon" href="/favicon.svg">
<link rel="stylesheet" href="/juridisk/juridisk.css">
<meta property="og:title" content="%(titel)s: TeleMakker">
<meta property="og:description" content="%(beskrivelse)s">
<meta property="og:locale" content="da_DK">
<meta property="og:type" content="article">
<meta property="og:url" content="https://www.telemakker.dk/juridisk/%(mappe)s">
</head>
<body>

<div class="top"><div class="baand">
  <a class="maerke" href="/">TeleMakker</a>
  <a class="retur" href="/juridisk/">Juridisk</a>
</div></div>

<main><div class="baand">
<h1>%(titel)s</h1>
<p class="dato">Senest opdateret %(dato)s</p>
%(krop)s
</div></main>

<footer>
<div class="baand">
  <div>
    <a href="/juridisk/">Juridisk</a> &middot;
    <a href="mailto:kontakt@telemakker.dk">kontakt@telemakker.dk</a>
  </div>
</div>
<div class="baand fod-adresse">TeleMakker ApS &middot; CVR 46720253 &middot; Platanvej 5, 1. 67., 1810 Frederiksberg C</div>
</footer>

</body>
</html>
"""


def stykker(html):
    """Sidens tekst, stykke for stykke, uden markup.

    Overskrifter OG brødtekst. Første udgave af værnet så kun på
    overskrifterne, og det var for lidt: den 8. oktober 2026 viste det
    sig, at værktøjet ville skrive fem afsnit af handelsbetingelserne
    om, uden at én overskrift skiftede.
    """
    krop = html[html.index("<main"):html.index("</main>")] if "<main" in html else html
    ud = []
    # Attributterne skal SPRINGES OVER, ikke taelles med som tekst.
    # Foerst gav <p class="dato"> stykket class="dato">Senest opdateret
    # ..., og saa ramte reglen om at holde datolinjen ude ikke, fordi
    # stykket ikke begyndte med "Senest".
    for m in re.finditer(r"<(h2|h3|p)(?:\s[^>]*)?>(.*?)</\1>",
                         krop, re.S):
        t = re.sub(r"<[^>]+>", "", m.group(2))
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            ud.append(t)
    return ud


def mistet(foer, efter):
    """Det, der stod før og ikke står bagefter.

    Datolinjen holdes ude: den SKAL skifte, når der er rettet noget.
    """
    dato = re.compile(r"^Senest opdateret ")
    gamle = [t for t in stykker(foer) if not dato.match(t)]
    nye = set(stykker(efter))
    return [t for t in gamle if t not in nye]


def skriv(mappe, titel, beskrivelse, krop):
    """Skriver siden, men ALDRIG hvis den ville miste et afsnit.

    HVORFOR VÆRNET FINDES.

    Den 8. oktober 2026 blev det opdaget, at tre afsnit i
    privatlivspolitikken stod LIVE uden at findes i kilden: postkassen,
    kundens accept og fagopgaverne. En kørsel af dette værktøj ville
    have slettet dem fra en juridisk side, i stilhed, og siden ville se
    helt rigtig ud bagefter.

    De ligger nu i vaerktoej/egne-afsnit.py og bygges med. Men værnet
    her bliver stående, for det er NÆSTE gang, det går galt, der
    tæller: en ny fil fra advokaten, et afsnit der skifter navn, en
    regel der holder op med at ramme. Den slags skal larme.

    Den sammenligner OVERSKRIFTERNE, ikke hele teksten: en rettelse i
    et afsnit er det normale, mens et afsnit, der forsvinder, aldrig er
    det. Vil man alligevel fjerne et, sættes JURIDISK_FJERN.
    """
    ud = os.path.join(ROD, "juridisk", mappe)
    os.makedirs(ud, exist_ok=True)
    sti = os.path.join(ud, "index.html")

    dato = DATOER.get(mappe)
    if not dato:
        sys.exit("STOP: der er ingen dato for \"%s\" i DATOER." % mappe)

    html = SIDE % {"titel": titel, "beskrivelse": beskrivelse,
                   "mappe": (mappe + "/") if mappe else "",
                   "dato": dato, "krop": krop}

    # Det, der stod før. Findes siden ikke endnu, er der intet at miste.
    if os.path.isfile(sti):
        tabt = mistet(io.open(sti, encoding="utf-8").read(), html)
        if tabt and not os.environ.get("JURIDISK_FJERN"):
            sys.exit(
                "STOP: \"%s\" ville miste %d stykker tekst, og det er en "
                "juridisk side:\n  %s%s\n\nDe står LIVE nu og findes ikke i "
                "det, der blev bygget.\n\nTre ting kan være sket:\n"
                "  1. De er rettet direkte ind i HTML-siden. Det er forkert, "
                "og de skal i vaerktoej/egne-afsnit.py i stedet.\n"
                "  2. Advokaten har sendt en ny fil, hvor de ikke er med.\n"
                "  3. Teksten her i værktøjet er nyere end siden, og siden "
                "er bare ikke bygget siden. Så er det en ÆNDRING AF JURIDISK "
                "TEKST, og den skal nogen sige ja til først.\n\n"
                "Skal de væk med vilje, så kør igen med JURIDISK_FJERN=1."
                % (mappe, len(tabt), "\n  ".join(t[:150] for t in tabt[:8]),
                   "\n  ... og %d mere" % (len(tabt) - 8) if len(tabt) > 8 else ""))

    io.open(sti, "w", encoding="utf-8", newline="\n").write(html)
    print("  skrev juridisk/%sindex.html  (%d tegn, dateret %s)"
          % ((mappe + "/") if mappe else "", len(html), dato))
    return html


def punkt(nr, html):
    """Et nummereret afsnit med nummeret ude i marginen."""
    return ('<div class="punkt"><div class="nr">%s</div><div><p>%s</p></div></div>'
            % (nr, html))


def liste(punkter):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % p for p in punkter)


def saml_lister(dele):
    """To lister lige efter hinanden er ÉN liste. Ellers får hvert
    punkt sin egen kugle med luft omkring."""
    return "\n".join(dele).replace("</ul>\n<ul>", "\n")


# ----------------------------------------------------------------------
# HANDELSBETINGELSER
# ----------------------------------------------------------------------

NOTE_HB = """<div class="note">
<p><strong>Det her er de gældende betingelser.</strong> Abonnementets
navn, prisen og opsigelsesvarslet aftales individuelt og står i den
bestilling, du skriver under på. Derfor står de ikke her.</p>
<p>Behandler vi personoplysninger for dig, gælder også vores
<a href="/juridisk/databehandleraftale/">databehandleraftale</a>. Vil du
vide, hvad vi gør med oplysninger om dig selv, står det i vores
<a href="/juridisk/privatlivspolitik/">privatlivspolitik</a>.</p>
</div>"""


def byg_handelsbetingelser():
    a = laes("handelsbetingelser.docx")
    set_hb = [False]

    # ORDRESEDLEN SKAL IKKE PÅ EN HJEMMESIDE. Word-filen er to ting i
    # ét: en bestillingsblanket med tomme felter til pris,
    # opsigelsesvarsel og underskrift, og derefter selve betingelserne.
    # Blanketten hører i en mail til den enkelte kunde. Stod den her,
    # ville der stå "Pris: DKK [BELØB]" på vores egen hjemmeside.
    blanket = find(a, "Valgt abonnement")
    start = find(a, "1. Aftalegrundlag")

    krop = []
    for af in a[:blanket]:
        if af.tekst == "Handelsbetingelser for TeleMakker":
            continue                      # står som h1 i forvejen
        if af.tekst == "Om TeleMakker":
            krop.append("<h2>Om TeleMakker</h2>")
        else:
            krop.append("<p>%s</p>" % af.html)
    krop.append(NOTE_HB)

    # Dokumentet har ingen typografi at læne sig på: alle afsnit er
    # almindelige. Til gengæld står numrene i selve teksten, "1.
    # Aftalegrundlag", så dem kan vi bruge.
    afsnit = 0
    nr = 0
    for af in a[start:]:
        m = re.match(r"^(\d{1,2})\.\s+(.+)$", af.tekst)
        if m and len(af.tekst) < 70:
            afsnit, nr = int(m.group(1)), 0
            krop.append("<h2>%s. %s</h2>" % (afsnit, m.group(2)))
            continue
        nr += 1
        html = af.html
        # VORES TO SAETNINGER BAG ADVOKATENS 2.2. Se
        # vaerktoej/egne-afsnit.py. De stod foer rettet direkte ind i
        # HTML-siden, og en koersel her ville have slettet dem.
        if html.startswith(EGNE.HB_EFTER):
            html += EGNE.HB_TILFOEJ
            set_hb[0] = True
        krop.append(punkt("%d.%d" % (afsnit, nr), html))

    if afsnit != 17:
        sys.exit("STOP: handelsbetingelserne slutter på afsnit %d og ikke 17. "
                 "Er kilden skiftet?" % afsnit)
    if not set_hb[0]:
        sys.exit("STOP: vores to saetninger om online accept og om "
                 "partnervirksomheder kom ikke med. Afsnittet, de haenger "
                 "paa, begynder ikke laengere med: \"%s\". Se "
                 "vaerktoej/egne-afsnit.py." % EGNE.HB_EFTER)

    skriv("handelsbetingelser", "Handelsbetingelser",
          "TeleMakkers handelsbetingelser for abonnement på platformen. "
          "Gælder for alle aftaler med TeleMakker ApS.", saml_lister(krop))


# ----------------------------------------------------------------------
# PRIVATLIVSPOLITIK
# ----------------------------------------------------------------------

NOTE_PRIV = """<div class="note">
<p><strong>Den her side handler om de oplysninger, vi selv er ansvarlige
for.</strong> Altså dig som besøgende, kunde, samarbejdspartner eller
leverandør.</p>
<p>Er du kunde hos en håndværker, der bruger TeleMakker, er det
håndværkeren og ikke os, der bestemmer over oplysningerne om dig. Vi
behandler dem på hans instruks, og rammerne for det står i vores
<a href="/juridisk/databehandleraftale/">databehandleraftale</a>. Vil du
have indsigt eller slettet noget, skal du kontakte håndværkeren. Vi må
ikke gå ind i hans sager af os selv.</p>
</div>"""

# STORE BOGSTAVER ER SKRIGERIGT PÅ EN SKÆRM. I Word er en overskrift
# med versaler en typografi; i HTML er det råb. Overskrifterne sættes
# derfor med stort begyndelsesbogstav, og de ord, der SKAL have stort,
# står her.
STORE_ORD = {"telemakker": "TeleMakker", "eu": "EU", "eøs": "EØS",
             "tiktok": "TikTok", "some": "SoMe"}


def paent(t):
    ud = []
    for i, o in enumerate(t.split()):
        lav = o.lower()
        bar = lav.strip(",.:/")
        if bar in STORE_ORD:
            ud.append(lav.replace(bar, STORE_ORD[bar]))
        elif i == 0:
            ud.append(lav.capitalize())
        else:
            ud.append(lav)
    t = " ".join(ud).replace("eu/eøs", "EU/EØS")
    # Slaafejl i advokatens overskrifter, se vaerktoej/egne-afsnit.py.
    return EGNE.RETTEDE_OVERSKRIFTER.get(t, t)


def byg_privatlivspolitik():
    a = laes("privatlivspolitik.docx")
    krop = [NOTE_PRIV]
    # Hvor mange afsnit vi selv lagde ind, saa resten kan omnummereres.
    # En liste og ikke et tal, fordi den saettes inde i loekken.
    set_egne = [0]

    for af in a:
        t = af.tekst
        if t == "Privatlivspolitik":
            continue

        # Punkterne i rettighedslisten er Words egne listepunkter.
        if (af.nummereret and af.niveau >= 1) or t.startswith("- "):
            krop.append(liste([re.sub(r"^-\s*", "", af.html)]))
            continue

        # HOVEDAFSNIT: "6.   DELING AF DINE PERSONOPLYSNINGER MED ANDRE".
        # De står med store bogstaver i filen, og det er det sikreste
        # kendetegn her, fordi mellemrummene efter tallet svinger og
        # typografien ikke er sat konsekvent.
        m = re.match(r"^(\d{1,2})\.\s+([A-ZÆØÅ].*)$", t)
        if m and len(t) < 90 and t.upper() == t:
            nummer = int(m.group(1))
            # VORES EGNE AFSNIT LIGGER FOERST, naar vi naar advokatens
            # sidste. Hendes "Opdatering af vores privatlivspolitik" er
            # nr. 10 i filen og skal staa til sidst paa siden, altsaa
            # efter vores tre, som nr. 13.
            if nummer == EGNE.FOERSTE_EGNE:
                krop.append(EGNE.PRIVATLIV)
                egne = EGNE.PRIVATLIV.count("<h2>")
                nummer += egne
                set_egne[0] = egne
            krop.append("<h2>%s. %s</h2>" % (nummer, paent(m.group(2))))
            continue

        m = re.match(r"^(\d{1,2}\.\d{1,2})\s+(.*)$", t)
        if m:
            nr, rest = m.group(1), m.group(2)
            # Numrene UNDER et omnummereret afsnit skal med. Uden det
            # ville der staa "13. Opdatering" med et punkt "10.1" under.
            hoved, under = nr.split(".")
            if set_egne[0] and int(hoved) >= EGNE.FOERSTE_EGNE:
                nr = "%d.%s" % (int(hoved) + set_egne[0], under)
                t = nr + " " + rest
            # Word har klistret overskrift og afsnit sammen i "3.2 Når du
            # er kundeHos TeleMakker ApS behandler vi...". Det er et
            # manglende linjeskift i filen og ikke to sætninger.
            k = re.match(r"^(.{5,40}?)([A-ZÆØÅ][a-zæøå].{20,})$", rest)
            if nr == "3.2" and k:
                krop.append("<h3>%s %s</h3>" % (nr, k.group(1).strip()))
                krop.append("<p>%s</p>" % k.group(2).strip())
            elif len(t) < 70 and not rest.endswith("."):
                krop.append("<h3>%s %s</h3>" % (nr, rest))
            else:
                krop.append(punkt(nr, af.html[len(nr):].strip()))
            continue

        if af.er_overskrift() or t == "TeleMakkers privatlivspolitik SoMe":
            krop.append("<h3>%s</h3>" % af.html)
            continue

        krop.append("<p>%s</p>" % af.html)

    if not set_egne[0]:
        sys.exit("STOP: vores egne afsnit kom ikke med. Advokatens afsnit %d "
                 "blev ikke fundet, saa der er ikke noget at haenge dem paa. "
                 "Er kilden skiftet? Se vaerktoej/egne-afsnit.py."
                 % EGNE.FOERSTE_EGNE)

    skriv("privatlivspolitik", "Privatlivspolitik",
          "Hvordan TeleMakker ApS behandler personoplysninger, når vi er "
          "dataansvarlige, og hvilke rettigheder du har.", saml_lister(krop))


# ----------------------------------------------------------------------
# DATABEHANDLERAFTALEN
# ----------------------------------------------------------------------

# Aftalen er Datatilsynets standardskabelon. Afsnittene har faste
# numre, som teksten selv krydshenviser til ("Bestemmelse 9.2", "Bilag
# C.8"). Numrene står IKKE i teksten; de ligger i Words nummerering.
# Rækkefølgen står her, så overskrifterne kan skrives med tal, og så
# værktøjet kan se, om kilden har flyttet rundt på dem.
DBA_AFSNIT = [
    (2, "Præambel"),
    (3, "Den dataansvarliges rettigheder og forpligtelser"),
    (4, "Databehandleren handler efter instruks"),
    (5, "Fortrolighed"),
    (6, "Behandlingssikkerhed"),
    (7, "Anvendelse af underdatabehandlere"),
    (8, "Overførsel til tredjelande eller internationale organisationer"),
    (9, "Bistand til den dataansvarlige"),
    (10, "Underretning om brud på persondatasikkerheden"),
    (11, "Sletning og returnering af oplysninger"),
    (12, "Revision, herunder inspektion"),
    (13, "Parternes aftale om andre forhold"),
    (14, "Ikrafttræden og ophør"),
    (15, "Kontaktpersoner hos den dataansvarlige og databehandleren"),
]

# Hvor mange punkter hvert hovedafsnit SKAL have. Tallene er
# Datatilsynets egne. De er den eneste måde at opdage, at en ny udgave
# har flyttet rundt på numrene: passer de ikke, stopper værktøjet i
# stedet for at udgive en aftale, hvor henvisningerne peger ved siden af.
# Et afsnit, der FORTSÆTTER det foregående punkt i stedet for at være
# et nyt. Se numrerede_punkter() for hvorfor det ene tilfælde findes.
FORTSAETTELSER = (
    "Dette indebærer, at databehandleren så vidt muligt skal bistå",
)

# SKAL BILAGENE STAA PAA HJEMMESIDEN?
#
# Nej. Besluttet 30. september 2026. Hjemmesiden viser AFTALEN, altsaa
# bestemmelse 1 til 15, som er den tekst en kommende kunde skal kunne
# laese, foer han skriver under. Bilagene er instruksen for den ENKELTE
# aftale, og de foelger den kontrakt, haandvaerkeren faar ved
# onboarding.
#
# Hvorfor det ogsaa er det rigtige, ud over at det er kortere: bilag A
# og C beskriver den konkrete behandling og den konkrete instruks. De
# siger ingenting til en, der overvejer at koebe, og bilag C er i
# forvejen delvist holdt tilbage af en grund.
#
# DET ENE, DER KAN TALES FOR AT LADE STAA, ER BILAG B, listen over
# underleverandoerer. Det er det foerste en kunde spoerger om, og en
# offentlig liste er almindelig praksis hos de fleste, der saelger
# software. Den er slaaet FRA her, men det er ét ord at slaa til, og
# resten af koden staar klar.
BILAG_PAA_SIDEN = False

DBA_ANTAL = {2: 10, 3: 3, 4: 2, 5: 2, 6: 5, 7: 8, 8: 5,
             9: 3, 10: 4, 11: 1, 12: 3, 13: 1, 14: 4, 15: 2}

# Underdatabehandlerne står som en TABEL i Word, og en tabel bliver
# løse linjer, når teksten skrabes: Anthropic har ingen CVR, og så
# skrider alle rækker under den. Derfor står de her som data.
# Værktøjet tjekker, at hvert navn også står i kilden, så en ny udgave
# med en leverandør mere eller mindre FEJLER i stedet for at blive
# bygget stiltiende.
# LEVERANDØRER, DER STÅR I KILDEN MEN IKKE PÅ SIDEN, og hvorfor.
# Et navn, der bare forsvandt, er farligt: listen ER kundens
# godkendelse, og en leverandør, vi glemmer at nævne, er en, han ikke
# har godkendt. Derfor skal hver udeladelse stå her med en grund.
# Tom 1. oktober 2026: advokaten har fjernet Google fra kilden, saa
# der er ikke laengere nogen forskel mellem hendes liste og vores.
UDELADT = {}

UNDERDATABEHANDLERE = [
    ("Anthropic", "", "548 Market Street, PMB 90375, San Francisco, CA 94104-5401, USA",
     "Leverer sprogmodellen. Overførselsgrundlaget er EU-Kommissionens "
     "standardkontraktbestemmelser"),
    ("Telecom X", "35645845", "Herstedvang 8, 2620 Albertslund, Danmark",
     "Håndtering af telefoni og optagelse af telefonsamtale"),
    ("Hetzner", "0666.662.390", "Industriestraße 25, 91710 Gunzenhausen, Tyskland",
     "Serveren og databasen står her"),
    ("GitHub", "36486627", "C/O CSC (Denmark) ApS, Sundkrogsgade 21, København",
     "Programmet ligger her, og de natlige sikkerhedskopier opbevares i 90 dage"),
    ("Simply.com", "29412006", "Højvangen 4, 8660 Skanderborg, Danmark",
     "Leverer domæne og postkassen kontakt@telemakker.dk"),
    ("Dataforsyning", "37284114", "Sankt Kjelds Plads 11, 2100 København Ø, Danmark",
     "Bruges til at slå kundens adresse op, så den staves som i det "
     "officielle register"),
    # Selskabet er bekraeftet i deres egne EU-vilkaar 1. oktober 2026. De
    # oplyser intet registreringsnummer, praecis som Anthropic.
    ("Eleven Labs, Inc.", "", "169 Madison Ave #2484, New York, NY 10016, USA",
     "Tale til tekst: modtager lydoptagelsen og returnerer den som skrift. "
     "Overførselsgrundlag: EU-Kommissionens standardkontraktbestemmelser og "
     "EU-US Data Privacy Framework. Data kan behandles i USA, EU eller Singapore"),
]

BILAG_NOTE = """<h2>Bilagene</h2>
<div class="note">
<p><strong>Der hører tre bilag til aftalen, og de følger den kontrakt,
du skriver under på.</strong></p>
<p><strong>Bilag A</strong> beskriver behandlingen af personoplysninger
for netop din aftale: formålet, hvad behandlingen består i, hvilke typer
oplysninger den omfatter, og hvor længe.<br>
<strong>Bilag B</strong> er listen over de underleverandører, du
godkender ved at skrive under.<br>
<strong>Bilag C</strong> er din instruks til os, og den beskriver
sletning, hvor behandlingen foregår, og hvordan der føres tilsyn.</p>
<p>Vil du se dem, før du skriver under, sender vi dem gerne. Skriv til
<a href="mailto:kontakt@telemakker.dk">kontakt@telemakker.dk</a>.</p>
</div>"""

NOTE_DBA = """<div class="note">
<p><strong>Det her er den aftale, vi indgår med hver kunde.</strong>
Når en håndværker bruger TeleMakker, er det ham, der bestemmer over
oplysningerne om hans egne kunder. Vi behandler dem for ham og kun
efter hans instruks. Aftalen her er rammen om det.</p>
<p>Teksten følger Datatilsynets standardkontraktbestemmelser efter
databeskyttelsesforordningens artikel 28, stk. 3. <strong>Her står
selve aftalen.</strong> De tre bilag, der hører til, følger den
kontrakt, du skriver under på, og du kan se dem på forhånd, hvis du
beder om det. Den udgave, der gælder mellem os og dig, er den, begge
parter har skrevet under på.</p>
</div>"""

# Felterne står som tekst og ikke som felter, man kan skrive i.
# Hjemmesiden viser den GÆLDENDE tekst; papiret, man skriver under på,
# er den udgave, der sendes til den enkelte kunde.
UNDERSKRIFT = """<h2>Underskrift</h2>
<div class="underskrift">
<h3>På vegne af den dataansvarlige</h3>
<p class="felt">Navn &middot; Stilling &middot; Telefonnummer &middot; E-mail &middot; Underskrift</p>
<h3>På vegne af databehandleren</h3>
<p class="felt">Navn &middot; Stilling &middot; Telefonnummer &middot; E-mail &middot; Underskrift</p>
</div>"""

KONTAKTPERSONER = """<div class="underskrift">
<h3>Hos den dataansvarlige</h3>
<p class="felt">Navn &middot; Stilling &middot; Telefonnummer &middot; E-mail</p>
<h3>Hos databehandleren</h3>
<p class="felt">TeleMakker ApS &middot;
<a href="mailto:kontakt@telemakker.dk">kontakt@telemakker.dk</a></p>
</div>"""


def byg_databehandleraftale():
    a = laes("databehandleraftale.docx")
    alt = "\n".join(x.tekst for x in a)
    for navn, _, _, _ in UNDERDATABEHANDLERE:
        if navn.split(",")[0].split(".")[0] not in alt:
            sys.exit("STOP: underdatabehandleren %r står ikke i kilden længere. "
                     "Listen i værktøjet skal rettes, før siden bygges." % navn)
    for navn in UDELADT:
        if navn not in alt:
            print("  bemærk: %s er ude af kilden nu, så UDELADT kan ryddes" % navn)

    krop = [NOTE_DBA,
            "<h2>Parterne</h2>",
            "<p>Bestemmelserne er indgået mellem kunden, herefter "
            "&rdquo;den dataansvarlige&rdquo;, og:</p>",
            "<p>TeleMakker ApS<br>CVR 46720253<br>Platanvej 5, 1. 67<br>"
            "1810 Frederiksberg C<br>Danmark<br>herefter "
            "&rdquo;databehandleren&rdquo;.</p>",
            "<p>Bestemmelserne er udformet med henblik på parternes "
            "efterlevelse af artikel 28, stk. 3, i forordning 2016/679 "
            "(databeskyttelsesforordningen).</p>"]

    numre = set()
    for pos, (nummer, overskrift) in enumerate(DBA_AFSNIT):
        i = find(a, overskrift)
        if nummer == 14:
            # UNDERSKRIFTSBLOKKEN LIGGER MELLEM 14 OG 15 i skabelonen.
            # Uden den her grænse ville de tomme linjer "Navn",
            # "Stilling", "Telefonnummer" blive til bestemmelse 14.5 og
            # fremefter. En aftale med et punkt, der bare hedder "Navn".
            slut = find(a, "Underskrift", i + 1)
        elif nummer == 15:
            # Samme slags blanket: to gange Navn, Stilling,
            # Telefonnummer, E-mail.
            slut = find(a, "Navn", i + 1)
        elif pos + 1 < len(DBA_AFSNIT):
            slut = find(a, DBA_AFSNIT[pos + 1][1], i + 1)
        else:
            slut = find(a, "Bilag AOplysninger om behandlingen", i + 1)

        krop.append("<h2>%d. %s</h2>" % (nummer, overskrift))
        bidder, antal = numrerede_punkter(a[i + 1:slut], nummer, numre)
        if antal != DBA_ANTAL[nummer]:
            sys.exit("STOP: afsnit %d fik %d punkter, men skal have %d. "
                     "Kilden er ændret, og numrene ville blive forkerte."
                     % (nummer, antal, DBA_ANTAL[nummer]))
        krop.extend(bidder)
        if nummer == 14:
            krop.append(UNDERSKRIFT)
        if nummer == 15:
            krop.append(KONTAKTPERSONER)

    if BILAG_PAA_SIDEN:
        krop.append(byg_bilag_a(a))
        krop.append("<h2>Bilag B: underdatabehandlere</h2>")
        krop.append("<p>Ved Bestemmelsernes ikrafttræden har den dataansvarlige "
                    "godkendt brugen af følgende underdatabehandlere:</p>")
        krop.append(byg_bilag_b())
        krop.append(byg_bilag_c(a))
    else:
        krop.append(BILAG_NOTE)
        # Bilagene bygges alligevel, saa vaerktoejet stadig faar fejl, hvis
        # kilden aendrer sig. Ellers ville en aendring i bilag B ligge
        # uopdaget, til nogen slog dem til igen.
        for bid in (byg_bilag_a(a), byg_bilag_b(), byg_bilag_c(a)):
            if len(bid) < 200:
                sys.exit("STOP: et bilag blev naesten tomt ved bygningen. "
                         "Kilden er aendret. Se byg_bilag_a, _b og _c.")

    # KRYDSHENVISNINGERNE SKAL PEGE PÅ NOGET. Teksten siger "Bestemmelse
    # 9.2" og "Bilag C.8". Har værktøjet nummereret forkert, peger de på
    # ingenting, og så er den offentliggjorte aftale selvmodsigende.
    html = saml_lister(krop)
    ren = re.sub("<[^>]+>", "", html)
    mangler = [r for r in sorted(set(re.findall(r"Bestemmelse\s+(\d{1,2}\.\d{1,2})", ren)))
               if r not in numre]
    if mangler:
        sys.exit("STOP: teksten henviser til bestemmelse(r), der ikke findes på "
                 "den byggede side: %s. Nummereringen er forkert." % ", ".join(mangler))
    print("  krydshenvisninger: alle peger på et punkt, der findes "
          "(%d punkter i alt)" % len(numre))

    skriv("databehandleraftale", "Databehandleraftale",
          "TeleMakkers standard databehandleraftale efter "
          "databeskyttelsesforordningens artikel 28, stk. 3.", html)


def numrerede_punkter(afsnit, nummer, numre):
    """Nummererer punkterne i ét hovedafsnit.

    LISTERNE KOMMER FRA WORD, og det er pålideligt: et afsnit på
    niveau 1 er et listepunkt under den forrige bestemmelse. Det var
    det, der gik galt, da værktøjet gættede, og det gætter det ikke
    på længere.

    PUNKTERNE TÆLLER VI SELV, og det er med vilje. Word BURDE også
    vide, hvad der er en bestemmelse, men nummereringen i filen er
    beskadiget: i afsnit 6 er kun tre af de fem punkter nummererede,
    fordi de to sidste har mistet deres nummer under redigeringen.
    Stolede vi på filen, ville aftalen på hjemmesiden have et afsnit 6
    med tre punkter, hvor Datatilsynets skabelon har fem, og så ville
    henvisningerne til 6.4 og 6.5 pege på ingenting.

    Derfor tælles hvert afsnit som et punkt, og DBA_ANTAL ovenfor er
    spærren: passer tallene ikke til skabelonen, bygges siden ikke.

    FORTSAETTELSER er den ene undtagelse. Skabelonens punkt 9.1 består
    af to afsnit: forpligtelsen, og så "Dette indebærer, at ...
    følgende:" med listen under. Tælles de som to, bliver alt derefter
    forskudt, og aftalens EGNE henvisninger til "Bestemmelse 9.2"
    peger på den forkerte tekst. Det er den slags fejl, der ikke ser
    ud som en fejl.
    """
    ud = []
    for slags, hvad in opdel(afsnit):
        if slags == "liste":
            ud.append(liste([x.html for x in hvad]))
        elif slags == "fortsaettelse":
            ud.append('<div class="punkt"><div class="nr"></div>'
                      "<div><p>%s</p></div></div>" % hvad.html)
        else:
            ud.append(None)               # pladsholder, nummereres nedenfor
            ud[-1] = hvad
    # Numrene sættes til sidst, så et listepunkt aldrig kan rykke dem.
    n = 0
    for k, bid in enumerate(ud):
        if isinstance(bid, Afsnit):
            n += 1
            ref = "%d.%d" % (nummer, n)
            numre.add(ref)
            ud[k] = punkt(ref, bid.html)
    return ud, n


def opdel(afsnit):
    """Deler et hovedafsnit op i punkter, lister og fortsættelser.

    DE TO SIGNALER LÆGGES SAMMEN, og det er nødvendigt, fordi ingen af
    dem er nok alene:

    WORDS EGET NIVEAU er rigtigt, når det er der. Et afsnit på niveau 1
    er et listepunkt. Det er den eneste måde at få listen i bilag C
    rigtigt, hvor punkterne starter skiftevis med stort og lille:
    "Fakta om det konstaterede brud", "Hvornår bruddet startede",
    "kategorierne og det omtrentlige antal".

    MEN NIVEAUET MANGLER MANGE STEDER, fordi filen er redigeret. I
    afsnit 9 er listen med de registreredes rettigheder ikke markeret
    som en liste overhovedet. Der virker den anden regel: en liste
    starter altid efter et afsnit, der ender på kolon, det første punkt
    hører altid med, og derefter fortsætter listen, så længe punkterne
    starter med lille bogstav, som juridiske lister på dansk gør.
    """
    ud = []
    i = 0
    while i < len(afsnit):
        af = afsnit[i]
        if af.nummereret and af.niveau >= 1:
            punkter = []
            while i < len(afsnit) and afsnit[i].nummereret and afsnit[i].niveau >= 1:
                punkter.append(afsnit[i])
                i += 1
            ud.append(("liste", punkter))
            continue
        if af.tekst.startswith(FORTSAETTELSER):
            ud.append(("fortsaettelse", af))
        else:
            ud.append(("punkt", af))
        i += 1
        if af.tekst.endswith(":") and i < len(afsnit):
            if afsnit[i].nummereret and afsnit[i].niveau >= 1:
                continue                  # Word har den, tages i næste omgang
            punkter = [afsnit[i]]
            j = i + 1
            while j < len(afsnit) and afsnit[j].tekst[:1].islower():
                punkter.append(afsnit[j])
                j += 1
            ud.append(("liste", punkter))
            i = j
    return ud


def byg_bilag_a(a):
    i = find(a, "Bilag AOplysninger om behandlingen")
    slut = find(a, "Bilag BUnderdatabehandlere", i + 1)
    ud = ["<h2>Bilag A: oplysninger om behandlingen</h2>"]
    for af in a[i + 1:slut]:
        m = re.match(r"^(A\.\d)\.?\s+(.*)$", af.tekst)
        if m:
            ud.append("<h3>%s. %s</h3>" % (m.group(1), m.group(2)))
        elif af.nummereret and af.niveau >= 1:
            ud.append(liste([af.html]))
        else:
            ud.append("<p>%s</p>" % af.html)
    return saml_lister(ud)


def byg_bilag_b():
    raekker = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (navn, cvr or "&ndash;", adresse, beskrivelse)
        for navn, cvr, adresse, beskrivelse in UNDERDATABEHANDLERE)
    return ('<div class="tabel-rul"><table>'
            "<thead><tr><th>Navn</th><th>CVR</th><th>Adresse</th>"
            "<th>Behandling</th></tr></thead><tbody>%s</tbody></table></div>"
            % raekker)


# HVOR SIKKERHEDSBESKRIVELSEN BEGYNDER, og hvorfor den ikke kommer på
# hjemmesiden.
#
# Bilag C.2 opremser, hvilke sikkerhedsforanstaltninger vi har. Den
# opremsning siger også, hvad vi IKKE har, og læst sammen er den en
# køreplan for at bryde ind hos os. Den skal ikke ligge på en offentlig
# adresse, som Google indekserer.
#
# DETALJERNE STÅR MED VILJE IKKE HER. Det her repo er offentligt, så en
# kommentar i det er lige så udgivet som selve siden. Vil du vide,
# hvilke huller der er tale om, står de i bilag C i kilden, i det
# private repo. Det er ikke en gåde, det er den samme regel som for
# selve dokumentet.
#
# Besluttet 30. september 2026: beskrivelsen skal ikke udleveres til
# andre end den, der har brug for den.
#
# Det er også det almindelige. Kunden får bilaget, når han beder om
# det, og han får det i den aftale, han skriver under på. Alle ANDRE
# får det ikke.
#
# Springet går fra den her linje til det næste C-underafsnit. Findes
# linjen ikke i kilden, STOPPER værktøjet i stedet for at udgive
# beskrivelsen ved et uheld.
SIKKERHED_START = "Pseudonymisering og kryptering"

SIKKERHED_NOTE = """<div class="note">
<p><strong>Beskrivelsen af de enkelte sikkerhedsforanstaltninger
udleveres på anmodning.</strong> Den står i den databehandleraftale, du
skriver under på, og vi sender den gerne på forhånd til en kunde, en
revisor eller en rådgiver, der har brug for den.</p>
<p>Den ligger ikke offentligt, fordi en detaljeret liste over et
systems indretning også er en liste over, hvor man skal prøve. Skriv
til <a href="mailto:kontakt@telemakker.dk">kontakt@telemakker.dk</a>.</p>
</div>"""


def er_maaleoverskrift(af):
    """De korte overskrifter i C.2, der ikke har numre: "Beskyttelse
    under transmission", "Logning og overvågning". Uden dem kan
    bilaget ikke skimmes.

    De er ikke sat som overskrifter i Word, så her er der stadig en
    vurdering. Fælden er fundet ved at se på den byggede side: C.5
    lister de steder, behandlingen må foregå, og selskabets egen
    adresse er kort og uden punktum. En adresse kendes på et tal lige
    efter et komma. Et afsnit, der starter med "Og", fortsætter det
    foregående og kan ikke være en overskrift.
    """
    t = af.tekst
    if len(t) >= 70 or t.endswith(".") or t.endswith(":"):
        return False
    if t.startswith("Og "):
        return False
    if re.search(r",\s*\d", t):
        return False
    return True


def byg_bilag_c(a):
    """Bilag C er instruksen, og den er den mest blandede del af hele
    aftalen: nummererede underafsnit, korte overskrifter uden numre, og
    to opremsninger.

    HER VIRKER HVERKEN WORDS NIVEAU ELLER STORT BEGYNDELSESBOGSTAV.
    Listen over, hvad en underretning om et databrud skal indeholde,
    er ikke markeret som en liste i filen, og punkterne starter
    skiftevis med stort og lille: "Fakta om det konstaterede brud",
    "Hvornår bruddet startede", "kategorierne og det omtrentlige
    antal". Gættede vi på store bogstaver, blev halvdelen af dem
    overskrifter.

    DET, DER VIRKER, er punktummet. Et listepunkt i det her bilag er en
    stump tekst uden punktum til sidst; et afsnit er en sætning, der
    slutter. Listen starter efter et kolon og løber, indtil et afsnit
    slutter med punktum eller et nyt C-underafsnit begynder.
    """
    i = find(a, "Bilag C Instruks vedrørende behandling af personoplysninger")
    ud = ["<h2>Bilag C: instruks vedrørende behandling af personoplysninger</h2>"]
    rest = a[i + 1:]
    if not any(x.tekst == SIKKERHED_START for x in rest):
        sys.exit("STOP: kunne ikke finde %r i bilag C. Uden den kan "
                 "sikkerhedsbeskrivelsen ikke holdes ude, og den maa IKKE "
                 "offentliggoeres. Se kommentaren ved SIKKERHED_START."
                 % SIKKERHED_START)
    k = 0
    springer = False
    while k < len(rest):
        af = rest[k]

        # SIKKERHEDSBESKRIVELSEN SPRINGES OVER. Se SIKKERHED_START.
        if af.tekst == SIKKERHED_START:
            springer = True
            ud.append(SIKKERHED_NOTE)
        if springer:
            if re.match(r"^C\.\d", af.tekst):
                springer = False          # næste underafsnit, vi er ude igen
            else:
                k += 1
                continue
        m = re.match(r"^(C\.\d)\.?\s+(.*)$", af.tekst)
        if m:
            ud.append("<h3>%s. %s</h3>" % (m.group(1), m.group(2)))
        elif af.nummereret and af.niveau >= 1:
            ud.append(liste([af.html]))
        elif er_maaleoverskrift(af):
            ud.append("<h3>%s</h3>" % af.html)
        else:
            ud.append("<p>%s</p>" % af.html)
        k += 1

        if af.tekst.endswith(":"):
            # EN LISTE SKAL HAVE MINDST TO PUNKTER. Ellers er det ikke en
            # liste, og så er den korte linje efter kolonet i stedet den
            # første overskrift i en opremsning af afsnit. Sådan ser C.2
            # ud: "gennemføre følgende foranstaltninger:" og derefter
            # "Pseudonymisering og kryptering" som overskrift med et
            # afsnit under. Uden den her grænse blev den første af de ti
            # foranstaltninger et listepunkt og de ni andre
            # overskrifter.
            start = k
            punkter = []
            while k < len(rest):
                n = rest[k]
                if n.tekst.endswith(".") or re.match(r"^C\.\d", n.tekst):
                    break
                punkter.append(n.html)
                k += 1
            if len(punkter) >= 2:
                ud.append(liste(punkter))
            else:
                k = start
    return saml_lister(ud)


# ----------------------------------------------------------------------
# FORSIDEN PÅ /juridisk/
# ----------------------------------------------------------------------

OVERSIGT = """<div class="note">
<p><strong>Tre dokumenter, og de dækker hver sin ting.</strong> Er du i
tvivl om hvilket, er det næsten altid handelsbetingelserne, du leder
efter.</p>
</div>
<ul class="liste">
<li><a href="/juridisk/handelsbetingelser/"><b>Handelsbetingelser</b>
<span>Hvad du køber, hvad vi leverer, og hvad der sker, hvis noget går
galt. Gælder for alle abonnementer.</span></a></li>
<li><a href="/juridisk/databehandleraftale/"><b>Databehandleraftale</b>
<span>Rammen om, at vi behandler dine kunders oplysninger for dig.
Efter databeskyttelsesforordningens artikel 28.</span></a></li>
<li><a href="/juridisk/privatlivspolitik/"><b>Privatlivspolitik</b>
<span>Hvad vi gør med oplysninger om dig selv, og hvilke rettigheder
du har over dem.</span></a></li>
</ul>"""


def byg_oversigt():
    skriv("", "Juridisk", "TeleMakkers handelsbetingelser, databehandleraftale "
          "og privatlivspolitik ét sted.", OVERSIGT)


if __name__ == "__main__":
    print("Bygger de juridiske sider ud fra juridisk/kilder/")
    byg_handelsbetingelser()
    byg_privatlivspolitik()
    byg_databehandleraftale()
    byg_oversigt()
    print("Færdig.")
