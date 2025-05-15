# %%
import os

import ee
import geemap

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
# Load the asset from GEE - 'NOT zonas urbanas'
zrural = ee.FeatureCollection(
    "projects/small-towns-col/assets/mun2018_nocabeceras_simpl10"
)
print("Zonas rurales: loaded successfully.")

# %%
# %%
# load nightlights data
# V1 for the 2016 - 2021 period
# V2 for the 2022 - 2024 period
dataset1 = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V21").filterDate(
    "2016-01-01", "2021-12-31"
)
dataset2 = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22").filterDate(
    "2022-01-01", "2025-01-01"
)


# %%
# Function to extract the year from the 'system:time_start' property
def extract_year(image):
    date = ee.Date(image.get("system:time_start"))
    year = date.get("year")
    return image.set("year", year)


# Map the function over both datasets
dataset1_with_year = dataset1.map(extract_year)
dataset2_with_year = dataset2.map(extract_year)

# Merge both datasets
merged_dataset = dataset1_with_year.merge(dataset2_with_year)

# Get the list of years from the merged dataset
years = merged_dataset.aggregate_array("year").getInfo()

# Print the years
print("Years of resulting images:", years)


# %% --zonal statistics __
def zonal_stats_per_image(img):
    date_str = img.date().format("YYYYMMdd")
    stats = img.reduceRegions(
        collection=zrural,
        reducer=ee.Reducer.mean()
        .combine(ee.Reducer.min(), sharedInputs=True)
        .combine(ee.Reducer.max(), sharedInputs=True)
        .combine(ee.Reducer.stdDev(), sharedInputs=True),
        scale=480,
    )
    # Add image date as a property to all features
    stats = stats.map(lambda f: f.set("image_date", date_str))
    return stats


# Apply to every image and flatten
stats_collection = merged_dataset.map(zonal_stats_per_image).flatten()

# %%
mun_stats_df = geemap.ee_to_df(stats_collection)
print(mun_stats_df.head())

# %%
# Export to CSV
export_path = "../../data/outputs/mun_nocabeceras_stats_raw_2.csv"
mun_stats_df.to_csv(export_path, index=False)
print(f"Exported zonal stats to {export_path}")
# %%
# %%
