import json
import random

records = []

MAX_WEIGHT_G = 31500  # 31.5 kg w gramach

for i in range(1, 100001):
    # Objętość w cm³
    volume_cm3 = round(random.uniform(600, 99712), 3)

    # Gęstość do 19,25 g/cm³
    density = random.uniform(0.1, 19.25)

    # Masa w gramach
    mass_g = round(volume_cm3 * density, 3)

    # Ograniczenie do 31.5 kg
    if mass_g > MAX_WEIGHT_G:
        mass_g = MAX_WEIGHT_G

    # Format: ID objętość masa
    record = f"{i} {volume_cm3} {mass_g}"
    records.append(record)

with open("paczki.json", "w") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
