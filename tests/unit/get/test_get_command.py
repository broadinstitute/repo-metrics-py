import csv
import json
import os
import tempfile

import pytest
from click.testing import CliRunner
from datetime import datetime
import mockito
from mockito import when, verify, unstub

from repo_metrics.get.command import main
from repo_metrics.metrics.github import GitHubMetricsHelper
from repo_metrics.metrics.dockerhub import DockerHubMetricsHelper
from repo_metrics.output.config import OutputConfig

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def unstub_mocks():
    yield
    unstub()

def test_github_and_dockerhub_csv(runner):
    when(GitHubMetricsHelper).get_repo_info(...).thenReturn({
        "forks": 10,
        "open_issues": 1000,
        "watchers": 100,
        "stargazers_count": 110,
        "subscribers_count": 120,
        "download_count": 40000,
    })
    when(DockerHubMetricsHelper).get_repo_info(...).thenReturn({
        "star_count": 10,
        "pull_count": 1000,
    })
    with tempfile.TemporaryDirectory() as temp_dir:

        tempfile_path = os.path.join(temp_dir, 'output.csv')

        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--dockerhub-repo', 'test_owner/test_repo_docker',
            '--output', tempfile_path,
            '--output-format', 'csv',
            '--include-timestamp',
            '--config', 'just_metrics'
        ])

        assert result.exit_code == 0
        
        with open(tempfile_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['github_forks'] == '10'
            assert rows[0]['github_open_issues'] == '1000'
            assert rows[0]['github_watchers'] == '100'
            assert rows[0]['github_stargazers_count'] == '110'
            assert rows[0]['github_subscribers_count'] == '120'
            assert rows[0]['github_download_count'] == '40000'
            assert rows[0]['dockerhub_star_count'] == '10'
            assert rows[0]['dockerhub_pull_count'] == '1000'

def test_github_and_dockerhub_json(runner):
    when(GitHubMetricsHelper).get_repo_info(...).thenReturn({
        "forks": 10,
        "open_issues": 1000,
        "watchers": 100,
        "stargazers_count": 110,
        "subscribers_count": 120,
        "download_count": 40000,
    })
    when(DockerHubMetricsHelper).get_repo_info(...).thenReturn({
        "star_count": 10,
        "pull_count": 1000,
    })
    with tempfile.TemporaryDirectory() as temp_dir:

        tempfile_path = os.path.join(temp_dir, 'output.json')

        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--dockerhub-repo', 'test_owner/test_repo_docker',
            '--output', tempfile_path,
            '--output-format', 'json',
            '--include-timestamp',
            '--config', 'just_metrics'
        ])

        assert result.exit_code == 0
        
        with open(tempfile_path, 'r') as f:
            json_array = json.load(f)
            assert len(json_array) == 1
            assert json_array[0]['github_forks'] == 10
            assert json_array[0]['github_open_issues'] == 1000
            assert json_array[0]['github_watchers'] == 100
            assert json_array[0]['github_stargazers_count'] == 110
            assert json_array[0]['github_subscribers_count'] == 120
            assert json_array[0]['github_download_count'] == 40000
            assert json_array[0]['dockerhub_star_count'] == 10
            assert json_array[0]['dockerhub_pull_count'] == 1000

def test_append_to_csv_with_different_fields(runner):
    # Mock the GitHubMetricsHelper methods
    when(GitHubMetricsHelper).get_repo_info(...).thenReturn({
        "forks": 10,
        "open_issues": 1000,
        "watchers": 100,
        "stargazers_count": 110,
        "subscribers_count": 120,
        "download_count": 40000,
    })
    when(DockerHubMetricsHelper).get_repo_info(...).thenReturn({
        "star_count": 10,
        "pull_count": 1000,
    })
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, 'output.csv')

        # Create an initial CSV file with some data
        with open(tempfile_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["github_forks", "github_open_issues", "extra_field"])
            writer.writeheader()
            writer.writerow({"github_forks": 5, "github_open_issues": 500, "extra_field": "extra_value"})

        # Append new data with different fields
        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--dockerhub-repo', 'test_owner/test_repo_docker',
            '--output', tempfile_path,
            '--output-format', 'csv',
            '--append',
            '--include-timestamp',
            '--config', 'just_metrics'
        ])

        assert result.exit_code == 0

        with open(tempfile_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['github_forks'] == '5'
            assert rows[0]['github_open_issues'] == '500'
            assert rows[0]['extra_field'] == 'extra_value'
            assert rows[1]['github_forks'] == '10'
            assert rows[1]['github_open_issues'] == '1000'
            assert rows[1]['github_watchers'] == '100'
            assert rows[1]['github_stargazers_count'] == '110'
            assert rows[1]['github_subscribers_count'] == '120'
            assert rows[1]['github_download_count'] == '40000'
            assert rows[1]['dockerhub_star_count'] == '10'
            assert rows[1]['dockerhub_pull_count'] == '1000'
            assert rows[1]['extra_field'] == ''

def test_append_to_json_with_different_fields(runner):
    # Mock the GitHubMetricsHelper methods
    when(GitHubMetricsHelper).get_repo_info(...).thenReturn({
        "forks": 10,
        "open_issues": 1000,
        "watchers": 100,
        "stargazers_count": 110,
        "subscribers_count": 120,
        "download_count": 40000,
    })
    when(DockerHubMetricsHelper).get_repo_info(...).thenReturn({
        "star_count": 10,
        "pull_count": 1000,
    })
    with tempfile.TemporaryDirectory() as temp_dir:
        tempfile_path = os.path.join(temp_dir, 'output.json')

        # Create an initial JSON file with some data
        initial_data = [
            {
                "github_forks": 5,
                "github_open_issues": 500,
                "extra_field": "extra_value"
            }
        ]
        with open(tempfile_path, 'w') as f:
            json.dump(initial_data, f, indent=4)

        # Append new data with different fields
        result = runner.invoke(main, [
            '--github-repo', 'test_owner/test_repo',
            '--dockerhub-repo', 'test_owner/test_repo_docker',
            '--output', tempfile_path,
            '--output-format', 'json',
            '--append',
            '--include-timestamp',
            '--config', 'just_metrics'
        ])

        assert result.exit_code == 0

        with open(tempfile_path, 'r') as f:
            json_array = json.load(f)
            assert len(json_array) == 2
            assert json_array[0]['github_forks'] == 5
            assert json_array[0]['github_open_issues'] == 500
            assert json_array[0]['extra_field'] == 'extra_value'
            assert json_array[1]['github_forks'] == 10
            assert json_array[1]['github_open_issues'] == 1000
            assert json_array[1]['github_watchers'] == 100
            assert json_array[1]['github_stargazers_count'] == 110
            assert json_array[1]['github_subscribers_count'] == 120
            assert json_array[1]['github_download_count'] == 40000
            assert json_array[1]['dockerhub_star_count'] == 10
            assert json_array[1]['dockerhub_pull_count'] == 1000
            assert 'extra_field' not in json_array[1]
