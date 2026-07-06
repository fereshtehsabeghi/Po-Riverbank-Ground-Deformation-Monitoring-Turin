import geopandas as gpd
import glob
import os

print("1. Loading our active hotspots to set the spatial boundary...")
hotspots = gpd.read_file("riverbank_hotspots.gpkg")
hotspots_4326 = hotspots.to_crs(epsg=4326)

print("2. Building the Turin River Corridor Bounding Box...")
bounds = hotspots_4326.geometry.total_bounds
minx, miny, maxx, maxy = bounds

bounding_box = gpd.GeoDataFrame(
    {"geometry": gpd.GeoSeries.from_wkt([f"POLYGON (({minx} {miny}, {maxx} {miny}, {maxx} {maxy}, {minx} {maxy}, {minx} {miny}))"])}, 
    crs="EPSG:4326"
)

print("3. Auto-searching for ISPRA shapefiles in your folders...")
folders_to_check = ["ISPRA2020", "ISPRA2024"]
shapefiles_found = []

# This loop digs into the folders and finds the exact .shp files for you
for folder in folders_to_check:
    files = glob.glob(f"{folder}/**/*.shp", recursive=True)
    shapefiles_found.extend(files)

if not shapefiles_found:
    print("Error: Could not find any .shp files! Make sure you unzipped the ISPRA files into these folders.")
else:
    print(f"   -> Found {len(shapefiles_found)} official hazard maps. Beginning clip process...\n")
    
    for shp_file in shapefiles_found:
        print(f"--- Processing: {shp_file} ---")
        try:
            # Load the government map and fix coordinates
            hazard_gdf = gpd.read_file(shp_file)
            hazard_gdf = hazard_gdf.to_crs(epsg=4326)
            
            # Clip the massive map down to just our small Turin study area
            local_hazard = gpd.clip(hazard_gdf, bounding_box)
            
            if local_hazard.empty:
                print("   -> Result: No hazard zones touch our specific river corridor in this file.")
            else:
                print(f"   -> Result: Retained {len(local_hazard)} hazard zones!")
                
                # Automatically name the output file based on the original ISPRA name
                base_name = os.path.basename(shp_file).replace('.shp', '')
                export_name = f"{base_name}_web.geojson"
                
                local_hazard.to_file(export_name, driver="GeoJSON")
                print(f"   -> Successfully saved as: {export_name}")
                
        except Exception as e:
            print(f"   -> Error processing {shp_file}: {e}")

print("\nSuccess! Drag any newly created _web.geojson files directly into Kepler.gl.")