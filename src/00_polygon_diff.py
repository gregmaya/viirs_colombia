# Hypothesis: DANE produced MGN polygons for the yesrs 2005, 2018, 2021, 2022 and 2023.
# Will there be significant changes in the selected municipios for the years 2018 and 2023?

# %%
import geopandas as gpd
import pandas as pd

import matplotlib.pyplot as plt
# %%
# Load data
df = pd.read_csv("./data/municipios_sel.csv")
gdf_2018 = gpd.read_file("./data/mpio_politico2018_dane/MGN_MPIO_POLITICO.shp")
gdf_2023 = gpd.read_file("./data/mpio_politico2023_dane/MGN_ADM_MPIO_GRAFICO.shp")

print(f"DANE MGN 2018: {len(gdf_2018)} municipios en Colombia. CRS : {gdf_2018.crs}")
print(f"DANE MGN 2023: {len(gdf_2023)} municipios en Colombia. CRS : {gdf_2023.crs}")
# %%
# Lowercase all column names
gdf_lst = [gdf_2018, gdf_2023]
for gdf in gdf_lst:
    gdf.columns = gdf.columns.str.lower()

# Print column names to verify
print("Columns in gdf_2018:", gdf_2018.columns)
print("Columns in gdf_2023:", gdf_2023.columns)
# %%
# Identify unique ID column in each GeoDataFrame
uid_2018 = "mpio_ccnct"
uid_2023 = "mpio_cdpmp"


# Function to homogenize IDs and geometries
def homogenize_gdf(gdf, uid, crs="EPSG:4686"):
    # Ensure the uid column exists
    if uid not in gdf.columns:
        raise KeyError(f"Column '{uid}' not found in GeoDataFrame")

    # Ensure the uid column is of type int
    gdf[uid] = gdf[uid].astype(int)

    if gdf[uid].is_unique:
        print(f"{gdf[uid].nunique()} unique values")
    else:
        print(f"{gdf[uid].nunique()} non-unique values")
        # Group geometries into multipolygons
        gdf = gdf.dissolve(by=uid, as_index=False)
        print(f"{gdf[uid].nunique()} unique values after dissolving")

    # Check CRS and change if not equal to the specified CRS
    if gdf.crs != crs:
        print(f"Changing CRS from {gdf.crs} to {crs}")
        gdf = gdf.to_crs(crs)
    else:
        print(f"CRS is already {crs}")

    return gdf

# Homogenize GeoDataFrames
gdf_2018 = homogenize_gdf(gdf_2018, uid_2018)
gdf_2023 = homogenize_gdf(gdf_2023, uid_2023)

# %%
# in df,lowecase cols and made 'id'
df.columns = df.columns.str.lower()

# new masking col in gdfs
gdf_2018['selected_mun'] = gdf_2018[uid_2018].isin(df["id"])
gdf_2023['selected_mun'] = gdf_2023[uid_2023].isin(df["id"])

print(f"{gdf_2018['selected_mun'].sum()} municipios were selected")
print(f"{gdf_2023['selected_mun'].sum()} municipios were selected")
# %%
# calculate the area and perimeter
gdf_2018['area'] = gdf_2018.area
gdf_2023['area'] = gdf_2023.area    

# Set the unique ID columns as the index
gdf_2018.set_index(uid_2018, inplace=True)
gdf_2023.set_index(uid_2023, inplace=True)

# join into a singel gdf only the selected municipios
gdf_diff = gdf_2018.merge(gdf_2023, 
                          left_index=True, 
                          right_index=True, 
                          how='outer', 
                          suffixes=('_2018', '_2023'))

gdf_diff = gdf_diff[gdf_diff['selected_mun_2018'] | gdf_diff['selected_mun_2023']]
# %%
# calculate the difference in area and perimeter
gdf_diff['area_diff'] = gdf_diff['area_2023'] - gdf_diff['area_2018']
gdf_diff['area_diff_pct'] = gdf_diff['area_diff'] / gdf_diff['area_2018']

equal_area = gdf_diff['area_diff'].abs() < 1e-6
print(f"{equal_area.sum()} municipios had no relevant change in area")

# %%
# set geometry to gdf_diff
gdf_diff = gpd.GeoDataFrame(gdf_diff, geometry='geometry_2018')
#plot the difference in area
gdf_diff.plot(column='area_diff_pct', legend=True)


# %%
#establish a +/- % threshold for significant changes
threshold = 0.05
significant_changes = gdf_diff[abs(gdf_diff['area_diff_pct']) > threshold]

print(f"{len(significant_changes)} municipios had +/- {threshold*100} % significant changes in area")
significant_changes.plot(column='area_diff_pct', legend=True)

# calculate the absolute change
significant_changes['area_diff_abs'] = significant_changes['area_diff'].abs()

# horizontal bar plot of the significant changes 
significant_changes.sort_values('area_diff_abs').plot.barh(x='mpio_cnmbr_2018', y='area_diff_pct')

# %%
#plot the significant changes with both geometries. the 2023 only outline in red
fig, ax = plt.subplots()
gdf_2018.plot(ax=ax, color='grey')
significant_changes.plot(ax=ax, color='red', edgecolor='black')
plt.show()
# %%
# %%
# Create clusters of touching geometries

# Function to create clusters of touching geometries
def create_clusters(gdf, geometry_column='geometry'):
    clusters = []
    used = set()
    
    for idx, geom in gdf[geometry_column].items():
        if idx in used:
            continue
        cluster = [idx]
        used.add(idx)
        for other_idx, other_geom in gdf[geometry_column].items():
            if other_idx in used:
                continue
            if geom.touches(other_geom) or geom.intersects(other_geom):
                cluster.append(other_idx)
                used.add(other_idx)
        clusters.append(cluster)
    
    return clusters

# Create clusters for significant changes
clusters = create_clusters(significant_changes, geometry_column='geometry_2018')

# Plot each cluster individually
for i, cluster in enumerate(clusters):
    cluster_gdf = significant_changes.loc[cluster]
    fig, ax = plt.subplots()
    cluster_gdf.set_geometry('geometry_2018').plot(ax=ax, color='grey', edgecolor='black', alpha=0.5)
    cluster_gdf.set_geometry('geometry_2023').plot(ax=ax, color='none', edgecolor='red')
    plt.title(f"Cluster {i+1}: {', '.join(cluster_gdf['mpio_cnmbr_2018'].unique())}")
    plt.show()
# %%
