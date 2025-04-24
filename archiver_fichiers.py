import os
import shutil
import datetime

# Créer un dossier d'archive avec la date du jour
date_str = datetime.datetime.now().strftime("%Y%m%d")
archive_dir = f"archive_{date_str}"

if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)
    print(f"Dossier d'archive créé: {archive_dir}")

# Liste des éléments à conserver (ne pas archiver)
elements_a_conserver = [
    "lots_par_idcc",                                # Nouveau dossier avec les lots par IDCC
    "cartographie",                                 # Dossier cartographie (à traiter séparément)
    "referentiel_idcc_lot.xlsx",                    # Référentiel IDCC-LOT
    "decoupage_par_lot_organise.py",                # Script de découpage par lot (version finale)
    "archiver_fichiers.py",                         # Ce script d'archivage
    "json_data"                                     # Dossier avec les données JSON
]

# Liste des éléments à archiver dans le dossier cartographie
elements_cartographie_a_archiver = [
    "INTERPRO_restructures_avec_college.xlsx",      # Ancien fichier Excel
    "INTERPRO_restructures_complet.xlsx",           # Ancien fichier Excel
    "INTERPRO_restructures_completfinalversion.xlsx", # Fichier Excel utilisé pour le découpage
    "restructurer_excel_complet.py",                # Ancien script de restructuration
    "restructurer_excel_complet_v2.py",             # Ancien script de restructuration
    "lot_0",                                        # Anciens dossiers de lots
    "lot_1",
    "lot_2",
    "lot_3",
    "lot_4",
    "lot_5",
    "sans_lot",
    "decoupage_par_lot.py",                         # Ancien script de découpage
    "decoupage_par_lot_strict.py"                   # Ancien script de découpage
]

# Éléments à conserver dans le dossier cartographie
elements_cartographie_a_conserver = [
    "carte_syndicale.html",                         # Interface HTML principale
    "excel2json_departements.py",                   # Script de conversion Excel vers JSON
    "js",                                           # Dossier avec les scripts JavaScript
    "css"                                           # Dossier avec les styles CSS
]

# Fonction pour archiver un élément
def archiver_element(element, source_dir=".", destination_dir=archive_dir):
    source_path = os.path.join(source_dir, element)
    dest_path = os.path.join(destination_dir, element)
    
    if os.path.exists(source_path):
        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
                shutil.rmtree(source_path)
                print(f"Dossier archivé: {source_path} -> {dest_path}")
            else:
                shutil.copy2(source_path, dest_path)
                os.remove(source_path)
                print(f"Fichier archivé: {source_path} -> {dest_path}")
            return True
        except Exception as e:
            print(f"Erreur lors de l'archivage de {source_path}: {e}")
            return False
    else:
        print(f"Élément non trouvé: {source_path}")
        return False

# 1. Archiver les éléments du dossier principal
print("\nArchivage des éléments du dossier principal...")
elements_archives = []

for element in os.listdir("."):
    if element not in elements_a_conserver and element != archive_dir:
        if archiver_element(element):
            elements_archives.append(element)

# 2. Créer un sous-dossier pour les éléments de cartographie à archiver
cartographie_archive_dir = os.path.join(archive_dir, "cartographie_archive")
if not os.path.exists(cartographie_archive_dir):
    os.makedirs(cartographie_archive_dir)
    print(f"\nDossier d'archive pour cartographie créé: {cartographie_archive_dir}")

# 3. Archiver les éléments du dossier cartographie
print("\nArchivage des éléments du dossier cartographie...")
elements_cartographie_archives = []

for element in os.listdir("cartographie"):
    if element in elements_cartographie_a_archiver:
        if archiver_element(element, "cartographie", cartographie_archive_dir):
            elements_cartographie_archives.append(element)

# Résumé de l'archivage
print("\nRésumé de l'archivage:")
print(f"Nombre d'éléments archivés du dossier principal: {len(elements_archives)}")
print(f"Éléments archivés: {', '.join(elements_archives)}")
print(f"\nNombre d'éléments archivés du dossier cartographie: {len(elements_cartographie_archives)}")
print(f"Éléments archivés: {', '.join(elements_cartographie_archives)}")

print("\nArchivage terminé avec succès!")
