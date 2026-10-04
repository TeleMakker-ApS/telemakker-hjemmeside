#!/usr/bin/env python3
"""
Bygger en underside pr. fag og "Fag"-menuen i toppen.

    python3 vaerktoej/byg-fagsider.py

HVAD DEN GOER
  1. Skriver tilbudsstyring-til-<fag>/index.html for hvert fag i FAG.
  2. Saetter "Fag"-menuen ind i forsidens top (mellem FAGMENU-markoererne),
     saa menuen altid matcher listen her.
  Sitemappet tager de nye sider med af sig selv (byg-sitemap.py).

HVORFOR ET SCRIPT: otte sider i haanden ville skride fra hinanden. Ret
teksten eller tilfoej et fag her, koer scriptet, og alle sider foelger med.

REGLER (se BRAND.md)
  - Kun fakta, der ogsaa staar paa forsiden. Lov ikke noget nyt.
  - Ingen grossistnavne i menuen, foer der faktisk er en kobling til dem.
  - Ingen opdigtede priser. Kun toemrer-eksemplet har tal, og det er det
    samme eksempel som paa forsiden.
"""
import html
import pathlib
import re

ROD = pathlib.Path(__file__).resolve().parent.parent
DOMAENE = "https://www.telemakker.dk"

# slug, navn (ental), navn (flertal), undertekst i menuen, overskrift,
# indledning, linjer i tilbuddet, typiske opkald [(titel, tekst)]
FAG = [
    dict(slug="tomrere", jeg='Jeg står på stilladset, når kunden ringer', sit='Du står på stilladset. Kunden ringer om en terrasse.', kender=['Du lover kunden et tilbud “i aften”, og så går der en uge.', 'Målene fra samtalen står på bagsiden af en kvittering fra trælasten.', 'Kunden har fået to andre tilbud, før du har sat dig ved computeren.'], ental="tømrer", flertal="tømrere", menu="Terrasse, gulv, vinduer",
         h1="Snak terrassen igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om en terrasse, et gulv eller nye vinduer. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Nedrivning af det gamle dæk og bortkørsel", "Fundament, stolpesko og strøer",
                 "Lægning af terrassebrædder, skruet i skjult", "Trappe på tre trin og afsluttende kantliste"],
         opkald=[("Terrasse og trapper", "Mål, træsort, fundament og hvem der kører det gamle væk."),
                 ("Gulve", "Kvadratmeter, undergulv, lister og om møblerne skal flyttes."),
                 ("Vinduer og døre", "Antal, mål, lysninger og afdækning indvendigt."),
                 ("Tag og udhæng", "Sternbrædder, udhæng og hvad der skal stilladseres."),
                 ("Køkken og indretning", "Montering, tilpasning og hvad kunden selv har købt."),
                 ("Carport og skur", "Størrelse, tag, fundament og byggetilladelse.")]),
    dict(slug="vvs", jeg='Jeg ligger under en håndvask, når kunden ringer', sit='Du ligger under en håndvask. Kunden ringer om et nyt badeværelse.', kender=['Du tager telefonen med våde hænder og husker halvdelen bagefter.', 'Tilbuddet på badeværelset bliver skrevet ved køkkenbordet kl. 22.', 'Kunden ringer igen og spørger, om du har glemt hende.'], ental="VVS'er", flertal="VVS'ere", menu="Bad, varme, afløb",
         h1="Snak badeværelset igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om et nyt badeværelse, en utæt radiator eller et stoppet afløb. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Nedtagning af gammelt toilet og håndvask", "Bruseniche, toilet og håndvask",
                 "Rørføring og tilslutning af vand og afløb", "Materialer fra din egen prisliste"],
         opkald=[("Badeværelse", "Bruseniche, toilet, håndvask, gulvvarme og hvem der laver fliserne."),
                 ("Varme", "Radiatorer, gulvvarme, fjernvarmeunit og hvor rørene skal føres."),
                 ("Afløb", "Stoppet afløb, ny gulvafløb og hvad der skal brydes op."),
                 ("Køkken", "Vandinstallation, opvaskemaskine og hvad kunden selv har købt."),
                 ("Varmepumpe", "Placering, eksisterende anlæg og hvad der skal fjernes."),
                 ("Vandvarmer og toilet", "Udskiftning, mærke og om det gamle skal køres væk.")]),
    dict(slug="elektrikere", jeg='Jeg står i en eltavle, når kunden ringer', sit='Du står i en eltavle. Kunden ringer om en ladestander.', kender=['Du noterer antal udtag på en papkasse og finder den ikke igen.', 'Fem små tilbud om ugen tager længere tid end de store.', 'Kunden har bestilt hos en anden, før dit tilbud er sendt.'], ental="elektriker", flertal="elektrikere", menu="Tavle, udtag, ladestander",
         h1="Snak tavlen igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om en ny eltavle, flere stikkontakter eller en ladestander. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Udskiftning af eltavle med nye HPFI-relæer", "Nye stikkontakter og udtag",
                 "Opsætning af belysning", "Materialer fra din egen prisliste"],
         opkald=[("Eltavle", "Gammel tavle, antal grupper, HPFI og hvad der skal opdateres."),
                 ("Stikkontakter og udtag", "Antal, placering og om der skal fræses i væggen."),
                 ("Belysning", "Spots, udendørslys, lampeudtag og hvem der leverer lamperne."),
                 ("Ladestander", "Afstand fra tavlen, kabelføring og hvilken lader kunden har valgt."),
                 ("Køkken", "Ovn, kogeplade, emhætte og hvad køkkenfirmaet selv laver."),
                 ("Fejlfinding", "Hvad der slår fra, hvornår, og hvad kunden selv har prøvet.")]),
    dict(slug="malere", jeg='Jeg har penslen i hånden, når kunden ringer', sit='Du har penslen i hånden. Kunden ringer om en lejlighed.', kender=['Du stiller penslen fra dig, tager opkaldet og har maling på telefonen.', 'Kvadratmeterne bliver regnet ud om aftenen med en lommeregner.', 'Kunden spørger efter tilbuddet, før du har nået at skrive det.'], ental="maler", flertal="malere", menu="Indvendigt, facade, træværk",
         h1="Snak rummene igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om en lejlighed, der skal males, en facade eller vinduer, der trænger. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Afdækning og forberedelse", "Spartling og slibning af vægge og loft",
                 "Maling af vægge og loft i to lag", "Materialer fra din egen prisliste"],
         opkald=[("Indvendig maling", "Antal rum, kvadratmeter, loft med eller uden, og om der bor nogen."),
                 ("Facade", "Højde, underlag, stillads og hvad der skal skrabes af først."),
                 ("Vinduer og træværk", "Antal rammer, kitning og om de skal males indvendigt også."),
                 ("Spartling", "Hvor slemme væggene er, og om det er fuldspartling eller pletspartling."),
                 ("Tapet", "Fjernelse af gammelt tapet, ny væv og hvem der vælger farven."),
                 ("Gulvbehandling", "Slibning, lak eller olie og om møblerne skal flyttes.")]),
    dict(slug="murere", jeg='Jeg har mørtel på hænderne, når kunden ringer', sit='Du har mørtel på hænderne. Kunden ringer om facaden.', kender=['Du kan ikke skrive noget ned, så du prøver at huske det hele.', 'Tilbuddet på facaden venter til weekenden.', 'Kunden har glemt, hvad I aftalte, når tilbuddet endelig kommer.'], ental="murer", flertal="murere", menu="Facade, fliser, skorsten",
         h1="Snak facaden igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om en facade, der skal fuges, et badeværelse eller en skorsten. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Stillads og afdækning", "Udkradsning og omfugning af facade",
                 "Reparation af revner og skader", "Materialer fra din egen prisliste"],
         opkald=[("Facade og fuger", "Kvadratmeter, fugetype, stillads og hvor slem facaden er."),
                 ("Badeværelse og fliser", "Membran, fliser på gulv og væg og hvem der laver VVS."),
                 ("Skorsten", "Højde, inddækning, nedrivning eller reparation."),
                 ("Tilbygning", "Fundament, mure, og hvad tømreren og elektrikeren laver."),
                 ("Sokkel og puds", "Længde, skader og om der skal vandskures eller pudses."),
                 ("Klinker", "Rum, type, gulvvarme og hvad der skal brydes op først.")]),
    dict(slug="anlaegsgartnere", jeg='Jeg sidder i minigraveren, når kunden ringer', sit='Du sidder i minigraveren. Kunden ringer om en ny indkørsel.', kender=['Du slukker maskinen, tager opkaldet og starter igen uden noter.', 'Kvadratmeter og sten bliver regnet ud på en blyant i bilen.', 'Foråret er travlt, og tilbuddene hober sig op.'], ental="anlægsgartner", flertal="anlægsgartnere", menu="Belægning, terrasse, dræn",
         h1="Snak haven igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om en ny indkørsel, en terrasse eller vand, der står i græsset. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Opgravning og bortkørsel af jord", "Afretning og stabilgrus",
                 "Lægning af belægningssten med kantsten", "Materialer fra din egen prisliste"],
         opkald=[("Belægning og indkørsel", "Kvadratmeter, sten, kantsten og hvad der skal graves af."),
                 ("Terrasse", "Fliser eller træ, niveau og trin ned til græsset."),
                 ("Hæk og beplantning", "Længde, planter og om den gamle hæk skal fjernes."),
                 ("Dræn", "Hvor vandet står, længde og hvor det skal ledes hen."),
                 ("Støttemur", "Højde, materiale og hvad der skal holdes tilbage."),
                 ("Græsplæne", "Kvadratmeter, rullegræs eller såning og jordforbedring.")]),
    dict(slug="kloakmestre", jeg='Jeg står i en udgravning, når kunden ringer', sit='Du står i en udgravning. Kunden ringer om et påbud fra kommunen.', kender=['Kunden forklarer længe om rotter og brønde, og du har ingen hånd fri.', 'Tilbuddet på separatkloakeringen tager en hel aften.', 'Kunden ringer til tre kloakmestre og tager den, der svarer først.'], ental="kloakmester", flertal="kloakmestre", menu="Separering, dræn, rotter",
         h1="Snak kloakken igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om separatkloakering, rotter i kloakken eller et dræn, der ikke virker. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["TV-inspektion af eksisterende ledninger", "Opgravning og udskiftning af ledning",
                 "Retablering af belægning", "Materialer fra din egen prisliste"],
         opkald=[("Separatkloakering", "Påbud fra kommunen, længde og hvor regnvandet skal hen."),
                 ("Rotter", "Hvor de er set, rottespærre og om der er brud på ledningen."),
                 ("Dræn", "Fugt i kælderen, omfangsdræn og dybde."),
                 ("Nedsivning", "Faskine, jordbund og afstand til huset."),
                 ("TV-inspektion", "Hvad kunden har oplevet, og hvor brønden ligger."),
                 ("Stoppet afløb", "Hvor det står til, hvor tit det sker, og hvad der er prøvet.")]),
    dict(slug="koeleteknikere", jeg='Jeg er ude på service, når kunden ringer', sit='Du er ude på service. Kunden ringer om et kølerum.', kender=['Du tager opkaldet mellem to anlæg og har ingen blok ved hånden.', 'Tilbud på varmepumper bliver skrevet om aftenen efter vagten.', 'Kunden har fået et tilbud fra en anden, før du er hjemme.'], ental="køletekniker", flertal="køleteknikere", menu="Kølerum, varmepumpe, service",
         h1="Snak anlægget igennem. Tilbuddet ligger klar.",
         intro="Kunden ringer om et kølerum, en varmepumpe eller et anlæg, der ikke køler. Du snakker med ham som altid. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser.",
         linjer=["Demontering af eksisterende anlæg", "Levering og montering af nyt anlæg",
                 "Kølerør, påfyldning og indregulering", "Materialer fra din egen prisliste"],
         opkald=[("Kølerum", "Størrelse, temperatur, isolering og placering af aggregatet."),
                 ("Luft-til-luft varmepumpe", "Rum, placering af ude- og indedel og rørlængde."),
                 ("Køle- og frysemøbler", "Antal, type og om de gamle skal fjernes."),
                 ("Service", "Anlægstype, alder, fejlkode og hvornår det sidst blev efterset."),
                 ("Aircondition", "Rum, størrelse, solindfald og hvor udedelen må stå."),
                 ("Lækage", "Hvad der sker, kølemiddel og om anlægget er F-gas-pligtigt.")]),
]


