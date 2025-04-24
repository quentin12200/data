import json
import os

# Charger le JSON du département 12
with open('../json_data/departement_12.json', encoding='utf-8') as f:
    data = json.load(f)

# Calculer le total des voix CGT et FO
voix_cgt = sum(pv['voix']['CGT'] for pv in data)
voix_fo = sum(pv['voix']['CGT-FO'] for pv in data)

print(f"Total voix CGT dans le 12 : {voix_cgt}")
print(f"Total voix FO dans le 12 : {voix_fo}")
print(f"Nombre de PV dans le 12 : {len(data)}")
