import pytest
import csv
from repo_metrics.output.csv_output import CsvOutput

@pytest.fixture
def temp_file(tmpdir):
    return tmpdir.join("test_output.csv")

def test_write_new_file(temp_file):
    data = {"name": "test", "value": '123'}
    csv_output = CsvOutput(str(temp_file))
    csv_output.write(data)

    with open(temp_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0] == data

def test_append_to_file(temp_file):
    data1 = {"name": "test1", "value": '123'}
    data2 = {"name": "test2", "value": '456'}
    csv_output = CsvOutput(str(temp_file))
    csv_output.write(data1)
    csv_output = CsvOutput(str(temp_file), append=True)
    csv_output.write(data2)

    with open(temp_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == data1
        assert rows[1] == data2
