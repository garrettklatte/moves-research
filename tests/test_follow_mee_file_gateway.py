import csv
from datetime import date
from pytest import mark
from definitions import SubjectLocationSummary
from gateways import FollowMeeFileGateway

def test_extracts_location():
    expected_longitude = -73.935242
    expected_latitude = 40.730610
    row_record = {
        'Data.Longitude': expected_longitude,
        'Data.Latitude': expected_latitude
    }
    
    longitude, latitude = FollowMeeFileGateway._extract_location(row_record)

    assert expected_longitude == longitude
    assert expected_latitude == latitude

def test_extracts_date():
    expected_date = date(2018, 9, 12)
    row_record = {
        'Data.Date': '2018-09-12T22:41:57-04:00'
    }

    actual_date = FollowMeeFileGateway._extract_date(row_record)
    
    assert expected_date == actual_date

@mark.parametrize('filename', [
    '11423412_2018-22-07_json.csv',
    '../11423412_2018-22-07_json.csv',
    '/home/gklatte/11423412_2018-22-07_json.csv'
])
def test_extracts_subject_id(filename):
    expected_subject_id = '11423412'

    subject_id = FollowMeeFileGateway._extract_subject_id(filename)

    assert expected_subject_id == subject_id

def test_itegration__extracts_subject_location_summary():
    expected = SubjectLocationSummary(
        '98123345',
        -73.935242,
        40.730610,
        date(2018, 9, 12)
    )

    filename = '/tmp/{subject_id}_follow_mee_integration_test.csv'.format(
        subject_id=expected.subject_id
    )
    row_record = {
        'Data.Longitude': expected.longitude,
        'Data.Latitude': expected.latitude,
        'Data.Date': '2018-09-12T22:41:57-04:00'
    }

    fieldnames = row_record.keys()

    with open(filename, 'w') as follow_mee_file:
        writer = csv.DictWriter(follow_mee_file, fieldnames)
        writer.writeheader()
        writer.writerow(row_record)

    actual = FollowMeeFileGateway.extract_subject_location_summary(filename)

    assert expected == actual
