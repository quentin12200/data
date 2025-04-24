// Carte des résultats syndicaux
document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    let width = document.getElementById('map-container').clientWidth;
    let height = 600;
    let currentMode = 'dominance'; // 'dominance', 'scores', 'ecart'
    let departements = [];
    let resultatsNationaux = {};
    let dominantsDepartements = {};
    
    // Couleurs des syndicats principaux
    const couleursOfficiellesSyndicats = {
        "CGT": "#E30613",
        "CFDT": "#FF7900",
        "CGT-FO": "#0066CC", // Utiliser le nom tel qu'il apparait dans les données
        "CFTC": "#1D71B8",
        "CFE-CGC": "#0055A4",
        "SOLIDAIRES": "#FF0000",
        "UNSA": "#009FE3",
        "AUTRES": "#999999" // Gris pour les autres
    };
    const defaultColor = "#999999"; // Gris pour les autres
    
    // Échelles de couleurs
    const echelleDominance = d3.scaleOrdinal()
        .domain(Object.keys(couleursOfficiellesSyndicats))
        .range(Object.values(couleursOfficiellesSyndicats))
        .unknown(defaultColor);
    
    const echelleScores = d3.scaleSequential()
        .domain([0, 20000]) // 0 à 20000 voix
        .interpolator(d3.interpolate("#FFFFFF", "#E30613"));
    
    const echelleEcart = d3.scaleSequential()
        .domain([-5000, 5000]) // -5000 à +5000 voix
        .interpolator(d3.interpolate("#FF7900", "#E30613"));
    
    // Initialiser la carte
    const svg = d3.select("#map-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    // Groupe pour les départements
    const g = svg.append("g");
    
    // Projection géographique pour la France métropolitaine
    const projection = d3.geoConicConformal()
        .center([2.454071, 46.279229]) // Centre de la France
        .scale(2600)
        .translate([width / 2, height / 2]);
    
    // Générateur de chemin
    const path = d3.geoPath()
        .projection(projection);
    
    // Tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    
    // Légende
    const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(20, 20)");
    
    // Fonction pour mettre à jour la coloration de la carte
    function updateMapColoring() {
        // Mettre à jour le titre de la carte (s'il existe)
        const mapTitleElement = document.getElementById('map-title');
        if (mapTitleElement) {
            mapTitleElement.textContent = getMapTitle();
        }
        
        // Mettre à jour la légende
        updateLegend();
        
        // Mettre à jour la coloration des départements
        g.selectAll('.departement')
            .transition()
            .duration(500)
            .attr('fill', d => {
                const dept = departements.find(dept => dept.code === d.id);
                if (!dept) return "#EEE"; // Couleur par défaut si pas de données
                
                switch(currentMode) {
                    case 'dominance':
                        return echelleDominance(dept.syndicat_dominant);
                    case 'scores':
                        const voixCGT = dept.voix.CGT || 0;
                        return echelleScores(voixCGT);
                    case 'ecart':
                        return echelleEcart(dept.ecart_voix_CGT_CFDT);
                    default:
                        return "#EEE";
                }
            });
    }
    
    // Fonction pour obtenir le titre de la carte
    function getMapTitle() {
        switch(currentMode) {
            case 'dominance':
                return "Syndicat dominant par département";
            case 'scores':
                return "Nombre de voix CGT par département";
            case 'ecart':
                return "Écart de voix entre CGT et CFDT par département";
            default:
                return "Résultats syndicaux par département";
        }
    }
    
    // Fonction pour mettre à jour la légende
    function updateLegend() {
        // Supprimer l'ancienne légende
        legend.selectAll("*").remove();
        
        switch(currentMode) {
            case 'dominance':
                // Légende pour le mode dominance
                const syndicats = Object.keys(couleursOfficiellesSyndicats);
                
                syndicats.forEach((syndicat, i) => {
                    const color = couleursOfficiellesSyndicats[syndicat];
                    
                    legend.append("rect")
                        .attr("x", 0)
                        .attr("y", i * 20)
                        .attr("width", 15)
                        .attr("height", 15)
                        .attr("fill", color);
                    
                    legend.append("text")
                        .attr("x", 20)
                        .attr("y", i * 20 + 12)
                        .text(syndicat)
                        .style("font-size", "12px");
                });
                break;
                
            case 'scores':
                // Légende pour le mode scores (gradient)
                const gradientScores = legend.append("defs")
                    .append("linearGradient")
                    .attr("id", "gradient-scores")
                    .attr("x1", "0%")
                    .attr("y1", "0%")
                    .attr("x2", "100%")
                    .attr("y2", "0%");
                
                gradientScores.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-color", "#FFFFFF");
                
                gradientScores.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", "#E30613");
                
                legend.append("rect")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("width", 200)
                    .attr("height", 15)
                    .style("fill", "url(#gradient-scores)");
                
                legend.append("text")
                    .attr("x", 0)
                    .attr("y", 30)
                    .text("0 voix")
                    .style("font-size", "10px");
                
                legend.append("text")
                    .attr("x", 170)
                    .attr("y", 30)
                    .text("20 000+ voix")
                    .style("font-size", "10px");
                break;
                
            case 'ecart':
                // Légende pour le mode écart (gradient)
                const gradientEcart = legend.append("defs")
                    .append("linearGradient")
                    .attr("id", "gradient-ecart")
                    .attr("x1", "0%")
                    .attr("y1", "0%")
                    .attr("x2", "100%")
                    .attr("y2", "0%");
                
                gradientEcart.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-color", "#FF7900");
                
                gradientEcart.append("stop")
                    .attr("offset", "50%")
                    .attr("stop-color", "#FFFFFF");
                
                gradientEcart.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", "#E30613");
                
                legend.append("rect")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("width", 200)
                    .attr("height", 15)
                    .style("fill", "url(#gradient-ecart)");
                
                legend.append("text")
                    .attr("x", 0)
                    .attr("y", 30)
                    .text("CFDT +5000")
                    .style("font-size", "10px");
                
                legend.append("text")
                    .attr("x", 85)
                    .attr("y", 30)
                    .text("Égalité")
                    .style("font-size", "10px");
                
                legend.append("text")
                    .attr("x", 150)
                    .attr("y", 30)
                    .text("CGT +5000")
                    .style("font-size", "10px");
                break;
        }
    }
    
    // Fonction pour afficher le tooltip
    function showTooltip(event, d) {
        const dept = departements.find(dept => dept.code === d.id);
        if (!dept) return;
        
        let content = `
            <strong>${dept.departement} (${dept.code})</strong><br>
            Syndicat dominant: <strong>${dept.syndicat_dominant}</strong><br>
            Total des voix: <strong>${dept.total_votes.toLocaleString()}</strong><br>
            <hr>
            <strong>CGT:</strong> ${(dept.voix.CGT || 0).toLocaleString()} voix<br>
            <strong>CFDT:</strong> ${(dept.voix.CFDT || 0).toLocaleString()} voix<br>
            <strong>CGT-FO:</strong> ${(dept.voix['CGT-FO'] || 0).toLocaleString()} voix<br>
        `;
        
        tooltip.transition()
            .duration(200)
            .style("opacity", .9);
        
        tooltip.html(content)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 28) + "px");
    }
    
    // Fonction pour masquer le tooltip
    function hideTooltip() {
        tooltip.transition()
            .duration(500)
            .style("opacity", 0);
    }
    
    // Fonction pour afficher les détails d'un département
    function showDepartementDetails(dept) {
        const detailsContainer = document.getElementById('details-container');
        if (!detailsContainer) return;
        
        // Calculer les pourcentages
        const pourcentages = {};
        if (dept.total_votes > 0) {
            Object.keys(dept.voix).forEach(syndicat => {
                pourcentages[syndicat] = (dept.voix[syndicat] || 0) * 100 / dept.total_votes;
            });
        }
        
        // Créer le contenu HTML
        let html = `
            <div class="card-header">
                <h5>${dept.departement} (${dept.code})</h5>
                <div class="text-muted">Région: ${dept.region || 'Non spécifiée'}</div>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Résultats par syndicat</h6>
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Syndicat</th>
                                    <th>Voix</th>
                                    <th>%</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        // Ajouter les lignes pour chaque syndicat
        const syndicats = Object.keys(dept.voix).sort((a, b) => (dept.voix[b] || 0) - (dept.voix[a] || 0));
        
        syndicats.forEach(syndicat => {
            const voix = dept.voix[syndicat] || 0;
            const pourcentage = pourcentages[syndicat] || 0;
            
            html += `
                <tr>
                    <td><span style="color: ${couleursOfficiellesSyndicats[syndicat] || defaultColor}">■</span> ${syndicat}</td>
                    <td>${voix.toLocaleString()}</td>
                    <td>${pourcentage.toFixed(1)}%</td>
                </tr>
            `;
        });
        
        html += `
                            </tbody>
                            <tfoot>
                                <tr>
                                    <th>Total</th>
                                    <th>${dept.total_votes.toLocaleString()}</th>
                                    <th>100%</th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Comparaison CGT/CFDT</h6>
                        <div class="card bg-light mb-3">
                            <div class="card-body">
                                <p>Écart en voix: <strong>${dept.ecart_voix_CGT_CFDT.toLocaleString()}</strong></p>
                                <p>Syndicat dominant: <strong>${dept.syndicat_dominant || 'N/A'}</strong></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        detailsContainer.innerHTML = html;
    }
    
    // Fonction pour charger les statistiques nationales
    function loadNationalStats() {
        fetch('./data/resultats_nationaux.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP ${response.status} lors du chargement de resultats_nationaux.json`);
                }
                return response.json();
            })
            .then(data => {
                resultatsNationaux = data.voix || data;
                updateStatistics();
            })
            .catch(error => {
                console.error('Erreur lors du chargement des statistiques nationales:', error);
            });
    }
    
    // Fonction pour charger les départements dominants
    function loadDominantDepartements() {
        fetch('./data/departements_dominants.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP ${response.status} lors du chargement de departements_dominants.json`);
                }
                return response.json();
            })
            .then(data => {
                dominantsDepartements = data;
                updateDominantStats();
            })
            .catch(error => {
                console.error('Erreur lors du chargement des départements dominants:', error);
            });
    }
    
    // Fonction pour mettre à jour les statistiques
    function updateStatistics() {
        const statsContainer = document.getElementById('stats-container');
        if (!statsContainer || !resultatsNationaux) return;
        
        // Calculer le total des voix
        const totalVoix = Object.values(resultatsNationaux).reduce((sum, val) => sum + val, 0);
        
        // Créer le contenu HTML
        let html = `
            <div class="card-header">Statistiques nationales</div>
            <div class="card-body">
                <p>Total des voix: <strong>${totalVoix.toLocaleString()}</strong></p>
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Syndicat</th>
                            <th>Voix</th>
                            <th>%</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // Ajouter les lignes pour chaque syndicat
        const syndicats = Object.keys(resultatsNationaux).sort((a, b) => resultatsNationaux[b] - resultatsNationaux[a]);
        
        syndicats.forEach(syndicat => {
            const voix = resultatsNationaux[syndicat];
            const pourcentage = totalVoix > 0 ? (voix * 100 / totalVoix) : 0;
            
            html += `
                <tr>
                    <td><span style="color: ${couleursOfficiellesSyndicats[syndicat] || defaultColor}">■</span> ${syndicat}</td>
                    <td>${voix.toLocaleString()}</td>
                    <td>${pourcentage.toFixed(2)}%</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        statsContainer.innerHTML = html;
    }
    
    // Fonction pour mettre à jour les statistiques des départements dominants
    function updateDominantStats() {
        const dominantContainer = document.getElementById('dominant-container');
        if (!dominantContainer || !dominantsDepartements) return;
        
        // Créer le contenu HTML
        let html = `
            <div class="card-header">Départements dominants par syndicat</div>
            <div class="card-body">
                <div class="row">
        `;
        
        // Ajouter les colonnes pour chaque syndicat
        const syndicats = Object.keys(dominantsDepartements).filter(s => dominantsDepartements[s].length > 0);
        
        syndicats.forEach(syndicat => {
            const depts = dominantsDepartements[syndicat];
            
            html += `
                <div class="col-md-4 mb-3">
                    <h6><span style="color: ${couleursOfficiellesSyndicats[syndicat] || defaultColor}">■</span> ${syndicat} (${depts.length})</h6>
                    <ul class="list-unstyled small">
            `;
            
            // Limiter à 10 départements maximum
            const displayDepts = depts.slice(0, 10);
            
            displayDepts.forEach(code => {
                const dept = departements.find(d => d.code === code);
                const nom = dept ? dept.departement : `Département ${code}`;
                
                html += `<li>${code} - ${nom}</li>`;
            });
            
            if (depts.length > 10) {
                html += `<li>... et ${depts.length - 10} autres</li>`;
            }
            
            html += `
                    </ul>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        dominantContainer.innerHTML = html;
    }
    
    // Charger les données géographiques et les données syndicales
    console.log("Chargement des données géographiques...");
    console.log("Chargement des données départementales...");
    
    Promise.all([
        // Chemin relatif vers le fichier de carte géographique
        fetch('../assets/france-departements.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP ${response.status} - ${response.statusText} lors du chargement de /assets/france-departements.json`);
                }
                return response.json();
            }),
        // Chemin absolu depuis la racine du serveur
        fetch('./data/departements.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP ${response.status} - ${response.statusText} lors du chargement de departements.json`);
                }
                console.log("departements.json trouvé, statut OK. Lecture en JSON...");
                return response.json();
            })
    ])
    .then(([franceGeo, departementsData]) => {
        // Vérifier que les données géographiques sont correctement formatées
        console.log("Données géographiques reçues:", franceGeo);
        
        if (!franceGeo) {
            console.error("franceGeo est null ou undefined");
            throw new Error("Données géographiques manquantes");
        }
        
        if (!franceGeo.features) {
            console.error("franceGeo.features est absent", franceGeo);
            throw new Error("Propriété 'features' manquante dans les données géographiques");
        }
        
        if (!Array.isArray(franceGeo.features)) {
            console.error("franceGeo.features n'est pas un tableau", franceGeo.features);
            throw new Error("La propriété 'features' n'est pas un tableau dans les données géographiques");
        }

        console.log(`Chargement de ${franceGeo.features.length} départements géographiques.`);

        // Afficher les données des départements
        console.log("--- Données des départements ---");
        console.log(departementsData);
        console.log("--- Fin données des départements ---");

        // Vérifier la structure des données
        if (departementsData && typeof departementsData === 'object' && departementsData !== null) {
            console.log(`Le fichier contient des données pour ${Object.keys(departementsData).length} départements.`);
            
            try {
                // Transformer en tableau pour la recherche par code
                departements = Object.entries(departementsData).map(([code, data]) => ({
                    code: code,
                    departement: data.departement || `Département ${code}`,
                    region: data.region || 'Inconnue',
                    voix: data.scores || {},
                    pourcentages: {},  // Sera calculé à partir des scores si nécessaire
                    syndicat_dominant: data.syndicat_dominant || 'N/A',
                    max_voix: data.max_voix || 0,
                    ecart_CGT_CFDT: data.ecart_CGT_CFDT || 0,
                    ecart_voix_CGT_CFDT: data.ecart_voix_CGT_CFDT || 0,
                    total_votes: data.total_votes || 0
                }));
                
                console.log(`${departements.length} départements chargés avec succès.`);
                
                // Dessiner la carte
                g.selectAll('path')
                    .data(franceGeo.features)
                    .enter()
                    .append('path')
                    .attr('d', path)
                    .attr('class', 'departement')
                    .attr('id', d => `dept-${d.id}`)
                    .attr('fill', '#EEE')
                    .on('mouseover', function(event, d) {
                        d3.select(this).attr('stroke', '#000').attr('stroke-width', 1.5);
                        showTooltip(event, d);
                    })
                    .on('mouseout', function(event, d) {
                        d3.select(this).attr('stroke', '#FFF').attr('stroke-width', 0.5);
                        hideTooltip();
                    })
                    .on('click', function(event, d) {
                        const dept = departements.find(dept => dept.code === d.id);
                        if (dept) {
                            d3.selectAll('.departement').classed('selected-dept', false);
                            d3.select(this).classed('selected-dept', true);
                            showDepartementDetails(dept);
                        }
                    });
                
                // Appliquer la coloration initiale
                updateMapColoring();
                
                // Charger les statistiques nationales et départements dominants
                loadNationalStats();
                loadDominantDepartements();
                
            } catch (e) {
                console.error("Erreur lors du traitement des données:", e);
                throw new Error(`Impossible de traiter les données des départements: ${e.message}`);
            }
        } else {
            console.error("Le contenu de departements.json n'est pas un objet valide:", departementsData);
            throw new Error("Format de données invalide pour departements.json");
        }
    })
    .catch(error => {
        // Log de diagnostic amélioré dans le catch principal
        console.error("--- ERREUR FINALE CAPTURÉE ---");
        console.error("Objet erreur brut:", error);
        console.error("Erreur stringify:", JSON.stringify(error));
        console.error("Message standard:", error.message);
        console.error("Stack trace:", error.stack);
        console.error("--- FIN ERREUR --- ");

        document.getElementById('map-container').innerHTML = `
            <div class="alert alert-danger">
                Erreur lors du chargement de la carte. Message: ${(error && error.message) ? error.message : 'Erreur inconnue (voir console)'}<br>
                Vérifiez que les fichiers de données (departements.json, assets/france-departements.json) sont correctement créés, accessibles et valides. Consultez la console (F12) pour plus de détails.
            </div>
        `;
       
        // Tenter de charger des informations de débogage
        fetch('assets/france-departements.json')
            .then(response => response.status)
            .then(status => {
                console.log(`Statut du fichier de carte: ${status}`);
            })
            .catch(e => console.error("Impossible d'accéder au fichier de carte", e));
    });
   
    // Gestionnaires d'événements pour les boutons de mode
    document.getElementById('btn-dominance').addEventListener('click', function() {
        currentMode = 'dominance';
        d3.selectAll('.btn-sm').classed('active', false);
        this.classList.add('active');
        updateMapColoring();
    });
    
    document.getElementById('btn-scores').addEventListener('click', function() {
        currentMode = 'scores';
        d3.selectAll('.btn-sm').classed('active', false);
        this.classList.add('active');
        updateMapColoring();
    });
    
    document.getElementById('btn-ecart').addEventListener('click', function() {
        currentMode = 'ecart';
        d3.selectAll('.btn-sm').classed('active', false);
        this.classList.add('active');
        updateMapColoring();
    });
    
    // Redimensionner la carte si la fenêtre change de taille
    window.addEventListener('resize', function() {
        width = document.getElementById('map-container').clientWidth;
        svg.attr("width", width);
        projection.translate([width / 2, height / 2]);
        g.selectAll('path').attr('d', path);
    });
});
