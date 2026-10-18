import requests
import pandas as pd
import sqlite3
from datetime import datetime

log_file = "logs/log.txt"
csv_path = "data/weather_data.csv"
#define url
url= 'https://api.open-meteo.com/v1/forecast'
#Cities of interest
cities = [
    {
        "city": "Mexico City",
        "country": "Mexico",
        "latitude": 19.4326,
        "longitude": -99.1332
    },
    {
        "city": "Madrid",
        "country": "Spain",
        "latitude": 40.4168,
        "longitude": -3.7038
    },
    {
        "city": "New York",
        "country": "USA",
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    {
        "city": "London",
        "country": "United Kingdom",
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    {
        "city": "Paris",
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522
    },
    {
        "city": "Tokyo",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503
    },
    {
        "city": "Bucharest",
        "country": "Romania",
        "latitude": 44.4268,
        "longitude": 26.1025
    },
    {
        "city": "Berlin",
        "country": "Germany",
        "latitude": 52.5200,
        "longitude": 13.4050
    },
    {
        "city": "Sydney",
        "country": "Australia",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    {
        "city": "Toronto",
        "country": "Canada",
        "latitude": 43.6532,
        "longitude": -79.3832
    }
]

#Extraction
def extract_weather(cities):
    weather_data = []
    for city in cities:
        params={
            "latitude" : city["latitude"],
            "longitude" : city["longitude"],
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m'
        }
        try:
            response = requests.get(url, params=params, timeout= 10)
            response.raise_for_status()
            data= response.json()
            current = data["current"]
            weather_dict = {
                        "city" : city["city"],
                        "country": city["country"],
                        "temperature" : current['temperature_2m'],
                        "humidity" : current["relative_humidity_2m"],
                        "wind_speed" : current["wind_speed_10m"],
                        "recorded_at" : current["time"]
                        }
            weather_data.append(weather_dict)
        except requests.exceptions.Timeout as e:
            log_message(f"Timeout extracting {city['city']}: {e}")
        except requests.exceptions.HTTPError as e:
            log_message(f"HTTP error extracting {city['city']}: {e}")
        except KeyError as e:
            log_message(f"Missing JSON key for {city['city']}: {e}")
        except requests.exceptions.ConnectionError as e:
            log_message(f"There was a connection error {e}")
        except requests.exceptions.RequestException as e:
            log_message(f"Error extracting {city['city']}: {e}")
            continue
    return weather_data

def transform_weather(data):
    df = pd.DataFrame(data)
    if df.isna().any().any() :
        raise ValueError("We found NA values")
    if df.duplicated().any():
        df = df.drop_duplicates()
    df['temperature'] = round(df["temperature"],2)
    df['wind_speed'] = round(df["wind_speed"],2)
    df['recorded_at'] = pd.to_datetime(df['recorded_at'])
    if ((df["humidity"] < 0) | (df["humidity"] > 100)).any():
        raise ValueError("Humidity has an invalid number")
    return df

def create_database() :
    conn = sqlite3.connect("database/weather.db")
    try:
        #tabla de ciudades
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cities(
                city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_name TEXT NOT NULL,
                country TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                UNIQUE(city_name, country)
            );
            """)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_readings(
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_id INTEGER NOT NULL,
                temperature REAL,
                humidity INTEGER,
                wind_speed REAL,
                recorded_at TEXT NOT NULL,
                UNIQUE(city_id, recorded_at),
                FOREIGN KEY (city_id) REFERENCES cities(city_id)
            );
            """)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"We had an error while trying to execute SQL: {e}")
        raise
    finally:
        conn.close()

def load_cities(cities):
    conn =sqlite3.connect("database/weather.db")
    try:
        for city in cities:
            conn.execute(
                """
                INSERT OR IGNORE INTO cities(
                    city_name,
                    country,
                    latitude,
                    longitude
                )
                VALUES(?,?,?,?)
                """,
                (city['city'],city['country'],city['latitude'],city['longitude'])
            )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        log_message(f"Database error : {e}")
        raise
    finally :
        conn.close()

def load_weather(df):
    conn = sqlite3.connect("database/weather.db")
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        for _, row in df.iterrows():
            cursor = conn.execute(
                """
                SELECT city_id
                FROM cities
                WHERE city_name = ? AND country = ?
                """,
                (row["city"], row["country"])
            )

            city_record = cursor.fetchone()
            if city_record is None:
                raise ValueError(f"City not found: {row['city']}")

            city_id = city_record[0]
            
            conn.execute(
                """
                INSERT OR IGNORE INTO weather_readings(
                    city_id,
                    temperature,
                    humidity,
                    wind_speed,
                    recorded_at
                )
                VALUES(?,?,?,?,?)
                """,
                (city_id,row["temperature"],row["humidity"],row["wind_speed"],row["recorded_at"].isoformat())
            )

        conn.commit()
    except (sqlite3.Error, ValueError) as e:
        conn.rollback()
        log_message(f"Database error: {e}")
        raise
    finally:    
        conn.close()

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as file:
        file.write(f"{timestamp} - {message}\n")


def main():
    log_message("Initiating ETL")
    log_message("Preliminaries completed")

    log_message("Starting extraction")
    result = extract_weather(cities)
    log_message(f"Extraction completed: {len(result)}/{len(cities)}")
    if not result:
        log_message("ERROR: No weather data extracted")
        raise ValueError("Extraction failed: No weather data available")
    log_message("Transforming the data")
    df = transform_weather(result)
    log_message("Transform completed")

    log_message("Exporting data to CSV")
    df.to_csv(csv_path, index=False)
    log_message("CSV export completed")

    log_message("Creating Database")
    create_database()
    log_message("Database created")

    log_message("Loading cities")
    load_cities(cities)
    log_message("Loading Weather")

    load_weather(df)
    log_message("ETL Completed")



if __name__ == "__main__":
    main()