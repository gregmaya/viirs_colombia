# %%
import ee
import geemap

# %%
service_account = "pythoneeapi@small-towns-col.iam.gserviceaccount.com"
key_file = "../earthengineapikey.json"

# Authenticate and initialize the Earth Engine API
try:
    credentials = ee.ServiceAccountCredentials(service_account, key_file)
    ee.Initialize(credentials)
    print("Earth Engine API initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Earth Engine API: {e}")

# %%
# Load the asset from GEE
try:
    mpios = ee.FeatureCollection("projects/small-towns-col/assets/municipios_col")
    print("FeatureCollection loaded successfully.")
except Exception as e:
    print(f"Failed to load FeatureCollection: {e}")

# %%
# Filter based on 'selected_m' property
try:
    selected_mpios = mpios.filter(ee.Filter.eq("selected_m", True))
    print("FeatureCollection filtered successfully.")
except Exception as e:
    print(f"Failed to filter FeatureCollection: {e}")

# create a bounding box for the selected municipios
bbox = selected_mpios.bounds()
print("Bounding box created successfully.")
print(bbox.getInfo())

# %%
try:
    # load nightlights data 2022
    dataset = ee.ImageCollection("NOAA/VIIRS/DNB/ANNUAL_V22").filter(
        ee.Filter.date("2022-01-01", "2023-01-01")
    )
    print("Nightlights data loaded successfully.")
except Exception as e:
    print(f"Failed to load nightlights data: {e}")

nighttime = dataset.select("median_masked")
# clipping because filterBounds() does not work
# only selecting the first as the image collection for a single yer has only one image
nighttime_clipped = nighttime.first().clip(bbox)
nighttimeVis = {min: 1.0, max: 50.0}

# %% ----- MAPPING -----
try:
    Map = geemap.Map()
    Map.centerObject(bbox)
    Map.addLayer(nighttime_clipped, nighttimeVis, "nightlights 2022 - VIIRS")
    # colour bounfing box red
    Map.addLayer(bbox, {"color": "red"}, "Bounding box")
    print("Map created successfully.")
except Exception as e:
    print(f"Failed to create map: {e}")
# %%
