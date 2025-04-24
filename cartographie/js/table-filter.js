// Fonctions pour le filtrage et le tri du tableau des PV
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter Bootstrap Icons pour les icônes
    const iconLink = document.createElement('link');
    iconLink.rel = 'stylesheet';
    iconLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css';
    document.head.appendChild(iconLink);
});

// Fonction à appeler après le chargement des PV d'un département
function initTableFilters(filteredPvs, codeDept, deptName) {
    // Récupérer les éléments du DOM
    const searchInput = document.getElementById('search-pv');
    const sortSelect = document.getElementById('sort-pv');
    const sortDirectionBtn = document.getElementById('sort-direction');
    const limitSelect = document.getElementById('limit-pv');
    const exportBtn = document.getElementById('btn-export-csv');
    
    if (!searchInput || !sortSelect || !sortDirectionBtn || !limitSelect || !exportBtn) {
        console.error('Éléments de filtrage non trouvés dans le DOM');
        return;
    }
    
    let sortDirection = 'desc';
    let currentPvs = [...filteredPvs]; // Copie des PV filtrés
    
    // Fonction pour mettre à jour le tableau
    function updateTable() {
        // Appliquer la recherche
        let searchTerm = searchInput.value.toLowerCase();
        let searchResults = currentPvs.filter(pv => 
            pv.raison_sociale.toLowerCase().includes(searchTerm) ||
            pv.ville.toLowerCase().includes(searchTerm) ||
            pv.idcc.toLowerCase().includes(searchTerm) ||
            pv.lib_idcc.toLowerCase().includes(searchTerm)
        );
        
        // Appliquer le tri
        let sortBy = sortSelect.value;
        searchResults.sort((a, b) => {
            let valA, valB;
            
            if (sortBy === 'raison_sociale') {
                valA = a.raison_sociale.toLowerCase();
                valB = b.raison_sociale.toLowerCase();
            } else if (sortBy === 'ville') {
                valA = a.ville.toLowerCase();
                valB = b.ville.toLowerCase();
            } else if (sortBy === 'date') {
                valA = new Date(a.date);
                valB = new Date(b.date);
            } else if (sortBy === 'inscrits') {
                valA = a.inscrits;
                valB = b.inscrits;
            } else if (sortBy === 'cgt') {
                valA = a.voix.CGT;
                valB = b.voix.CGT;
            }
            
            if (sortDirection === 'asc') {
                return valA > valB ? 1 : -1;
            } else {
                return valA < valB ? 1 : -1;
            }
        });
        
        // Appliquer la limite
        let limit = parseInt(limitSelect.value);
        let displayResults = limit > 0 ? searchResults.slice(0, limit) : searchResults;
        
        // Mettre à jour le tableau
        const tbody = document.querySelector('#pv-table tbody');
        tbody.innerHTML = '';
        
        for (const pv of displayResults) {
            const date = new Date(pv.date);
            const formattedDate = date.toLocaleDateString('fr-FR');
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${pv.siret}</td>
                <td>${pv.raison_sociale}</td>
                <td>${pv.ville}</td>
                <td>${pv.idcc} - ${pv.lib_idcc}</td>
                <td><span class="badge bg-secondary college-badge">${pv.college}</span></td>
                <td>${formattedDate}</td>
                <td>${pv.inscrits}</td>
                <td>${pv.votants}</td>
                <td>${pv.sve_total}</td>
                <td>${pv.voix.CGT}</td>
                <td>${pv.voix.CFDT}</td>
                <td>${pv.voix["CGT-FO"]}</td>
                <td>${pv.voix.CFTC}</td>
                <td>${pv.voix["CFE-CGC"]}</td>
                <td>${pv.voix.SOLIDAIRES}</td>
                <td>${pv.voix.UNSA}</td>
                <td>${pv.voix.AUTRES}</td>
            `;
            tbody.appendChild(tr);
        }
    }
    
    // Fonction pour exporter en CSV
    function exportToCSV() {
        console.log('Début export CSV pour', codeDept, deptName, 'avec', currentPvs.length, 'PV');
        
        try {
            // En-têtes CSV
            const headers = ['SIRET', 'Raison Sociale', 'Ville', 'IDCC', 'Collège', 'Date', 'Inscrits', 'Votants', 'SVE', 'CGT', 'CFDT', 'CGT-FO', 'CFTC', 'CFE-CGC', 'SOLIDAIRES', 'UNSA', 'AUTRES'];
            
            // Générer le contenu CSV
            let csvContent = headers.join(';') + '\n';
            
            // Ajouter chaque ligne
            for (const pv of currentPvs) {
                // Formater la date si nécessaire
                let formattedDate = pv.date;
                if (pv.date && pv.date.match(/^\d{4}-\d{2}-\d{2}$/)) {
                    const dateParts = pv.date.split('-');
                    formattedDate = `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`;
                }
                
                // Préparer les données de la ligne
                const rowData = [
                    pv.siret || '',
                    escapeCsvValue(pv.raison_sociale || ''),
                    escapeCsvValue(pv.ville || ''),
                    escapeCsvValue(`${pv.idcc || ''} - ${pv.lib_idcc || ''}`),
                    pv.college || '',
                    formattedDate || '',
                    pv.inscrits || 0,
                    pv.votants || 0,
                    pv.sve_total || 0,
                    pv.voix ? (pv.voix.CGT || 0) : 0,
                    pv.voix ? (pv.voix.CFDT || 0) : 0,
                    pv.voix ? (pv.voix["CGT-FO"] || 0) : 0,
                    pv.voix ? (pv.voix.CFTC || 0) : 0,
                    pv.voix ? (pv.voix["CFE-CGC"] || 0) : 0,
                    pv.voix ? (pv.voix.SOLIDAIRES || 0) : 0,
                    pv.voix ? (pv.voix.UNSA || 0) : 0,
                    pv.voix ? (pv.voix.AUTRES || 0) : 0
                ];
                
                // Ajouter la ligne au CSV
                csvContent += rowData.join(';') + '\n';
            }
            
            // Fonction pour échapper les valeurs CSV
            function escapeCsvValue(value) {
                if (typeof value !== 'string') return value;
                // Si la valeur contient des points-virgules, des guillemets ou des sauts de ligne, l'entourer de guillemets
                if (value.includes(';') || value.includes('"') || value.includes('\n')) {
                    // Doubler les guillemets existants
                    return '"' + value.replace(/"/g, '""') + '"';
                }
                return value;
            }
            
            // Créer un blob avec le contenu CSV
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            
            // Créer un lien de téléchargement
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `PV_Departement_${codeDept}_${deptName.replace(/\s+/g, '_')}.csv`);
            document.body.appendChild(link);
            
            // Déclencher le téléchargement
            link.click();
            
            // Nettoyer
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            console.log('Export CSV terminé avec succès');
        } catch (error) {
            console.error('Erreur lors de l\'export CSV:', error);
            alert('Une erreur est survenue lors de l\'export CSV. Veuillez réessayer.');
        }
    }
    
    // Ajouter les écouteurs d'événements
    searchInput.addEventListener('input', updateTable);
    sortSelect.addEventListener('change', updateTable);
    sortDirectionBtn.addEventListener('click', () => {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        sortDirectionBtn.textContent = sortDirection === 'asc' ? '↑' : '↓';
        updateTable();
    });
    limitSelect.addEventListener('change', updateTable);
    exportBtn.addEventListener('click', exportToCSV);
    
    // Initialiser le tableau
    updateTable();
}
