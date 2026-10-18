from main import transform_weather

def test_invalid_humidity():
    test_data = [
        {
            "city": "Madrid",
            "country": "Spain",
            "temperature": 25.4,
            "humidity": 150,
            "wind_speed": 4.0,
            "recorded_at": "2026-10-12T12:45:00"
        }
    ]

    try:
        transform_weather(test_data)
        print("FAILED: Invalid humidity accepted")

    except ValueError:
        print("PASSED: Invalid humidity rejected")

def test_round():
    test_data = [
        {
            "city": "Madrid",
            "country": "Spain",
            "temperature": 25.6789,
            "humidity": 65,
            "wind_speed": 12.3456,
            "recorded_at": "2026-10-18 10:00:00"
        }
    ]

    result = transform_weather(test_data)

    assert result.loc[0, 'temperature'] == 25.68
    assert result.loc[0, 'wind_speed'] == 12.35

    print("PASSED: Rounding works correctly")
    
def test_duplicates() :
    test_data = [
    {
        "city": "Madrid",
        "temperature": 25.5,
        "humidity": 65,
        "wind_speed": 10.5,
        "recorded_at": "2026-10-18 10:00:00"
    },
    {
        "city": "Madrid",
        "temperature": 25.5,
        "humidity": 65,
        "wind_speed": 10.5,
        "recorded_at": "2026-10-18 10:00:00"
    }
    ]  
    result = transform_weather(test_data)
    assert len(result) == 1
    print("PASSED: Duplicates works correctly")

if __name__ == "__main__":
    test_invalid_humidity()
    test_round()
    test_duplicates()