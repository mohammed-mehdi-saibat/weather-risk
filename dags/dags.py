from extraction.extract_weather import extract_data
from transformation.transform_silver_weather import transform_silver_data
from transformation.transform_gold_weather import transform_gold_data
from load.load_gold_weather import load_gold_data
from datetime import datetime
from airflow import DAG
from airflow.decorators import task


with DAG(dag_id = "etl_pipeline", start_date = datetime(2026, 9, 19), schedule = "@daily", catchup = False) as dag:
    @task
    def extract():
        print("Exctracting data...")
        extract_data()
        print("Data loaded successefully.")
    @task
    def transform():
        print("Transforming data...")
        transform_silver_data()
        transform_gold_data()
        print("Data transformed successefully.")
    @task
    def save():
        print("Saving data...")
        load_gold_data()
        print("Data loaded and saved successefully.")

    extract() >> transform() >> save()