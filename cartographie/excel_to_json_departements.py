import pandas as pd
import json
import os

# Chemin du fichier Excel
excel_file = 'c:/Users/Qleyrat/Desktop/ListeElectionsM2025/data/cartographie/INTERPRO_restructures_completfinalversion.xlsx'

# Répertoire de sortie pour les fichiers JSON
output_dir = 'c:/Users/Qleyrat/Desktop/ListeElectionsM2025/data/json_data_new'

# Créer le répertoire de sortie s'il n'existe pas
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Charger le fichier Excel
print(f"Chargement du fichier Excel: {excel_file}")
try:
    df = pd.read_excel(excel_file)
    print(f"Fichier Excel chargé avec succès. {len(df)} lignes trouvées.")
except Exception as e:
    print(f"Erreur lors du chargement du fichier Excel: {e}")
    exit(1)

# Afficher les colonnes pour vérification
print("\nColonnes disponibles dans le fichier Excel:")
for col in df.columns:
    print(f"- {col}")

# Vérifier si les colonnes nécessaires existent
required_columns = ['Département', 'CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"\nAttention: Colonnes manquantes: {missing_columns}")
    print("Veuillez vérifier les noms des colonnes dans le fichier Excel.")
    
    # Afficher les premières lignes pour aider à identifier les colonnes
    print("\nAperçu des premières lignes du fichier Excel:")
    print(df.head())
    
    # Demander à l'utilisateur de mapper les colonnes
    column_mapping = {}
    for col in missing_columns:
        print(f"\nColonne '{col}' non trouvée.")
        available_cols = [c for c in df.columns if c not in column_mapping.values()]
        print(f"Colonnes disponibles: {available_cols}")
        mapped_col = input(f"Entrez le nom de la colonne correspondant à '{col}' (ou laissez vide pour ignorer): ")
        if mapped_col:
            column_mapping[col] = mapped_col
    
    # Renommer les colonnes si nécessaire
    if column_mapping:
        df = df.rename(columns={v: k for k, v in column_mapping.items()})
        print("\nColonnes renommées selon le mapping fourni.")

# Vérifier à nouveau les colonnes requises
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"\nImpossible de continuer. Colonnes toujours manquantes: {missing_columns}")
    exit(1)

# Regrouper les données par département
print("\nRegroupement des données par département...")
departements = {}

for index, row in df.iterrows():
    dept = str(row['Département']).strip()
    
    # Ignorer les lignes sans département
    if not dept or pd.isna(dept) or dept == 'nan':
        continue
    
    # Convertir le département en code à 2 chiffres (ou 3 pour les DOM-TOM)
    try:
        dept_code = dept
        if dept_code.isdigit() and len(dept_code) == 1:
            dept_code = '0' + dept_code
    except:
        print(f"Erreur avec le département: {dept}")
        continue
    
    # Initialiser le département s'il n'existe pas encore
    if dept_code not in departements:
        departements[dept_code] = {
            'nom': dept_code,
            'total_scrutins': 0,
            'total_inscrits': 0,
            'total_votants': 0,
            'total_sve': 0,
            'voix': {
                'CGT': 0,
                'CFDT': 0,
                'CGT-FO': 0,
                'CFTC': 0,
                'CFE-CGC': 0,
                'SOLIDAIRES': 0,
                'UNSA': 0,
                'AUTRES': 0
            },
            'pourcentages': {
                'CGT': 0,
                'CFDT': 0,
                'CGT-FO': 0,
                'CFTC': 0,
                'CFE-CGC': 0,
                'SOLIDAIRES': 0,
                'UNSA': 0,
                'AUTRES': 0
            }
        }
    
    # Ajouter les données de cette ligne au département
    departements[dept_code]['total_scrutins'] += 1
    
    # Ajouter les voix pour chaque syndicat (si disponibles)
    for syndicat in ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']:
        if syndicat in row and not pd.isna(row[syndicat]):
            try:
                departements[dept_code]['voix'][syndicat] += float(row[syndicat])
            except (ValueError, TypeError):
                print(f"Erreur lors de la conversion de {row[syndicat]} en nombre pour {syndicat} dans le département {dept_code}")
    
    # Ajouter les inscrits, votants et SVE si disponibles
    for field, col_name in [('total_inscrits', 'Inscrits'), ('total_votants', 'Votants')]:
        if col_name in row and not pd.isna(row[col_name]):
            try:
                departements[dept_code][field] += float(row[col_name])
            except (ValueError, TypeError):
                print(f"Erreur lors de la conversion de {row[col_name]} en nombre pour {col_name} dans le département {dept_code}")
    
    # Utiliser sve_total pour le total SVE
    if 'sve_total' in row and not pd.isna(row['sve_total']):
        try:
            departements[dept_code]['total_sve'] += float(row['sve_total'])
        except (ValueError, TypeError):
            print(f"Erreur lors de la conversion de {row['sve_total']} en nombre pour sve_total dans le département {dept_code}")

# Calculer les pourcentages pour chaque département
print("\nCalcul des pourcentages...")
for dept_code, dept_data in departements.items():
    total_sve = dept_data['total_sve']
    if total_sve > 0:
        for syndicat in ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']:
            voix = dept_data['voix'][syndicat]
            pourcentage = (voix / total_sve) * 100
            dept_data['pourcentages'][syndicat] = round(pourcentage, 2)
    
    # Déterminer le syndicat dominant
    if total_sve > 0:
        syndicat_dominant = max(dept_data['voix'].items(), key=lambda x: x[1])[0]
        dept_data['syndicat_dominant'] = syndicat_dominant
    else:
        dept_data['syndicat_dominant'] = 'Inconnu'

# Créer un fichier JSON global pour tous les départements
print("\nCréation du fichier JSON global...")
with open(os.path.join(output_dir, 'resultats_departements_new.json'), 'w', encoding='utf-8') as f:
    json.dump(departements, f, ensure_ascii=False, indent=2)

# Créer des fichiers JSON individuels pour chaque département
print("\nCréation des fichiers JSON individuels par département...")
for dept_code, dept_data in departements.items():
    with open(os.path.join(output_dir, f'departement_{dept_code}.json'), 'w', encoding='utf-8') as f:
        json.dump(dept_data, f, ensure_ascii=False, indent=2)

# Créer un fichier JSON pour la carte finale
print("\nCréation du fichier JSON pour la carte finale...")
dept_list = []
for dept_code, dept_data in departements.items():
    dept_list.append({
        'code': dept_code,
        'nom': dept_data['nom'],
        'total_scrutins': int(dept_data['total_scrutins']),
        'total_sve': int(dept_data['total_sve']),
        'voix': {k: int(v) for k, v in dept_data['voix'].items()},
        'pourcentages': dept_data['pourcentages'],
        'syndicat_dominant': dept_data['syndicat_dominant']
    })

with open(os.path.join(output_dir, 'carte_data.json'), 'w', encoding='utf-8') as f:
    json.dump(dept_list, f, ensure_ascii=False, indent=2)

print("\nTraitement terminé avec succès!")
print(f"Nombre de départements traités: {len(departements)}")
print(f"Fichiers JSON créés dans le répertoire: {output_dir}")
