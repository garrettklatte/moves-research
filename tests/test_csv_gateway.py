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
        2,
        81.3,
        96.4,
        63.4
    )

    row = {
        'mean_temp': expected.mean_temp,
        'max_temp': expected.max_temp,
        'min_temp': expected.min_temp,
        'precipitation': expected.precipitation,
        'apparent_mean_temp': expected.apparent_mean_temp,
        'apparent_max_temp': expected.apparent_max_temp,
        'apparent_min_temp': expected.apparent_min_temp
    }

    actual = CsvGateway._extract_weather_summary(row)

    assert expected == actual

def test_handles_nonfloat_weather_summary_value():
    expected = WeatherSummary(
        None,
        None,
        None,
        None,
        None,
        None,
        None
    )

    row = {
        'mean_temp': 'N',
        'max_temp': 'A',
        'min_temp': 'T',
        'precipitation': 'A',
        'apparent_mean_temp': 'L',
        'apparent_max_temp': 'I',
        'apparent_min_temp': 'E'
    }

    actual = CsvGateway._extract_weather_summary(row)

    assert expected == actual

def test_integration_records_weather_summary():
    csv_gateway = CsvGateway('/tmp/test_integration_csv_gateway.csv')

    expected_weather_summary = WeatherSummary(
        75.1,
        90.4,
        63.9,
        2,
        81.3,
        96.4,
        63.4
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

def test_makes_row():
    expected_row = {
        'subject_id': '904299266',
        'longitude': -118.2437,
        'latitude': 34.0522,
        'date': '1995-06-20',
        'mean_temp': '1.10',
        'max_temp': '12.43',
        'min_temp': '0.05',
        'apparent_mean_temp': None,
        'apparent_max_temp': None,
        'apparent_min_temp': None,
        'precipitation': '0.3300'
    }

    weather_summary = WeatherSummary(
        1.1,
        12.43112,
        0.049,
        0.33
    )

    subject_location_summary = SubjectLocationSummary(
        expected_row['subject_id'],
        expected_row['longitude'],
        expected_row['latitude'],
        date(1995, 6, 20)
    )

    row = CsvGateway._make_row(weather_summary, subject_location_summary)

    assert expected_row == row
