import csv
import json
import os
import tempfile

import pytest
from click.testing import CliRunner
import mockito
from mockito import when, verify, unstub

from repo_metrics.github_traffic_stats.command import main
from repo_metrics.metrics.github import GitHubMetricsHelper

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def unstub_mocks():
    yield
    unstub()

def test_github_traffic_stats_csv(runner):
    when(GitHubMetricsHelper).get_repo_traffic(...).thenReturn([
        {"timestamp": "2023-10-01T00:00:00Z", "clones": 10, "unique clones": 5, "views": 20, "unique views": 10},
        {"timestamp": "2023-10-02T00:00:00Z", "clones": 15, "unique clones": 7, "views": 25, "unique views": 12},
    ])
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, 'output.csv')

        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--output', tempfile_path,
            '--output-format', 'csv',
        ])

        assert result.exit_code == 0

        with open(tempfile_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['timestamp'] == '2023-10-01T00:00:00Z'
            assert rows[0]['clones'] == '10'
            assert rows[0]['unique clones'] == '5'
            assert rows[0]['views'] == '20'
            assert rows[0]['unique views'] == '10'
            assert rows[1]['timestamp'] == '2023-10-02T00:00:00Z'
            assert rows[1]['clones'] == '15'
            assert rows[1]['unique clones'] == '7'
            assert rows[1]['views'] == '25'
            assert rows[1]['unique views'] == '12'

def test_github_traffic_stats_json(runner):
    when(GitHubMetricsHelper).get_repo_traffic(...).thenReturn([
        {"timestamp": "2023-10-01T00:00:00Z", "clones": 10, "unique clones": 5, "views": 20, "unique views": 10},
        {"timestamp": "2023-10-02T00:00:00Z", "clones": 15, "unique clones": 7, "views": 25, "unique views": 12},
    ])
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, 'output.json')

        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--output', tempfile_path,
            '--output-format', 'json',
        ])

        assert result.exit_code == 0

        with open(tempfile_path, 'r') as f:
            json_array = json.load(f)
            assert len(json_array) == 2
            assert json_array[0]['timestamp'] == "2023-10-01T00:00:00Z"
            assert json_array[0]['clones'] == 10
            assert json_array[0]['unique clones'] == 5
            assert json_array[0]['views'] == 20
            assert json_array[0]['unique views'] == 10
            assert json_array[1]['timestamp'] == "2023-10-02T00:00:00Z"
            assert json_array[1]['clones'] == 15
            assert json_array[1]['unique clones'] == 7
            assert json_array[1]['views'] == 25
            assert json_array[1]['unique views'] == 12

def test_append_to_csv_with_different_fields(runner):
    when(GitHubMetricsHelper).get_repo_traffic(...).thenReturn([
        {"timestamp": "2023-10-01T00:00:00Z", "clones": 10, "unique clones": 5, "views": 20, "unique views": 10},
        {"timestamp": "2023-10-02T00:00:00Z", "clones": 15, "unique clones": 7, "views": 25, "unique views": 12},
    ])
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, 'output.csv')

        # Create an initial CSV file with some data
        with open(tempfile_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "clones", "extra_field"])
            writer.writeheader()
            writer.writerow({"timestamp": "2023-09-30T00:00:00Z", "clones": 5, "extra_field": "extra_value"})

        # Append new data with different fields
        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--output', tempfile_path,
            '--output-format', 'csv',
            '--append',
        ])

        assert result.exit_code == 0

        with open(tempfile_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]['timestamp'] == '2023-09-30T00:00:00Z'
            assert rows[0]['clones'] == '5'
            assert rows[0]['extra_field'] == 'extra_value'
            assert rows[1]['timestamp'] == '2023-10-01T00:00:00Z'
            assert rows[1]['clones'] == '10'
            assert rows[1]['unique clones'] == '5'
            assert rows[1]['views'] == '20'
            assert rows[1]['unique views'] == '10'
            assert rows[1]['extra_field'] == ''
            assert rows[2]['timestamp'] == '2023-10-02T00:00:00Z'
            assert rows[2]['clones'] == '15'
            assert rows[2]['unique clones'] == '7'
            assert rows[2]['views'] == '25'
            assert rows[2]['unique views'] == '12'
            assert rows[2]['extra_field'] == ''

def test_append_to_json_with_different_fields(runner):
    when(GitHubMetricsHelper).get_repo_traffic(...).thenReturn([
        {"timestamp": "2023-10-01T00:00:00Z", "clones": 10, "unique clones": 5, "views": 20, "unique views": 10},
        {"timestamp": "2023-10-02T00:00:00Z", "clones": 15, "unique clones": 7, "views": 25, "unique views": 12},
    ])
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, 'output.json')

        # Create an initial JSON file with some data
        initial_data = [
            {
                "timestamp": "2023-09-30T00:00:00Z",
                "clones": 5,
                "extra_field": "extra_value"
            }
        ]
        with open(tempfile_path, 'w') as f:
            json.dump(initial_data, f, indent=4)

        # Append new data with different fields
        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--output', tempfile_path,
            '--output-format', 'json',
            '--append',
        ])

        assert result.exit_code == 0

        with open(tempfile_path, 'r') as f:
            json_array = json.load(f)
            assert len(json_array) == 3
            assert json_array[0]['timestamp'] == "2023-09-30T00:00:00Z"
            assert json_array[0]['clones'] == 5
            assert json_array[0]['extra_field'] == 'extra_value'
            assert json_array[1]['timestamp'] == "2023-10-01T00:00:00Z"
            assert json_array[1]['clones'] == 10
            assert json_array[1]['unique clones'] == 5
            assert json_array[1]['views'] == 20
            assert json_array[1]['unique views'] == 10
            assert 'extra_field' not in json_array[1]
            assert json_array[2]['timestamp'] == "2023-10-02T00:00:00Z"
            assert json_array[2]['clones'] == 15
            assert json_array[2]['unique clones'] == 7
            assert json_array[2]['views'] == 25
            assert json_array[2]['unique views'] == 12
            assert 'extra_field' not in json_array[2]
