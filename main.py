import pridobi
import izlusci
import shrani

STEVILO_STRANI = 25

pridobi.pridobi_htmlje(STEVILO_STRANI)

osnovni_podatki = izlusci.osnovni_podatki(STEVILO_STRANI)
print(f"Št. osnovnih podatkov: {len(osnovni_podatki)}")

podatki_in_htmlji = pridobi.pridobi_htmlje_knjig(osnovni_podatki)
print(f"Št. prenesenih HTML-jev knjig: {len(podatki_in_htmlji)}")

knjige = izlusci.podrobnosti_knjig(podatki_in_htmlji)
print(f"Št. izluščenih knjig: {len(knjige)}")

shrani.zapisi_knjige_csv(knjige, "podatki", "knjige.csv")