import os
import requests
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}

BASE_URL = "https://www.dobreknjige.si/organizacija/mestna-knjiznica-ljubljana/"


def pridobi_ali_preberi_html(url, pot_datoteke, poskusi=3):
    """Vrne HTML vsebino strani - iz lokalne datoteke, če že obstaja,
    sicer jo prenese s spleta, shrani na disk in vrne."""
    if os.path.exists(pot_datoteke):
        with open(pot_datoteke, "r", encoding="utf-8") as f:
            return f.read()

    for poskus in range(1, poskusi + 1):
        odgovor = requests.get(url, headers=HEADERS)
        if odgovor.status_code == 200:
            vsebina = odgovor.text
            with open(pot_datoteke, "w", encoding="utf-8") as f:
                f.write(vsebina)
            time.sleep(1)
            return vsebina

        print(f"Napaka pri prenosu ({odgovor.status_code}, poskus {poskus}/{poskusi}): {url}")
        time.sleep(1)

    print(f"Strani ni bilo mogoče prenesti: {url}")
    return None


def sestavi_url_strani(stevilka_strani):
    """Sestavi URL seznamske strani glede na številko strani."""
    if stevilka_strani <= 1:
        return BASE_URL
    return f"{BASE_URL}page/{stevilka_strani}/"


def pridobi_htmlje(stevilo_strani, mapa="podatki/html_strani"):
    """Prenese (ali prebere iz predpomnilnika) HTML vseh seznamskih strani
    organizacije Mestna knjižnica Ljubljana."""
    os.makedirs(mapa, exist_ok=True)
    for i in range(1, stevilo_strani + 1):
        pot_datoteke = os.path.join(mapa, f"stran{i}.html")
        url = sestavi_url_strani(i)
        pridobi_ali_preberi_html(url, pot_datoteke)


def pridobi_htmlje_knjig(osnovni_podatki, mapa="podatki/html_knjig"):
    """Prenese (ali prebere iz predpomnilnika) HTML podstrani vsake knjige.

    Vrne seznam parov (osnovni_podatek(slovar), html_knjige(string)).
    """
    os.makedirs(mapa, exist_ok=True)
    podatki_in_htmlji = []

    for podatek in osnovni_podatki:
        ime_datoteke = f"{podatek['id']}.html"
        pot_datoteke = os.path.join(mapa, ime_datoteke)

        vsebina = pridobi_ali_preberi_html(podatek["url"], pot_datoteke)
        if vsebina is not None:
            podatki_in_htmlji.append((podatek, vsebina))

    return podatki_in_htmlji