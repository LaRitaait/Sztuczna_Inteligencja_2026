# algorytm_harmoniczny.py
import json
import random
import time


def wczytaj_dane(nazwa_pliku="paczki_hs.json"):
    with open(nazwa_pliku, 'r', encoding='utf-8') as f:
        dane = json.load(f)
    return {int(k): v for k, v in dane.items()}


def ocena_fitness(wektor_rozwiazania, baza_paczek, max_weight, max_volume, min_pack, max_pack):
    unikalne_paczki = set([p for p in wektor_rozwiazania if p != 0])
    ilosc = len(unikalne_paczki)

    calkowita_waga = sum(baza_paczek[pid]["waga"] for pid in unikalne_paczki)
    calkowita_objetosc = sum(baza_paczek[pid]["objetosc"] for pid in unikalne_paczki)

    kara = 0.0

    # 1. NALICZANIE KAR (zostaje tak samo)
    if calkowita_waga > max_weight:
        kara += 1500 + (calkowita_waga - max_weight) * 2.0
    if calkowita_objetosc > max_volume:
        kara += 1500 + (calkowita_objetosc - max_volume) * 0.001
    if ilosc < min_pack:
        kara += 1500 + (min_pack - ilosc) * 50.0
    elif ilosc > max_pack:
        kara += 1500 + (ilosc - max_pack) * 50.0

    # 2. NALICZANIE NAGRODY (Wielokryterialne)

    # Punkty za wagę (max to np. 1500)
    punkty_waga = calkowita_waga

    # Punkty za objętość - skalujemy je!
    # Dzielimy obecną objętość przez maksymalną (daje to ułamek np. 0.8 czyli 80% zapełnienia).
    # Następnie mnożymy to przez max_weight (1500).
    # Dzięki temu pełna objętość 2,5 mln cm3 daje dokładnie 1500 punktów.
    punkty_objetosc = (calkowita_objetosc / max_volume) * max_weight

    # Wyciągamy średnią. Idealny van ma 1500 z wagi i 1500 z objętości,
    # więc (1500+1500)/2 = 1500 fitnessu
    nagroda = (punkty_waga + punkty_objetosc) / 2.0

    # Ostateczny wynik to zbilansowana nagroda minus ewentualne kary
    fitness = nagroda - kara

    return fitness, calkowita_waga, calkowita_objetosc, ilosc


def stworz_losowe_rozwiazanie(max_id, max_pack):
    rozwiazanie = []
    for _ in range(max_pack):
        # Całkowita losowość: 30% na pusty slot, 70% na wylosowanie paczki.
        if random.random() < 0.30:
            rozwiazanie.append(0)
        else:
            rozwiazanie.append(random.randint(1, max_id))
    return rozwiazanie


# Zmieniony nagłówek funkcji (dodano krok_akt)
def uruchom_hs(ni, hms, hmcr, par, max_weight, max_volume, min_pack, max_pack, krok_akt=1000, kolejka=None):
    baza_paczek = wczytaj_dane()
    MAX_ID = len(baza_paczek)

    harmony_memory = []

    # 1. Inicjalizacja początkowa
    for _ in range(hms):
        wektor = stworz_losowe_rozwiazanie(MAX_ID, max_pack)
        fit, waga, obj, ilosc = ocena_fitness(wektor, baza_paczek, max_weight, max_volume, min_pack, max_pack)
        harmony_memory.append({
            "wektor": wektor, "fitness": fit, "waga": waga, "objetosc": obj, "ilosc": ilosc
        })

    # Startowy punkt dla wykresu - ZMIANA: Wysyłamy też najlepszy wektor!
    if kolejka is not None:
        najlepszy_start = max(harmony_memory, key=lambda x: x["fitness"])
        kolejka.put((0, najlepszy_start["fitness"], najlepszy_start["wektor"]))

    # 2. Główna pętla
    for iteracja in range(1, ni + 1):
        nowy_wektor = []
        for kolumna in range(max_pack):
            if random.random() < hmcr:
                losowy_wiersz = random.randint(0, hms - 1)
                wybrana_paczka = harmony_memory[losowy_wiersz]["wektor"][kolumna]

                if random.random() < par:
                    wybrana_paczka = random.randint(0, MAX_ID)
                nowy_wektor.append(wybrana_paczka)
            else:
                if random.random() < 0.10:
                    nowy_wektor.append(0)
                else:
                    nowy_wektor.append(random.randint(1, MAX_ID))

        fit, waga, obj, ilosc = ocena_fitness(nowy_wektor, baza_paczek, max_weight, max_volume, min_pack, max_pack)

        najgorszy_indeks = 0
        najgorszy_fitness = harmony_memory[0]["fitness"]
        for i in range(1, hms):
            if harmony_memory[i]["fitness"] < najgorszy_fitness:
                najgorszy_fitness = harmony_memory[i]["fitness"]
                najgorszy_indeks = i

        if fit > najgorszy_fitness:
            harmony_memory[najgorszy_indeks] = {
                "wektor": nowy_wektor, "fitness": fit, "waga": waga, "objetosc": obj, "ilosc": ilosc
            }

        # ZMIANA: Wysyłamy paczkę z danymi zawierającą wektor!
        if iteracja % krok_akt == 0 and kolejka is not None:
            najlepszy_hm = max(harmony_memory, key=lambda x: x["fitness"])
            kolejka.put((iteracja, najlepszy_hm["fitness"], najlepszy_hm["wektor"]))
            #time.sleep(0.001)

    harmony_memory.sort(key=lambda x: x["fitness"], reverse=True)
    return harmony_memory[0]
