import geopandas as gpd

print("1. Loading original layers...")
hotspots = gpd.read_file("riverbank_hotspots.gpkg")
infra = gpd.read_file("riverbank_infrastructure_all.gpkg")

print("2. THE CRITICAL FIX: Converting coordinates to Web/GPS format (EPSG:4326)...")
# This is what Kepler needs to actually see the data on the globe
hotspots_4326 = hotspots.to_crs(epsg=4326)
infra_4326 = infra.to_crs(epsg=4326)

print("3. Exporting Hotspots...")
hotspots_4326.to_file("riverbank_hotspots_web.geojson", driver="GeoJSON")

print("4. Isolating and exporting Buildings (Polygons)...")
buildings = infra_4326[infra_4326.geometry.type.isin(['Polygon', 'MultiPolygon'])].copy()
buildings['geometry'] = buildings.geometry.make_valid()
buildings = buildings[~buildings.geometry.is_empty & buildings.geometry.notnull()]
# Keeping only the geometry to prevent any nested-data crashes
buildings_nuclear = buildings[['geometry']].copy()
buildings_nuclear.to_file("riverbank_buildings_web.geojson", driver="GeoJSON")

print("5. Isolating and exporting Lines (Bridges/Walls)...")
lines = infra_4326[infra_4326.geometry.type.isin(['LineString', 'MultiLineString'])].copy()
lines['geometry'] = lines.geometry.make_valid()
lines = lines[~lines.geometry.is_empty & lines.geometry.notnull()]
# Keeping only the geometry
lines_nuclear = lines[['geometry']].copy()
lines_nuclear.to_file("riverbank_lines_web.geojson", driver="GeoJSON")

print("\nSuccess! Your data is now perfectly formatted for Kepler.gl.")