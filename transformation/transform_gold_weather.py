import pandas as pd 
from pathlib import Path

def transform_gold_data():
    root = Path(__file__).resolve().parents[1]

    input_file = root / "data" / "silver" / "weather_silver.parquet"
    gold_cities = root / "data" / "gold" / "cities_gold.parquet"
    gold_weather = root / "data" / "gold" / "weather_gold.parquet"

    df = pd.read_parquet(input_file)

    print(f"Loaded {len(df)} silver records.")
    print(f"Silver columns: {len(df.columns)}")

    # Create citites dimension table

    cities_gold = df[["city", "latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
    cities_gold.insert(0, "city_id", range(1, len(cities_gold) + 1))

    print("City table created.")
    print(f"Number of cities: {len(cities_gold)}")

    # Merge to bring city_id back into daily records and drop redundants from daily table

    df = df.merge(cities_gold, on=["city", "latitude", "longitude"], how="left")
    df = df.drop(columns=["city", "latitude", "longitude"])

    # Create temperature categories 

    df["temperature_category"] = pd.cut(
        df["temperature_max"],
        bins=[-float("inf"), 10, 25, 35, float("inf")],
        labels=["Cold", "Normal", "Hot", "Extreme"],    
        right=False
    )

    print("Temperature categories created.")
    print(df["temperature_category"].value_counts())

    # Create precipitation categories

    df["precipitation_category"] = pd.cut(
        df["precipitation_sum"],
        bins=[-float("inf"), 0, 5, 20, float("inf")],
        labels=["None", "Light", "Moderate", "Heavy"],
        right=True
    )

    print("Percipitaion categories created.")
    print(df["precipitation_category"].value_counts())

    # Create wind cetegories

    df["wind_category"] = pd.cut(
        df["wind_speed_max"],
        bins=[-float("inf"), 20, 40, 60, float("inf")],
        labels=["Calm", "Moderate", "Strong", "Extreme"],
        right=False
    )

    print("Wind speed categories created.")
    print(df["wind_category"].value_counts)

    # Calculate risk score (0 to 100 scale)

    def calculate_risk(row):
        score = 0
        if row["temperature_category"] == "Extreme":
            score += 40
        elif row["temperature_category"] == "Hot":
            score += 20

        if row["precipitation_category"] == "Heavy":
            score += 40
        elif row["precipitation_category"] == "Moderate":
            score += 20

        if row["wind_category"] == "Extreme":
            score += 20
        elif row["wind_category"] == "Strong":
            score += 10
        
        return min(score, 100)

    df["risk_score"] = df.apply(calculate_risk, axis=1)

    print("Risk score calculated.")

    # Save gold tables as parquet
    # Make city_id the first row

    df.insert(0, "city_id", df.pop("city_id")) 
        
    cities_gold.to_parquet(gold_cities, index=False)
    df.to_parquet(gold_weather, index=False)

    print("Gold parquet files saved successefully.")
    print(f"Cities gold records: {len(cities_gold)}")
    print(f"Weather gold records: {len(df)}")