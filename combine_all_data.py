import pandas as pd
import json

def convert_to_float(value):
    """Convertit une valeur en float, retourne 0 si c'est un tiret ou NaN"""
    if pd.isna(value) or value == '-':
        return 0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

# Charger les données TPE et AGRI
df_tpe = pd.read_excel('voix_tpe_dpt.xlsx')
df_agri = pd.read_excel('voix_agri_par_dpt.xlsx')

# Charger les données totales actuelles
with open('json_data_ordonnees/resultats_departements_avec_tpe.json', 'r', encoding='utf-8') as f:
    data_totale = json.load(f)

# Créer le nouveau dictionnaire pour stocker toutes les données
resultats_combines = {}

# Mapping des noms de syndicats
syndicats_mapping = {
    'CGT': 'CGT',
    'CFDT': 'CFDT',
    'FO': 'CGT-FO',  # Dans TPE, FO est utilisé au lieu de CGT-FO
    'CGT-FO': 'CGT-FO',
    'CFTC': 'CFTC',
    'CFE-CGC': 'CFE-CGC',
    'Solidaires': 'SOLIDAIRES',  # Dans TPE, Solidaires est utilisé au lieu de SOLIDAIRES
    'SOLIDAIRES': 'SOLIDAIRES',
    'UNSA': 'UNSA',
    'CAT': 'AUTRES',  # Dans TPE, CAT va dans AUTRES
    'AUTRES': 'AUTRES'
}

# Pour chaque département dans les données totales
for dept, dept_data in data_totale.items():
    resultats_combines[dept] = {
        'total_inscrits': dept_data['total_inscrits'],
        'total_votants': dept_data['total_votants'],
        'total_sve': dept_data['total_sve'],
        'voix': {
            'CSE': {},
            'TPE': {},
            'AGRI': {}
        }
    }
    
    # Récupérer les voix TPE pour ce département
    tpe_dept = df_tpe[df_tpe['N_département'] == int(dept)] if dept.isdigit() else pd.DataFrame()
    
    # Récupérer les voix AGRI pour ce département
    agri_dept = df_agri[df_agri['Département'] == int(dept)] if dept.isdigit() else pd.DataFrame()
    
    # Initialiser les compteurs pour chaque type de voix
    for syndicat in ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']:
        # Voix TPE
        voix_tpe = 0
        if not tpe_dept.empty:
            # Pour TPE, on doit gérer les différents noms de syndicats
            for tpe_syndicat, total_syndicat in syndicats_mapping.items():
                if total_syndicat == syndicat and tpe_syndicat in df_tpe.columns:
                    voix_tpe += convert_to_float(tpe_dept[tpe_syndicat].iloc[0])
        resultats_combines[dept]['voix']['TPE'][syndicat] = voix_tpe
        
        # Voix AGRI
        voix_agri = convert_to_float(agri_dept[syndicat].iloc[0]) if not agri_dept.empty and syndicat in agri_dept.columns else 0
        resultats_combines[dept]['voix']['AGRI'][syndicat] = voix_agri
        
        # Voix CSE = Total - TPE - AGRI
        voix_totales = dept_data['voix'].get(syndicat, 0)
        voix_cse = max(0, voix_totales - voix_tpe - voix_agri)
        resultats_combines[dept]['voix']['CSE'][syndicat] = voix_cse

# Sauvegarder les résultats
with open('json_data_ordonnees/resultats_combines.json', 'w', encoding='utf-8') as f:
    json.dump(resultats_combines, f, indent=2, ensure_ascii=False)

print("Fichier resultats_combines.json créé avec succès!")
