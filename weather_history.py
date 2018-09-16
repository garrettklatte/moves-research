import os
import time

from gateways import CsvGateway, FollowMeeFileGateway, WeatherGateway

def get_weather_history():
    downloaded_files_path = '/vagrant/Downloaded Files'

    files = [os.path.join(downloaded_files_path, downloaded_file)
             for downloaded_file in os.listdir(downloaded_files_path)]

    print('Total number of downloaded files: {}'.format(len(files)))
    
    csvGateway = CsvGateway('all_data.csv')
    
    locations = [FollowMeeFileGateway.extract_subject_location_summary(f) for f
                 in files if FollowMeeFileGateway.extract_subject_location_summary(f)]

    print('Total number of locations: {}'.format(len(locations)))

    unprocessed_locations = [location for location in locations
                             if not csvGateway.fetch_weather_summary(location)]

    print('Total number of unprocessed data points: {}'.format(len(
        unprocessed_locations
    )))
    
    count = 0
    
    for unprocessed_location in unprocessed_locations:
        print(f'Count: {count}')
        
        if count > 400:
            return

        weather_summary = WeatherGateway.fetch_weather_summary(
            unprocessed_location
        )

        print(weather_summary)
        
        csvGateway.record_weather_summary(
            weather_summary,
            unprocessed_location
        )

        time.sleep(6.1)
        
        count += 1

if __name__ == '__main__':
    get_weather_history()
