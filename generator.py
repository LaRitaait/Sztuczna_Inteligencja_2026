# generator.py
import json
import random


def generuj_dane(nazwa_pliku="paczki_hs.json", ilosc=100000):
    print(f"Generowanie {ilosc} paczek...")
    paczki = {}

    for i in range(1, ilosc + 1):
        # Generujemy paczki o zróżnicowanej wadze (np. od 1 do 50 kg)
        # i objętości (np. od 10 000 do 100 000 cm3)
        waga = round(random.uniform(1.0, 50.0), 2)
        objetosc = round(random.uniform(10000.0, 100000.0), 2)

        # Zapisujemy w formacie słownika, gdzie kluczem jest ID
        paczki[i] = {"waga": waga, "objetosc": objetosc}

    with open(nazwa_pliku, 'w', encoding='utf-8') as f:
        json.dump(paczki, f, indent=2)

    print(f"Zapisano do pliku {nazwa_pliku}")


if __name__ == "__main__":
    generuj_dane()