def e(s):
    return html.escape(s, quote=True)


def fagmenu(aktiv=None, rod=""):
    punkter = "\n".join(
        f'        <a href="{rod}/tilbudsstyring-til-{f["slug"]}/"'
        + (' aria-current="page"' if f["slug"] == aktiv else "")
        + f'><b>{e(f["ental"].capitalize() if f["ental"][0].islower() else f["ental"])}</b><span>{e(f["jeg"])}</span></a>'
        for f in FAG)
    return f'''<details class="fagmenu">
      <summary>Vælg dit fag</summary>
      <div class="fagmenu-liste">
{punkter}
      </div>
    </details>'''


FAGMENU_CSS = """
/* FAG-MENU i toppen: en dropdown med en underside pr. fag. Bygges af
   vaerktoej/byg-fagsider.py. Synlig ogsaa paa mobil. */
.fagmenu{position:relative}
.fagmenu summary{list-style:none;cursor:pointer;color:rgba(255,255,255,.85);font-size:15.5px;padding:6px 0;user-select:none}
.fagmenu summary::-webkit-details-marker{display:none}
.fagmenu summary::after{content:"";display:inline-block;margin-left:7px;width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-3px) rotate(45deg)}
.fagmenu[open] summary::after{transform:translateY(1px) rotate(225deg)}
.fagmenu summary:hover{color:#fff}
.fagmenu-liste{position:absolute;top:calc(100% + 14px);left:50%;transform:translateX(-50%);width:330px;max-height:min(70vh,560px);overflow:auto;background:#fffdf9;border-radius:3px;box-shadow:0 18px 40px rgba(0,0,0,.35);padding:8px;z-index:30}
.fagmenu-liste a{display:block;padding:11px 14px;border-radius:3px;text-decoration:none;color:#1c1e1c}
.fagmenu-liste a b{display:block;font-weight:600;font-size:16px}
.fagmenu-liste a span{display:block;color:#6b665e;font-size:14px;margin-top:2px}
.fagmenu-liste a:hover,.fagmenu-liste a[aria-current]{background:#f2eee7}
@media(max-width:900px){header nav .fagmenu-liste a{display:block}.fagmenu-liste{left:auto;right:-90px;transform:none;width:min(330px,calc(100vw - 32px))}}
"""

