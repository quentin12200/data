// Charger les données nationales
function loadNationalStats() {
    fetch('../json_data_ordonnees/resultats_departements_avec_tpe.json')
        .then(response => response.json())
        .then(data => {
            // Calculer les statistiques nationales
            let totalInscrits = 0;
            let totalVotants = 0;
            let totalSVE = 0;
            let totalVoixCGT = 0;
            let totalVoixCFDT = 0;
            let totalVoixFO = 0;

            // Parcourir tous les départements
            Object.values(data).forEach(dept => {
                // Pour les totaux nationaux, on prend directement les valeurs car elles incluent déjà les TPE
                totalInscrits += dept.total_inscrits;
                totalVotants += dept.total_votants;
                totalSVE += dept.total_sve;
                
                // Pour les voix par syndicat, on prend aussi directement les valeurs
                totalVoixCGT += dept.voix.CGT || 0;
                totalVoixCFDT += dept.voix.CFDT || 0;
                totalVoixFO += dept.voix['CGT-FO'] || 0;
            });

            // Mettre à jour l'affichage des statistiques nationales
            document.getElementById('stats-nationales').innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Inscrits</h5>
                                <div class="display-6">${totalInscrits.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Votants</h5>
                                <div class="display-6">${totalVotants.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>SVE</h5>
                                <div class="display-6">${totalSVE.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Participation</h5>
                                <div class="display-6">${(totalVotants/totalInscrits*100).toFixed(2)}%</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>CGT</h5>
                                <div class="display-6">${totalVoixCGT.toLocaleString()}</div>
                                <div class="small text-muted">${(totalVoixCGT/totalSVE*100).toFixed(2)}%</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>CFDT</h5>
                                <div class="display-6">${totalVoixCFDT.toLocaleString()}</div>
                                <div class="small text-muted">${(totalVoixCFDT/totalSVE*100).toFixed(2)}%</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>CGT-FO</h5>
                                <div class="display-6">${totalVoixFO.toLocaleString()}</div>
                                <div class="small text-muted">${(totalVoixFO/totalSVE*100).toFixed(2)}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Erreur lors du chargement des données nationales:', error);
        });
}

// Charger les statistiques au chargement de la page
document.addEventListener('DOMContentLoaded', loadNationalStats);
