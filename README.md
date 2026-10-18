# Global Weather Data Pipeline

A Python-based ETL (Extract, Transform, Load) pipeline that collects real-time weather data from 10 cities worldwide using the Open-Meteo API, cleans and validates the data with Pandas, and stores the results in CSV format and a relational SQLite database.

## Technologies Used

- **Python** — Pipeline development and automation
- **Requests** — REST API integration
- **Pandas** — Data transformation and validation
- **SQLite** — Relational data storage
- **Logging** — Pipeline execution monitoring
- **Python Assertions** — Basic automated testing

## ETL Pipeline

### 1. Extract

Fetch weather information from the Open-Meteo API for 10 international cities, including temperature, relative humidity, wind speed and observation time.

### 2. Transform

Clean and validate the extracted data:

- Check for missing values.
- Remove duplicate records.
- Round temperature and wind speed to two decimal places.
- Convert timestamps into datetime values.
- Validate humidity values within the 0–100 range.

### 3. Load

Store the processed data in:

- **CSV:** `data/weather_data.csv`
- **SQLite:** `database/weather.db`

The database contains two related tables:

**cities**
- `city_id` — Primary key
- `city_name`
- `country`
- `latitude`
- `longitude`

**weather_readings**
- `reading_id` — Primary key
- `city_id` — Foreign key referencing `cities`
- `temperature`
- `humidity`
- `wind_speed`
- `recorded_at`

Unique constraints help prevent duplicate city records and repeated weather observations for the same city and timestamp.

## Data Quality Testing

Basic tests verify that the transformation function:

- Rejects invalid humidity values.
- Correctly rounds numeric values.
- Removes duplicate records.

Run the tests from the project root:

```bash
python3 -m tests.test_pipeline
```

## Installation and Usage

Clone the repository and navigate into the project directory.

Install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Execute the ETL pipeline:

```bash
python3 main.py
```

## Project Goals

This project was developed as hands-on practice in Data Engineering, focusing on API integration, ETL development, data quality validation, relational database design, and automated testing.

## Future Improvements

- Implement testing with pytest.
- Schedule automatic pipeline executions.
- Add historical weather analysis.
- Migrate data storage to PostgreSQL.
- Explore cloud deployment.