FAGMENU_JS = """<script>
/* Fag-menuen lukker, naar man klikker ved siden af eller trykker Esc. */
(function(){var m=document.querySelector('.fagmenu');if(!m)return;
document.addEventListener('click',function(e){if(m.open&&!m.contains(e.target))m.open=false});
document.addEventListener('keydown',function(e){if(e.key==='Escape')m.open=false});})();
</script>"""

SIDE = """<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tilbudsstyring til {flertal} | TeleMakker</title>
<meta name="description" content="{beskrivelse}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:locale" content="da_DK">
<meta property="og:url" content="{url}">
<meta property="og:title" content="Tilbudsstyring til {flertal} | TeleMakker">
<meta property="og:description" content="Du snakker med kunden. Tilbuddet ligger klar, når du lægger på.">
<meta property="og:image" content="https://www.telemakker.dk/billeder/deling.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/skrift/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" as="image" href="/billeder/foto-rundsav-1200.webp" media="(max-width:800px)" fetchpriority="high">
<link rel="preload" as="image" href="/billeder/foto-rundsav-2400.webp" media="(min-width:801px)" fetchpriority="high">
<!-- Bygget af vaerktoej/byg-fagsider.py. Ret i scriptet, ikke her. -->
<style>
@font-face{{font-family:Archivo;src:url(/skrift/archivo.woff2) format('woff2');font-weight:100 900;font-display:swap}}
:root{{--antracit:#1b1e21;--antracit-lys:#24282c;--antracit-moerk:#141618;--birk:#e3c99f;--lys:#f1ece4;--daempet:#b9b2a8;--papir:#fffdf9;--blaek:#1c1e1c;--kant:rgba(227,201,159,.18)}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--antracit);color:var(--lys);font:400 17px/1.65 Archivo,-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:inherit}}
h1,h2,h3{{font-weight:700;letter-spacing:-.02em;line-height:1.12;margin:0}}
h2{{font-size:clamp(26px,3.2vw,38px);margin-bottom:14px}}
h3{{font-size:18.5px;margin-bottom:6px}}
p{{margin:0 0 14px}}
.baand{{max-width:1120px;margin:0 auto;padding:0 24px}}
.knap{{display:inline-block;padding:13px 22px;border-radius:3px;font-weight:600;text-decoration:none;border:1.5px solid transparent;font-size:16px}}
.knap.lys{{background:#fff;color:var(--blaek)}}
.knap.hul{{border-color:rgba(255,255,255,.45);color:#fff}}
.knap.moerk{{background:var(--antracit);color:#fff}}
header{{background:var(--antracit);border-bottom:1px solid rgba(255,255,255,.08);position:sticky;top:0;z-index:20}}
header .baand{{display:flex;justify-content:space-between;align-items:center;height:70px;gap:16px}}
.logo{{font-weight:700;font-size:21px;letter-spacing:-.02em;text-decoration:none;color:#fff}}
.logo b{{color:var(--birk);font-weight:700}}
header nav{{display:flex;gap:24px;align-items:center}}
header nav a{{text-decoration:none;font-size:15.5px;color:rgba(255,255,255,.85)}}
header nav a.knap{{color:var(--blaek);padding:10px 18px}}
@media(max-width:900px){{header nav>a:not(.knap){{display:none}}}}
{fagmenu_css}
.hero{{background:var(--antracit) center/cover no-repeat;background-image:linear-gradient(to bottom,rgba(27,30,33,0) calc(100% - 120px),#1b1e21 100%),url(/billeder/foto-rundsav-1200.webp);padding:clamp(56px,9vw,120px) 0 clamp(56px,8vw,100px)}}
@media(min-width:801px){{.hero{{background-image:linear-gradient(to bottom,rgba(27,30,33,0) calc(100% - 120px),#1b1e21 100%),url(/billeder/foto-rundsav-2400.webp)}}}}
.hero .emne{{display:block;color:var(--birk);font-size:clamp(17px,1.6vw,21px);font-weight:700;margin-bottom:12px;letter-spacing:-.01em}}
.hero h1{{font-size:clamp(32px,4.4vw,56px);max-width:20ch;margin-bottom:22px;color:#fff}}
.hero .under{{font-size:clamp(17px,1.5vw,20px);color:rgba(255,255,255,.86);max-width:42ch;margin-bottom:30px}}
.hero .knapper{{display:flex;gap:12px;flex-wrap:wrap}}
.brod{{color:var(--daempet);max-width:62ch;font-size:17.5px}}
section{{padding:clamp(56px,8vw,96px) 0}}
.lys-sek{{background:var(--antracit-lys)}}
.kender{{padding-top:clamp(40px,6vw,72px)}}
.kender-liste{{list-style:none;padding:0;margin:26px 0 22px;display:grid;gap:10px;max-width:780px}}
.kender-liste li{{background:var(--antracit-lys);border-left:3px solid var(--birk);border-radius:3px;padding:16px 20px;font-size:18px;color:var(--lys)}}
.trin{{list-style:none;padding:0;margin:34px 0 0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;counter-reset:t}}
.trin li{{background:var(--antracit);border:1px solid var(--kant);border-radius:3px;padding:20px 18px;counter-increment:t}}
.trin li::before{{content:counter(t);display:block;color:var(--birk);font-weight:700;font-size:28px;margin-bottom:8px}}
.trin p{{color:var(--daempet);font-size:15.5px;margin:0}}
@media(max-width:900px){{.trin{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:520px){{.trin{{grid-template-columns:1fr}}}}
.eksempel{{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:clamp(28px,5vw,64px);align-items:start;margin-top:34px}}
.eksempel figure{{margin:0;background:var(--papir);border-radius:3px;overflow:hidden;box-shadow:0 18px 40px rgba(0,0,0,.35)}}
.eksempel img{{display:block;width:100%;height:auto}}
.linjer{{background:var(--papir);color:var(--blaek);border-radius:3px;padding:20px 22px}}
.linjer h3{{color:var(--blaek);font-size:16px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}}
.linjer table{{width:100%;border-collapse:collapse;font-size:15.5px}}
.linjer td{{padding:9px 0;border-bottom:1px solid #e6e1d8;vertical-align:top}}
.linjer td:last-child{{text-align:right;white-space:nowrap;padding-left:14px}}
.linjer tr.ialt td{{border-bottom:0;font-weight:700;font-size:17px;padding-top:14px}}
.linjeliste{{list-style:none;margin:0;padding:0;font-size:15.5px}}
.linjeliste li{{padding:9px 0;border-bottom:1px solid #e6e1d8}}
.linjer .note{{font-size:13.5px;color:#5d5a54;margin:12px 0 0}}
@media(max-width:860px){{.eksempel{{grid-template-columns:1fr}}}}
.opgaver{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:30px}}
.opgave{{background:var(--antracit-lys);border:1px solid var(--kant);border-radius:3px;padding:18px 20px}}
.opgave p{{color:var(--daempet);font-size:15.5px;margin:0}}
@media(max-width:860px){{.opgaver{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:520px){{.opgaver{{grid-template-columns:1fr}}}}
.faq{{margin-top:26px;max-width:780px}}
.faq details{{border-bottom:1px solid var(--kant);padding:4px 0}}
.faq summary{{cursor:pointer;list-style:none;font-weight:600;font-size:18px;padding:16px 30px 16px 0;position:relative}}
.faq summary::-webkit-details-marker{{display:none}}
.faq summary::after{{content:"+";position:absolute;right:4px;top:12px;color:var(--birk);font-size:24px;font-weight:400}}
.faq details[open] summary::after{{content:"–"}}
.faq details p{{color:var(--daempet);margin:0 0 18px}}
.cta .boks{{background:var(--papir);color:var(--blaek);border-radius:3px;padding:clamp(26px,4vw,44px);display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap}}
.cta h2{{color:var(--blaek);margin-bottom:8px}}
.cta p{{color:#4a4844;margin:0;max-width:52ch}}
.andre{{margin-top:18px;font-size:15.5px;color:var(--daempet)}}
.andre a{{color:var(--lys)}}
footer{{background:var(--antracit-moerk);padding:44px 0 30px;font-size:15px}}
footer .baand{{display:flex;gap:60px;flex-wrap:wrap}}
footer .fod-gruppe{{display:flex;flex-direction:column;gap:4px}}
footer .fod-gruppe b{{color:var(--birk);font-weight:600}}
footer .fod-gruppe a{{text-decoration:none;color:var(--lys)}}
footer .fod-adresse{{display:block;border-top:1px solid rgba(255,255,255,.1);margin-top:30px;padding-top:20px;color:var(--daempet)}}
{beregner_css}
</style>
<script type="application/ld+json">
{{"@context":"https://schema.org","@graph":[
{{"@type":"WebPage","@id":"{url}#side","url":"{url}","name":"Tilbudsstyring til {flertal}","inLanguage":"da-DK","isPartOf":{{"@id":"https://www.telemakker.dk/#website"}},"publisher":{{"@id":"https://www.telemakker.dk/#organisation"}},"breadcrumb":{{"@id":"{url}#sti"}}}},
{{"@type":"BreadcrumbList","@id":"{url}#sti","itemListElement":[{{"@type":"ListItem","position":1,"name":"TeleMakker","item":"https://www.telemakker.dk/"}},{{"@type":"ListItem","position":2,"name":"Tilbudsstyring til {flertal}","item":"{url}"}}]}}]}}
</script>
</head>
<body>

<header>
  <div class="baand">
    <a class="logo" href="/">Tele<b>Makker</b></a>
    <nav>
      {fagmenu}
      <a href="#saadan">Sådan virker det</a>
      <a href="#spoergsmaal">Spørgsmål</a>
      <a href="https://app.telemakker.dk">Log ind</a>
      <a href="/#kontakt" class="knap lys">Bliv ringet op</a>
    </nav>
  </div>
</header>

<main id="indhold">

<section class="hero">
  <div class="baand">
    <h1><span class="emne">Tilbudsstyring til {flertal}</span>{sit}</h1>
    <p class="under">Du snakker med kunden, som du plejer. Når du lægger på, ligger tilbuddet klar med arbejdet, materialerne og dine egne priser. Så er aftenen din igen.</p>
    <div class="knapper">
      <a class="knap lys" href="/#kontakt">Bliv ringet op</a>
      <a class="knap hul" href="#tilbud">Se et tilbud</a>
    </div>
  </div>
</section>

<section class="kender">
  <div class="baand">
    <h2>Kender du det?</h2>
    <ul class="kender-liste">
{kender}
    </ul>
    <p class="brod">Det er ikke håndværket, der tager tiden. Det er papirarbejdet bagefter.</p>
  </div>
</section>

{beregner}

<section id="saadan" class="lys-sek">
  <div class="baand">
    <h2>Fra opkald til færdigt tilbud</h2>
    <p class="brod">Du skal ikke lære et nyt program. Du skal bare tage telefonen.</p>
    <ol class="trin">
      <li><h3>Kunden ringer</h3><p>På dit eget nummer. Det, der står på bilen og visitkortet, bliver.</p></li>
      <li><h3>Kunden siger ja</h3><p>Kunden bliver spurgt, om samtalen må optages. Siger han nej, gemmes der intet.</p></li>
      <li><h3>Tilbuddet ligger klar</h3><p>Arbejdet, materialerne, tidsplanen og forbeholdene. Med dine priser og dit logo.</p></li>
      <li><h3>Du retter og sender</h3><p>Læs det igennem, ret det, du vil, og send. Intet går til kunden, før du trykker.</p></li>
    </ol>
  </div>
</section>

<section id="tilbud">
  <div class="baand">
{eksempel}
  </div>
</section>

<section class="lys-sek">
  <div class="baand">
    <h2>Det ringer dine kunder om</h2>
    <p class="brod">Det, du alligevel spørger om i telefonen, ender i tilbuddet.</p>
    <div class="opgaver">
{opkald}
    </div>
  </div>
</section>

<section id="spoergsmaal">
  <div class="baand">
    <h2>Det vil du sikkert spørge om</h2>
    <div class="faq">
      <details><summary>Skal jeg skifte telefonnummer?</summary><p>Nej. Du beholder dit eget nummer. Kunderne ringer, som de plejer, og du tager telefonen, som du plejer.</p></details>
      <details><summary>Hvad hvis kunden ikke vil optages?</summary><p>Så bliver der ikke optaget noget, og der gemmes ingen tekst. Opkaldet går stadig igennem, og du skriver tilbuddet selv, som du plejer.</p></details>
      <details><summary>Taler der en robot med mine kunder?</summary><p>Nej. Kun beskeden om samtykke er automatisk. Resten af samtalen er dig.</p></details>
      <details><summary>Hvor kommer priserne fra?</summary><p>Fra din egen prisliste og din egen timepris. Ikke fra et gennemsnit. Er en pris ikke nævnt, står feltet tomt, så du selv udfylder det.</p></details>
      <details><summary>Sender den tilbuddet af sig selv?</summary><p>Aldrig. Du læser det igennem og trykker selv på knappen. Har du koblet din egen Outlook eller Gmail på, kommer det fra din egen adresse.</p></details>
      <details><summary>Passer det til alle opgaver?</summary><p>Nej. Nogle opgaver er for særlige til et udkast. Så skriver du det selv. Det er stadig dit tilbud.</p></details>
      <details><summary>Hvor ligger mine data?</summary><p>Inden for EU. Det står i databehandleraftalen under <a href="/juridisk/">Juridisk</a>.</p></details>
    </div>
  </div>
</section>

<section class="cta">
  <div class="baand">
    <div class="boks">
      <div>
        <h2>Er du {ental}? Vi ringer til dig</h2>
        <p>Vi er ved at sætte de første firmaer op. Skriv dit nummer, så ringer vi og viser det på en af dine egne samtaler.</p>
      </div>
      <a class="knap moerk" href="/#kontakt">Bliv ringet op</a>
    </div>
    <p class="andre">Se også: <a href="/">Tilbudsstyring til håndværkere</a></p>
  </div>
</section>

</main>

<footer>
  <div class="baand">
    <div class="fod-gruppe">
      <b>Juridisk</b>
      <a href="/juridisk/handelsbetingelser/">Handelsbetingelser</a>
      <a href="/juridisk/databehandleraftale/">Databehandleraftale</a>
      <a href="/juridisk/privatlivspolitik/">Privatlivspolitik</a>
    </div>
    <div class="fod-gruppe">
      <b>Kontakt</b>
      <a href="mailto:kontakt@telemakker.dk">kontakt@telemakker.dk</a>
      <a href="https://app.telemakker.dk">Log ind</a>
    </div>
  </div>
  <div class="baand fod-adresse">TeleMakker ApS &middot; CVR 46720253 &middot; Platanvej 5, 1. 67., 1810 Frederiksberg C</div>
</footer>
{fagmenu_js}
{beregner_js}
</body>
</html>
"""

