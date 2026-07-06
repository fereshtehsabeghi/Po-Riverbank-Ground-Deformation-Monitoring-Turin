import geopandas as gpd

print("1. Loading layers...")
hotspots = gpd.read_file("riverbank_hotspots.gpkg")
infra = gpd.read_file("riverbank_infrastructure_all.gpkg")

# Isolate the critical 20 points
critical_points = hotspots[hotspots['cluster_type'] == 'Significant_Uplift'].copy()

print("\n--- CRS VERIFICATION ---")
print(f"Hotspot CRS: {critical_points.crs}")
print(f"Infrastructure CRS: {infra.crs}")

# Force them to match exactly just in case
if critical_points.crs != infra.crs:
    print("Warning: CRS mismatch detected! Aligning infrastructure to match points...")
    infra = infra.to_crs(critical_points.crs)

print("\n--- DISTANCE CHECK ---")
print(f"Analyzing distances for {len(critical_points)} active hotspot points...")

# Calculate the distance from each point to the absolute closest building
distances = []
for idx, point in critical_points.iterrows():
    # Find the distance to all building geometries and take the minimum
    min_dist = infra.distance(point.geometry).min()
    distances.append(min_dist)

import pandas as pd
dist_series = pd.Series(distances)

print("\nDistance Summary (in meters):")
print(dist_series.describe())

print("\nClosest 5 distances found:")
print(dist_series.nsmallest(5))