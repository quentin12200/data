import pandas as pd
import json
import os
import re

def clean_department_code(code):
    """Nettoyer et standardiser le code département."""
    if isinstance(code, float):
        code = str(int(code))
    elif isinstance(code, int):
        code = str(code)
    elif isinstance(code, str):
        # Enlever les caractères non-numériques sauf A et B (pour la Corse)
        code = re.sub(r'[^0-9AB]', '', code)
    
    # Ajouter un zéro devant pour les codes à un chiffre
    if len(code) == 1:
        code = '0' + code
    
    return code

def load_cse_data(file_path):
    """Charger les données CSE depuis le fichier Excel."""
    try:
        # Déterminer l'extension du fichier pour utiliser le bon reader
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            print(f"Format de fichier non pris en charge: {ext}")
            return {}
        
        # Structure pour stocker les données par département
        dept_data = {}
        
        # Colonnes attendues pour les organisations syndicales
        orgs = ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']
        
        # Traiter chaque ligne
        for _, row in df.iterrows():
            try:
                # Extraire le code département et le nettoyer
                if 'code_departement' in df.columns:
                    dept_code = clean_department_code(row['code_departement'])
                elif 'Département' in df.columns:
                    dept_code = clean_department_code(row['Département'])
                else:
                    # Essayer de trouver une colonne qui pourrait contenir le code département
                    dept_cols = [col for col in df.columns if 'dep' in col.lower() or 'dpt' in col.lower() or 'dépt' in col.lower()]
                    if dept_cols:
                        dept_code = clean_department_code(row[dept_cols[0]])
                    else:
                        print("Impossible de trouver la colonne de code département")
                        continue
                
                # Initialiser les données pour ce département si c'est la première fois
                if dept_code not in dept_data:
                    dept_data[dept_code] = {
                        "nom": "",  # Sera rempli plus tard
                        "total_scrutins": 0,
                        "total_inscrits": 0.0,
                        "total_votants": 0.0,
                        "total_sve": 0.0,
                        "voix": {
                            "CSE": {org: 0 for org in orgs},
                            "TPE": {org: 0 for org in orgs},
                            "AGRI": {org: 0 for org in orgs}
                        },
                        "code": dept_code
                    }
                
                # Ajouter le nom du département si disponible
                if 'nom_departement' in df.columns and pd.notna(row['nom_departement']):
                    dept_data[dept_code]["nom"] = row['nom_departement']
                elif 'Libellé' in df.columns and pd.notna(row['Libellé']):
                    dept_data[dept_code]["nom"] = row['Libellé']
                
                # Récupérer et ajouter les données pour chaque organisation
                for org in orgs:
                    voix = 0
                    if org in df.columns and pd.notna(row[org]):
                        voix = float(row[org])
                    elif org.lower() in df.columns and pd.notna(row[org.lower()]):
                        voix = float(row[org.lower()])
                    elif org.upper() in df.columns and pd.notna(row[org.upper()]):
                        voix = float(row[org.upper()])
                    
                    dept_data[dept_code]["voix"]["CSE"][org] = voix
                
                # Récupérer les informations sur les inscrits, votants et SVE
                if 'inscrits' in df.columns and pd.notna(row['inscrits']):
                    dept_data[dept_code]["total_inscrits"] += float(row['inscrits'])
                elif 'Inscrits' in df.columns and pd.notna(row['Inscrits']):
                    dept_data[dept_code]["total_inscrits"] += float(row['Inscrits'])
                
                if 'votants' in df.columns and pd.notna(row['votants']):
                    dept_data[dept_code]["total_votants"] += float(row['votants'])
                elif 'Votants' in df.columns and pd.notna(row['Votants']):
                    dept_data[dept_code]["total_votants"] += float(row['Votants'])
                
                if 'sve' in df.columns and pd.notna(row['sve']):
                    dept_data[dept_code]["total_sve"] += float(row['sve'])
                elif 'SVE' in df.columns and pd.notna(row['SVE']):
                    dept_data[dept_code]["total_sve"] += float(row['SVE'])
                elif 'exprimés' in df.columns and pd.notna(row['exprimés']):
                    dept_data[dept_code]["total_sve"] += float(row['exprimés'])
                elif 'Exprimés' in df.columns and pd.notna(row['Exprimés']):
                    dept_data[dept_code]["total_sve"] += float(row['Exprimés'])
                
                # Incrémenter le nombre de scrutins
                dept_data[dept_code]["total_scrutins"] += 1
                
                # Calculer le total CSE
                cse_total = sum(dept_data[dept_code]["voix"]["CSE"].values())
                dept_data[dept_code]["voix"]["CSE"]["total"] = cse_total
                
            except Exception as e:
                print(f"Erreur lors du traitement d'une ligne: {str(e)}")
        
        return dept_data
    
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSE: {str(e)}")
        return {}

