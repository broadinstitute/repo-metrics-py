import csv
import json
import os
import tempfile

import pytest
from click.testing import CliRunner
from mockito import unstub, when

from repo_metrics.github_download_stats.command import main
from repo_metrics.metrics.github import GitHubMetricsHelper


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def unstub_mocks():
    yield
    unstub()


def test_github_download_stats_csv(runner):
    when(GitHubMetricsHelper).get_release_download_counts(...).thenReturn(
        {
            "v1.0.0": 100,
            "v1.1.0": 200,
        }
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, "output.csv")

        result = runner.invoke(
            main,
            [
                "--github-repo",
                "test_owner/test_repo",
                "--output",
                tempfile_path,
                "--output-format",
                "csv",
                "--include-timestamp",
            ],
        )

        assert result.exit_code == 0

        with open(tempfile_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["v1.0.0"] == "100"
            assert rows[0]["v1.1.0"] == "200"


def test_github_download_stats_json(runner):
    when(GitHubMetricsHelper).get_release_download_counts(...).thenReturn(
        {
            "v1.0.0": 100,
            "v1.1.0": 200,
        }
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, "output.json")

        result = runner.invoke(
            main,
            [
                "--github-repo",
                "test_owner/test_repo",
                "--output",
                tempfile_path,
                "--output-format",
                "json",
                "--include-timestamp",
            ],
        )

        assert result.exit_code == 0

        with open(tempfile_path, "r") as f:
            json_array = json.load(f)
            assert len(json_array) == 1
            assert json_array[0]["v1.0.0"] == 100
            assert json_array[0]["v1.1.0"] == 200


def test_append_to_csv_with_different_fields(runner):
    when(GitHubMetricsHelper).get_release_download_counts(...).thenReturn(
        {
            "v1.0.0": 100,
            "v1.1.0": 200,
        }
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, "output.csv")

        # Create an initial CSV file with some data
        with open(tempfile_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["v1.0.0", "extra_field"])
            writer.writeheader()
            writer.writerow({"v1.0.0": 50, "extra_field": "extra_value"})

        # Append new data with different fields
        result = runner.invoke(
            main,
            [
                "--github-repo",
                "test_owner/test_repo",
                "--output",
                tempfile_path,
                "--output-format",
                "csv",
                "--append",
                "--include-timestamp",
            ],
        )

        assert result.exit_code == 0

        with open(tempfile_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["v1.0.0"] == "50"
            assert rows[0]["extra_field"] == "extra_value"
            assert rows[1]["v1.0.0"] == "100"
            assert rows[1]["v1.1.0"] == "200"
            assert rows[1]["extra_field"] == ""


def test_append_to_json_with_different_fields(runner):
    when(GitHubMetricsHelper).get_release_download_counts(...).thenReturn(
        {
            "v1.0.0": 100,
            "v1.1.0": 200,
        }
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, "output.json")

        # Create an initial JSON file with some data
        initial_data = [{"v1.0.0": 50, "extra_field": "extra_value"}]
        with open(tempfile_path, "w") as f:
            json.dump(initial_data, f, indent=4)

        # Append new data with different fields
        result = runner.invoke(
            main,
            [
                "--github-repo",
                "test_owner/test_repo",
                "--output",
                tempfile_path,
                "--output-format",
                "json",
                "--append",
                "--include-timestamp",
            ],
        )

        assert result.exit_code == 0

        with open(tempfile_path, "r") as f:
            json_array = json.load(f)
            assert len(json_array) == 2
            assert json_array[0]["v1.0.0"] == 50
            assert json_array[0]["extra_field"] == "extra_value"
            assert json_array[1]["v1.0.0"] == 100
            assert json_array[1]["v1.1.0"] == 200
            assert "extra_field" not in json_array[1]
