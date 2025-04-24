import pandas as pd

# Charger le nouveau fichier Excel
excel_path = '../PV_RETENUS_M2025/INTERPRO_RETENUS_2025_20250331.xlsx'
df = pd.read_excel(excel_path)

# Afficher les valeurs uniques de la colonne Département
print('Valeurs uniques dans la colonne Département:')
print(df['Département'].unique())

# Afficher le nombre de lignes par département
print('\nNombre de lignes par département:')
print(df['Département'].value_counts())

# Calculer la somme des voix CGT et FO pour le département 12 (toutes variantes de "12")
def is_dept_12(val):
    if pd.isna(val):
        return False
    val_str = str(val).strip().lstrip('0')
    return val_str == '12'

mask_12 = df['Département'].apply(is_dept_12)
df_12 = df[mask_12]

somme_cgt = df_12['CGT'].sum()
somme_fo = df_12['CGT-FO'].sum()
print(f"\nLignes avec Département=12 : {len(df_12)}")
print(f"Somme CGT (Excel) pour 12 : {somme_cgt}")
print(f"Somme FO (Excel) pour 12 : {somme_fo}")
