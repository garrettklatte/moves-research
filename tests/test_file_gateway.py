from datetime import date
from pytest import mark
from definitions import SpacetimePoint
from gateways import FileGateway

@mark.parametrize('filename', [
    '123432_2018-09-03_json.csv',
    '234234_2017-12-01_json.csv'
    ])
def test_identifies_valid_files(filename):
    assert FileGateway._valid_file(filename)

@mark.parametrize('filename', [
    'NA_2016-12-11_json.csv',
    'cancelled_2015-01-01_json.csv'
    ])
def test_identifies_invalid_files(filename):
    assert not FileGateway._valid_file(filename)
                  
def test_makes_filename():
    point = SpacetimePoint(123.43, -54.345, date(2018, 1, 1))
    file_path = '/home/gklatte'
    filename = FileGateway._create_filename(point, file_path)
    expected_filename = '/home/gklatte/123.43_-54.345_2018-01-01.json'

    assert expected_filename == filename