TOMRER_EKSEMPEL = """    <h2>Et rigtigt tømrertilbud: nyt terrassedæk</h2>
    <p class="brod">Bygget ud fra én samtale om et terrassedæk i lærk på ca. 24 m². Kunden ser dit firmanavn, dit CVR og dine priser, ikke vores.</p>
    <div class="eksempel">
      <figure><img src="/billeder/tilbud-1.png" width="1190" height="1683" loading="lazy" decoding="async" alt="Første side af et tømrertilbud på nyt terrassedæk i lærk, med arbejde og materialer på hver sin linje."></figure>
      <div>
        <div class="linjer">
          <h3>Arbejdet</h3>
          <table>
            <tr><td>Nedrivning af det gamle dæk og bortkørsel</td><td>3.124,80 kr.</td></tr>
            <tr><td>Fundament, stolpesko og strøer</td><td>5.728,80 kr.</td></tr>
            <tr><td>Lægning af terrassebrædder, skruet i skjult</td><td>9.374,40 kr.</td></tr>
            <tr><td>Trappe på tre trin og afsluttende kantliste</td><td>3.645,60 kr.</td></tr>
            <tr class="ialt"><td>Samlet pris inkl. moms</td><td>40.158,88 kr.</td></tr>
          </table>
          <p class="note">Materialer, tidsplan og forbehold står på resten af tilbuddet. Alle oplysninger i eksemplet er opdigtede.</p>
        </div>
        <p class="brod" style="margin-top:22px">Materialerne slås op i din egen prisliste fra grossisten, og din timepris ganges på timerne. Blev en pris ikke nævnt i samtalen, står feltet tomt. Det bliver aldrig udfyldt med et gæt.</p>
      </div>
    </div>"""


