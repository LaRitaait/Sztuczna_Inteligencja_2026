import json
import random

records = []

MAX_WEIGHT_G = 31500  # 31.5 kg w gramach
MAX_DENSITY = 10      # g/cm^3

for i in range(1, 100001):
    # Objętość w cm³ (liczba całkowita)
    volume_cm3 = random.randint(600, 99712)

    # Maksymalna masa wynikająca z ograniczenia gęstości (10 g/cm^3)
    max_mass_from_density = volume_cm3 * MAX_DENSITY

    # Rzeczywisty maksymalny zakres masy: nie więcej niż 31 500 g
    max_mass_possible = min(MAX_WEIGHT_G, max_mass_from_density)

    # Masa w gramach (liczba całkowita, co najmniej 1 g)
    mass_g = random.randint(1, max_mass_possible)

    # Format: ID objętość masa
    record = f"{i} {volume_cm3} {mass_g}"
    records.append(record)

with open("paczki.json", "w") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
