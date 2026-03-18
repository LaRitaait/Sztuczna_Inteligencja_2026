# algorytm_harmoniczny.py
import json
import random


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
    if calkowita_waga > max_weight: kara += (calkowita_waga - max_weight) * 1000
    if calkowita_objetosc > max_volume: kara += (calkowita_objetosc - max_volume) * 1000
    if ilosc < min_pack:
        kara += (min_pack - ilosc) * 5000
    elif ilosc > max_pack:
        kara += (ilosc - max_pack) * 5000

    fitness = calkowita_waga - kara
    return fitness, calkowita_waga, calkowita_objetosc, ilosc


def stworz_losowe_rozwiazanie(max_id, max_pack):
    rozwiazanie = []
    for _ in range(max_pack):
        if random.random() < 0.1:
            rozwiazanie.append(0)
        else:
            rozwiazanie.append(random.randint(1, max_id))
    return rozwiazanie


def uruchom_hs(ni, hms, hmcr, par, max_weight, max_volume, min_pack, max_pack, kolejka=None):
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

    # Krok aktualizacji wykresu (np. co 1% wszystkich iteracji, by nie przeciążyć GUI)
    krok_aktualizacji = max(1, ni // 100)

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
                if random.random() < 0.1:
                    nowy_wektor.append(0)
                else:
                    nowy_wektor.append(random.randint(1, MAX_ID))

        fit, waga, obj, ilosc = ocena_fitness(nowy_wektor, baza_paczek, max_weight, max_volume, min_pack, max_pack)

        # Aktualizacja pamięci
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

        # Wysyłanie danych do GUI dokładnie co 1000 iteracji
        if iteracja % 100 == 0 and kolejka is not None:
            obecny_najlepszy = max(hm["fitness"] for hm in harmony_memory)
            kolejka.put((iteracja, obecny_najlepszy))

    harmony_memory.sort(key=lambda x: x["fitness"], reverse=True)
    return harmony_memory[0]