def load_tpe_data(file_path, dept_data):
    """Charger et intégrer les données TPE dans les données existantes."""
    try:
        # Charger le fichier Excel
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            print(f"Format de fichier non pris en charge: {ext}")
            return dept_data
        
        # Colonnes attendues pour les organisations syndicales
        orgs = ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']
        
        # Traiter chaque ligne
        for _, row in df.iterrows():
            try:
                # Extraire le code département et le nettoyer
                if 'code_departement' in df.columns:
                    dept_code = clean_department_code(row['code_departement'])
                elif 'Département' in df.columns:
                    dept_code = clean_department_code(row['Département'])
                else:
                    dept_cols = [col for col in df.columns if 'dep' in col.lower() or 'dpt' in col.lower() or 'dépt' in col.lower()]
                    if dept_cols:
                        dept_code = clean_department_code(row[dept_cols[0]])
                    else:
                        print("Impossible de trouver la colonne de code département dans le fichier TPE")
                        continue
                
                # Vérifier si le département existe déjà dans les données, sinon le créer
                if dept_code not in dept_data:
                    dept_data[dept_code] = {
                        "nom": "",
                        "total_scrutins": 0,
                        "total_inscrits": 0.0,
                        "total_votants": 0.0,
                        "total_sve": 0.0,
                        "voix": {
                            "CSE": {org: 0 for org in orgs},
                            "TPE": {org: 0 for org in orgs},
                            "AGRI": {org: 0 for org in orgs}
                        },
                        "code": dept_code
                    }
                
                # Ajouter le nom du département si nécessaire
                if not dept_data[dept_code]["nom"] and 'nom_departement' in df.columns and pd.notna(row['nom_departement']):
                    dept_data[dept_code]["nom"] = row['nom_departement']
                elif not dept_data[dept_code]["nom"] and 'Libellé' in df.columns and pd.notna(row['Libellé']):
                    dept_data[dept_code]["nom"] = row['Libellé']
                
                # Récupérer et ajouter les données pour chaque organisation
                for org in orgs:
                    voix = 0
                    if org in df.columns and pd.notna(row[org]):
                        voix = float(row[org])
                    elif org.lower() in df.columns and pd.notna(row[org.lower()]):
                        voix = float(row[org.lower()])
                    elif org.upper() in df.columns and pd.notna(row[org.upper()]):
                        voix = float(row[org.upper()])
                    
                    dept_data[dept_code]["voix"]["TPE"][org] = voix
                
                # Récupérer les informations sur les inscrits, votants et SVE
                if 'inscrits' in df.columns and pd.notna(row['inscrits']):
                    dept_data[dept_code]["total_inscrits"] += float(row['inscrits'])
                elif 'Inscrits' in df.columns and pd.notna(row['Inscrits']):
                    dept_data[dept_code]["total_inscrits"] += float(row['Inscrits'])
                
                if 'votants' in df.columns and pd.notna(row['votants']):
                    dept_data[dept_code]["total_votants"] += float(row['votants'])
                elif 'Votants' in df.columns and pd.notna(row['Votants']):
                    dept_data[dept_code]["total_votants"] += float(row['Votants'])
                
                if 'sve' in df.columns and pd.notna(row['sve']):
                    dept_data[dept_code]["total_sve"] += float(row['sve'])
                elif 'SVE' in df.columns and pd.notna(row['SVE']):
                    dept_data[dept_code]["total_sve"] += float(row['SVE'])
                elif 'exprimés' in df.columns and pd.notna(row['exprimés']):
                    dept_data[dept_code]["total_sve"] += float(row['exprimés'])
                elif 'Exprimés' in df.columns and pd.notna(row['Exprimés']):
                    dept_data[dept_code]["total_sve"] += float(row['Exprimés'])
                
                # Incrémenter le nombre de scrutins
                dept_data[dept_code]["total_scrutins"] += 1
                
                # Calculer le total TPE
                tpe_total = sum(dept_data[dept_code]["voix"]["TPE"].values())
                dept_data[dept_code]["voix"]["TPE"]["total"] = tpe_total
                
            except Exception as e:
                print(f"Erreur lors du traitement d'une ligne TPE: {str(e)}")
        
        return dept_data
    
    except Exception as e:
        print(f"Erreur lors du chargement du fichier TPE: {str(e)}")
        return dept_data

