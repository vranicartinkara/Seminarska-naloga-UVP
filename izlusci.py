import re
import os
import json

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
    """Odstrani podvojene elemente iz seznama slovarjev glede na dani ključ,
    pri čemer obdrži prvo pojavitev vsakega unikatnega vnosa."""
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
    """Iz HTML vsebine podstrani posamezne knjige izlušči avtorja, oceno,
    število ocen, število strani, čas branja in podatek o nagradah.

    Ocena ni zapisana kot golo besedilo (npr. "4,3"), ampak kot odstotek
    širine vrstice zvezdic (style="width:86%", kar ustreza 86 % od 5
    zvezdic oz. oceni 4,3), zato jo iz odstotka izračunamo nazaj.

    Število nagrad iščemo posebej po strukturi
    <span class="label-bold">Nagrade</span> ... <p class="feature__subtitle ...">2</p>,
    saj se beseda "Nagrade" na strani pojavi tudi drugje (navigacija, zavihki),
    kjer ne pomeni dejanskega števila nagrad."""

    avtor_re = re.search(
        r'<a[^>]*href="https://www\.dobreknjige\.si/avtorji/[^"]+"[^>]*>(?P<avtor>.*?)</a>',
        vsebina,
        re.DOTALL,
    )

    stevilo_strani_re = re.search(
        r'Število strani\s*(?:</[^>]+>\s*<[^>]+>\s*)*?(?P<st_strani>\d+)',
        vsebina,
        re.DOTALL,
    )

    cas_branja_re = re.search(
        r'Čas branja.*?(?P<cas_branja>\d+(?:-\d+)?\s*(?:ur|min))',
        vsebina,
        re.DOTALL,
    )

    sirina_re = re.search(
        r'rating-calculated"\s+style="width:\s*(?P<sirina>[\d.]+)%"',
        vsebina,
    )
    ocena = round(float(sirina_re["sirina"]) / 100 * 5, 1) if sirina_re else None

    stevilo_ocen_re = re.search(r'Število ocen:[^0-9]{0,50}(?P<st_ocen>\d+)', vsebina)

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