import json
import random

records = []

for _ in range(100000):
    size = round(random.uniform(0.01, 5.0), 3)
    weight = round(random.uniform(0.1, 1.5), 3)
    records.append([size, weight])  # LISTA zamiast set

with open("paczki.json", "w") as f:
    json.dump(records, f)