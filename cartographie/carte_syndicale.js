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
    const mapContainer = document.getElementById('map-container');
    if (!mapContainer) return;

    // Dimensions de la carte
    const width = mapContainer.clientWidth;
    const height = 500;
    const margin = { top: 10, right: 10, bottom: 10, left: 10 };

    // Créer l'élément SVG
    const svg = d3.select('#map-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height])
        .attr('style', 'max-width: 100%; height: auto;');

    // Créer une projection géographique
    const projection = d3.geoMercator()
        .center([2.5, 46.8]) // Centre de la France
        .scale(width * 3.5)
        .translate([width / 2, height / 2]);

    // Créer un générateur de chemin
    const path = d3.geoPath()
        .projection(projection);

    // Dessiner les départements
    const departments = svg.append('g')
        .selectAll('path')
        .data(geoData.features)
        .join('path')
        .attr('d', path)
        .attr('fill', d => getDepartmentColor(d.properties.code))
        .attr('stroke', '#FFF')
        .attr('stroke-width', 0.5)
        .attr('class', 'department')
        .attr('data-code', d => d.properties.code)
        .on('click', function(event, d) {
            showDepartmentDetails(d.properties.code);
        })
        .on('mouseover', function(event, d) {
            d3.select(this)
                .attr('stroke-width', 1.5);
            
            // Afficher une infobulle
            const dept = window.departementData[d.properties.code];
            if (dept) {
                const tooltip = d3.select('#tooltip');
                tooltip.style('display', 'block')
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY + 10) + 'px')
                    .html(`
                        <strong>${d.properties.code} - ${d.properties.nom}</strong><br>
                        ${dept.syndicat_dominant || 'Non défini'}
                    `);
            }
        })
        .on('mouseout', function() {
            d3.select(this)
                .attr('stroke-width', 0.5);
            
            d3.select('#tooltip').style('display', 'none');
        });

    // Légende
    const legendData = [
        { color: '#e41a1c', label: 'CGT' },
        { color: '#377eb8', label: 'CFDT' },
        { color: '#ff7f00', label: 'CGT-FO' },
        { color: '#984ea3', label: 'CFTC' },
        { color: '#4daf4a', label: 'CFE-CGC' },
        { color: '#ffff33', label: 'SOLIDAIRES' },
        { color: '#a65628', label: 'UNSA' },
        { color: '#999999', label: 'AUTRES' },
        { color: '#e0e0e0', label: 'Non défini' }
    ];

    const legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', `translate(20, ${height - 20 - legendData.length * 20})`);

    legend.selectAll('rect')
        .data(legendData)
        .join('rect')
        .attr('x', 0)
        .attr('y', (d, i) => i * 20)
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', d => d.color);

    legend.selectAll('text')
        .data(legendData)
        .join('text')
        .attr('x', 20)
        .attr('y', (d, i) => i * 20 + 12)
        .text(d => d.label)
        .attr('font-size', '12px')
        .attr('fill', '#333');

    // Zoom interactif
    const zoom = d3.zoom()
        .scaleExtent([1, 8])
        .on('zoom', (event) => {
            svg.selectAll('g').attr('transform', event.transform);
        });

    svg.call(zoom);

    // Mettre à jour la coloration
    updateMapColoring();
}

// Obtenir la couleur en fonction du syndicat dominant
function getDepartmentColor(code) {
    const deptData = window.departementData?.[code];
    if (!deptData || !deptData.syndicat_dominant) return '#e0e0e0';
    
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
    
    return colorMap[deptData.syndicat_dominant] || '#e0e0e0';
}

// Mettre à jour la coloration de la carte
function updateMapColoring() {
    d3.selectAll('.department')
        .attr('fill', function() {
            const code = d3.select(this).attr('data-code');
            return getDepartmentColor(code);
        });
}

// Afficher les détails d'un département
function showDepartmentDetails(code) {
    const deptData = window.departementData?.[code];
    if (!deptData) {
        console.error('Données non disponibles pour le département', code);
        return;
    }
    
    // Récupérer les éléments pour afficher les détails
    const deptName = d3.select('#dept-name');
    const deptStats = d3.select('#dept-stats');
    const deptPV = d3.select('#dept-pv');
    
    // Mettre à jour le nom du département
    deptName.html(`${code} - ${deptData.nom || 'Département'}`);
    
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
    
    // Mettre à jour les statistiques du département
    deptStats.html(`
        <div class="card mb-3">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Statistiques du département</h5>
            </div>
            <div class="card-body p-3">
                <div class="row">
                    <div class="col-md-4 mb-2">
                        <div class="border rounded p-2">
                            <div class="small text-muted">Inscrits</div>
                            <div class="h5 mb-0">${Math.round(deptData.total_inscrits || 0).toLocaleString()}</div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-2">
                        <div class="border rounded p-2">
                            <div class="small text-muted">Votants</div>
                            <div class="h5 mb-0">${Math.round(deptData.total_votants || 0).toLocaleString()}</div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-2">
                        <div class="border rounded p-2">
                            <div class="small text-muted">SVE</div>
                            <div class="h5 mb-0">${Math.round(totalSVE).toLocaleString()}</div>
                        </div>
                    </div>
                </div>
                
                <div class="table-responsive mt-3">
                    <table class="table table-sm table-striped">
                        <thead>
                            <tr>
                                <th>Organisation</th>
                                <th class="text-end">CSE</th>
                                <th class="text-end">TPE</th>
                                <th class="text-end">AGRI</th>
                                <th class="text-end">Total</th>
                                <th class="text-end">%</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${syndicats.map(syndicat => {
                                const voixCSE = deptData.voix.CSE[syndicat] || 0;
                                const voixTPE = deptData.voix.TPE[syndicat] || 0;
                                const voixAGRI = deptData.voix.AGRI[syndicat] || 0;
                                const totalVoix = voixTotales[syndicat];
                                const pourcentage = totalSVE > 0 ? (totalVoix / totalSVE * 100) : 0;
                                
                                return `
                                    <tr>
                                        <td>${syndicat}</td>
                                        <td class="text-end">${Math.round(voixCSE).toLocaleString()}</td>
                                        <td class="text-end">${Math.round(voixTPE).toLocaleString()}</td>
                                        <td class="text-end">${Math.round(voixAGRI).toLocaleString()}</td>
                                        <td class="text-end">${Math.round(totalVoix).toLocaleString()}</td>
                                        <td class="text-end">${pourcentage.toFixed(2)}%</td>
                                    </tr>
                                `;
                            }).join('')}
                            <tr class="table-info fw-bold">
                                <td>Total</td>
                                <td class="text-end">${Math.round(deptData.voix.CSE.total || 0).toLocaleString()}</td>
                                <td class="text-end">${Math.round(deptData.voix.TPE.total || 0).toLocaleString()}</td>
                                <td class="text-end">${Math.round(deptData.voix.AGRI.total || 0).toLocaleString()}</td>
                                <td class="text-end">${Math.round(totalSVE).toLocaleString()}</td>
                                <td class="text-end">100%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `);
    
    // Afficher les détails et scrollez vers eux
    document.getElementById('department-details').style.display = 'block';
    document.getElementById('department-details').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Charger les statistiques au chargement de la page
document.addEventListener('DOMContentLoaded', loadNationalStats);
