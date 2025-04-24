import re
import os

def nettoyer_fichier_html():
    """
    Nettoie le fichier carte_croisee.html en supprimant les données simulées
    et en corrigeant les erreurs de syntaxe.
    """
    # Chemins des fichiers
    fichier_source = "carte_croisee.html"
    fichier_destination = "carte_croisee_clean.html"
    
    # Vérifier si le fichier source existe
    if not os.path.exists(fichier_source):
        print(f"Erreur : Le fichier source {fichier_source} n'existe pas.")
        return
    
    # Lire le contenu du fichier source
    with open(fichier_source, 'r', encoding='utf-8') as f:
        contenu = f.read()
    
    # Extraire la partie valide du fichier (jusqu'à la fin de la fonction generateEntreprises)
    match = re.search(r'(.*?function generateEntreprises.*?return html;\s*})', contenu, re.DOTALL)
    if not match:
        print("Erreur : Impossible de trouver la fonction generateEntreprises dans le fichier source.")
        return
    
    partie_valide = match.group(1)
    
    # Ajouter la fonction updateTopDepartements
    partie_valide += """
        
        // Mettre à jour le top 5 des départements
        function updateTopDepartements() {
            console.log("Mise à jour du top 5 des départements...");
            
            // Récupérer les valeurs des filtres
            const syndicatFiltre = document.getElementById("filtre-syndicat").value;
            const federationFiltre = document.getElementById("filtre-federation").value;
            
            // Convertir les données des départements en tableau
            const depts = Object.entries(window.departementsData || {}).map(([code, data]) => {
                return {
                    code,
                    nom: data.nom,
                    valeur: syndicatFiltre !== 'tous' && federationFiltre !== 'tous' ?
                        (data.croisement[syndicatFiltre]?.[federationFiltre] || 0) :
                        syndicatFiltre !== 'tous' ?
                            (data.confederations[syndicatFiltre] || 0) :
                            federationFiltre !== 'tous' ?
                                (data.idcc[federationFiltre] || 0) :
                                data.total_votes
                };
            });
            
            // Trier par valeur décroissante
            depts.sort((a, b) => b.valeur - a.valeur);
            
            // Prendre les 5 premiers
            const top5 = depts.slice(0, 5);
            
            // Générer le HTML
            let html = '';
            top5.forEach(dept => {
                html += `
                    <div class="top-departements-item">
                        <span>${dept.nom} (${dept.code})</span>
                        <span>${dept.valeur.toLocaleString()} voix</span>
                    </div>
                `;
            });
            
            // Mettre à jour le contenu
            document.getElementById('top-departements').innerHTML = html;
        }
    </script>
</body>
</html>"""
    
    # Écrire le contenu nettoyé dans le fichier de destination
    with open(fichier_destination, 'w', encoding='utf-8') as f:
        f.write(partie_valide)
    
    print(f"Fichier nettoyé créé : {fichier_destination}")
    return fichier_destination

if __name__ == "__main__":
    nettoyer_fichier_html()
