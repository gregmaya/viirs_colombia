"""
Trying to download street network connections from Overture API for all selected municipalities
"""

# %%
import geopandas as gpd
from overturemaps import core

# %%
bounds = gpd.read_file("../data/gee_assets/municipios_mgn2018_selected.geojson")
selected_bounds = bounds[bounds["selected_mun"]]

# bounds_geom_wgs = selected_bounds.to_crs(4326).union_all()
# bounds_geom_wgs

# selected the smallets municipality to test
xs_mask = selected_bounds["shape_area"] == selected_bounds["shape_area"].min()
muni = selected_bounds[xs_mask]
muni_geom = muni["geometry"].iloc[0]
muni_geom

# %%
# testing downloads. options "building", "infrastructure", "place", "connector", "segment"
gdf_dict = {}
overture_cats = ["infrastructure", "segment"]
for cat in overture_cats:
    print(f"Downloading {cat} data")
    gdf = core.geodataframe(cat, muni_geom.bounds)
    gdf.set_crs(4326, inplace=True)
    print(f"Downloaded {len(gdf)} rows")
    gdf_dict[cat] = gdf
    gdf.plot()

# %%
# export to geopackage with two different layers
gdf_dict["infrastructure"].to_file(
    "../data/tests/overture_sabaneta.gpkg", layer="infrastructure", driver="GPKG"
)
gdf_dict["segment"].to_file(
    "../data/tests/overture_sabaneta.gpkg", layer="segment", driver="GPKG"
)

# %%
"""
# %%
# set CRS
buildings_gdf.set_crs(4326, inplace=True)
buildings_gdf.to_crs(bounds.crs, inplace=True)
# set index
buildings_gdf.set_index("id", inplace=True)
# process as wanted
buildings_gdf.rename(columns={"geometry": "geom"}, inplace=True)
buildings_gdf.set_geometry("geom", inplace=True)
# drop columns that are not needed, e.g.
buildings_gdf.drop(columns=["bbox", "sources", "names"], inplace=True)
buildings_gdf
"""
