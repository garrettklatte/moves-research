from datetime import date
from definitions import SubjectLocationSummary, WeatherSummary
from gateways import CsvGateway

def test_extracts_subject_location_summary():
    expected = SubjectLocationSummary(
        '904299266',
        -118.2437,
        34.0522,
        date(1995, 6, 20)
    )
        
    row = {
        'subject_id': expected.subject_id,
        'longitude': expected.longitude,
        'latitude': expected.latitude,
        'date': '1995-06-20'
    }

    actual = CsvGateway._extract_subject_location_summary(row)

    assert expected == actual

def test_extracts_weather_summary():
    expected = WeatherSummary(
        75.1,
        90.4,
        63.9,
        2
    )

    row = {
        'mean_temp': expected.mean_temp,
        'max_temp': expected.max_temp,
        'min_temp': expected.min_temp,
        'precipitation': expected.precipitation
    }

    actual = CsvGateway._extract_weather_summary(row)

    assert expected == actual

def test_handles_nonfloat_weather_summary_value():
    expected = WeatherSummary(
        20.1,
        30.4,
        10.9,
        None
    )

    row = {
        'mean_temp': expected.mean_temp,
        'max_temp': expected.max_temp,
        'min_temp': expected.min_temp,
        'precipitation': 'T'
    }

    actual = CsvGateway._extract_weather_summary(row)

    assert expected == actual
    
def test_integration_records_weather_summary():
    csv_gateway = CsvGateway('/tmp/test_integration_csv_gateway.csv')

    expected_weather_summary = WeatherSummary(
        75.1,
        90.4,
        63.9,
        2
    )

    subject_location_summary = SubjectLocationSummary(
        '904299266',
        -118.2437,
        34.0522,
        date(1995, 6, 20)
    )
    
    csv_gateway.record_weather_summary(
        expected_weather_summary,
        subject_location_summary
    )

    weather_summary = csv_gateway.fetch_weather_summary(
        subject_location_summary
    )
    
    assert expected_weather_summary == weather_summary
