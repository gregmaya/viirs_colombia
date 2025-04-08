# %%
import geopandas as gpd
import pandas as pd

# %%
# load files into dataframes
df = pd.read_csv("../data/municipios_sel.csv")
print(f"Loaded : {len(df)} municipios to select")

# load respective shapefile into geodataframe

gdf = gpd.read_file("../data/mpio_politico2018_dane/MGN_MPIO_POLITICO.shp")
print(f"Loaded : {len(gdf)} rows fro municipios in Colombia. CRS : {gdf.crs}")
# gdf = gpd.read_file("../data/mpio_politico2023_dane/MGN_URB_ZONA_URBANA.shp")
# print(f"Loaded : {len(gdf)} zonas urbanas en Colombia. CRS : {gdf.crs}")

gdf.plot()
# %%
# lowercase columnd
gdf.columns = gdf.columns.str.lower()
# Identify unique ID column
uid = "mpio_ccnct"

# Ensure the uid column is of type int
gdf[uid] = gdf[uid].astype(int)

if gdf[uid].is_unique:
    print(f"{gdf[uid].nunique()} unique values")
else:
    # Group geometries into multipolygons
    gdf = gdf.dissolve(by=uid, as_index=False)
    print(f"{gdf[uid].nunique()} unique values after dissolving")

# new masking col 'selected_mun' in gdf
gdf["selected_mun"] = gdf[uid].isin(df["ID"])
# print how many municipios were selected
print(f"{gdf['selected_mun'].sum()} municipios were selected")
# plot gdf with selected_mun mask
gdf.plot(column="selected_mun", legend=True)

# %%
# change crs to metric UTM for Colombia
gdf = gdf.to_crs("EPSG:21818")
print("Reprojected to EPSG:21818")

# simplyfy geometries retaining topology with tolerance 10m
gdf["geometry"] = gdf.simplify(tolerance=10, preserve_topology=True)

# checking for valid geometries
if gdf.is_valid.all():
    print("All geometries are valid")
else:
    print("Some geometries are invalid")

# %%
gdf = gdf.to_crs("EPSG:4326")
print("Reprojected to EPSG:4326")

# export shapefile in crs 4326 for Google Earth engine
filepath = "../data/gee_assets/municipios_mgn2018_selected.shp"
gdf.to_file(filepath, driver="ESRI Shapefile")
print(f"Exported to {filepath}")
# %%
