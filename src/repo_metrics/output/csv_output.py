import csv
import os

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

    def write(self, data: list[dict]) -> None:
        """
        Prints the specified data in CSV format

        :param data: The data to print
        """
        # Flatten the data
        flattened_data = []
        for d in data:
            flattened_data.append(flatten(d))
        data = flattened_data

        fieldnames_set = set()

        # Rewrite the file if the header is different
        rewrite = False

        # Read existing fieldnames if appending
        if self.append:
            try:
                with open(self.path, "r") as f:
                    # Check if the header is different
                    reader = csv.DictReader(f)
                    existing_fieldnames = reader.fieldnames
                    if existing_fieldnames is not None:
                        if set(existing_fieldnames) != fieldnames_set:
                            rewrite = True
                    # Add existing fieldnames to the set
                    fieldnames_set.update(existing_fieldnames)
            except FileNotFoundError:
                pass

        # Add new fieldnames to the set
        for d in data:
            fieldnames_set.update(d.keys())
        fieldnames_list = sorted(fieldnames_set)

        # If we have to rewrite the file, read from the existing file and write to a temporary file
        if rewrite:
            with open(self.path, "r") as f:
                with open(self.path + ".tmp", "w", newline="") as f_tmp:
                    reader = csv.DictReader(f)
                    writer = csv.DictWriter(f_tmp, fieldnames=fieldnames_list, restval="", extrasaction="ignore")
                    writer.writeheader()
                    # Write the existing rows to the temporary file
                    for row in reader:
                        # row.update((k, "") for k in fieldnames_list if k not in row)
                        writer.writerow(row)
                    # Write the new data to the temporary file
                    for d in data:
                        writer.writerow(d)
            # Replace the existing file with the temporary file
            os.replace(self.path + ".tmp", self.path)
        # Otherwise, just write the data to the file
        else:
            with open(self.path, "a" if self.append else "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames_list)
                if not self.append:
                    writer.writeheader()
                for d in data:
                    writer.writerow(d)