def load_agri_data(file_path, dept_data):
    """Charger et intégrer les données AGRI dans les données existantes."""
    try:
        # Charger le fichier Excel
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            print(f"Format de fichier non pris en charge: {ext}")
            return dept_data
        
        # Colonnes attendues pour les organisations syndicales
        orgs = ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']
        
        # Traiter chaque ligne
        for _, row in df.iterrows():
            try:
                # Extraire le code département et le nettoyer
                if 'code_departement' in df.columns:
                    dept_code = clean_department_code(row['code_departement'])
                elif 'Département' in df.columns:
                    dept_code = clean_department_code(row['Département'])
                else:
                    dept_cols = [col for col in df.columns if 'dep' in col.lower() or 'dpt' in col.lower() or 'dépt' in col.lower()]
                    if dept_cols:
                        dept_code = clean_department_code(row[dept_cols[0]])
                    else:
                        print("Impossible de trouver la colonne de code département dans le fichier AGRI")
                        continue
                
                # Vérifier si le département existe déjà dans les données, sinon le créer
                if dept_code not in dept_data:
                    dept_data[dept_code] = {
                        "nom": "",
                        "total_scrutins": 0,
                        "total_inscrits": 0.0,
                        "total_votants": 0.0,
                        "total_sve": 0.0,
                        "voix": {
                            "CSE": {org: 0 for org in orgs},
                            "TPE": {org: 0 for org in orgs},
                            "AGRI": {org: 0 for org in orgs}
                        },
                        "code": dept_code
                    }
                
                # Ajouter le nom du département si nécessaire
                if not dept_data[dept_code]["nom"] and 'nom_departement' in df.columns and pd.notna(row['nom_departement']):
                    dept_data[dept_code]["nom"] = row['nom_departement']
                elif not dept_data[dept_code]["nom"] and 'Libellé' in df.columns and pd.notna(row['Libellé']):
                    dept_data[dept_code]["nom"] = row['Libellé']
                
                # Récupérer et ajouter les données pour chaque organisation
                for org in orgs:
                    voix = 0
                    if org in df.columns and pd.notna(row[org]):
                        voix = float(row[org])
                    elif org.lower() in df.columns and pd.notna(row[org.lower()]):
                        voix = float(row[org.lower()])
                    elif org.upper() in df.columns and pd.notna(row[org.upper()]):
                        voix = float(row[org.upper()])
                    
                    dept_data[dept_code]["voix"]["AGRI"][org] = voix
                
                # Récupérer les informations sur les inscrits, votants et SVE
                if 'inscrits' in df.columns and pd.notna(row['inscrits']):
                    dept_data[dept_code]["total_inscrits"] += float(row['inscrits'])
                elif 'Inscrits' in df.columns and pd.notna(row['Inscrits']):
                    dept_data[dept_code]["total_inscrits"] += float(row['Inscrits'])
                
                if 'votants' in df.columns and pd.notna(row['votants']):
                    dept_data[dept_code]["total_votants"] += float(row['votants'])
                elif 'Votants' in df.columns and pd.notna(row['Votants']):
                    dept_data[dept_code]["total_votants"] += float(row['Votants'])
                
                if 'sve' in df.columns and pd.notna(row['sve']):
                    dept_data[dept_code]["total_sve"] += float(row['sve'])
                elif 'SVE' in df.columns and pd.notna(row['SVE']):
                    dept_data[dept_code]["total_sve"] += float(row['SVE'])
                elif 'exprimés' in df.columns and pd.notna(row['exprimés']):
                    dept_data[dept_code]["total_sve"] += float(row['exprimés'])
                elif 'Exprimés' in df.columns and pd.notna(row['Exprimés']):
                    dept_data[dept_code]["total_sve"] += float(row['Exprimés'])
                
                # Incrémenter le nombre de scrutins
                dept_data[dept_code]["total_scrutins"] += 1
                
                # Calculer le total AGRI
                agri_total = sum(dept_data[dept_code]["voix"]["AGRI"].values())
                dept_data[dept_code]["voix"]["AGRI"]["total"] = agri_total
                
            except Exception as e:
                print(f"Erreur lors du traitement d'une ligne AGRI: {str(e)}")
        
        return dept_data
    
    except Exception as e:
        print(f"Erreur lors du chargement du fichier AGRI: {str(e)}")
        return dept_data

