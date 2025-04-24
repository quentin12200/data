import pandas as pd
import os
import numpy as np
import shutil

# Chemins des fichiers
fichier_pv = 'cartographie/INTERPRO_restructures_completfinalversion.xlsx'
fichier_referentiel = 'referentiel_idcc_lot.xlsx'
dossier_principal = 'lots_par_idcc'

# S'assurer que le dossier principal existe
if not os.path.exists(dossier_principal):
    os.makedirs(dossier_principal)
    print(f"Dossier principal {dossier_principal} créé")

# Créer les dossiers pour chaque lot dans le dossier principal
for lot in range(6):  # Lots de 0 à 5
    dossier_lot = os.path.join(dossier_principal, f'lot_{lot}')
    if not os.path.exists(dossier_lot):
        os.makedirs(dossier_lot)
        print(f"Dossier {dossier_lot} créé")

# Charger le référentiel IDCC-LOT
print("Chargement du référentiel IDCC-LOT...")
try:
    referentiel = pd.read_excel(fichier_referentiel)
    # Vérifier les colonnes du référentiel
    print(f"Colonnes du référentiel: {referentiel.columns.tolist()}")
    
    # Créer un dictionnaire des IDCC par lot
    idcc_par_lot = {}
    for lot in range(6):
        idcc_par_lot[lot] = referentiel[referentiel['Lot M2025'] == lot]['IDCC'].tolist()
        # Convertir les IDCC en chaînes avec padding de zéros
        idcc_par_lot[lot] = [str(idcc).zfill(4) for idcc in idcc_par_lot[lot]]
        print(f"Lot {lot}: {len(idcc_par_lot[lot])} IDCC - {idcc_par_lot[lot]}")
    
except Exception as e:
    print(f"Erreur lors du chargement du référentiel: {e}")
    exit(1)

# Charger le fichier des PV
print("\nChargement du fichier des PV...")
try:
    pv_data = pd.read_excel(fichier_pv)
    print(f"Nombre de PV chargés: {len(pv_data)}")
    
    # Vérifier si la colonne IDCC existe
    if 'idcc' not in pv_data.columns and 'IDCC' in pv_data.columns:
        pv_data = pv_data.rename(columns={'IDCC': 'idcc'})
    
    # Convertir les IDCC en chaînes de caractères avec padding de zéros
    pv_data['idcc'] = pv_data['idcc'].astype(str).str.zfill(4)
    
except Exception as e:
    print(f"Erreur lors du chargement du fichier PV: {e}")
    exit(1)

# Créer un dossier pour les PV sans lot attribué
dossier_sans_lot = os.path.join(dossier_principal, 'sans_lot')
if not os.path.exists(dossier_sans_lot):
    os.makedirs(dossier_sans_lot)
    print(f"Dossier {dossier_sans_lot} créé")

# Traiter chaque lot
print("\nTraitement des lots...")
try:
    # Compteurs pour les statistiques
    total_pv_traites = 0
    total_pv_sans_lot = 0
    
    # Créer un fichier pour les PV sans lot attribué
    pv_sans_lot = pv_data[~pv_data['idcc'].isin([idcc for lot_idccs in idcc_par_lot.values() for idcc in lot_idccs])]
    total_pv_sans_lot = len(pv_sans_lot)
    if total_pv_sans_lot > 0:
        fichier_sans_lot = os.path.join(dossier_sans_lot, 'pv_sans_lot.xlsx')
        pv_sans_lot.to_excel(fichier_sans_lot, index=False)
        print(f"PV sans lot attribué: {total_pv_sans_lot} PV sauvegardés dans {fichier_sans_lot}")
    
    # Traiter chaque lot
    for lot, idccs in idcc_par_lot.items():
        print(f"\nTraitement du lot {lot}...")
        
        # Filtrer les PV pour ce lot
        pv_lot = pv_data[pv_data['idcc'].isin(idccs)]
        total_pv_lot = len(pv_lot)
        total_pv_traites += total_pv_lot
        
        if total_pv_lot > 0:
            # Chemin du dossier pour ce lot
            dossier_lot = os.path.join(dossier_principal, f'lot_{lot}')
            
            # Créer un fichier global pour le lot
            fichier_global = os.path.join(dossier_lot, f'pv_lot_{lot}_global.xlsx')
            pv_lot.to_excel(fichier_global, index=False)
            print(f"  - Fichier global créé: {fichier_global} avec {total_pv_lot} PV")
            
            # Créer un fichier par IDCC dans ce lot
            for idcc in idccs:
                pv_idcc = pv_lot[pv_lot['idcc'] == idcc]
                nb_pv_idcc = len(pv_idcc)
                
                if nb_pv_idcc > 0:
                    # Récupérer le libellé de l'IDCC
                    libelle = ""
                    if 'Lib IDCC' in pv_idcc.columns:
                        libelle_raw = pv_idcc['Lib IDCC'].iloc[0]
                        if pd.notna(libelle_raw):
                            libelle = str(libelle_raw)
                            # Nettoyer le libellé pour le nom de fichier
                            libelle = libelle.replace('/', '_').replace('\\', '_')
                            libelle = libelle.replace(':', '_').replace('*', '_')
                            libelle = libelle.replace('?', '_').replace('"', '_')
                            libelle = libelle.replace('<', '_').replace('>', '_')
                            libelle = libelle.replace('|', '_')
                            if len(libelle) > 50:
                                libelle = libelle[:50]
                    
                    # Créer le nom du fichier
                    nom_fichier = f"idcc_{idcc}"
                    if libelle:
                        nom_fichier += f"_{libelle}"
                    
                    # Chemin complet du fichier
                    fichier_idcc = os.path.join(dossier_lot, f"{nom_fichier}.xlsx")
                    
                    # Sauvegarder le fichier
                    pv_idcc.to_excel(fichier_idcc, index=False)
                    print(f"  - IDCC {idcc}: {nb_pv_idcc} PV sauvegardés dans {fichier_idcc}")
                else:
                    print(f"  - IDCC {idcc}: Aucun PV trouvé")
        else:
            print(f"  - Aucun PV trouvé pour ce lot")
    
    # Afficher le résumé
    print("\nRésumé:")
    print(f"Total PV traités: {total_pv_traites}")
    print(f"Total PV sans lot attribué: {total_pv_sans_lot}")
    print(f"Total PV: {total_pv_traites + total_pv_sans_lot}")
    
except Exception as e:
    print(f"Erreur lors du traitement: {e}")
    exit(1)

print("\nTraitement terminé avec succès!")
