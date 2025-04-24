# Cartographie des Résultats Syndicaux - CGT

Ce projet présente une visualisation interactive des résultats des élections syndicales professionnelles 2025, avec un focus particulier sur la CGT.

## Structure du projet

- `index.html` - Page d'accueil du projet
- `/data/cartographie/` - Contient les fichiers HTML des cartes et visualisations
  - `carte_data.html` - Carte interactive avec données par département
  - `carte_syndicale.html` - Carte syndicale avec visualisation géographique
  - `carte_finale.html` - Version finale de la carte pour présentation
  - Autres fichiers HTML de visualisation
- `/data/json_data_ordonnees/` - Contient les données JSON structurées
  - `carte_data.json` - Données globales pour la carte
  - `resultats_departements.json` - Résultats complets par département
  - `stats_regions.json` - Statistiques agrégées par région
  - Fichiers individuels par département

## Fonctionnalités

- Visualisation des résultats par département et par région
- Filtrage des départements selon différents critères (syndicat dominant, pourcentage CGT, etc.)
- Affichage détaillé des résultats pour chaque organisation syndicale
- Statistiques nationales et régionales
- Interface responsive adaptée à tous les appareils

## Technologies utilisées

- HTML5, CSS3, JavaScript
- Bootstrap pour l'interface utilisateur
- D3.js pour les visualisations de données
- Python pour le traitement des données (scripts inclus)

## Déploiement

Ce projet est déployé sur Vercel et accessible à l'adresse [URL à venir].

## Données

Les données utilisées proviennent des élections professionnelles 2025 et ont été traitées pour être présentées de manière claire et interactive.
