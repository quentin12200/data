#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour générer un nouveau fichier JSON qui inclut les données TPE, AGRI et CSE
à partir du fichier PV_FINAUX_TPE_AGRI_PAR_DPT.xlsx et des données existantes.
"""

import pandas as pd
import json
import os
import numpy as np

# Chemins des fichiers
tpe_agri_path = 'PV_FINAUX_TPE_AGRI_PAR_DPT.xlsx'
resultats_dept_path = '../json_data_ordonnees/resultats_departements.json'
output_path = '../json_data_ordonnees/resultats_departements_complets.json'

print(f"Lecture du fichier TPE/AGRI: {tpe_agri_path}...")
df_tpe_agri = pd.read_excel(tpe_agri_path)

# Afficher les informations générales
print(f"Nombre de lignes dans le fichier TPE/AGRI: {len(df_tpe_agri)}")
print(f"Colonnes dans le fichier TPE/AGRI: {df_tpe_agri.columns.tolist()}")

# Charger les données départementales existantes
print(f"Lecture du fichier JSON existant: {resultats_dept_path}...")
with open(resultats_dept_path, 'r', encoding='utf-8') as f:
    resultats_dept = json.load(f)

# Créer un dictionnaire pour stocker les données TPE et AGRI par département
tpe_agri_data = {}

# Traiter les données TPE et AGRI
for _, row in df_tpe_agri.iterrows():
    dept = str(row['Département']).strip()
    
    # Formater le code département sur 2 chiffres si c'est un nombre
    if dept.isdigit() and len(dept) == 1:
        dept = '0' + dept
    elif dept == 'nan' or dept == '':
        continue
    
    # Initialiser les données pour ce département si nécessaire
    if dept not in tpe_agri_data:
        tpe_agri_data[dept] = {
            'TPE': {
                'inscrits': 0,
                'votants': 0,
                'sve': 0,
                'voix': {
                    'CGT': 0, 'CFDT': 0, 'CGT-FO': 0, 'CFTC': 0, 
                    'CFE-CGC': 0, 'SOLIDAIRES': 0, 'UNSA': 0, 'AUTRES': 0
                }
            },
            'AGRI': {
                'inscrits': 0,
                'votants': 0,
                'sve': 0,
                'voix': {
                    'CGT': 0, 'CFDT': 0, 'CGT-FO': 0, 'CFTC': 0, 
                    'CFE-CGC': 0, 'SOLIDAIRES': 0, 'UNSA': 0, 'AUTRES': 0
                }
            }
        }
    
    # Déterminer le type (TPE ou AGRI) en fonction de IDCC ou Coll
    idcc = str(row.get('IDCC', '')).upper() if not pd.isna(row.get('IDCC', '')) else ''
    lib_idcc = str(row.get('Lib IDCC', '')).upper() if not pd.isna(row.get('Lib IDCC', '')) else ''
    college = str(row.get('Coll', '')).upper() if not pd.isna(row.get('Coll', '')) else ''
    
    # Identifier TPE
    is_tpe = False
    if 'TPE' in idcc or 'TPE' in lib_idcc or 'TPE' in college:
        is_tpe = True
        election_type = 'TPE'
    # Identifier AGRI
    elif 'AGRI' in idcc or 'AGRI' in lib_idcc or 'AGRICULTURE' in lib_idcc or 'AGRI' in college:
        election_type = 'AGRI'
    else:
        continue  # Ni TPE ni AGRI
    
    # Extraire les données avec gestion des valeurs non numériques
    def safe_convert_to_int(val, default=0):
        if pd.isna(val):
            return default
        if isinstance(val, (int, float)):
            return int(val)
        try:
            val_str = str(val).strip()
            if val_str == '-' or val_str == '':
                return default
            return int(float(val_str))
        except (ValueError, TypeError):
            print(f"Valeur non convertible: {val} - mise à {default}")
            return default
    
    inscrits = safe_convert_to_int(row.get('Inscrits', 0))
    votants = safe_convert_to_int(row.get('Votants', 0))
    sve = safe_convert_to_int(row.get('sve_total', 0))
    
    # Ajouter les données au dictionnaire
    tpe_agri_data[dept][election_type]['inscrits'] += inscrits
    tpe_agri_data[dept][election_type]['votants'] += votants
    tpe_agri_data[dept][election_type]['sve'] += sve
    
    # Ajouter les voix par syndicat
    for syndicat in ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']:
        voix_val = row.get(syndicat, 0)
        # Gérer les différents cas de valeurs
        if pd.isna(voix_val):
            voix = 0
        elif isinstance(voix_val, (int, float)):
            voix = int(voix_val)
        else:
            # Essayer de convertir en nombre, sinon mettre 0
            try:
                voix_str = str(voix_val).strip()
                if voix_str == '-' or voix_str == '':
                    voix = 0
                else:
                    voix = int(float(voix_str))
            except (ValueError, TypeError):
                print(f"Valeur non convertible pour {syndicat}: {voix_val} - mise à 0")
                voix = 0
        
        tpe_agri_data[dept][election_type]['voix'][syndicat] += voix

# Fusionner les données avec les résultats départementaux existants
resultats_complets = {}

for dept_code, dept_data in resultats_dept.items():
    # Copier les données existantes
    resultats_complets[dept_code] = dept_data.copy()
    
    # Ajouter les données TPE et AGRI si disponibles
    if dept_code in tpe_agri_data:
        resultats_complets[dept_code]['TPE'] = tpe_agri_data[dept_code]['TPE']
        resultats_complets[dept_code]['AGRI'] = tpe_agri_data[dept_code]['AGRI']
    else:
        # Initialiser avec des valeurs vides si pas de données
        resultats_complets[dept_code]['TPE'] = {
            'inscrits': 0, 'votants': 0, 'sve': 0,
            'voix': {'CGT': 0, 'CFDT': 0, 'CGT-FO': 0, 'CFTC': 0, 
                    'CFE-CGC': 0, 'SOLIDAIRES': 0, 'UNSA': 0, 'AUTRES': 0}
        }
        resultats_complets[dept_code]['AGRI'] = {
            'inscrits': 0, 'votants': 0, 'sve': 0,
            'voix': {'CGT': 0, 'CFDT': 0, 'CGT-FO': 0, 'CFTC': 0, 
                    'CFE-CGC': 0, 'SOLIDAIRES': 0, 'UNSA': 0, 'AUTRES': 0}
        }
    
    # Calculer les données CSE (tout ce qui n'est ni TPE ni AGRI)
    resultats_complets[dept_code]['CSE'] = {
        'inscrits': dept_data.get('total_inscrits', 0) - 
                   resultats_complets[dept_code]['TPE']['inscrits'] - 
                   resultats_complets[dept_code]['AGRI']['inscrits'],
        'votants': dept_data.get('total_votants', 0) - 
                  resultats_complets[dept_code]['TPE']['votants'] - 
                  resultats_complets[dept_code]['AGRI']['votants'],
        'sve': dept_data.get('total_sve', 0) - 
              resultats_complets[dept_code]['TPE']['sve'] - 
              resultats_complets[dept_code]['AGRI']['sve'],
        'voix': {}
    }
    
    # Calculer les voix CSE par syndicat
    for syndicat in ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES']:
        voix_totales = dept_data.get('voix', {}).get(syndicat, 0)
        voix_tpe = resultats_complets[dept_code]['TPE']['voix'].get(syndicat, 0)
        voix_agri = resultats_complets[dept_code]['AGRI']['voix'].get(syndicat, 0)
        
        resultats_complets[dept_code]['CSE']['voix'][syndicat] = max(0, voix_totales - voix_tpe - voix_agri)
    
    # S'assurer que les valeurs ne sont pas négatives
    for key in ['inscrits', 'votants', 'sve']:
        resultats_complets[dept_code]['CSE'][key] = max(0, resultats_complets[dept_code]['CSE'][key])

# Enregistrer le nouveau fichier JSON
print(f"Enregistrement du nouveau fichier JSON: {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(resultats_complets, f, ensure_ascii=False, indent=2)

print("Traitement terminé.")

# Afficher quelques statistiques
total_tpe_inscrits = sum(dept_data['TPE']['inscrits'] for dept_data in resultats_complets.values())
total_agri_inscrits = sum(dept_data['AGRI']['inscrits'] for dept_data in resultats_complets.values())
total_cse_inscrits = sum(dept_data['CSE']['inscrits'] for dept_data in resultats_complets.values())

print(f"\nStatistiques globales:")
print(f"Total inscrits TPE: {total_tpe_inscrits}")
print(f"Total inscrits AGRI: {total_agri_inscrits}")
print(f"Total inscrits CSE: {total_cse_inscrits}")
print(f"Total inscrits tous types: {total_tpe_inscrits + total_agri_inscrits + total_cse_inscrits}")

# Afficher les départements avec le plus de TPE et AGRI
print("\nTop 5 départements avec le plus d'inscrits TPE:")
top_tpe = sorted([(dept, data['TPE']['inscrits']) for dept, data in resultats_complets.items()], 
                key=lambda x: x[1], reverse=True)[:5]
for dept, inscrits in top_tpe:
    print(f"Département {dept}: {inscrits} inscrits TPE")

print("\nTop 5 départements avec le plus d'inscrits AGRI:")
top_agri = sorted([(dept, data['AGRI']['inscrits']) for dept, data in resultats_complets.items()], 
                 key=lambda x: x[1], reverse=True)[:5]
for dept, inscrits in top_agri:
    print(f"Département {dept}: {inscrits} inscrits AGRI")
