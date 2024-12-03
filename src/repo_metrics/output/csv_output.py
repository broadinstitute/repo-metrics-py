import csv
from enum import Enum

from .output_type import Output
from .preprocess import flatten

class CsvOutput(Output):

    def __init__(self, path, append=False):
        """
        Constructor for the CsvOutput class

        :param path: The path to the file to write
        :param mode: Mode for writing to the file
        """
        self.path = path
        self.append = append

    def write(self, data: dict) -> None:
        """
        Prints the specified data in CSV format

        :param data: The data to print
        """
        data_to_write = []
        # If the mode is append, read the existing file and append to it
        if self.append:
            with open(self.path, "r") as f:
                reader = csv.DictReader(f)
                data_to_write.extend(reader)

        # Flatten the data so it writes correctly
        data = flatten(data)
        data_to_write.append(data)

        # Make sure we have all the field names from both the existing data (if we have any) and the new data
        fieldnames_set = set(data.keys())
        fieldnames_set.update(data_to_write[0].keys() if data_to_write else [])
        fieldnames_list = list(fieldnames_set)
        fieldnames_list.sort()

        with open(self.path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_list)
            writer.writeheader()
            for row in data_to_write:
                writer.writerow(row)
