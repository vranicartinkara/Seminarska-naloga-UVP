import csv
import os


def zapisi_csv(fieldnames, rows, directory, filename):
    """Zapiše podatke iz 'rows' v CSV datoteko 'directory'/'filename',
    s stolpci definiranimi v 'fieldnames'."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def zapisi_knjige_csv(knjige, directory="podatki", filename="knjige.csv"):
    """Zapiše podatke o knjigah v CSV datoteko. Predpostavi, da imajo vsi
    slovarji v 'knjige' enake ključe in da seznam ni prazen."""
    assert knjige and all(k.keys() == knjige[0].keys() for k in knjige)
    zapisi_csv(knjige[0].keys(), knjige, directory, filename)