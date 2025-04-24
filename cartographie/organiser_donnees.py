import pandas as pd
import json
import os
import re
from collections import OrderedDict

# Chemins des fichiers
input_dir = 'c:/Users/Qleyrat/Desktop/ListeElectionsM2025/data/json_data_new'
output_dir = 'c:/Users/Qleyrat/Desktop/ListeElectionsM2025/data/json_data_ordonnees'

# Créer le répertoire de sortie s'il n'existe pas
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Dictionnaire des noms de départements
noms_departements = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence", "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes", "09": "Ariège", "10": "Aube",
    "11": "Aude", "12": "Aveyron", "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal",
    "16": "Charente", "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud",
    "2B": "Haute-Corse", "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne",
    "25": "Doubs", "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde", "34": "Hérault",
    "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire", "38": "Isère", "39": "Jura",
    "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire", "44": "Loire-Atlantique",
    "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère", "49": "Maine-et-Loire",
    "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle",
    "55": "Meuse", "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord",
    "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin", "68": "Haut-Rhin", "69": "Rhône",
    "70": "Haute-Saône", "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres",
    "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse",
    "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne",
    "90": "Territoire de Belfort", "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis", "94": "Val-de-Marne",
    "95": "Val-d'Oise", "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion",
    "975": "Saint-Pierre-et-Miquelon", "976": "Mayotte", "977": "Saint-Barthélemy", "978": "Saint-Martin",
    "NAT": "National"
}

# Ordre des syndicats pour l'affichage
ordre_syndicats = ["CGT", "CFDT", "CGT-FO", "CFTC", "CFE-CGC", "SOLIDAIRES", "UNSA", "AUTRES"]

print("Chargement des données...")

# Charger le fichier JSON global
with open(os.path.join(input_dir, 'resultats_departements_new.json'), 'r', encoding='utf-8') as f:
    departements_data = json.load(f)

# Créer une liste pour stocker les données triées
departements_ordonnes = []

print("Traitement des départements...")

# Traiter chaque département
for dept_code, dept_data in departements_data.items():
    # Ajouter le nom complet du département
    if dept_code in noms_departements:
        dept_data['nom'] = noms_departements[dept_code]
    
    # Arrondir les nombres
    for syndicat in dept_data['voix']:
        dept_data['voix'][syndicat] = round(dept_data['voix'][syndicat])
    
    # Recalculer les pourcentages pour s'assurer qu'ils sont corrects
    total_voix = sum(dept_data['voix'].values())
    if total_voix > 0:
        for syndicat in dept_data['voix']:
            dept_data['pourcentages'][syndicat] = round((dept_data['voix'][syndicat] / total_voix) * 100, 2)
    
    # Déterminer le syndicat dominant
    if total_voix > 0:
        syndicat_dominant = max(dept_data['voix'].items(), key=lambda x: x[1])[0]
        dept_data['syndicat_dominant'] = syndicat_dominant
    
    # Réorganiser les syndicats dans l'ordre défini
    voix_ordonnees = OrderedDict()
    pourcentages_ordonnes = OrderedDict()
    for syndicat in ordre_syndicats:
        if syndicat in dept_data['voix']:
            voix_ordonnees[syndicat] = dept_data['voix'][syndicat]
            pourcentages_ordonnes[syndicat] = dept_data['pourcentages'][syndicat]
    
    dept_data['voix'] = voix_ordonnees
    dept_data['pourcentages'] = pourcentages_ordonnes
    
    # Ajouter le code du département
    dept_data['code'] = dept_code
    
    # Ajouter aux départements ordonnés
    departements_ordonnes.append(dept_data)

print("Tri des départements...")

# Fonction pour trier les départements
def tri_departements(dept):
    code = dept['code']
    # Gérer les cas spéciaux
    if code == 'NAT':
        return 'ZZZ'  # Pour que National soit à la fin
    elif code.startswith('97'):
        return 'ZZ' + code  # Pour que les DOM-TOM soient après les départements métropolitains
    elif code in ['2A', '2B']:
        # Convertir 2A et 2B en nombres pour le tri
        return '20' + ('1' if code == '2A' else '2')
    else:
        return code

# Trier les départements
departements_ordonnes.sort(key=tri_departements)

print("Création des fichiers JSON...")

# Créer un fichier JSON pour la carte
with open(os.path.join(output_dir, 'carte_data.json'), 'w', encoding='utf-8') as f:
    json.dump(departements_ordonnes, f, ensure_ascii=False, indent=2)

# Créer un fichier JSON global
departements_dict = {dept['code']: dept for dept in departements_ordonnes}
with open(os.path.join(output_dir, 'resultats_departements.json'), 'w', encoding='utf-8') as f:
    json.dump(departements_dict, f, ensure_ascii=False, indent=2)

