import pridobi
import izlusci
import shrani

STEVILO_STRANI = 25  # skupno število strani organizacije Mestna knjižnica Ljubljana

# 1. korak: prenesi (ali preberi iz predpomnilnika) vse seznamske strani
pridobi.pridobi_htmlje(STEVILO_STRANI)

# 2. korak: iz seznamskih strani izlušči osnovne podatke o vsaki knjigi
osnovni_podatki = izlusci.osnovni_podatki(STEVILO_STRANI)
print(f"Št. osnovnih podatkov: {len(osnovni_podatki)}")

# 3. korak: prenesi (ali preberi iz predpomnilnika) podstran vsake knjige
podatki_in_htmlji = pridobi.pridobi_htmlje_knjig(osnovni_podatki)
print(f"Št. prenesenih HTML-jev knjig: {len(podatki_in_htmlji)}")

# 4. korak: iz podstrani knjig izlušči dodatne podrobnosti in jih združi
knjige = izlusci.podrobnosti_knjig(podatki_in_htmlji)
print(f"Št. izluščenih knjig: {len(knjige)}")

# 5. korak: shrani vse skupaj v CSV
shrani.zapisi_knjige_csv(knjige, "podatki", "knjige.csv")