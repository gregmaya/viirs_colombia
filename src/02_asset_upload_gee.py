# %%
import json
import os

import ee
import geemap
import geopandas as gpd

# %%
# Get credentials from environment variables
service_account = os.environ.get("EE_SERVICE_ACCOUNT")
key_file = "../../earthengineapikey.json"

# Check if the environment variables are set
if not service_account or not key_file:
    raise ValueError(
        "EE_SERVICE_ACCOUNT and key_file(.json) environment variables must be set."
    )

# Authenticate and initialize the Earth Engine API
credentials = ee.ServiceAccountCredentials(service_account, key_file)
ee.Initialize(credentials)
print("Earth Engine API initialized successfully.")

# %%
# Load the GeoJSON file
geojson_path = "../data/gee_assets/municipios_mgn2018_selected.geojson"
gdf = gpd.read_file(geojson_path)

# filtering to only selected municipios to reduce capacity in GEE
gdf = gdf[gdf["selected_mun"]]

# %%
# Convert to GeoJSON dict
geojson_dict = json.loads(gdf.to_json())


# Function to batch the GeoJSON features
def batch_geojson_features(geojson_dict, batch_size=250):
    features = geojson_dict["features"]
    for i in range(0, len(features), batch_size):
        yield features[i : i + batch_size]


# Create an empty list to store the batched FeatureCollections
ee_fc_list = []
# Batch the features and convert each batch to an Earth Engine FeatureCollection
for i, batch in enumerate(batch_geojson_features(geojson_dict)):
    print(f"Processing batch {i + 1}")
    batch_geojson_dict = {"type": "FeatureCollection", "features": batch}
    ee_fc_batch = geemap.geojson_to_ee(batch_geojson_dict)
    ee_fc_list.append(ee_fc_batch)
    print(f"Batch {i + 1} processed successfully")

# Combine all the batched FeatureCollections into a single FeatureCollection
print("Combining all batches into a single FeatureCollection")
ee_fc = ee.FeatureCollection(ee_fc_list).flatten()
print("FeatureCollection combined successfully")

# %% ----- EXPORT TO GEE -----
# Create a task to export
task = ee.batch.Export.table.toAsset(
    collection=ee_fc,
    description="my_geojson_upload",
    assetId="projects/small-towns-col/assets/municipios_mgn2018_selected",
)

# Start the task
task.start()

# %%# %%
