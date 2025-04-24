// Charger les données nationales
function loadNationalStats() {
    fetch('../json_data_ordonnees/resultats_departements_avec_tpe.json')
        .then(response => response.json())
        .then(data => {
            // Calculer les statistiques nationales
            let total_scrutins = 0;
            let total_inscrits = 0;
            let total_votants = 0;
            let total_sve = 0;
            let voix_nationales = {
                'CGT': 0,
                'CFDT': 0,
                'CGT-FO': 0,
                'CFTC': 0,
                'CFE-CGC': 0,
                'SOLIDAIRES': 0,
                'UNSA': 0,
                'AUTRES': 0
            };

            Object.values(data).forEach(dept => {
                if (!dept || !dept.voix) return;

                // Ajouter les voix CSE
                Object.entries(dept.voix.CSE || {}).forEach(([syndicat, voix]) => {
                    voix_nationales[syndicat] = (voix_nationales[syndicat] || 0) + (Number(voix) || 0);
                });

                // Ajouter les voix AGRI
                Object.entries(dept.voix.AGRI || {}).forEach(([syndicat, voix]) => {
                    voix_nationales[syndicat] = (voix_nationales[syndicat] || 0) + (Number(voix) || 0);
                });

                // Ajouter les voix TPE
                Object.entries(dept.voix.TPE || {}).forEach(([syndicat, voix]) => {
                    voix_nationales[syndicat] = (voix_nationales[syndicat] || 0) + (Number(voix) || 0);
                });

                // Ajouter les totaux du département
                total_scrutins += Number(dept.total_scrutins) || 0;
                total_inscrits += (Number(dept.inscrits?.CSE) || 0) + (Number(dept.inscrits?.TPE) || 0) + (Number(dept.inscrits?.AGRI) || 0);
                total_votants += Number(dept.total_votants) || 0;
                total_sve += Number(dept.total_sve) || 0;
            });

            console.log('Statistiques nationales calculées:', {
                total_scrutins,
                total_inscrits,
                total_votants,
                total_sve,
                voix: voix_nationales
            });

            // Afficher les statistiques nationales
            document.getElementById('national-stats').innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-danger">${Math.round(voix_nationales.CGT).toLocaleString()}</div>
                            <div class="stat-label">Voix CGT</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-info">${Math.round(voix_nationales.CFDT).toLocaleString()}</div>
                            <div class="stat-label">CFDT</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-warning">${Math.round(voix_nationales['CGT-FO']).toLocaleString()}</div>
                            <div class="stat-label">CGT-FO</div>
                        </div>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">${Math.round(total_inscrits).toLocaleString()}</div>
                            <div class="stat-label">Inscrits</div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">${Math.round(total_sve).toLocaleString()}</div>
                            <div class="stat-label">SVE</div>
                        </div>
                    </div>
                </div>
            `;

            // Remplir le tableau des départements
            const tbody = document.querySelector('#dept-table tbody');
            if (tbody) {
                tbody.innerHTML = '';
                Object.entries(data)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .forEach(([codeDept, dept]) => {
                        if (!dept || !dept.voix || !dept.inscrits) return;

                        const totalInscritsCSE = Number(dept.inscrits.CSE) || 0;
                        const totalInscritsTPE = Number(dept.inscrits.TPE) || 0;
                        const totalInscritsAGRI = Number(dept.inscrits.AGRI) || 0;

                        ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES'].forEach(syndicat => {
                            const voixCSE = Number(dept.voix.CSE[syndicat]) || 0;
                            const voixTPE = Number(dept.voix.TPE[syndicat]) || 0;
                            const voixAGRI = Number(dept.voix.AGRI[syndicat]) || 0;
                            
                            const totalVoixCSE = Object.values(dept.voix.CSE).reduce((a, b) => a + (Number(b) || 0), 0);
                            const totalVoixTPE = Object.values(dept.voix.TPE).reduce((a, b) => a + (Number(b) || 0), 0);
                            const totalVoixAGRI = Object.values(dept.voix.AGRI).reduce((a, b) => a + (Number(b) || 0), 0);
                            
                            const totalVoixSyndicat = voixCSE + voixTPE + voixAGRI;
                            const totalVoixGlobal = totalVoixCSE + totalVoixTPE + totalVoixAGRI;

                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${codeDept}</td>
                                <td>${syndicat}</td>
                                <td>${Math.round(totalInscritsCSE).toLocaleString()}</td>
                                <td>${Math.round(voixCSE).toLocaleString()}</td>
                                <td>${totalVoixCSE > 0 ? ((voixCSE / totalVoixCSE) * 100).toFixed(2) : '0.00'}%</td>
                                <td>${Math.round(totalInscritsTPE).toLocaleString()}</td>
                                <td>${Math.round(voixTPE).toLocaleString()}</td>
                                <td>${totalVoixTPE > 0 ? ((voixTPE / totalVoixTPE) * 100).toFixed(2) : '0.00'}%</td>
                                <td>${Math.round(totalInscritsAGRI).toLocaleString()}</td>
                                <td>${Math.round(voixAGRI).toLocaleString()}</td>
                                <td>${totalVoixAGRI > 0 ? ((voixAGRI / totalVoixAGRI) * 100).toFixed(2) : '0.00'}%</td>
                                <td>${Math.round(totalVoixSyndicat).toLocaleString()}</td>
                                <td>${totalVoixGlobal > 0 ? ((totalVoixSyndicat / totalVoixGlobal) * 100).toFixed(2) : '0.00'}%</td>
                            `;
                            tbody.appendChild(row);
                        });
                    });
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des données nationales:', error);
        });
}

// Charger les statistiques au chargement de la page
document.addEventListener('DOMContentLoaded', loadNationalStats);