def eksempel(f):
    if f["slug"] == "tomrere":
        return TOMRER_EKSEMPEL
    rows = "\n".join(f"            <li>{e(l)}</li>" for l in f["linjer"])
    return f"""    <h2>Sådan ser tilbuddet ud</h2>
    <p class="brod">Linjerne bliver skrevet ud fra det, du og kunden siger i telefonen. Kunden ser dit firmanavn, dit CVR og dine priser, ikke vores.</p>
    <div class="eksempel">
      <figure><img src="/billeder/tilbud-1.png" width="1190" height="1683" loading="lazy" decoding="async" alt="Eksempel på et færdigt tilbud med firmanavn, CVR, arbejde og materialer på hver sin linje."></figure>
      <div>
        <div class="linjer">
          <h3>Typiske linjer</h3>
          <ul class="linjeliste">
{rows}
          </ul>
          <p class="note">Eksemplet til venstre er et tømrertilbud. Dit eget tilbud får linjer fra din samtale og priser fra din prisliste.</p>
        </div>
        <p class="brod" style="margin-top:22px">Materialerne slås op i din egen prisliste fra grossisten, og din timepris ganges på timerne. Blev en pris ikke nævnt i samtalen, står feltet tomt. Det bliver aldrig udfyldt med et gæt.</p>
      </div>
    </div>"""