# Créer des fichiers JSON individuels pour chaque département
for dept in departements_ordonnes:
    with open(os.path.join(output_dir, f'departement_{dept["code"]}.json'), 'w', encoding='utf-8') as f:
        json.dump(dept, f, ensure_ascii=False, indent=2)

# Créer un fichier de statistiques par région
print("Création des statistiques par région...")

# Dictionnaire des régions et leurs départements
regions = {
    "Auvergne-Rhône-Alpes": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"],
    "Bourgogne-Franche-Comté": ["21", "25", "39", "58", "70", "71", "89", "90"],
    "Bretagne": ["22", "29", "35", "56"],
    "Centre-Val de Loire": ["18", "28", "36", "37", "41", "45"],
    "Corse": ["2A", "2B"],
    "Grand Est": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"],
    "Hauts-de-France": ["02", "59", "60", "62", "80"],
    "Île-de-France": ["75", "77", "78", "91", "92", "93", "94", "95"],
    "Normandie": ["14", "27", "50", "61", "76"],
    "Nouvelle-Aquitaine": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"],
    "Occitanie": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"],
    "Pays de la Loire": ["44", "49", "53", "72", "85"],
    "Provence-Alpes-Côte d'Azur": ["04", "05", "06", "13", "83", "84"],
    "DOM-TOM": ["971", "972", "973", "974", "975", "976", "977", "978"]
}

# Calculer les statistiques par région
stats_regions = {}
for region_nom, dept_codes in regions.items():
    stats_regions[region_nom] = {
        "nom": region_nom,
        "total_scrutins": 0,
        "total_inscrits": 0,
        "total_votants": 0,
        "total_sve": 0,
        "voix": {syndicat: 0 for syndicat in ordre_syndicats},
        "pourcentages": {syndicat: 0 for syndicat in ordre_syndicats}
    }
    
    # Agréger les données des départements
    for dept_code in dept_codes:
        if dept_code in departements_dict:
            dept = departements_dict[dept_code]
            stats_regions[region_nom]["total_scrutins"] += dept["total_scrutins"]
            stats_regions[region_nom]["total_inscrits"] += dept["total_inscrits"]
            stats_regions[region_nom]["total_votants"] += dept["total_votants"]
            stats_regions[region_nom]["total_sve"] += dept["total_sve"]
            
            for syndicat in ordre_syndicats:
                if syndicat in dept["voix"]:
                    stats_regions[region_nom]["voix"][syndicat] += dept["voix"][syndicat]
    
    # Calculer les pourcentages
    total_voix = sum(stats_regions[region_nom]["voix"].values())
    if total_voix > 0:
        for syndicat in ordre_syndicats:
            stats_regions[region_nom]["pourcentages"][syndicat] = round((stats_regions[region_nom]["voix"][syndicat] / total_voix) * 100, 2)
    
    # Déterminer le syndicat dominant
    if total_voix > 0:
        syndicat_dominant = max(stats_regions[region_nom]["voix"].items(), key=lambda x: x[1])[0]
        stats_regions[region_nom]["syndicat_dominant"] = syndicat_dominant

# Sauvegarder les statistiques par région
with open(os.path.join(output_dir, 'stats_regions.json'), 'w', encoding='utf-8') as f:
    json.dump(stats_regions, f, ensure_ascii=False, indent=2)

# Créer un fichier CSV pour une utilisation facile dans Excel
print("Création du fichier CSV...")

# Préparer les données pour le CSV
csv_data = []
for dept in departements_ordonnes:
    row = {
        "Code": dept["code"],
        "Département": dept["nom"],
        "Scrutins": dept["total_scrutins"],
        "Inscrits": int(dept["total_inscrits"]),
        "Votants": int(dept["total_votants"]),
        "SVE": int(dept["total_sve"]),
        "Syndicat dominant": dept["syndicat_dominant"]
    }
    
    # Ajouter les voix et pourcentages pour chaque syndicat
    for syndicat in ordre_syndicats:
        if syndicat in dept["voix"]:
            row[f"Voix {syndicat}"] = int(dept["voix"][syndicat])
            row[f"% {syndicat}"] = dept["pourcentages"][syndicat]
    
    csv_data.append(row)

# Créer un DataFrame pandas et sauvegarder en CSV
df = pd.DataFrame(csv_data)
df.to_csv(os.path.join(output_dir, 'resultats_departements.csv'), index=False, encoding='utf-8-sig')

print("Traitement terminé avec succès!")
print(f"Fichiers créés dans le répertoire: {output_dir}")
print(f"Nombre de départements traités: {len(departements_ordonnes)}")
print(f"Nombre de régions traitées: {len(stats_regions)}")
