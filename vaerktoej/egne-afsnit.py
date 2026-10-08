#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VORES EGNE AFSNIT I DE JURIDISKE SIDER

HVORFOR FILEN FINDES.

byg-juridisk.py bygger siderne ud af ADVOKATENS Word-filer. Reglen er
god: siden er en afledning af kilden, aldrig en kopi, nogen har rettet
i, og derfor kan hjemmesiden og aftalen ikke skride fra hinanden.

MEN NOGLE AFSNIT ER VORES EGNE. Postkassen, kundens accept af tilbuddet
og fagopgaverne til en partner er funktioner, vi har bygget, og
teksterne om dem er skrevet her, ikke af advokaten.

De blev foerst rettet direkte ind i HTML-siderne. Det var forkert, og
det blev opdaget den 8. oktober 2026: kildefilerne manglede TRE afsnit,
der stod live. Havde nogen koert byg-juridisk.py, var afsnit 10, 11 og
12 af privatlivspolitikken forsvundet FRA EN JURIDISK SIDE, i stilhed.
Og den slags ser rigtigt ud bagefter.

DE HOERER HELLER IKKE IND I ADVOKATENS FILER. Saetter man dem derind,
forsvinder de naeste gang Sofie sender en ny udgave, og saa er vi
tilbage ved samme fejl, bare et halvt aar senere.

Derfor staar de HER, i deres egen fil, og byg-juridisk.py laegger dem
paa. Saa kan hverken en ny fil fra advokaten eller en koersel af
vaerktoejet fjerne dem, og det er til gengaeld tydeligt, hvad der er
vores eget, og hvad der er hendes.

NAAR DER RETTES HER, SKAL DATOEN MED. Se DATOER i byg-juridisk.py.
"""

# ----------------------------------------------------------------------
# PRIVATLIVSPOLITIKKEN
# ----------------------------------------------------------------------
#
# Afsnittene laegges ind FOER advokatens sidste afsnit, "Opdatering af
# vores privatlivspolitik", som i hendes fil er nr. 10. Det bliver
# derfor nr. 13. Se FOERSTE_EGNE og byg_privatlivspolitik().
FOERSTE_EGNE = 10

PRIVATLIV = u"""<h2>10. Tilslutning af din egen postkasse</h2>
<div class="punkt"><div class="nr">10.1</div><div><p>TeleMakker kan sende tilbud gennem din egen postkasse hos Microsoft (Outlook) eller Google (Gmail), så tilbuddet kommer fra din egen adresse, ligger i din egen Sendt-mappe, og kundens svar går direkte til dig. Tilslutningen er frivillig. Vælger du den fra, sendes tilbuddene i stedet fra TeleMakkers egen adresse.</p></div></div>
<div class="punkt"><div class="nr">10.2</div><div><p>Tilslutningen sker ved, at du logger ind hos udbyderen og giver TeleMakker tilladelse. Vi beder udelukkende om tilladelse til at <strong>sende</strong> e-mail på dine vegne: <span class="nobr">Mail.Send</span> hos Microsoft og <span class="nobr">gmail.send</span> hos Google. Det er de snævreste tilladelser, udbyderne tilbyder til formålet.</p></div></div>
<div class="punkt"><div class="nr">10.3</div><div><p><strong>Vi har ikke adgang til at læse din post.</strong> Vi kan hverken åbne, hente, gennemsøge eller slette indholdet af din indbakke, dine mapper eller dine sendte mails, og vi kan ikke få den adgang uden at du udtrykkeligt giver den på ny hos udbyderen.</p></div></div>
<div class="punkt"><div class="nr">10.4</div><div><p>I forbindelse med tilslutningen opbevarer vi din e-mailadresse hos udbyderen, hvilken udbyder der er tale om, de adgangsnøgler der er nødvendige for at kunne sende, samt tidspunktet for tilslutningen og en eventuel fejlbesked fra udbyderen. Vi opbevarer ikke indholdet af din postkasse. Grundlaget for behandlingen er opfyldelse af aftalen med dig efter databeskyttelsesforordningen artikel 6(1)(b).</p></div></div>
<div class="punkt"><div class="nr">10.5</div><div><p>Oplysningerne anvendes <strong>udelukkende</strong> til at sende de tilbud og beskeder, du selv godkender i TeleMakker. De anvendes ikke til andre formål, de videregives ikke til tredjeparter, de sælges ikke, og de anvendes ikke til markedsføring, profilering eller til at træne modeller. Dette gælder både de oplysninger, vi modtager fra udbyderen, og oplysninger udledt heraf. For data fra Google API Services sker anvendelsen i overensstemmelse med <a href="https://developers.google.com/terms/api-services-user-data-policy" rel="noopener" target="_blank">Google API Services User Data Policy</a>, herunder kravene om begrænset anvendelse (Limited Use).</p></div></div>
<div class="punkt"><div class="nr">10.6</div><div><p>Du kan til enhver tid afbryde forbindelsen under Indstillinger i TeleMakker. Når du gør det, slettes adgangsnøglerne hos os med det samme, og vi kan ikke længere sende på dine vegne. Du kan desuden trække tilladelsen tilbage direkte hos Microsoft eller Google.</p></div></div>
<h2>11. Når din kunde åbner et tilbud</h2>
<div class="punkt"><div class="nr">11.1</div><div><p>Når du sender et tilbud, følger der en personlig adresse med, hvor din kunde kan læse tilbuddet og svare ja eller nej med ét tryk. Du kan på din egen sagsliste se, om tilbuddet er åbnet, og hvad der blev svaret.</p></div></div>
<div class="punkt"><div class="nr">11.2</div><div><p>Vi noterer tidspunktet for den første åbning, tidspunktet for svaret, om svaret var en accept eller et afslag, og den IP-adresse, åbningen og svaret kom fra. Vi noterer ikke andet om din kundes besøg på siden, og adressen giver ikke adgang til noget andet end netop det tilbud.</p></div></div>
<div class="punkt"><div class="nr">11.3</div><div><p>Formålet er dokumentation: at du kan vise, at tilbuddet er modtaget, og hvad der blev svaret. Oplysningerne opbevares sammen med sagen og slettes, når du sletter sagen.</p></div></div>
<div class="punkt"><div class="nr">11.4</div><div><p>Du er dataansvarlig for oplysningerne om din egen kunde, og TeleMakker behandler dem på dine vegne efter databehandleraftalen. <strong>Det er derfor dig, der skal oplyse din kunde om behandlingen.</strong> Der står en linje om det på selve tilbudssiden, så din kunde kan se det, inden der trykkes.</p></div></div>

