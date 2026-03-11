import json
import random

records = []

for i in range(1, 100001):
    size = round(random.uniform(0.01, 5.0), 3)
    weight_tons = round(random.uniform(0.1, 1.5), 3)
    weight_kg = round(weight_tons * 1000, 3)  # zamiana ton na kilogramy

    record = f"{i} {size} {weight_kg}"
    records.append(record)

with open("paczki.json", "w") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