# ------------------------------------------------------------------
# BEREGNEREN. Markup og script hentes direkte fra forsiden, saa tal og
# standardvaerdier altid er de samme begge steder. Ret dem paa forsiden
# (index.html) og koer dette script igen.
# ------------------------------------------------------------------
BEREGNER_CSS = """/* BEREGNEREN (samme som paa forsiden) */
.regne{background:var(--antracit);padding:clamp(24px,4vw,48px) 0 clamp(56px,8vw,96px)}
.regnekort{background:var(--antracit-lys);border:1px solid rgba(227,201,159,.22);border-radius:3px;
  box-shadow:0 30px 60px -34px rgba(0,0,0,.45);max-width:900px;margin:0 auto;padding:clamp(28px,4vw,44px);color:#fff}
.regnekort h2{font-size:clamp(24px,2.6vw,30px);color:#fff;margin-bottom:6px}
.regnekort .lead{color:rgba(255,255,255,.74);font-size:15px;margin-bottom:0}
.regne .indhold{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,4vw,44px);align-items:center;margin-top:26px}
.felter{display:grid;gap:18px}
.felt label{display:block;font-size:14.5px;color:rgba(255,255,255,.82);margin-bottom:7px}
.felt .raek{display:flex;align-items:center;gap:14px}
.felt input[type=range]{flex:1;height:26px;min-width:0;-webkit-appearance:none;appearance:none;background:transparent;cursor:pointer}
.felt input[type=range]::-webkit-slider-runnable-track{height:6px;border-radius:3px;background:rgba(255,255,255,.30)}
.felt input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:22px;height:22px;border-radius:50%;background:#fff;border:0;margin-top:-8px;box-shadow:0 1px 4px rgba(0,0,0,.28);transition:transform .12s}
.felt input[type=range]:active::-webkit-slider-thumb{transform:scale(1.12)}
.felt input[type=range]::-moz-range-track{height:6px;border-radius:3px;background:rgba(255,255,255,.30)}
.felt input[type=range]::-moz-range-thumb{width:22px;height:22px;border-radius:50%;background:#fff;border:0;box-shadow:0 1px 4px rgba(0,0,0,.28)}
.felt input[type=range]:focus-visible{outline:2px solid #fff;outline-offset:4px}
.felt .tal{min-width:86px;text-align:right;font:700 19px/1 Archivo,sans-serif;font-variant-numeric:tabular-nums;color:#fff}
.felt .tal small{font-weight:500;font-size:13px;opacity:.78;margin-left:3px}
.svar .stort{display:block;font:700 clamp(44px,5.6vw,68px)/1 Archivo,sans-serif;font-variant-numeric:tabular-nums;letter-spacing:-.04em}
.svar .enhed{font-size:.34em;font-weight:600;letter-spacing:-.01em;margin-left:9px}
.svar .under{color:rgba(255,255,255,.84);margin:11px 0 0;font-size:15.5px}
.svar .noegle{display:flex;flex-wrap:wrap;gap:8px 24px;margin-top:16px;font-size:14.5px;color:rgba(255,255,255,.78)}
.svar .noegle b{color:#fff;font-variant-numeric:tabular-nums}
.antagelse{margin:20px 0 0;font-size:14.5px;color:rgba(255,255,255,.78);line-height:2}
.antagelse input{width:58px;font:700 14.5px/1 Archivo,sans-serif;font-variant-numeric:tabular-nums;text-align:center;padding:5px 3px;margin:0 3px;background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.34);border-radius:3px}
.antagelse input:focus-visible{outline:2px solid #fff;outline-offset:2px}
.skjult-label{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
@media(max-width:760px){.regne .indhold{grid-template-columns:1fr;gap:24px}
  .regne .svar{margin-top:6px;padding-top:22px;border-top:1px solid rgba(255,255,255,.22)}}"""


