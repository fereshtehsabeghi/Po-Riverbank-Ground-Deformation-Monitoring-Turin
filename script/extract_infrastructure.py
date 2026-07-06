import geopandas as gpd
import osmnx as ox
import pandas as pd
import warnings

# Suppress geometry clean-up warnings from OSMnx
warnings.filterwarnings("ignore", category=UserWarning)

print("1. Loading your calculated hotspot data...")
# Load the results from your previous step
hotspots_gdf = gpd.read_file("riverbank_hotspots.gpkg")

# Isolate just the 20 statistically significant movement points
critical_points = hotspots_gdf[hotspots_gdf['cluster_type'] == 'Significant_Uplift'].copy()
print(f"   -> Found {len(critical_points)} active deformation hotspots to analyze.")

print("2. Re-generating the 250m river corridor boundary...")
# We fetch the river again to ensure our infrastructure search area matches perfectly
try:
    river_gdf = ox.features_from_place("Turin, Italy", tags={"waterway": "river", "name": ["Po", "Fiume Po"]})
except AttributeError:
    river_gdf = ox.geometries_from_place("Turin, Italy", tags={"waterway": "river", "name": ["Po", "Fiume Po"]})

river_gdf_3035 = river_gdf.to_crs(epsg=3035)
river_geometry = river_gdf_3035.union_all()
corridor_polygon_3035 = river_geometry.buffer(250)

# OSMnx requires WGS84 (EPSG:4326) polygons to query features from the internet
corridor_gdf_4326 = gpd.GeoDataFrame(geometry=[corridor_polygon_3035], crs="EPSG:3035").to_crs(epsg=4326)
polygon_4326 = corridor_gdf_4326.geometry.iloc[0]

print("3. Querying OpenStreetMap for buildings, bridges, and retaining walls...")
# Defining tags to capture a wide array of civil infrastructure along the banks
tags = {
    "building": True, 
    "bridge": True, 
    "man_made": ["retaining_wall", "embankment", "pier"]
}

try:
    infra_gdf = ox.features_from_polygon(polygon_4326, tags=tags)
except AttributeError:
    infra_gdf = ox.geometries_from_polygon(polygon_4326, tags=tags)

# Project the retrieved infrastructure back to EPSG:3035 to match our spatial metrics
infra_gdf_3035 = infra_gdf.to_crs(epsg=3035)

# Keep only the essential columns to keep the file clean and lightweight
columns_to_keep = ['element_type', 'building', 'bridge', 'man_made', 'name', 'building:levels', 'start_date', 'geometry']
existing_columns = [col for col in columns_to_keep if col in infra_gdf_3035.columns]
infra_gdf_clean = infra_gdf_3035[existing_columns].copy()

print(f"   -> Downloaded {len(infra_gdf_clean)} structural features within the corridor.")

print("4. Executing Spatial Join with a 10-meter tolerance buffer...")
# Create a temporary 10-meter buffer around our critical points
# Since critical_points is in EPSG:3035, the buffer distance is exactly in meters
critical_buffers = critical_points.copy()
critical_buffers['geometry'] = critical_points.geometry.buffer(10)

# Execute the spatial join using the buffered points instead of raw points
try:
    exposed_structures = gpd.sjoin(infra_gdf_clean, critical_buffers, how="inner", predicate="intersects")
except TypeError:
    exposed_structures = gpd.sjoin(infra_gdf_clean, critical_buffers, how="inner", op="intersects")

# Drop any duplicate structural entries if multiple points hit the same building
exposed_structures = exposed_structures.loc[~exposed_structures.index.duplicated(keep='first')]

print("5. Saving layers for your interactive Kepler.gl map...")
# Save the complete background infrastructure layer
infra_gdf_clean.to_file("riverbank_infrastructure_all.gpkg", driver="GPKG")

# Save the subset of structural elements that are actively at risk
exposed_structures.to_file("exposed_structures_at_risk.gpkg", driver="GPKG")

print("\n--- INFRASTRUCTURE ASSESSMENT SUMMARY ---")
print(f"Total structures mapped along the Po riverbank: {len(infra_gdf_clean)}")
print(f"Structures directly intersected by an active deformation cluster: {len(exposed_structures)}")
print("Success! Both GeoPackages are ready. Time to match them against the ISPRA PAI maps.")
