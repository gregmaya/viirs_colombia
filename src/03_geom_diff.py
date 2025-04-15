"""
creating a geometry og the difference between the municipio and the cabecera
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# %%
# Load data
muns = gpd.read_file(
    "../../data/gee_assets/mun2018_simpl10/municipios_mgn2018_selected.shp"
)
print(f"Municipios: {len(muns)} municipios en Colombia. CRS : {muns.crs}")

cabs = gpd.read_file("../../data/mpio_politico2023_dane/MGN_URB_ZONA_URBANA.shp")
print(f"Cabeceras: {len(cabs)} cabeceras en Colombia. CRS : {cabs.crs}")
# %%
WORKING_CRS = "EPSG:4326"
muns = muns.to_crs(WORKING_CRS)
cabs = cabs.to_crs(WORKING_CRS)

# filter to only the seleceted municipios
muns = muns[muns["selected_m"] == True]
print(f"Filtered municipios: {len(muns)} municipios en Colombia. CRS : {muns.crs}")

# changing cabs.mpio_cdpmp to int
cabs["mpio_cdpmp"] = cabs["mpio_cdpmp"].astype(int)
# filtering to only the cabeceras. clas_ccdgo == 1
cabs_only = cabs[cabs["clas_ccdgo"] == "1"]
print(f"Filtered cabeceras: {len(cabs)} cabeceras en Colombia. CRS : {cabs.crs}")

# joining the cabs geometry to the muns gdf
muns_merged = muns.merge(
    cabs_only[["mpio_cdpmp", "geometry"]],
    how="left",
    left_on="mpio_ccnct",
    right_on="mpio_cdpmp",
)

muns_merged.head()
# %%
# create a diff_geom from geometry_x and geometry_y
# the diff_geom is the geometry of the mun minus the geometry of the cabecera
muns_merged["geom"] = muns_merged.apply(
    lambda row: row["geometry_x"].difference(row["geometry_y"])
    if row["geometry_y"] is not None
    else row["geometry_x"],
    axis=1,
)
muns_merged.set_geometry("geom", inplace=True)
# %%
# plot that geom on map
# only ANTIOQUIA
mask = muns_merged["dpto_cnmbr"] == "ANTIOQUIA"
fig, ax = plt.subplots(figsize=(10, 10))
muns_merged[mask].plot(ax=ax, color="blue")
plt.title("Municipios and Cabeceras in Antioquia")
plt.show()
# %%
# check for invalid geometries in geom
mask = muns_merged["geom"].is_valid
len(muns_merged[~mask])
# %%
keep_cols = ["mpio_ccnct", "mpio_cnmbr", "dpto_cnmbr", "geom"]
# keep only the selected columns
muns_diff_cabs = muns_merged[keep_cols]
muns_diff_cabs.set_crs(WORKING_CRS, inplace=True)
# simplify geometry
# UTM CRS to meters 10m
muns_diff_cabs = muns_diff_cabs.to_crs("EPSG:21818")
muns_diff_cabs["geom"] = muns_diff_cabs["geom"].simplify(10, preserve_topology=True)


# %%
# for the multigeometries, drop the individual polygons that are smaller than 500sqm
# this is a workaround for the simplification
muns_diff_cabs = muns_diff_cabs.explode()
muns_diff_cabs["area"] = muns_diff_cabs["geom"].area
# extract only the largest area per mpio_ccnct
# create a series per group of the largest area
largest_areas = muns_diff_cabs.groupby("mpio_ccnct")["area"].max()
# inf gdf compare area to largets area per mpio_ccnct
muns_diff_cabs_maxareas = muns_diff_cabs[
    muns_diff_cabs["area"] == muns_diff_cabs["mpio_ccnct"].map(largest_areas)
]

len(muns_diff_cabs_maxareas)


# %%
# difference muns_diff_cabs_maxareas to muns_diff_cabs to investigate the small areas
muns_diff_cabs_smallareas = muns_diff_cabs[
    ~muns_diff_cabs.area.isin(muns_diff_cabs_maxareas.area)
]
print(f"Small areas: {len(muns_diff_cabs_smallareas)}")

# histogram of the small areas
ax = muns_diff_cabs_smallareas["area"].hist(bins=20)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.title("Histogram of small areas")
plt.xlabel("Area")
plt.ylabel("Frequency")
plt.show()

# %%
threshold = 60000
# create a table with the histogram bins
hist, bin_edges = np.histogram(
    muns_diff_cabs_smallareas[muns_diff_cabs_smallareas["area"] < threshold]["area"],
    bins=20,
)
hist_df = pd.DataFrame({"bin_min": bin_edges[:-1], "frequency": hist})
hist_df["bin_min"] = hist_df["bin_min"].apply(lambda x: f"{x:,.0f}")
hist_df["frequency"] = hist_df["frequency"].apply(lambda x: f"{x:,.0f}")
hist_df
# %%
ax = muns_diff_cabs_smallareas[muns_diff_cabs_smallareas["area"] < threshold][
    "area"
].hist(bins=20)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.title("Histogram of small areas")
plt.xlabel("Area")
plt.ylabel("Frequency")
plt.show()
print(
    f"Small areas (below {threshold} sqm): {len(muns_diff_cabs_smallareas[muns_diff_cabs_smallareas['area'] < threshold])}"
)

# %%
# filter out the small areas
muns_diff_cabs = muns_diff_cabs[muns_diff_cabs["area"] > threshold]
print(f"Remaining polygons: {len(muns_diff_cabs)}")
print(f"Ratio of the 698 polygons: {len(muns_diff_cabs) / 698}")

# group gdf by mpio_ccnct and merge the geometries
muns_diff_cabs = muns_diff_cabs.dissolve(by="mpio_ccnct", as_index=False)
# number of multipolygons
num_mutipol = len(muns_diff_cabs[muns_diff_cabs.geom_type == "MultiPolygon"])
print(f"Number of multipolygons: {num_mutipol}")

# CRS back to WGS84
muns_diff_cabs = muns_diff_cabs.to_crs(WORKING_CRS)

# save to file
# muns_diff_cabs.to_file("../../data/gee_assets/mun_diff_cab_simpl10.shp")
print("Saved to file: ../../data/gee_assets/mun_diff_cab_simpl10.shp")
# %%
