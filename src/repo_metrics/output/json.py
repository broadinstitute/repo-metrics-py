import json

from .output_type import Output

class JsonOutput(Output):

    def __init__(self, path):
        self.path = path

    def write(self, data: dict) -> None:
        """
        Prints the specified data in Json format

        :param data: The data to print
        """
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4)