def calculate_dominant_syndicat(dept_data):
    """Déterminer le syndicat dominant pour chaque département."""
    for dept_code, dept in dept_data.items():
        # Calculer le total des voix pour chaque syndicat (somme de CSE, TPE et AGRI)
        voix_totales = {}
        orgs = ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']
        
        for org in orgs:
            voix_totales[org] = (
                dept["voix"]["CSE"].get(org, 0) +
                dept["voix"]["TPE"].get(org, 0) +
                dept["voix"]["AGRI"].get(org, 0)
            )
        
        # Trouver le syndicat avec le plus de voix
        if voix_totales:
            dominant = max(voix_totales.items(), key=lambda x: x[1])
            dept["syndicat_dominant"] = dominant[0]
        else:
            dept["syndicat_dominant"] = "Non défini"
    
    return dept_data

def main():
    # Chemins des fichiers Excel
    cse_file = r'c:\ANALYSELECTION\data\cartographie\INTERPRO_restructures_completfinalversion.xlsx'
    tpe_file = r'c:\ANALYSELECTION\data\voix_tpe_dpt.xlsx'
    agri_file = r'c:\ANALYSELECTION\data\voix_agri_par_dpt.xlsx'
    
    # Vérifier que les fichiers existent
    for f in [cse_file, tpe_file, agri_file]:
        if not os.path.exists(f):
            print(f"Le fichier {f} n'existe pas.")
            return
    
    # Charger les données CSE
    print("Chargement des données CSE...")
    dept_data = load_cse_data(cse_file)
    
    # Intégrer les données TPE
    print("Intégration des données TPE...")
    dept_data = load_tpe_data(tpe_file, dept_data)
    
    # Intégrer les données AGRI
    print("Intégration des données AGRI...")
    dept_data = load_agri_data(agri_file, dept_data)
    
    # Calculer le syndicat dominant pour chaque département
    print("Calcul des syndicats dominants...")
    dept_data = calculate_dominant_syndicat(dept_data)
    
    # Créer le répertoire de sortie s'il n'existe pas
    output_dir = r'c:\ANALYSELECTION\data\json_data_ordonnees'
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder toutes les données dans un seul fichier JSON
    output_file = os.path.join(output_dir, 'resultats_departements_avec_tpe.json')
    print(f"Sauvegarde des données dans {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dept_data, f, ensure_ascii=False, indent=2)
    
    print(f"Traitement terminé. Données sauvegardées dans {output_file}")
    
    # Créer aussi des fichiers individuels par département pour référence
    for dept_code, dept_info in dept_data.items():
        dept_file = os.path.join(output_dir, f'departement_{dept_code}.json')
        with open(dept_file, 'w', encoding='utf-8') as f:
            json.dump(dept_info, f, ensure_ascii=False, indent=2)
    
    print(f"Des fichiers individuels par département ont été créés dans {output_dir}")

if __name__ == "__main__":
    main()
