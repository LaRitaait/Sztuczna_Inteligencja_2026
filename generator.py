import json
import random


def generuj_dane(nazwa_pliku="paczki_hs.json", ilosc=100000):
    print(f"Generowanie {ilosc} realistycznych paczek na podstawie gęstości...")
    paczki = {}

    for i in range(1, ilosc + 1):
        # 1. Najpierw losujemy gabaryt paczki w cm3
        # (od 1 litra do 120 litrów - duży karton kurierski)
        objetosc_cm3 = random.uniform(1000.0, 120000.0)
        objetosc_litry = objetosc_cm3 / 1000.0

        # 2. Losujemy kategorię gęstości ładunku
        typ_ladunku = random.random()

        if typ_ladunku < 0.35:
            # 35% paczek to "puszyste" i lekkie rzeczy (0.05 - 0.2 kg/litr)
            gestosc = random.uniform(0.05, 0.2)
        elif typ_ladunku < 0.85:
            # 50% paczek to standardowe przedmioty (0.2 - 0.6 kg/litr)
            gestosc = random.uniform(0.2, 0.6)
        else:
            # 15% paczek to małe, ale ciężkie przedmioty (np. książki, 0.6 - 1.5 kg/litr)
            gestosc = random.uniform(0.6, 1.5)

        # 3. Obliczamy wagę z objętości i gęstości
        waga_kg = objetosc_litry * gestosc

        # Zabezpieczenie: jeśli z jakiegoś powodu paczka ważyłaby ponad 50 kg
        # (limit kurierski), ograniczamy jej wagę, żeby zachować pełen realizm.
        if waga_kg > 50.0:
            waga_kg = 50.0

        paczki[i] = {"waga": round(waga_kg, 2), "objetosc": round(objetosc_cm3, 2)}

    with open(nazwa_pliku, 'w', encoding='utf-8') as f:
        json.dump(paczki, f, indent=2)

    print(f"Zapisano do pliku {nazwa_pliku}. Dane są teraz zgodne z prawami fizyki!")


if __name__ == "__main__":
    generuj_dane()
