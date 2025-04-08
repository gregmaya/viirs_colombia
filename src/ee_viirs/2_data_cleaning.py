# %%
import itertools

import pandas as pd

# %%
# Read the data
mun_stats_df = pd.read_csv("../../data/outputs/mun_stats_raw_2.csv")
print("Number of rows:", mun_stats_df.shape[0])
print("Number of columns:", mun_stats_df.shape[1])
print("Columns:", mun_stats_df.columns)
# Display the first few rows
mun_stats_df.head()
# %%
# indexing per mpio_ccnct and image_date
mun_stats_df.set_index(["mpio_ccnct", "image_date"], inplace=True)

# %%
# Lists of bands and calculated stats
bands = [
    "average",
    "average_masked",
    "cf_cvg", #Cloud-free coverages; the total number of observations that went into each pixel. This band can be used to identify areas with low numbers of observations where the quality is reduced.
    "cvg", #Total number of observations free of sunlight and moonlight.
    "maximum",
    "median",
    "median_masked",
    "minimum",
]
calculted_stats = ["mean", "min", "max", "stdDev"]

# Generate the Cartesian product
combined_columns = [
    f"{band}_{stat}" for band, stat in itertools.product(bands, calculted_stats)
]
# adding extra col to be able to identify munucupios with multipolygons
extra_col = "shape_area" # "mpio_narea"
combined_columns = [extra_col] + combined_columns
# Print the result
print(combined_columns)
# %%
# Create a new DataFrame with the combined columns
mun_stats_cl = mun_stats_df[combined_columns].copy()  
mun_stats_cl.reset_index(inplace=True)
#create year column
mun_stats_cl["year"] = mun_stats_cl["image_date"].astype(str).str[:4].astype(int)
# remove image_date column
mun_stats_cl.drop(columns=["image_date"], inplace=True)
mun_stats_cl.tail()
# %%
#Export to CSV
export_path = "../../data/outputs/mun_stats_clean_2.csv"
mun_stats_cl.to_csv(export_path, index=False)
print(f"Exported zonal stats to {export_path}")

# %%
