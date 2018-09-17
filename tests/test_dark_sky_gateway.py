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
                        '?exclude=currently,minutely,alerts,flags')
    
    request = DarkSkyGateway._make_request(subject_location_summary, api_key)
    
    assert expected_request == request

def test_plucks_response():
    apparent_temperatures = [12.1, 31.3, 43.2]
    precipitations = [0.01, 0.02, 0.04]
    temperatures = [23.1, 32.4, 54.3]    

    expected = WeatherSummary(
        mean_temp=sum(temperatures)/len(temperatures),
        max_temp=55.2,
        min_temp=17.6,
        precipitation=sum(precipitations),
        apparent_mean_temp=sum(apparent_temperatures)/len(apparent_temperatures),
        apparent_max_temp=47.0,
        apparent_min_temp=11.8
    )

    response = {
        'daily': {
            'data': [{
                'apparentTemperatureHigh': expected.apparent_max_temp,
                'apparentTemperatureLow': expected.apparent_min_temp,
                'precipIntensity': expected.precipitation,
                'temperatureHigh': expected.max_temp,
                'temperatureLow': expected.min_temp
            }]
        },
        'hourly': {
            'data': [
                {
                    'apparentTemperature': apparent_temperatures[i],
                    'precipIntensity': precipitations[i],
                    'temperature': temperatures[i]
                } for i in range(3)
            ]
        }
    }
    
    weather_summary = DarkSkyGateway._pluck_response(response)
    
    assert expected == weather_summary

def test_handles_response_without_data():
    expected = WeatherSummary(
        None,
        None,
        None,
        None,
        None,
        None,
        None
    )

    response = {}
    
    weather_summary = DarkSkyGateway._pluck_response(response)
    
    assert expected == weather_summary

    
