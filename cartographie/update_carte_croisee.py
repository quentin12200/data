import re
import os
import shutil

def update_carte_croisee():
    """
    Met à jour le fichier carte_croisee.html pour utiliser les nouveaux fichiers JSON
    et afficher toutes les colonnes des PV.
    """
    # Chemins des fichiers
    fichier_source = os.path.join(os.getcwd(), "carte_croisee.html")
    fichier_backup = os.path.join(os.getcwd(), "carte_croisee_backup3.html")
    fichier_destination = os.path.join(os.getcwd(), "carte_croisee_updated.html")
    
    # Créer une copie de sauvegarde
    shutil.copy2(fichier_source, fichier_backup)
    print(f"Copie de sauvegarde créée : {fichier_backup}")
    
    # Lire le contenu du fichier source
    with open(fichier_source, 'r', encoding='utf-8') as f:
        contenu = f.read()
    
    # 1. Mettre à jour la fonction loadScrutinsData pour utiliser les nouveaux fichiers JSON
    nouveau_loadScrutinsData = """
        function loadScrutinsData() {
            console.log("Chargement des données des scrutins...");
            
            // Définir les confédérations syndicales principales
            const syndicats = ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES'];
            
            // Charger les données des départements et les détails des PV
            Promise.all([
                fetch('../json_data/resultats_departements.json'),
                fetch('../json_data/statistiques_nationales.json')
            ])
                .then(responses => {
                    // Vérifier si toutes les réponses sont OK
                    for (const response of responses) {
                        if (!response.ok) {
                            throw new Error(`Erreur HTTP ${response.status} - ${response.statusText}`);
                        }
                    }
                    return Promise.all(responses.map(response => response.json()));
                })
                .then(([resultatsDeptsData, statsNationalesData]) => {
                    // Stocker les résultats par département dans une variable globale
                    window.departementsData = resultatsDeptsData;
                    console.log("Résultats par département chargés:", Object.keys(window.departementsData).length, "départements");
                    
                    // Stocker les statistiques nationales
                    window.statsNationales = statsNationalesData;
                    console.log("Statistiques nationales chargées");
                    
                    // Initialiser la carte avec les données chargées
                    initMap();
                    
                    // Mettre à jour les statistiques
                    updateStatistics();
                    
                    // Mettre à jour le top 5 des départements
                    updateTopDepartements();
                })
                .catch(error => {
                    console.error("Erreur lors du chargement des données:", error);
                    document.getElementById('map-container').innerHTML = `
                        <div class="alert alert-danger">
                            <h4 class="alert-heading">Erreur de chargement</h4>
                            <p>Impossible de charger les données: ${error.message}</p>
                        </div>
                    `;
                });
        }
    """
    
    # Remplacer la fonction loadScrutinsData
    pattern_loadScrutinsData = r'function loadScrutinsData\(\) \{.*?\}'
    contenu = re.sub(pattern_loadScrutinsData, nouveau_loadScrutinsData, contenu, flags=re.DOTALL)
    
    # 2. Mettre à jour la fonction generateEntreprises pour afficher toutes les colonnes des PV
    nouveau_generateEntreprises = """
        function generateEntreprises(codeDept, syndicat, federation) {
            // Vérifier si les données du département sont disponibles
            if (!codeDept || !window.departementsData || !window.departementsData[codeDept]) {
                return `<div class="alert alert-warning">Aucune donnée disponible pour le département ${codeDept}</div>`;
            }
            
            // Charger les PV du département
            fetch(`../json_data/departement_${codeDept}.json`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erreur HTTP ${response.status} - ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(pvDepartement => {
                    console.log(`${pvDepartement.length} PV trouvés pour le département ${codeDept}`);
                    
                    // Filtrer les PV selon le syndicat et la fédération (IDCC) si spécifiés
                    let pvFiltres = pvDepartement;
                    
                    if (syndicat && syndicat !== 'tous') {
                        // Filtrer par syndicat (celui qui a le plus de voix dans le PV)
                        pvFiltres = pvFiltres.filter(pv => {
                            const voix = pv.voix;
                            const syndicatMax = Object.entries(voix)
                                .sort((a, b) => b[1] - a[1])[0][0];
                            return syndicatMax === syndicat;
                        });
                    }
                    
                    if (federation && federation !== 'tous') {
                        // Filtrer par IDCC (fédération)
                        pvFiltres = pvFiltres.filter(pv => pv.idcc === federation);
                    }
                    
                    // Si aucun PV ne correspond aux critères
                    if (pvFiltres.length === 0) {
                        document.getElementById('details-section').innerHTML = `
                            <div class="alert alert-warning">
                                Aucun PV ne correspond aux critères sélectionnés pour le département ${codeDept}
                            </div>
                        `;
                        return;
                    }
                    
                    // Générer le tableau HTML des PV
                    let html = `
                        <div class="card mb-4">
                            <div class="card-header bg-primary text-white">
                                <h5 class="mb-0">Liste des PV du département ${codeDept} (${pvFiltres.length} PV)</h5>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover mb-0">
                                        <thead>
                                            <tr>
                                                <th>Raison sociale</th>
                                                <th>SIRET</th>
                                                <th>Ville</th>
                                                <th>CP</th>
                                                <th>IDCC</th>
                                                <th>Libellé IDCC</th>
                                                <th>Date</th>
                                                <th>Collège</th>
                                                <th>Inscrits</th>
                                                <th>Votants</th>
                                                <th>SVE</th>
                                                <th>CGT</th>
                                                <th>CFDT</th>
                                                <th>CGT-FO</th>
                                                <th>CFTC</th>
                                                <th>CFE-CGC</th>
                                                <th>SOLIDAIRES</th>
                                                <th>UNSA</th>
                                                <th>AUTRES</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                    `;
                    
                    // Trier les PV par raison sociale
                    pvFiltres.sort((a, b) => a.raison_sociale.localeCompare(b.raison_sociale));
                    
                    // Limiter à 100 PV maximum pour des raisons de performance
                    const pvAffichables = pvFiltres.slice(0, 100);
                    
                    // Générer les lignes du tableau
                    pvAffichables.forEach(pv => {
                        html += `
                            <tr>
                                <td>${pv.raison_sociale}</td>
                                <td>${pv.siret}</td>
                                <td>${pv.ville}</td>
                                <td>${pv.cp}</td>
                                <td>${pv.idcc}</td>
                                <td>${pv.lib_idcc}</td>
                                <td>${pv.date}</td>
                                <td>${pv.college}</td>
                                <td>${pv.inscrits}</td>
                                <td>${pv.votants}</td>
                                <td>${pv.sve_total}</td>
                                <td>${pv.voix.CGT}</td>
                                <td>${pv.voix.CFDT}</td>
                                <td>${pv.voix['CGT-FO']}</td>
                                <td>${pv.voix.CFTC}</td>
                                <td>${pv.voix['CFE-CGC']}</td>
                                <td>${pv.voix.SOLIDAIRES}</td>
                                <td>${pv.voix.UNSA}</td>
                                <td>${pv.voix.AUTRES}</td>
                            </tr>
                        `;
                    });
                    
                    // Ajouter un message si tous les PV ne sont pas affichés
                    if (pvFiltres.length > 100) {
                        html += `
                            <tr>
                                <td colspan="19" class="text-center font-italic">
                                    ${pvFiltres.length - 100} autres PV non affichés
                                </td>
                            </tr>
                        `;
                    }
                    
                    html += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Mettre à jour la section des détails
                    document.getElementById('details-section').innerHTML = html;
                })
                .catch(error => {
                    console.error("Erreur lors du chargement des PV:", error);
                    document.getElementById('details-section').innerHTML = `
                        <div class="alert alert-danger">
                            <h4 class="alert-heading">Erreur de chargement</h4>
                            <p>Impossible de charger les PV: ${error.message}</p>
                        </div>
                    `;
                });
                
                // Afficher un message de chargement en attendant
                return `<div class="alert alert-info">Chargement des PV du département ${codeDept}...</div>`;
        }
    """
    
    # Remplacer la fonction generateEntreprises
    pattern_generateEntreprises = r'function generateEntreprises\(.*?\) \{.*?\}'
    contenu = re.sub(pattern_generateEntreprises, nouveau_generateEntreprises, contenu, flags=re.DOTALL)
    
    # 3. Mettre à jour la fonction initMap pour utiliser les nouvelles données
    pattern_initMap_click = r'\.on\("click", function\(event\) \{.*?details-section.*?\}\);'
    nouveau_initMap_click = """.on("click", function(event) {
                const codeDept = event.target.__data__.properties.code;
                const nomDept = event.target.__data__.properties.nom;
                
                console.log(`Département cliqué: ${nomDept} (${codeDept})`);
                
                // Mettre à jour le titre de la section des détails
                document.getElementById('details-title').textContent = `Détails du département ${nomDept} (${codeDept})`;
                
                // Afficher les PV du département
                document.getElementById('details-section').innerHTML = generateEntreprises(codeDept, document.getElementById('filtre-syndicat').value, document.getElementById('filtre-federation').value);
                
                // Faire défiler jusqu'à la section des détails
                document.getElementById('details-container').scrollIntoView({ behavior: 'smooth' });
            });"""
    
    contenu = re.sub(pattern_initMap_click, nouveau_initMap_click, contenu, flags=re.DOTALL)
    
    # Écrire le contenu mis à jour dans le fichier de destination
    with open(fichier_destination, 'w', encoding='utf-8') as f:
        f.write(contenu)
    
    print(f"Fichier mis à jour créé : {fichier_destination}")
    return fichier_destination

if __name__ == "__main__":
    # Se placer dans le répertoire de la cartographie
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    update_carte_croisee()
