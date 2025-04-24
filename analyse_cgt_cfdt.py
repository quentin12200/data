"""
Script principal pour l'analyse de l'écart entre la CGT et la CFDT.
Ce script orchestre l'exécution séquentielle des trois modules d'analyse :
- analyse_cgt_cfdt_part1.py : Analyse globale et par région
- analyse_cgt_cfdt_part2.py : Analyse par département et par collège
- analyse_cgt_cfdt_part3.py : Génération de la page HTML finale

Exécuter ce script lancera l'ensemble du processus d'analyse.
"""

import os
import subprocess
import time
from datetime import datetime
import sys

def print_header(message):
    print(f"\n{'=' * 80}")
    print(f"{message.center(80)}")
    print(f"{'=' * 80}\n")

def print_step(step_num, message):
    print(f"[Étape {step_num}] {message}")

def run_module(module_name, step_num, description):
    """Exécute un module Python et surveille son exécution"""
    print_step(step_num, description)
    
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, module_name], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        if result.returncode == 0:
            execution_time = time.time() - start_time
            print(f"✓ Module {module_name} exécuté avec succès en {execution_time:.2f} secondes")
            print(result.stdout)
            return True
        else:
            print(f"✗ Erreur lors de l'exécution du module {module_name}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Exception lors de l'exécution du module {module_name}: {str(e)}")
        return False

def main():
    # Afficher un en-tête
    print_header("ANALYSE DE L'ÉCART ENTRE LA CGT ET LA CFDT")
    print(f"Démarrage de l'analyse complète le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
    print(f"Répertoire de travail : {os.getcwd()}")
    
    # Exécuter les modules d'analyse dans l'ordre
    modules = [
        ("analyse_cgt_cfdt_part1.py", "Analyse globale et par région"),
        ("analyse_cgt_cfdt_part2.py", "Analyse par département et par collège"),
        ("analyse_cgt_cfdt_part3.py", "Génération de la page HTML finale")
    ]
    
    success = True
    for i, (module, description) in enumerate(modules, 1):
        if not run_module(module, i, description):
            success = False
            print(f"Erreur lors de l'exécution du module {module}. L'analyse continue...")
    
    # Afficher un résumé
    if success:
        print_header("ANALYSE TERMINÉE AVEC SUCCÈS")
        print("Les résultats sont disponibles dans le dossier 'analyse_cgt_cfdt'")
        print("Vous pouvez consulter l'analyse en ouvrant le fichier 'analyse_cgt_cfdt/index.html'")
    else:
        print_header("ANALYSE TERMINÉE AVEC DES ERREURS")
        print("Certains modules ont rencontré des erreurs. Vérifiez les messages ci-dessus.")
    
    print(f"Fin de l'analyse le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")

if __name__ == "__main__":
    main()