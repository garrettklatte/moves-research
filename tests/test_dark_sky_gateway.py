from datetime import date
from definitions import SubjectLocationSummary, WeatherSummary
from gateways import DarkSkyGateway

def test_makes_request():

    subject_location_summary = SubjectLocationSummary(
        '904299266',
        -73.98859,
        40.71567,
        date(1995, 6, 20)
    )

    api_key = 'fake_api_key'

    expected_request = ('https://api.darksky.net/forecast/fake_api_key/'
                        '40.71567,-73.98859,1995-06-20T00:00:00'
                        '?exclude=currently,minutely,hourly,alerts,flags')
    
    request = DarkSkyGateway._make_request(subject_location_summary, api_key)
    
    assert expected_request == request

def test_plucks_response():
    expected = WeatherSummary(
        None,
        75.1,
        56.4,
        1.2
    )

    response = {
        'daily': {
            'data': [{
                'apparentTemperatureHigh': expected.max_temp,
                'apparentTemperatureLow': expected.min_temp,
                'precipIntensity': expected.precipitation
            }]
        }
    }
    
    weather_summary = DarkSkyGateway._pluck_response(response)
    
    assert expected == weather_summary

def test_handles_response_without_precipitation():
    expected = WeatherSummary(
        None,
        75.1,
        56.4,
        None
    )

    response = {
        'daily': {
            'data': [{
                'apparentTemperatureHigh': expected.max_temp,
                'apparentTemperatureLow': expected.min_temp,
            }]
        }
    }
    
    weather_summary = DarkSkyGateway._pluck_response(response)
    
    assert expected == weather_summary

    
