# Analiza knjig Mestne knjižnice Ljubljana
## Uvod

Za projektno nalogo pri predmetu Uvod v programiranje sem podatke črpala iz spletne strani dobreknjige.si, kjer je zbran katalog knjig z ocenami bralcev. Osredotočila sem se na knjige, ki jih ima v svoji zbirki Mestna knjižnica Ljubljana. Za vsako knjigo so na voljo podatki o naslovu, avtorju, povprečni oceni, številu ocen, številu strani, ocenjenem času branja in o tem, ali je bila knjiga kdaj nagrajena.

Na dan pridobivanja podatkov je bilo na strani organizacije zajetih 25 strani s knjigami, kar znaša 991 unikatnih knjig. Od tega jih ima 821 vsaj eno oceno. Pri knjigah brez ocen je v podatkih ocena zapisana kot 0.0, kar pomeni "še ni ocenjeno" in ne dejanske ocene nič, zato jih pri analizi ocen izpustim.

## Navodila za uporabo

Glavna datoteka, s katero lahko uporabnik zažene program, je main.py. Ta po vrsti pokliče pridobivanje HTML strani (pridobi.py), izluščevanje podatkov iz njih (izlusci.py) in zapis podatkov v CSV datoteko (shrani.py). Program potrebuje knjižnico requests (pip install requests).

HTML strani s seznamom knjig in podstrani posameznih knjig se ob prenosu shranijo v mapi podatki/html_strani in podatki/html_knjig, ki služita kot predpomnilnik. Če datoteka že obstaja, se ponovno ne prenese, zato je vsak nadaljnji zagon hiter. Ker sta mapi veliki (skoraj 1000 datotek), nista del repozitorija (.gitignore), pri prvem zagonu pa se prenesejo znova. Ta postopek je zamuden, ker gre za prenos ~1000 spletnih strani s premorom med zahtevami. Priloženi so že izluščeni podatki v podatki/vse_knjige.json in podatki/knjige.csv.

Za analizo podatkov poženite analiza.ipynb, ki podatke prebere iz podatki/knjige.csv in potrebuje knjižnici pandas in matplotlib.

## Analiza podatkov

Datoteka analiza.ipynb pripravi tabelarično in grafično analizo pridobljenih podatkov – med drugim prikaže porazdelitev ocen in dolžine knjig, najbolje in najslabše ocenjene knjige, primerja povprečno oceno nagrajenih in nenagrajenih knjig, prikaže avtorje z največ knjigami v zbirki ter poišče povezave med številom strani, časom branja, oceno in številom ocen.