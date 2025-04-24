import pandas as pd
import os
import json

# Paramètres à adapter
EXCEL_FILE = "c:/Users/Qleyrat/Desktop/ListeElectionsM2025/data/cartographie/INTERPRO_restructures_completfinalversion.xlsx"  # chemin du fichier source
OUTPUT_DIR = "../json_data"  # dossier où écrire les JSON par département

# Colonnes attendues dans l'Excel
COLS_KEEP = [
    "Département", "SIRET", "N°PV", "Raison sociale", "Ville", "CP", "IDCC", "Lib IDCC",
    "Coll", "Date", "Inscrits", "Votants", "sve_total",
    "CGT", "CFDT", "CGT-FO", "CFTC", "CFE-CGC", "SOLIDAIRES", "UNSA", "AUTRES"
]

# Charger l'Excel
df = pd.read_excel(EXCEL_FILE, dtype=str)

# Nettoyer/convertir les colonnes numériques
for col in ["Inscrits", "Votants", "sve_total", "CGT", "CFDT", "CGT-FO", "CFTC", "CFE-CGC", "SOLIDAIRES", "UNSA", "AUTRES"]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

def safe_str(x):
    return str(x) if pd.notnull(x) else ""

# Créer le dossier de sortie si besoin
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Vérifier et normaliser les noms de colonnes
if "Département" in df.columns:
    dept_col = "Département"
elif "Departement" in df.columns:
    dept_col = "Departement"
else:
    raise ValueError("Colonne Département non trouvée dans l'Excel")

if "Coll" in df.columns:
    college_col = "Coll"
elif "Collège" in df.columns:
    college_col = "Collège"
else:
    college_col = "Coll"  # Par défaut
    df[college_col] = ""  # Créer une colonne vide si elle n'existe pas

print(f"Utilisation de la colonne '{dept_col}' pour le département")
print(f"Utilisation de la colonne '{college_col}' pour le collège")

grouped = df.groupby(dept_col)
for code_dept, group in grouped:
    records = []
    for _, row in group.iterrows():
        record = {
            "siret": safe_str(row["SIRET"]),
            "raison_sociale": safe_str(row["Raison sociale"]),
            "ville": safe_str(row["Ville"]),
            "cp": safe_str(row["CP"]),
            "idcc": safe_str(row["IDCC"]),
            "lib_idcc": safe_str(row["Lib IDCC"]),
            "college": safe_str(row[college_col]),
            "date": safe_str(row["Date"]),
            "inscrits": int(row["Inscrits"]),
            "votants": int(row["Votants"]),
            "sve_total": int(row["sve_total"]),
            "voix": {
                "CGT": int(row["CGT"]),
                "CFDT": int(row["CFDT"]),
                "CGT-FO": int(row["CGT-FO"]),
                "CFTC": int(row["CFTC"]),
                "CFE-CGC": int(row["CFE-CGC"]),
                "SOLIDAIRES": int(row["SOLIDAIRES"]),
                "UNSA": int(row["UNSA"]),
                "AUTRES": int(row["AUTRES"])
            }
        }
        records.append(record)
    # Écriture du fichier JSON
    out_file = os.path.join(OUTPUT_DIR, f"departement_{code_dept}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Export terminé : {len(grouped)} fichiers créés dans {OUTPUT_DIR}")
