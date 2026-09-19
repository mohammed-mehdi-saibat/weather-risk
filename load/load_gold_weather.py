import os
import pandas as pd
from sqlalchemy import create_engine



def load_gold_data():
    # Use the Docker service name 'postgres' as host
    DB_URI = os.getenv(
        "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
        "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
    )

    engine = create_engine(DB_URI)

    cities_parquet_path = "/opt/airflow/data/gold/cities_gold.parquet"
    if os.path.exists(cities_parquet_path):
        df_cities = pd.read_parquet(cities_parquet_path)
        df_cities.to_sql("cities_gold", con=engine, if_exists="replace", index=False)
        print(f"Loaded {len(df_cities)} rows into 'cities_gold'.")

    weather_parquet_path = "/opt/airflow/data/gold/weather_gold.parquet"
    if os.path.exists(weather_parquet_path):
        df_weather = pd.read_parquet(weather_parquet_path)
        df_weather.to_sql("weather_gold", con=engine, if_exists="replace", index=False)
        print(f"Loaded {len(df_weather)} rows into 'weather_gold'.")
