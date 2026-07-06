import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point

# --- A. Define the River Corridor Buffer ---
print("1. Fetching the Po river geometry from OpenStreetMap...")
# We use 'features_from_place' (or geometries_from_place for older OSMnx versions)
try:
    river_gdf = ox.features_from_place("Turin, Italy", tags={"waterway": "river", "name": ["Po", "Fiume Po"]})
except AttributeError:
    river_gdf = ox.geometries_from_place("Turin, Italy", tags={"waterway": "river", "name": ["Po", "Fiume Po"]})

# EGMS L3 data is typically in EPSG:3035 (LAEA Europe). 
# We must reproject our OSM river data to match before doing distance calculations.
river_gdf_3035 = river_gdf.to_crs(epsg=3035)

print("2. Creating a 250-meter spatial buffer along the river...")
# Merge all river segments into one single continuous geometry
river_geometry = river_gdf_3035.union_all()

# Buffer outward by 250 meters (EPSG:3035 uses meters as its unit)
# You can adjust this number up or down depending on how far inland you want to look.
buffer_distance_m = 250
corridor_polygon = river_geometry.buffer(buffer_distance_m)

# Create a GeoDataFrame from our new buffer polygon
aoi_gdf_3035 = gpd.GeoDataFrame(geometry=[corridor_polygon], crs="EPSG:3035")

# Get bounding box of this buffer to use as a fast pre-filter for the CSV
minx, miny, maxx, maxy = aoi_gdf_3035.total_bounds


# --- B. Chunk and Filter the Massive CSV ---
print("3. Bounding box established. Filtering EGMS data (this may take a minute)...")

# MAKE SURE THIS FILENAME MATCHES YOUR EXTRACTED CSV EXACTLY
csv_file = 'EGMS_L3_E41N24_100km_U_2019_2023_1.csv' 
chunk_size = 1000000  # Read 1 million rows at a time
filtered_chunks = []

for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
    in_bbox = chunk[
        (chunk['easting'] >= minx) & 
        (chunk['easting'] <= maxx) & 
        (chunk['northing'] >= miny) & 
        (chunk['northing'] <= maxy)
    ]
    filtered_chunks.append(in_bbox)

# Stitch the surviving bounding-box points back together
df_corridor = pd.concat(filtered_chunks)


# --- C. Precise Spatial Clip and Export ---
print(f"4. Converting {len(df_corridor)} points into spatial geometries...")
geometry = [Point(xy) for xy in zip(df_corridor['easting'], df_corridor['northing'])]
gdf_points = gpd.GeoDataFrame(df_corridor, crs="EPSG:3035", geometry=geometry)

print("5. Clipping points precisely to the 250m riverbank corridor...")
# This removes any points that fell inside the rectangular bounding box 
# but outside our curved river buffer.
gdf_clipped = gpd.clip(gdf_points, aoi_gdf_3035)

print("6. Saving final output to GeoPackage...")
# Save out to a GeoPackage for your upcoming Getis-Ord Gi* hotspot analysis
gdf_clipped.to_file("riverbank_deformation_E_2019_2023.gpkg", driver="GPKG")

print(f"Success! {len(gdf_clipped)} points saved securely to your project folder.")