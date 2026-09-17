import json, pandas as pd

input_file = "../data/bronze/weather_raw.json"

print(input_file)

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} cities from bronze.")

rows = []

for city in data:

    daily = city["weather"]["daily"]

    for i in range(len(daily["time"])):
        row = {
            "city": city["city"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "date": daily["time"][i],
            "temperature_max": daily["temperature_2m_max"][i],
            "temperature_min": daily["temperature_2m_min"][i],
            "precipitation_sum": daily["precipitation_sum"][i],
            "precipitation_probability_max": daily["precipitation_probability_max"][i],
            "wind_speed_max": daily["wind_speed_10m_max"][i],
            "wind_gusts_max": daily["wind_gusts_10m_max"][i],
            "weather_code": daily["weather_code"][i],
        }

        rows.append(row)

print(f"Created {len(rows)} weather records")

# Turn rows into a data frame
df = pd.DataFrame(rows)

# Standardize data types
df["date"] = pd.to_datetime(df["date"]) 
df["latitude"] = pd.to_numeric(df["latitude"])
df["longitude"] = pd.to_numeric(df["longitude"])
df["temperature_max"] = pd.to_numeric(df["temperature_max"])
df["temperature_min"] = pd.to_numeric(df["temperature_min"])
df["precipitation_sum"] = pd.to_numeric(df["precipitation_sum"])
df["precipitation_probability_max"] = pd.to_numeric(df["precipitation_probability_max"])
df["wind_speed_max"] = pd.to_numeric(df["wind_speed_max"])
df["wind_gusts_max"] = pd.to_numeric(df["wind_gusts_max"])
df["weather_code"] = pd.to_numeric(df["weather_code"])


# Check for missing values
missing_values = df.isna().sum()

print(f"Missing values: {missing_values}")

# Check for duplicates
duplicates = df.duplicated().sum()

print(f"Duplicate records: {duplicates}")

# Check for invalid data chunks

invalid_records = []

for row in rows:
    if row["temperature_max"] < row["temperature_min"]:
        invalid_records.append((row["city"], row["date"], "temperature"))

    if row["precipitation_sum"] < 0:
        invalid_records.append((row["city"], row["date"], "precipitation"))

    if row["wind_speed_max"] < 0:
        invalid_records.append((row["city"], row["date"], "wind_speed"))

    if row["wind_gusts_max"] < 0:
        invalid_records.append((row["city"], row["date"], "wind_gusts"))

    if not -90 <= row["latitude"] <= 90:
        invalid_records.append((row["city"], row["date"], "latitude"))

    if not -180 <= row["longitude"] <= 180:
        invalid_records.append((row["city"], row["date"], "longitude"))

print(f"{len(invalid_records)} invalid data chunks were found! {invalid_records}")

# Load original cities data

cities_file = "../data/bronze/simplemaps_cities.csv"

cities = pd.read_csv(cities_file)

# keep only the columns we need

cities =  cities[["city", "lat", "lng"]]

# Rename columns to match the weather data

cities = cities.rename(columns={
    "lat": "latitude",
    "lng": "longitude"
})

# Merge weather with cities 

merged = df.merge(
    cities,
    on="city",
    how="left",
    suffixes=("_weather", "_cities")
)

# Check coordinate differences
coordinate_mismatch = (
    (merged["latitude_weather"] != merged["latitude_cities"])
    | (merged["longitude_weather"] != merged["longitude_weather"])
)

print(f"City coordinate mismatches: {coordinate_mismatch.sum()}")

# extract only the columns demanded

merged = merged.rename(columns={
    "latitude_weather": "latitude",
    "longitude_weather": "longitude"
})

silver_columns = [
    "city", 
    "latitude",
    "longitude",
    "date",
    "temperature_max",
    "temperature_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_max",
    "wind_gusts_max",
    "weather_code"
]

silver_df = merged[silver_columns].copy()

output_file = "../data/silver/weather_silver.parquet"

silver_df["date"] = silver_df["date"].dt.strftime("%Y-%m-%d")

silver_df.to_parquet(output_file, index=False)

print(f"Silver Data saved to {output_file}")
print(f"Silver records: {len(silver_df)}")
print(f"Silver columns: {len(silver_df.columns)}")

# python -c "import pyarrow.parquet as pq; print(pq.read_table('../data/silver/weather_silver.parquet').slice(0, 5).to_pandas())"