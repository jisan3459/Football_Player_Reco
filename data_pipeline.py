import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

print("Starting data pipeline...")

# Load the dataset
print("Loading dataset...")
df = pd.read_csv("All_Players_1992-2025.csv")

# Filter for season 2024-2025
df_2024_25 = df[df["Season"] == "2024-2025"].copy()

print(f"Filtered to 2024-2025: {len(df_2024_25)} rows")

# Save player names and basic info for the frontend
player_info = df_2024_25[['PlayerID', 'Player', 'Squad', 'League', 'Pos']].drop_duplicates(subset=['Player']).copy()
player_info.to_csv("player_info.csv", index=False)

# Remove duplicates
df_2024_25.drop_duplicates(inplace=True)

# Save player names in order
player_names = df_2024_25["Player"].values

drop_cols = [
    'Player',
    'Nation',
    'Squad',
    'League',
    'Season',
    'Born'
]

# Remove only if present
df_2024_25.drop(columns=[c for c in drop_cols if c in df_2024_25.columns], inplace=True)

# Convert to numeric
for col in df_2024_25.columns:
    if df_2024_25[col].dtype == 'object' and col != 'Pos':
        df_2024_25[col] = pd.to_numeric(df_2024_25[col], errors='coerce')

# Handle missing values
numeric_cols = df_2024_25.select_dtypes(include=np.number).columns
for col in numeric_cols:
    df_2024_25[col] = df_2024_25[col].fillna(df_2024_25[col].median())

# Standardize
print("Standardizing...")
scaler = StandardScaler()
df_2024_25[numeric_cols] = scaler.fit_transform(df_2024_25[numeric_cols])

# One hot encoding
df_2024_25 = pd.get_dummies(df_2024_25, columns=['Pos'], dtype=int)

# Feature Weighting
weighted_df = df_2024_25.copy()
weights = {
    'Gls': 3.0, 'xG': 2.5, 'SoT%': 2.0, 'Sh/90': 2.0,
    'Ast': 2.5, 'xA': 2.5, 'KP': 2.0, 'PrgP': 2.0, 'PrgC': 2.0,
    'Tkl': 3.0, 'TklW': 3.0, 'Int': 2.5, 'Blocks': 2.5, 'Clr': 2.5, 'Recov': 2.0,
    'Save%': 3.0, 'Saves': 3.0, 'CS': 2.5
}

for col, weight in weights.items():
    if col in weighted_df.columns:
        weighted_df[col] *= weight

# PCA
print("Applying PCA...")
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(weighted_df)

# Cosine Similarity
print("Calculating cosine similarity...")
cosine_sim = cosine_similarity(X_pca)

# Save the similarity matrix and player names
print("Saving outputs...")
with open('similarity_model.pkl', 'wb') as f:
    pickle.dump({
        'cosine_sim': cosine_sim,
        'player_names': player_names
    }, f)

print("Data pipeline finished successfully.")
