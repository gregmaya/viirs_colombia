# %%
import itertools

import pandas as pd

# %%
mgn_detail = "mun_nocabeceras"  # ['mun', 'cabeceras', 'mun_nocabeceras']
version = "2"

# Read the data
stats_df = pd.read_csv(f"../../data/outputs/{mgn_detail}_stats_raw_{version}.csv")
print("Number of rows:", stats_df.shape[0])
print("Number of columns:", stats_df.shape[1])
# lowercase all columns
stats_df.columns = stats_df.columns.str.lower()

print("Columns:", stats_df.columns)
# Display the first few rows
stats_df.head()
# %%
# indexing based on mgn_detail
if mgn_detail == "mun" or mgn_detail == "mun_nocabeceras":
    # indexing per mpio_ccnct and image_date
    stats_df.set_index(["mpio_ccnct", "image_date"], inplace=True)
elif mgn_detail == "cabeceras":
    # indexing per cabecera and image_date
    stats_df.set_index(["clas_ccdgo", "mpio_cdpmp", "image_date"], inplace=True)
# worth notign that for cabeceras only the 2024 data is available
# there the code to indentify municipios chances label from mpio_ccnct (2018) to mpio_cdpmp (2023)
# %%
# Lists of bands and calculated stats
bands = [
    "average",
    "average_masked",
    "cf_cvg",  # Cloud-free coverages; the total number of observations that went into each pixel. This band can be used to identify areas with low numbers of observations where the quality is reduced.
    "cvg",  # Total number of observations free of sunlight and moonlight.
    "maximum",
    "median",
    "median_masked",
    "minimum",
]
calculted_stats = ["mean", "min", "max", "stddev"]

# Generate the Cartesian product
combined_columns = [
    f"{band}_{stat}" for band, stat in itertools.product(bands, calculted_stats)
]
# adding extra col to be able to identify munucupios with multipolygons
if mgn_detail == "mun" or mgn_detail == "cabeceras":
    extra_col = "shape_area"  # "mpio_narea"
    combined_columns = [extra_col] + combined_columns

# Print the result
print(combined_columns)
# %%
# Create a new DataFrame with the combined columns
stats_cl = stats_df[combined_columns].copy()
stats_cl.reset_index(inplace=True)
# create year column
stats_cl["year"] = stats_cl["image_date"].astype(str).str[:4].astype(int)
# remove image_date column
stats_cl.drop(columns=["image_date"], inplace=True)
stats_cl.tail()
# %%
# Export to CSV
export_path = f"../../data/outputs/{mgn_detail}_stats_clean_{version}.csv"
stats_cl.to_csv(export_path, index=False)
print(f"Exported zonal stats to {export_path}")

# %%
