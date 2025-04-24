// Charger les données nationales
function loadNationalStats() {
    Promise.all([
        fetch('../json_data_ordonnees/resultats_departements_avec_tpe.json'),
        fetch('assets/france-departements.json')
    ])
    .then(responses => Promise.all(responses.map(r => r.json())))
    .then(([deptData, geoData]) => {
        // Stocker les données pour utilisation ultérieure
        window.departementData = deptData;

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

        // Afficher les statistiques nationales
        const statsElement = document.getElementById('national-stats');
        if (statsElement) {
            statsElement.innerHTML = `
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
                            <div class="stat-value text-info">${voix_nationales.CFDT.toLocaleString('fr-FR', {maximumFractionDigits: 2})}</div>
                            <div class="stat-label">CFDT</div>
                            <div class="small text-muted">${((voix_nationales.CFDT / total_sve) * 100).toFixed(2)}%</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value text-warning">${voix_nationales['CGT-FO'].toLocaleString('fr-FR', {maximumFractionDigits: 2})}</div>
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
                            <div class="stat-value">${total_sve.toLocaleString('fr-FR', {maximumFractionDigits: 2})}</div>
                            <div class="stat-label">SVE</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Initialiser la carte
        initMap(geoData);
    })
    .catch(error => {
        console.error('Erreur lors du chargement des données:', error);
        document.getElementById('national-stats').innerHTML = `
            <div class="alert alert-danger">
                Erreur lors du chargement des données nationales: ${error.message}
            </div>
        `;
    });
}

// Initialiser la carte
function initMap(geoData) {
    const width = document.getElementById('map-container').clientWidth;
    const height = 600;
    
    // Créer le SVG
    const svg = d3.select('#map-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Créer la projection et le path
    const projection = d3.geoMercator()
        .center([2.5, 46.5])
        .scale(width * 3)
        .translate([width / 2, height / 2]);
    
    const path = d3.geoPath().projection(projection);
    
    // Ajouter les départements
    svg.selectAll('.departement')
        .data(geoData.features)
        .enter()
        .append('path')
        .attr('class', 'departement')
        .attr('d', path)
        .attr('id', d => `dept-${d.properties.code}`)
        .on('click', function(event, d) {
            showDepartmentDetails(d.properties.code);
        })
        .on('mouseover', function(event, d) {
            const dept = window.departementData[d.properties.code];
            if (!dept) return;

            const tooltip = d3.select('#tooltip');
            tooltip.style('display', 'block')
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY + 10) + 'px')
                .html(`
                    <strong>${dept.nom || 'Département'} (${d.properties.code})</strong><br>
                    Inscrits: ${Math.round(dept.total_inscrits || 0).toLocaleString()}<br>
                    SVE: ${Math.round(dept.total_sve || 0).toLocaleString()}
                `);
        })
        .on('mouseout', function() {
            d3.select('#tooltip').style('display', 'none');
        });

    // Colorer les départements
    updateMapColoring();
}

// Mettre à jour la coloration de la carte
function updateMapColoring() {
    d3.selectAll('.departement')
        .style('fill', function(d) {
            const dept = window.departementData[d.properties.code];
            if (!dept || !dept.syndicat_dominant) return '#f5f5f5';
            
            const colorMap = {
                'CGT': '#e41a1c',
                'CFDT': '#377eb8',
                'CGT-FO': '#ff7f00',
                'CFTC': '#984ea3',
                'CFE-CGC': '#4daf4a',
                'SOLIDAIRES': '#ffff33',
                'UNSA': '#a65628',
                'AUTRES': '#999999'
            };
            
            return colorMap[dept.syndicat_dominant] || '#f5f5f5';
        });
}

// Afficher les détails d'un département
function showDepartmentDetails(code) {
    const deptData = window.departementData[code];
    if (!deptData) {
        console.error('Données non disponibles pour le département', code);
        return;
    }
    
    // Afficher les détails du département
    const deptDetails = document.getElementById('departement-details');
    if (!deptDetails) return;

    deptDetails.classList.remove('d-none');
    
    // Calculer les voix totales pour chaque syndicat
    const syndicats = ['CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES'];
    const voixTotales = {};
    
    syndicats.forEach(syndicat => {
        voixTotales[syndicat] = (
            (deptData.voix.CSE[syndicat] || 0) +
            (deptData.voix.TPE[syndicat] || 0) +
            (deptData.voix.AGRI[syndicat] || 0)
        );
    });
    
    // Préparer les données pour l'affichage
    const totalSVE = deptData.total_sve || 
                    (deptData.voix.CSE.total || 0) + 
                    (deptData.voix.TPE.total || 0) + 
                    (deptData.voix.AGRI.total || 0);
    
    deptDetails.innerHTML = `
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Département ${code} - ${deptData.nom || 'Département'}</h5>
            </div>
            <div class="card-body">
                <div class="row text-center mb-4">
                    <div class="col-md-3">
                        <div class="h4 mb-0">${Math.round((deptData.voix.CSE.total || 0)).toLocaleString()}</div>
                        <div class="small text-muted">voix CSE</div>
                    </div>
                    <div class="col-md-3">
                        <div class="h4 mb-0">${Math.round((deptData.voix.TPE.total || 0)).toLocaleString()}</div>
                        <div class="small text-muted">voix TPE</div>
                    </div>
                    <div class="col-md-3">
                        <div class="h4 mb-0">${Math.round((deptData.voix.AGRI.total || 0)).toLocaleString()}</div>
                        <div class="small text-muted">voix AGRI</div>
                    </div>
                    <div class="col-md-3">
                        <div class="h4 mb-0">${Math.round(totalSVE).toLocaleString()}</div>
                        <div class="small text-muted">Total voix</div>
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Organisation</th>
                                <th class="text-end">Voix CSE</th>
                                <th class="text-end">%</th>
                                <th class="text-end">Voix TPE</th>
                                <th class="text-end">%</th>
                                <th class="text-end">Voix AGRI</th>
                                <th class="text-end">%</th>
                                <th class="text-end">Total</th>
                                <th class="text-end">% Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${syndicats.map(syndicat => {
                                const voixCSE = deptData.voix.CSE[syndicat] || 0;
                                const voixTPE = deptData.voix.TPE[syndicat] || 0;
                                const voixAGRI = deptData.voix.AGRI[syndicat] || 0;
                                const totalVoix = voixTotales[syndicat];
                                
                                const pctCSE = deptData.voix.CSE.total > 0 ? (voixCSE / deptData.voix.CSE.total * 100) : 0;
                                const pctTPE = deptData.voix.TPE.total > 0 ? (voixTPE / deptData.voix.TPE.total * 100) : 0;
                                const pctAGRI = deptData.voix.AGRI.total > 0 ? (voixAGRI / deptData.voix.AGRI.total * 100) : 0;
                                const pctTotal = totalSVE > 0 ? (totalVoix / totalSVE * 100) : 0;

                                return `
                                    <tr>
                                        <td>${syndicat}</td>
                                        <td class="text-end">${Math.round(voixCSE).toLocaleString()}</td>
                                        <td class="text-end">${pctCSE.toFixed(2)}%</td>
                                        <td class="text-end">${Math.round(voixTPE).toLocaleString()}</td>
                                        <td class="text-end">${pctTPE.toFixed(2)}%</td>
                                        <td class="text-end">${Math.round(voixAGRI).toLocaleString()}</td>
                                        <td class="text-end">${pctAGRI.toFixed(2)}%</td>
                                        <td class="text-end">${Math.round(totalVoix).toLocaleString()}</td>
                                        <td class="text-end">${pctTotal.toFixed(2)}%</td>
                                    </tr>
                                `;
                            }).join('')}
                            <tr class="table-info fw-bold">
                                <td>Total</td>
                                <td class="text-end">${Math.round(deptData.voix.CSE.total || 0).toLocaleString()}</td>
                                <td class="text-end">100%</td>
                                <td class="text-end">${Math.round(deptData.voix.TPE.total || 0).toLocaleString()}</td>
                                <td class="text-end">100%</td>
                                <td class="text-end">${Math.round(deptData.voix.AGRI.total || 0).toLocaleString()}</td>
                                <td class="text-end">100%</td>
                                <td class="text-end">${Math.round(totalSVE).toLocaleString()}</td>
                                <td class="text-end">100%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Charger les statistiques au chargement de la page
document.addEventListener('DOMContentLoaded', loadNationalStats);
