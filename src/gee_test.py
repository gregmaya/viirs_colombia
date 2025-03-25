# %%
import ee
import geemap

# %%
service_account = "pythoneeapi@small-towns-col.iam.gserviceaccount.com"
key_file = "../earthengineapikey.json"

# Authenticate and initialize the Earth Engine API
credentials = ee.ServiceAccountCredentials(service_account, key_file)
ee.Initialize(credentials)
print("Earth Engine API initialized successfully.")

# %%
# Load the asset from GEE
mpios = ee.FeatureCollection("projects/small-towns-col/assets/col_mpios_sel_simpl10")
print("FeatureCollection loaded successfully.")

# %%
# Filter based on 'selected_m' property
selected_mpios = mpios.filter(ee.Filter.eq("selected_m", "T"))
print("FeatureCollection filtered successfully.")

# create a bounding box for the selected municipios
bbox = selected_mpios.geometry().bounds()
print("Bounding box created successfully.")
print(bbox.getInfo())

# %%
# load nightlights data 2022
dataset = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22").filterDate(
    "2022-01-01", "2023-01-01"
)
print("Nightlights data loaded successfully.")

nighttime = dataset.select("median_masked")
# only selecting the first as the image collection for a single year has only one image
nighttime_clipped = nighttime.first().clip(bbox)
nighttimeVis = {"min": 1.0, "max": 50.0, "gamma": 2.3}

# %% ----- MAPPING -----
Map = geemap.Map()
Map.add_basemap("CartoDB.PositronNoLabels")  # Set the basemap to Positron No Labels
Map.centerObject(bbox)
Map.addLayer(nighttime_clipped, nighttimeVis, "nightlights 2022 - VIIRS")

# style for selected_mpios
styled = selected_mpios.style(**{"color": "white", "fillColor": "grey", "width": 0.3})
Map.addLayer(styled, {"opacity": 0.2}, "Selected municipios styled")

Map

# %%
 