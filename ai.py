import json
import time
import os
import random

# Ograniczenia i cele (ujednolicone jednostki)
MAX_WEIGHT_G = 1_500_000.0  # Maksymalny udźwig: 1500 kg = 1 500 000 gramów
TARGET_VOLUME_CM3 = 2_500_000.0  # Cel: połowa z 5 m^3 = 2 500 000 cm^3
BATCH_SIZE = 10000  # Rozmiar pojedynczej paczki danych do przetworzenia


def load_data_from_json(filename):
    """Wczytuje dane paczek z pliku JSON (lista stringów 'id objetosc waga')."""
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    packages = []
    for item in data:
        parts = item.strip().split()
        pkg_id = int(parts[0])
        volume = float(parts[1])  # Objętość w cm^3
        weight_g = float(parts[2])  # Waga w gramach
        packages.append((pkg_id, weight_g, volume))

    return packages


def generate_test_json(filename, count=100000):
    """Generuje plik testowy paczki.json w zadanym formacie."""
    print(f"Tworzenie pliku testowego {filename} z {count} paczek...")
    dummy_data = []
    for i in range(1, count + 1):
        v = round(random.uniform(100.0, 5000.0), 1)
        w = round(random.uniform(100.0, 10000.0), 1)
        dummy_data.append(f"{i} {v} {w}")

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(dummy_data, file, indent=2)
    print("Zakończono tworzenie pliku testowego.\n")


def save_batched_results_to_json(all_results, filename="wynik.json"):
    """Zapisuje wyniki wszystkich iteracji z podsumowaniem do pliku JSON."""
    formatted_results = {}

    for batch_num, data in all_results.items():
        packed_packages = data['packages']

        # Obliczanie podsumowania dla danej iteracji
        total_vol = sum(p[2] for p in packed_packages)
        total_weight = sum(p[1] for p in packed_packages)

        formatted_results[f"Iteracja_{batch_num}"] = {
            "podsumowanie": {
                "liczba_paczek": len(packed_packages),
                "calkowita_objetosc_cm3": total_vol,
                "calkowita_waga_kg": total_weight / 1000.0,
                "brakuje_do_celu_cm3": TARGET_VOLUME_CM3 - total_vol
            },
            "zapakowane_paczki": [
                {"id": p[0], "objetosc_cm3": p[2], "waga_g": p[1]} for p in packed_packages
            ]
        }

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(formatted_results, file, indent=4)
    print(f"\nPomyślnie zapisano wszystkie wyniki do pliku {filename}.")


def optimize_packing(packages):
    """Algorytm optymalizujący objętość (Greedy + Hill Climbing) dla danej puli paczek."""
    # KROK 1: Sortowanie
    packages.sort(key=lambda x: (x[2] / x[1]) if x[1] > 0 else float('inf'), reverse=True)

    selected_packages = set()
    current_weight = 0.0
    current_volume = 0.0

    # Faza zachłanna
    for pkg in packages:
        pkg_id, weight, volume = pkg
        if current_volume + volume <= TARGET_VOLUME_CM3 and current_weight + weight <= MAX_WEIGHT_G:
            selected_packages.add(pkg_id)
            current_weight += weight
            current_volume += volume

    # KROK 2: Przeszukiwanie lokalne
    packed = [p for p in packages if p[0] in selected_packages]
    unpacked = [p for p in packages if p[0] not in selected_packages]

    improvements = True
    iterations = 0
    max_iterations = 2000

    while improvements and iterations < max_iterations:
        improvements = False
        iterations += 1

        # Próba 1: Dokładanie
        for j in range(len(unpacked) - 1, -1, -1):
            u_id, u_w, u_v = unpacked[j]
            if current_volume + u_v <= TARGET_VOLUME_CM3 and current_weight + u_w <= MAX_WEIGHT_G:
                packed.append(unpacked.pop(j))
                current_volume += u_v
                current_weight += u_w
                improvements = True

        # Próba 2: Zamiana
        if not improvements:
            for i in range(len(packed)):
                p_id, p_w, p_v = packed[i]
                for j in range(len(unpacked)):
                    u_id, u_w, u_v = unpacked[j]

                    if u_v > p_v:
                        new_volume = current_volume - p_v + u_v
                        new_weight = current_weight - p_w + u_w

                        if new_volume <= TARGET_VOLUME_CM3 and new_weight <= MAX_WEIGHT_G:
                            current_volume = new_volume
                            current_weight = new_weight
                            packed[i] = unpacked[j]
                            unpacked[j] = (p_id, p_w, p_v)
                            improvements = True
                            break
                if improvements:
                    break

    return packed, current_volume, current_weight


# --- URUCHOMIENIE PROGRAMU ---
if __name__ == "__main__":
    input_filename = 'paczki.json'
    output_filename = 'wynik.json'

    if not os.path.exists(input_filename):
        generate_test_json(input_filename, count=100000)

    print(f"Wczytywanie danych z pliku {input_filename}...\n")
    start_time = time.time()

    all_parsed_packages = load_data_from_json(input_filename)

    # Słownik do przechowywania wyników ze wszystkich iteracji
    all_batch_results = {}

    # Podział 100 000 elementów na partie po 10 000
    for i in range(0, len(all_parsed_packages), BATCH_SIZE):
        batch_number = (i // BATCH_SIZE) + 1
        current_batch = all_parsed_packages[i:i + BATCH_SIZE]

        print(f"--- Przetwarzanie iteracji {batch_number} (Paczki od {i + 1} do {i + len(current_batch)}) ---")

        # Przekazujemy kopię listy (current_batch.copy()), żeby nie modyfikować oryginału
        solution_packages, final_volume, final_weight = optimize_packing(current_batch.copy())

        print(f"-> Końcowa objętość: {final_volume:.2f} cm^3 (Brakuje: {TARGET_VOLUME_CM3 - final_volume:.2f} cm^3)")
        print(f"-> Końcowa waga: {final_weight / 1000:.2f} kg (Max: {MAX_WEIGHT_G / 1000} kg)")
        print(f"-> Użytych paczek: {len(solution_packages)}\n")

        # Zapisanie wyniku tej iteracji do zbiorczego słownika
        all_batch_results[batch_number] = {
            'packages': solution_packages
        }

    print("Trwa generowanie pliku wynikowego...")
    save_batched_results_to_json(all_batch_results, output_filename)

    end_time = time.time()
    print(f"Całkowity czas wykonywania wszystkich 10 iteracji: {end_time - start_time:.4f} sekund")