<h2>12. Når du sender en del af opgaven til en partner</h2>
<div class="punkt"><div class="nr">12.1</div><div><p>TeleMakker kan sende en del af en opgave videre til en anden virksomhed, du selv vælger, for eksempel en elektriker eller en vvs'er. Det sker kun, når du selv opretter opgaven og selv giver linket videre. Der sendes ikke noget af sig selv.</p></div></div>
<div class="punkt"><div class="nr">12.2</div><div><p>Partneren modtager navnet på din virksomhed, den beskrivelse af opgaven, du selv skriver, og den adresse, arbejdet skal udføres på. Partneren modtager <strong>ikke</strong> din kundes navn, telefonnummer eller e-mailadresse, ikke tilbuddet, ikke dine priser, ikke samtalen med kunden og ikke billeder.</p></div></div>
<div class="punkt"><div class="nr">12.3</div><div><p>Adressen sendes med, fordi en pris afhænger af, hvor arbejdet skal udføres. Adressen er en oplysning om din kunde, og det er derfor en videregivelse af personoplysninger til en anden virksomhed.</p></div></div>
<div class="punkt"><div class="nr">12.4</div><div><p><strong>Du bestemmer, om det skal ske, og du bestemmer hvem.</strong> Du er dataansvarlig for oplysningerne om din egen kunde. TeleMakker stiller alene midlet til rådighed og behandler oplysningerne på dine vegne efter databehandleraftalen. Partneren er en selvstændig modtager og handler ikke på TeleMakkers vegne.</p></div></div>
<div class="punkt"><div class="nr">12.5</div><div><p><strong>Det er derfor dig, der skal have et grundlag for at videregive oplysningerne, og dig, der skal oplyse din kunde om det.</strong> Som regel vil grundlaget være, at videregivelsen er nødvendig for at opfylde aftalen med kunden, jf. databeskyttelsesforordningen artikel 6(1)(b), eller din legitime interesse i at indhente et tilbud, jf. artikel 6(1)(f). Er du i tvivl, så spørg din kunde først.</p></div></div>
<div class="punkt"><div class="nr">12.6</div><div><p>Vi noterer, hvad der blev sendt, til hvem, hvornår linket blev åbnet første gang, hvornår der blev svaret, og den IP-adresse, åbningen og svaret kom fra. Formålet er dokumentation: at du kan vise, hvad du har bedt om, og hvad du har fået svar på. Oplysningerne opbevares sammen med sagen og slettes, når du sletter sagen.</p></div></div>
<div class="punkt"><div class="nr">12.7</div><div><p>Linket til partneren indeholder en tilfældig nøgle og giver ikke adgang til andet end netop den ene opgave. Det giver ingen adgang til din platform, til dine øvrige sager eller til dine priser.</p></div></div>
"""


# ----------------------------------------------------------------------
# HANDELSBETINGELSERNE
# ----------------------------------------------------------------------
#
# Her er det ikke et helt afsnit, men to saetninger, der laegges BAG
# advokatens 2.2 om, hvad tjenesten goer. Afsnittet beskriver forloebet,
# og de to funktioner er en del af det forloeb.
HB_EFTER = u"På baggrund af samtalens indhold udarbejder systemet"

HB_TILFOEJ = (
    u" Tilbuddet kan desuden stilles til rådighed for kundens slutkunde på "
    u"en personlig adresse, hvor slutkunden kan læse tilbuddet og acceptere "
    u"eller afslå det. TeleMakker registrerer tidspunktet for åbning og svar "
    u"samt den IP-adresse, de kom fra, som dokumentation til kunden."
    u" Kunden kan endvidere stille en afgrænset del af en opgave til "
    u"rådighed for en partnervirksomhed, kunden selv udpeger, med henblik "
    u"på at indhente et underleverandørtilbud. Der stilles alene den "
    u"opgavebeskrivelse, kunden selv forfatter, samt arbejdsstedets adresse "
    u"til rådighed. Kunden er ansvarlig for valget af partnervirksomhed og "
    u"for grundlaget for videregivelsen."
)

# ----------------------------------------------------------------------
# OVERSKRIFTER, DER ER PUDSET AF
# ----------------------------------------------------------------------
#
# Advokatens fil har et par slaafejl i overskrifterne, som ikke skal ud
# paa en side, folk skal laese: "SAMARBEJDSPARTNERE OG/ ELLER
# LEVERAND\u00d8 RER" har baade et mellemrum midt i et ord og en
# skraastreg, der ikke betyder noget.
#
# De blev foer rettet direkte i HTML-siden, og saa ville en koersel af
# vaerktoejet saette slaafejlen tilbage. Vaernet i skriv() fangede det
# den 8. oktober 2026.
#
# DE RETTER KUN OVERSKRIFTER, aldrig selve teksten. Teksten er
# advokatens, og den skal staa, som hun har skrevet den.
#
# Noeglen er det, paent() laver af kilden, saa den er til at slaa op.
RETTEDE_OVERSKRIFTER = {
    u"Samarbejdspartnere og/ eller leverand\u00f8 rer til TeleMakker":
        u"Samarbejdspartnere og leverand\u00f8rer til TeleMakker",
}

# ----------------------------------------------------------------------
# PLADSHOLDERE, DER IKKE MÅ UD PÅ EN OFFENTLIG SIDE
# ----------------------------------------------------------------------
#
# Advokatens handelsbetingelser er to ting i én: en bestillingsblanket
# til den enkelte kunde, og selve betingelserne. Blanketten har tomme
# felter, og ét af dem står midt i en sætning, der også hører til
# betingelserne: "[OPSIGELSESVARSEL]".
#
# EN OFFENTLIG SIDE MÅ IKKE HAVE ET TOMT FELT PÅ SIG. Det blev fanget
# 8. oktober 2026 af værnet i skriv(): siden sagde "6 måneders varsel",
# og en kørsel ville have sat pladsholderen i stedet.
#
# VARSLET HER ER DET, DER ALLEREDE STÅR LIVE, og det er ikke en ny
# beslutning. **De kommercielle vilkår er Mikkels**, og skal varslet
# være et andet, skal det rettes både her og i advokatens fil.
PLADSHOLDERE = {
    u"[OPSIGELSESVARSEL]": u"6 måneders varsel",
}
