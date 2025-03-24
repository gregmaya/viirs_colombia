# %%
import geopandas as gpd
import pandas as pd

# %%
# load files into dataframes
df = pd.read_csv("../data/municipios_sel.csv")
print(f"Loaded : {len(df)} municipios seleccionados")

# load respective shapefile into geodataframe
gdf = gpd.read_file("../data/mpio_politico2023_dane/MGN_ADM_MPIO_GRAFICO.shp")
print(f"Loaded : {len(gdf)} municipios en Colombia. CRS : {gdf.crs}")

gdf = gpd.read_file("../data/mpio_politico2023_dane/MGN_URB_ZONA_URBANA.shp")
print(f"Loaded : {len(gdf)} zonas urbanas en Colombia. CRS : {gdf.crs}")
gdf.plot()
# %%
# convert 'mpio_cdpmp' to int in gdf
gdf["mpio_cdpmp"] = gdf["mpio_cdpmp"].astype(int)

# new masking col 'selected_mun' in gdf
gdf["selected_mun"] = gdf["mpio_cdpmp"].isin(df["ID"])
# print howe many municipios were selected
print(f"{gdf['selected_mun'].sum()} municipios were selected")
# plot gdf with selected_mun mask
gdf.plot(column="selected_mun", legend=True)

# %%
# export shapefile in crs 4326 for Google Earth engine
filepath = "../data/mpios_selected/col_zon_urb_selected.shp"
gdf.to_crs(epsg=4326).to_file(filepath, driver="ESRI Shapefile")
# %%
