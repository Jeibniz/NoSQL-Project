""" AUTHOR: Jonathan Persgården (jpersgarden@gmail.com) """

import json

class FileWriter:
    """
    A simple class that writes json data do a file.
    """
    def __init__(self, file = None):
        """
        :param file: The path to the wile which this calss will write data.
        """
        if file is None:
            'Set client to the default when running on local machine'
            self.file = 'batch1.json'

    def send_data(self, data):
        """
        Writes JSON data to the file specified in the constructor. The data written
        will append the existing data n the file. If the file does not exists it
        will be created.

        :param data: Tha data that will be written. The data has to be passed as
        an JSON object.
        """

        with open(self.file, 'a') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write("\n")

