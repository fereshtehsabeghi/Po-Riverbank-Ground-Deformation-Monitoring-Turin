import geopandas as gpd

print("1. Converting hotspot points to GeoJSON...")
# Load your hotspot points and export
hotspots = gpd.read_file("riverbank_hotspots.gpkg")
hotspots.to_file("riverbank_hotspots.geojson", driver="GeoJSON")

print("2. Converting all infrastructure polygons to GeoJSON...")
# Load your 7,680 background structures and export
infra = gpd.read_file("riverbank_infrastructure_all.gpkg")
infra.to_file("riverbank_infrastructure_all.geojson", driver="GeoJSON")

print("\nSuccess! Your layers are converted:")
print(" -> riverbank_hotspots.geojson")
print(" -> riverbank_infrastructure_all.geojson")
print("You can now drag and drop these directly into Kepler.gl!")