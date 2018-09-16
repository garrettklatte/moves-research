from datetime import date
from definitions import SubjectLocationSummary, WeatherSummary
from gateways import WeatherGateway

def test_makes_history_request():
    api_key = '123345'
    summary = SubjectLocationSummary(
        subject_id='123123123',
        longitude=109.2,
        latitude=34.9,
        date=date(2018, 1, 1)
    )
    request = WeatherGateway._make_history_request(api_key, summary)

    expected_request = ('http://api.wunderground.com/api/123345/history_20180101'
                        '/q/34.9,109.2.json')

    assert expected_request == request
    
def test_plucks_history_response():
    response = {
        'history': {
            'dailysummary':
            [
                {
                    'meantempi': 70,
                    'maxtempi': 80,
                    'mintempi': 60,
                    'precipi': 3
                }
            ]
        }
    }
    summary = WeatherGateway._pluck_history_response(response)
    expected_summary = WeatherSummary(
        mean_temp=70,
        max_temp=80,
        min_temp=60,
        precipitation=3
    )

    assert expected_summary == summary
    
