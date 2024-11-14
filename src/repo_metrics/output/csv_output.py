import csv

from .output_type import Output
from .preprocess import flatten


class CsvOutput(Output):

    def __init__(self, path, append=False):
        """
        Constructor for the CsvOutput class

        :param path: The path to the file to write
        :param append: Whether to append to the file
        """
        self.path = path
        self.append = append

    def write(self, data: dict) -> None:
        """
        Prints the specified data in CSV format

        :param data: The data to print
        """
        open_mode = "a" if self.append else "w"

        # Flatten the data so it writes correctly
        data = flatten(data)

        with open(self.path, open_mode) as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not self.append:
                writer.writeheader()
            writer.writerow(data)
