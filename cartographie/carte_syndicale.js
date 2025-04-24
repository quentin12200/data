// Charger les données nationales
function loadNationalStats() {
    fetch('../json_data_ordonnees/resultats_departements_avec_tpe.json')
        .then(response => response.json())
        .then(data => {
            // Statistiques nationales (valeurs fixes)
            const voix_nationales = {
                'CGT': 1086341.70,
                'CFDT': 1300107.25,
                'CGT-FO': 729054.71,
                'CFTC': 0,
                'CFE-CGC': 0,
                'SOLIDAIRES': 0,
                'UNSA': 0,
                'AUTRES': 0
            };
            const total_sve = 4890549.56;

            console.log('Statistiques nationales:', {
                total_sve,
                voix: voix_nationales
            });

            // Afficher les statistiques nationales
            document.getElementById('national-stats').innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-danger">${voix_nationales.CGT.toLocaleString('fr-FR', {maximumFractionDigits: 2})}</div>
                            <div class="stat-label">Voix CGT</div>
                            <div class="small text-muted">22.21%</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-info">${Math.round(voix_nationales.CFDT).toLocaleString()}</div>
                            <div class="stat-label">CFDT</div>
                            <div class="small text-muted">${((voix_nationales.CFDT / total_sve) * 100).toFixed(2)}%</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-warning">${Math.round(voix_nationales['CGT-FO']).toLocaleString()}</div>
                            <div class="stat-label">CGT-FO</div>
                            <div class="small text-muted">${((voix_nationales['CGT-FO'] / total_sve) * 100).toFixed(2)}%</div>
                        </div>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">8 849 298</div>
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

            // Afficher les détails du département
            map.on('click', function(e) {
                const feature = e.features[0];
                if (!feature) return;

                const codeDept = feature.properties.code;
                const dept = data[codeDept];
                
                if (!dept || !dept.voix || !dept.inscrits) {
                    console.error('Données manquantes pour le département', codeDept);
                    return;
                }

                const totalInscritsCSE = Number(dept.inscrits.CSE) || 0; // Inclut déjà les TPE
                const totalInscritsAGRI = Number(dept.inscrits.AGRI) || 0;
                
                const totalVoixCSE = Object.values(dept.voix.CSE).reduce((a, b) => a + (Number(b) || 0), 0);
                const totalVoixTPE = Object.values(dept.voix.TPE).reduce((a, b) => a + (Number(b) || 0), 0);
                const totalVoixAGRI = Object.values(dept.voix.AGRI).reduce((a, b) => a + (Number(b) || 0), 0);

                const deptDetails = document.getElementById('dept-details');
                deptDetails.classList.remove('d-none');
                deptDetails.querySelector('.card-body').innerHTML = `
                    <h5 class="mb-4">${codeDept} - ${dept.nom || 'Département ' + codeDept}</h5>
                    
                    <div class="mb-4">
                        <h6 class="text-primary">CSE</h6>
                        <p>Inscrits : ${Math.round(totalInscritsCSE).toLocaleString()}</p>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Syndicat</th>
                                        <th>Voix</th>
                                        <th>%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(dept.voix.CSE)
                                        .map(([syndicat, voix]) => `
                                            <tr>
                                                <td>${syndicat}</td>
                                                <td>${Math.round(Number(voix)).toLocaleString()}</td>
                                                <td>${totalVoixCSE > 0 ? ((Number(voix) / totalVoixCSE) * 100).toFixed(2) : '0.00'}%</td>
                                            </tr>
                                        `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="mb-4">
                        <h6 class="text-success">TPE</h6>
                        <p>Inscrits : ${Math.round(Number(dept.inscrits?.TPE || 0)).toLocaleString()}</p>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Syndicat</th>
                                        <th>Voix</th>
                                        <th>%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(dept.voix.TPE)
                                        .map(([syndicat, voix]) => `
                                            <tr>
                                                <td>${syndicat}</td>
                                                <td>${Math.round(Number(voix)).toLocaleString()}</td>
                                                <td>${totalVoixTPE > 0 ? ((Number(voix) / totalVoixTPE) * 100).toFixed(2) : '0.00'}%</td>
                                            </tr>
                                        `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="mb-4">
                        <h6 class="text-warning">AGRI</h6>
                        <p>Inscrits : ${Math.round(totalInscritsAGRI).toLocaleString()}</p>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Syndicat</th>
                                        <th>Voix</th>
                                        <th>%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(dept.voix.AGRI)
                                        .map(([syndicat, voix]) => `
                                            <tr>
                                                <td>${syndicat}</td>
                                                <td>${Math.round(Number(voix)).toLocaleString()}</td>
                                                <td>${totalVoixAGRI > 0 ? ((Number(voix) / totalVoixAGRI) * 100).toFixed(2) : '0.00'}%</td>
                                            </tr>
                                        `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div>
                        <h6 class="text-secondary">Total</h6>
                        <p>Total Inscrits : ${Math.round(totalInscritsCSE + totalInscritsAGRI).toLocaleString()}</p>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des données nationales:', error);
        });
}

// Charger les statistiques au chargement de la page
document.addEventListener('DOMContentLoaded', loadNationalStats);
