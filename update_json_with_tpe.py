import pandas as pd
import json

# Lire les données TPE
df_tpe = pd.read_excel('Résultats départementaux agrégés par OS nationales et interprofessionnelles.xlsx')
df_tpe = df_tpe.dropna(subset=['Code'])

# Remplacer les '-' par 0
for col in df_tpe.columns:
    df_tpe[col] = df_tpe[col].replace('-', 0)

# Lire le fichier JSON existant
with open('json_data_ordonnees/resultats_departements.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mapping des noms de colonnes
mapping = {
    'CFE-CGC': 'CFE-CGC',
    'CFTC': 'CFTC',
    'FO': 'CGT-FO',
    'Solidaires': 'SOLIDAIRES',
    'UNSA': 'UNSA',
    'CGT': 'CGT',
    'CFDT': 'CFDT',
    'CAT': 'AUTRES',
    'CNT-SO': 'AUTRES',
    'le_SGJ': 'AUTRES'
}

# Pour chaque département dans le fichier JSON
for code, dept in data.items():
    if code == 'NAT':  # Ignorer les données nationales
        continue
        
    # Trouver les données TPE correspondantes
    tpe_row = df_tpe[df_tpe['Code'].astype(str).str.zfill(2) == str(code).zfill(2)]
    if not tpe_row.empty:
        # Ajouter les voix TPE aux voix existantes
        for tpe_col, json_col in mapping.items():
            voix_tpe = tpe_row[tpe_col].iloc[0]
            if pd.notna(voix_tpe):
                dept['voix'][json_col] = dept['voix'].get(json_col, 0) + int(float(voix_tpe))
        
        # Mettre à jour le total des suffrages exprimés
        total_tpe = tpe_row['Suffrages exprimés'].iloc[0]
        if pd.notna(total_tpe):
            dept['total_sve'] = dept['total_sve'] + float(total_tpe)
            
        # Recalculer les pourcentages
        total_voix = sum(dept['voix'].values())
        for syndicat in dept['voix'].keys():
            dept['pourcentages'][syndicat] = round((dept['voix'][syndicat] / total_voix) * 100, 2)
            
        # Déterminer le syndicat dominant
        max_voix = max(dept['voix'].items(), key=lambda x: x[1])
        dept['syndicat_dominant'] = max_voix[0]

# Sauvegarder le fichier JSON mis à jour
with open('json_data_ordonnees/resultats_departements_avec_tpe.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Les données ont été mises à jour avec les voix TPE et sauvegardées dans 'resultats_departements_avec_tpe.json'")
