import pandas as pd

# Charger le fichier complet des PV retenus
df = pd.read_excel('../PV_RETENUS_M2025/INTERPRO_RETENUS_2025_20250331.xlsx')

# Colonnes à extraire (ajuster si besoin selon vos besoins d'analyse)
colonnes_utiles = [
    'SIRET', 'N°PV', 'Raison sociale', 'CP', 'Ville', 'Département', 'Région',
    'IDCC ', 'Lib IDCC ', 'Date', 'Coll', 'Inscrits', 'Votants', 'SVE',
    'Confédération', 'Code Syndicat', 'Lib Synd LC', 'Lib Synd'
]

# On ne garde que les colonnes utiles si elles existent
colonnes_finales = [col for col in colonnes_utiles if col in df.columns]
df = df[colonnes_finales]

# Nettoyage : suppression des espaces dans les noms de colonnes
# (pour compatibilité future avec d'autres scripts)
df.columns = [c.strip() for c in df.columns]

# Exporter le fichier Excel propre et complet
output_path = 'INTERPRO_complet_avec_college.xlsx'
df.to_excel(output_path, index=False)
print(f"Fichier exporté : {output_path} ({len(df)} lignes)")
