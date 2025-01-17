import json

from .output_type import Output


class JsonOutput(Output):

    def __init__(self, path, append=False):
        self.path = path
        self.append = append

    def write(self, data: list[dict]) -> None:
        """
        Prints the specified data in Json format

        :param data: The data to print
        """
        # If we are appending, read the existing data
        if self.append:
            try:
                with open(self.path, "r") as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = []
            data = existing_data + data
        # Write the data to the file
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
