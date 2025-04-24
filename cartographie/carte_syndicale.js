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
            let totalVoixTPE = 0;

            // Parcourir tous les départements
            Object.values(data).forEach(dept => {
                // Calculer le total des voix TPE pour ce département
                const voixTPEDept = {
                    'CGT': dept.voix_tpe ? dept.voix_tpe['CGT'] || 0 : 0,
                    'CFDT': dept.voix_tpe ? dept.voix_tpe['CFDT'] || 0 : 0,
                    'CGT-FO': dept.voix_tpe ? dept.voix_tpe['CGT-FO'] || 0 : 0,
                    'CFTC': dept.voix_tpe ? dept.voix_tpe['CFTC'] || 0 : 0,
                    'CFE-CGC': dept.voix_tpe ? dept.voix_tpe['CFE-CGC'] || 0 : 0,
                    'SOLIDAIRES': dept.voix_tpe ? dept.voix_tpe['SOLIDAIRES'] || 0 : 0,
                    'UNSA': dept.voix_tpe ? dept.voix_tpe['UNSA'] || 0 : 0,
                    'AUTRES': dept.voix_tpe ? (dept.voix_tpe['CAT'] || 0) + (dept.voix_tpe['CNT-SO'] || 0) + (dept.voix_tpe['le_SGJ'] || 0) : 0
                };
                const totalTPEDept = Object.values(voixTPEDept).reduce((a, b) => a + b, 0);

                // Ajouter au total national
                totalInscrits += dept.total_inscrits + totalTPEDept;
                totalVotants += dept.total_votants + totalTPEDept;
                totalSVE += dept.total_sve + totalTPEDept;
                
                // Ajouter les voix par syndicat
                totalVoixCGT += (dept.voix.CGT || 0) + voixTPEDept.CGT;
                totalVoixCFDT += (dept.voix.CFDT || 0) + voixTPEDept.CFDT;
                totalVoixFO += (dept.voix['CGT-FO'] || 0) + voixTPEDept['CGT-FO'];
                totalVoixTPE += totalTPEDept;
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
                                <div class="small text-muted">dont TPE: ${totalVoixTPE.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>SVE</h5>
                                <div class="display-6">${totalSVE.toLocaleString()}</div>
                                <div class="small text-muted">dont TPE: ${totalVoixTPE.toLocaleString()}</div>
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
                                <div class="small text-muted">dont TPE: ${(data[75].voix_tpe?.CGT || 0).toLocaleString()}</div>
                                <div class="small text-muted">${(totalVoixCGT/totalSVE*100).toFixed(2)}%</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>CFDT</h5>
                                <div class="display-6">${totalVoixCFDT.toLocaleString()}</div>
                                <div class="small text-muted">dont TPE: ${(data[75].voix_tpe?.CFDT || 0).toLocaleString()}</div>
                                <div class="small text-muted">${(totalVoixCFDT/totalSVE*100).toFixed(2)}%</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>CGT-FO</h5>
                                <div class="display-6">${totalVoixFO.toLocaleString()}</div>
                                <div class="small text-muted">dont TPE: ${(data[75].voix_tpe?.['CGT-FO'] || 0).toLocaleString()}</div>
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
