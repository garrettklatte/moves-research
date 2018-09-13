"""Module for file_gateway."""

class FileGateway:
    """Interface for persisting files to local storage."""
    def __init__(self, file_path):
        self._file_path = file_path
        
    def store_weather_data(self, spacetime_point, weather_data):
        """Save the data in 'weather_data' to a file named after
        'spacetime_point' and located at 'file_path'.
        """
        filename = FileGateway._make_filename(spacetime_point, self._file_path)
        with open(filename, 'w') as out_file:
            out_file.write(weather_data)
        return filename

    @staticmethod
    def fetch_valid_files_in_directory(absolute_directory_name):
        files = os.listdir(path=absolute_directory_name)
        valid_files = [f for f in files if FileGateway._valid_file(f)]
        return [os.path.join(absolute_directory_name, valid_file)
                for valid_file in valid_files]

    @staticmethod
    def _make_filename(spacetime_point, file_path):
        """
        """
        point_string = '{latitude}_{longitude}_{date_string}.json'.format(
            latitude=spacetime_point.latitude,
            longitude=spacetime_point.longitude,
            date_string=spacetime_point.date.isoformat()
        )
        return '{file_path}/{point_string}'.format(
            file_path=file_path,
            point_string=point_string
        )

    @staticmethod
    def _valid_file(filename):
        """Use this function to filter out files that should not be analyzed.
        """
        tokens = filename.split('_')

        if tokens[0] == 'NA':
            return False

        if tokens[0] == 'cancelled':
            return False

        return True

