import pandas as pd, requests, json

cities_file = "../data/bronze/simplemaps_cities.csv"
output_file = "../data/bronze/weather_raw.json"

cities =  pd.read_csv(cities_file)

results = []

for _, city in cities.iterrows():
    name = city["city"]
    latitude = city["lat"]
    longitude = city["lng"]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "weather_code"],
        "forecast_days": 7,
        "timezone": "Africa/Casablanca"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        results.append(
            {
                "city": name,
                "latitude": latitude,
                "longitude": longitude,
                "weather": response.json()
            }
        )
    else: 
        print(f"Error fetching {name}: {response.status_code}")

    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("Extraction finished!")
    print(f"Saved to {output_file}")