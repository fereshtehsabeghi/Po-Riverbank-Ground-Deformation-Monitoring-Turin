import geopandas as gpd
import libpysal
from esda.getisord import G_Local
import numpy as np
import warnings

# Suppress the harmless disconnected components warning to keep your terminal clean
warnings.filterwarnings("ignore", message="The weights matrix is not fully connected")

print("1. Loading clipped riverbank data...")
gdf = gpd.read_file("riverbank_deformation_E_2019_2023.gpkg")

# --- THE FIXES ---
# 1. Using the exact column name we found in your dataset
vel_col = 'mean_velocity' 

# 2. Converting the text strings into numeric decimals (floats) so PySAL can do the math
gdf[vel_col] = gdf[vel_col].astype(float)
# -----------------

print("2. Building Spatial Weights Matrix (KNN)...")
# K=8 ensures we look at the 8 closest scatterers to establish the local neighborhood
w = libpysal.weights.KNN.from_dataframe(gdf, k=8)
w.transform = 'R' # Row-standardize the weights

print("3. Calculating Getis-Ord Gi* Statistic...")
# star=True includes the target point itself in its own neighborhood (Gi* instead of Gi)
gi_star = G_Local(gdf[vel_col], w, star=True)

print("4. Appending statistics to the dataset...")
# Extracting the Z-scores and Pseudo P-values directly into our GeoDataFrame
gdf['z_score'] = gi_star.Zs
gdf['p_value'] = gi_star.p_sim

print("5. Classifying Risk Zones (95% Confidence)...")
# Defining our spatial clusters based on statistical significance (p < 0.05 and Z > 1.96 or < -1.96)
conditions = [
    (gdf['p_value'] < 0.05) & (gdf['z_score'] < -1.96),  # Cluster of highly negative values (Subsidence)
    (gdf['p_value'] < 0.05) & (gdf['z_score'] > 1.96)    # Cluster of highly positive values (Uplift)
]
choices = ['Significant_Subsidence', 'Significant_Uplift']
gdf['cluster_type'] = np.select(conditions, choices, default='Not_Significant')

print("6. Saving Hotspot map to GeoPackage...")
# Save the results to a new, analysis-ready file
gdf.to_file("riverbank_hotspots.gpkg", driver="GPKG")

# Print a quick summary of what the algorithm found
subsidence_count = len(gdf[gdf['cluster_type'] == 'Significant_Subsidence'])
uplift_count = len(gdf[gdf['cluster_type'] == 'Significant_Uplift'])

print("\n--- ANALYSIS SUMMARY ---")
print(f"Total points processed: {len(gdf)}")
print(f"Significant Subsidence points found: {subsidence_count}")
print(f"Significant Uplift points found: {uplift_count}")
print("Success! Your riverbank_hotspots.gpkg is ready for validation.")