import re
import os
import json

# --- OPOMBA ---
# Ker gre za regex-parsanje surove HTML kode, so spodnji vzorci narejeni na
# podlagi opazovane strukture strani. Za naslov/url knjige (<h2><a href=...>)
# je vzorec zanesljiv, saj WordPress naslove knjig dosledno ovija v <h2>.
# Za avtorja in oznako (nagrajena/ocena) pa je vzorec "najboljša ocena" -
# če po prvem zagonu pridobi.py + izlusci.py katero od teh polj ostane
# prazno, odpri eno od datotek v podatki/html_strani/, poišči (Ctrl+F) en
# naslov knjige in mi prilepi ~30 vrstic kode okoli njega, da vzorec
# prilagodim.

vzorec_knjige = re.compile(
    r'<h2[^>]*>\s*<a[^>]*href="(?P<url>https://www\.dobreknjige\.si/knjige/[^"]+)"[^>]*>'
    r'(?P<naslov>.*?)</a>\s*</h2>',
    re.DOTALL,
)


def id_iz_url(url):
    """Iz URL-ja knjige (npr. .../knjige/hiperion-2/) izlušči 'slug' kot id."""
    return url.strip("/").split("/")[-1]


def pocisti(besedilo):
    """Odstrani morebitne preostale HTML oznake in odvečen presledke."""
    besedilo = re.sub(r"<[^>]+>", "", besedilo)
    return re.sub(r"\s+", " ", besedilo).strip()


def odstrani_duplikate(seznam, kljuc):
    videni = set()
    unikatni = []
    for element in seznam:
        if element[kljuc] not in videni:
            videni.add(element[kljuc])
            unikatni.append(element)
    return unikatni


def osnovni_podatki(stevilo_strani, mapa="podatki/html_strani"):
    """Iz vseh predpomnjenih seznamskih strani izlušči osnovne podatke
    (id, naslov, url) vsake knjige in jih zaradi preglednosti shrani v
    json datoteko."""
    osnovni = []

    for i in range(1, stevilo_strani + 1):
        pot_datoteke = os.path.join(mapa, f"stran{i}.html")

        if not os.path.exists(pot_datoteke):
            print(f"html{i}-te strani nisem našel")
            continue

        with open(pot_datoteke, "r", encoding="utf-8") as dat:
            vsebina = dat.read()

        for najdba in vzorec_knjige.finditer(vsebina):
            url = najdba["url"]
            osnovni.append({
                "id": id_iz_url(url),
                "naslov": pocisti(najdba["naslov"]),
                "url": url,
            })

    unikatni_osnovni = odstrani_duplikate(osnovni, "id")

    os.makedirs("podatki", exist_ok=True)
    with open("podatki/vse_knjige.json", "w", encoding="utf-8") as f:
        json.dump(unikatni_osnovni, f, ensure_ascii=False, indent=2)

    print(f"Shranjenih {len(unikatni_osnovni)} knjig v vse_knjige.json")
    return unikatni_osnovni


def podrobnosti_knjig(podatki_in_htmlji):
    """Sprejme seznam parov (slovar_osnovnih_podatkov, html_knjige) in za
    vsako knjigo izlušči dodatne podrobnosti, ki jih združi z osnovnimi
    podatki."""
    knjige = []
    for osnovni_podatek, html_knjige in podatki_in_htmlji:
        podrobnosti = izlusci_podrobnosti_o_knjigi(html_knjige)
        knjige.append(podrobnosti | osnovni_podatek)

    return knjige


def izlusci_podrobnosti_o_knjigi(vsebina):
    """Iz HTML vsebine PODSTRANI POSAMEZNE KNJIGE izlušči avtorja, oceno,
    število strani in čas branja."""

    avtor_re = re.search(
        r'<a[^>]*href="https://www\.dobreknjige\.si/avtorji/[^"]+"[^>]*>(?P<avtor>.*?)</a>',
        vsebina,
        re.DOTALL,
    )

    # "Število strani" je sledeno (morda čez nekaj HTML oznak) s samim
    # številom
    stevilo_strani_re = re.search(
        r'Število strani\s*(?:</[^>]+>\s*<[^>]+>\s*)*?(?P<st_strani>\d+)',
        vsebina,
        re.DOTALL,
    )

    # Za "Čas branja" je med napisom in dejansko vrednostjo (npr. "16-17 ur")
    # vrinjeno pojasnilo, zato iščemo prvo naslednjo vrednost oblike
    # "ŠTEVILKA ur" ali "ŠTEVILKA min" (lahko tudi razpon "16-17 ur")
    cas_branja_re = re.search(
        r'Čas branja.*?(?P<cas_branja>\d+(?:-\d+)?\s*(?:ur|min))',
        vsebina,
        re.DOTALL,
    )

    # Ocena ni zapisana kot golo besedilo "4,3", ampak kot odstotek širine
    # vrstice zvezdic: style="width:86%" (86 % od 5 zvezdic = 4,3)
    sirina_re = re.search(
        r'rating-calculated"\s+style="width:\s*(?P<sirina>[\d.]+)%"',
        vsebina,
    )
    ocena = round(float(sirina_re["sirina"]) / 100 * 5, 1) if sirina_re else None

    # "Število ocen:" je ločena statistika bolj proti dnu strani
    stevilo_ocen_re = re.search(r'Število ocen:[^0-9]{0,50}(?P<st_ocen>\d+)', vsebina)

    # Beseda "Nagrade" se na strani pojavi večkrat (navigacija, zavihki ...),
    # zato iščemo POSEBEJ blok z isto strukturo kot pri "Število strani":
    # <span class="label-bold">Nagrade</span> ... <p class="feature__subtitle ...">2</p>
    nagrade_re = re.search(
        r'label-bold">Nagrade</span>.*?feature__subtitle[^>]*>\s*(?P<st_nagrad>\d+)\s*</p>',
        vsebina,
        re.DOTALL,
    )
    nagrajena = bool(nagrade_re) and int(nagrade_re["st_nagrad"]) > 0

    return {
        "avtor": pocisti(avtor_re["avtor"]) if avtor_re else None,
        "ocena": ocena,
        "stevilo_ocen": int(stevilo_ocen_re["st_ocen"]) if stevilo_ocen_re else None,
        "stevilo_strani": int(stevilo_strani_re["st_strani"]) if stevilo_strani_re else None,
        "cas_branja": cas_branja_re["cas_branja"] if cas_branja_re else None,
        "nagrajena": nagrajena,
    }