def hent_beregner():
    """Henter beregnerens markup og script fra forsiden."""
    s = (ROD / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<section class="regne" id="regnestykket">.*?</section>', s, re.S)
    j = re.search(r'<script>\s*/\* -+\s*REGNESTYKKET.*?</script>', s, re.S)
    if not m or not j:
        raise SystemExit("Fandt ikke beregneren paa forsiden")
    return m.group(0), j.group(0)


def beregner(f, markup):
    return markup.replace("Hvor mange timer bruger du som håndværker på tilbud?",
                          f"Hvor mange timer bruger du som {e(f['ental'])} på tilbud?")


def byg_side(f):
    url = f"{DOMAENE}/tilbudsstyring-til-{f['slug']}/"
    opkald = "\n".join(f'      <div class="opgave"><h3>{e(t)}</h3><p>{e(p)}</p></div>' for t, p in f["opkald"])
    besk = (f"Tilbudsstyring til {f['flertal']}: Du snakker med kunden i telefonen, og tilbuddet "
            f"ligger klar med dine egne priser, når du lægger på. Du retter og sender.")
    s = SIDE.format(flertal=e(f["flertal"]), ental=e(f["ental"]), url=url, beskrivelse=e(besk),
                    sit=e(f["sit"]), kender="\n".join(f"      <li>{e(k)}</li>" for k in f["kender"]), eksempel=eksempel(f), opkald=opkald,
                    fagmenu=fagmenu(f["slug"]), fagmenu_css=FAGMENU_CSS, fagmenu_js=FAGMENU_JS,
                    beregner=beregner(f, BEREGNER[0]), beregner_css=BEREGNER_CSS, beregner_js=BEREGNER[1])
    mappe = ROD / f"tilbudsstyring-til-{f['slug']}"
    mappe.mkdir(exist_ok=True)
    (mappe / "index.html").write_text(s, encoding="utf-8")
    print(f"{mappe.name}/index.html")


def opdater_forside():
    """Saetter Fag-menuen, dens CSS og script ind paa forsiden mellem markoerer."""
    p = ROD / "index.html"
    s = p.read_text(encoding="utf-8")
    blok_nav = "<!-- FAGMENU START -->\n      " + fagmenu() + "\n      <!-- FAGMENU SLUT -->"
    blok_css = "/* FAGMENU-CSS START */" + FAGMENU_CSS + "/* FAGMENU-CSS SLUT */"
    blok_js = "<!-- FAGMENU-JS START -->\n" + FAGMENU_JS + "\n<!-- FAGMENU-JS SLUT -->"
    if "<!-- FAGMENU START -->" in s:
        s = re.sub(r"<!-- FAGMENU START -->.*?<!-- FAGMENU SLUT -->", lambda m: blok_nav, s, flags=re.S)
        s = re.sub(r"/\* FAGMENU-CSS START \*/.*?/\* FAGMENU-CSS SLUT \*/", lambda m: blok_css, s, flags=re.S)
        s = re.sub(r"<!-- FAGMENU-JS START -->.*?<!-- FAGMENU-JS SLUT -->", lambda m: blok_js, s, flags=re.S)
    else:
        anker = '<nav>\n      <a href="#regnestykket">'
        assert s.count(anker) == 1, "fandt ikke forsidens menu"
        s = s.replace(anker, '<nav>\n      ' + blok_nav + '\n      <a href="#regnestykket">', 1)
        h = s.index("</head>")
        st = s.rfind("</style>", 0, h)
        s = s[:st] + blok_css + "\n" + s[st:]
        b = s.rindex("</body>")
        s = s[:b] + blok_js + "\n" + s[b:]
    p.write_text(s, encoding="utf-8")
    print("index.html: Fag-menu opdateret")


if __name__ == "__main__":
    BEREGNER = hent_beregner()
    for f in FAG:
        byg_side(f)
    opdater_forside()
