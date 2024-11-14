import mockito
import pytest
import requests

from repo_metrics.metrics.github import GitHubException, GitHubMetricsHelper
from repo_metrics.settings import Settings


@pytest.fixture
def github_helper():
    mockito.when(Settings).get_github_token().thenReturn("test_token")
    return GitHubMetricsHelper()


@pytest.fixture(autouse=True)
def unstub():
    yield
    mockito.unstub()


def test_get_repo_info_success(github_helper):
    owner = "test_owner"
    repo = "test_repo"
    url = f"https://api.github.com/repos/{owner}/{repo}"
    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {"Authorization": "token test_token"}

    mockito.when(requests).get(url, headers=headers).thenReturn(
        mockito.mock({"status_code": 200, "json": lambda: {"name": repo, "full_name": f"{owner}/{repo}"}})
    )
    mockito.when(requests).get(releases_url, headers=headers, params={"page": 1, "per_page": 100}).thenReturn(
        mockito.mock({"status_code": 200, "json": lambda: [{"assets": [{"download_count": 10}]}]})
    )
    mockito.when(requests).get(releases_url, headers=headers, params={"page": 2, "per_page": 100}).thenReturn(
        mockito.mock({"status_code": 200, "json": lambda: []})
    )

    repo_info = github_helper.get_repo_info(owner, repo)

    assert repo_info["name"] == repo
    assert repo_info["full_name"] == f"{owner}/{repo}"
    assert repo_info["download_count"] == 10


def test_get_repo_info_failure(github_helper):
    owner = "test_owner"
    repo = "test_repo"
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": "token test_token"}

    mockito.when(requests).get(url, headers=headers).thenReturn(mockito.mock({"status_code": 404}))

    with pytest.raises(GitHubException):
        github_helper.get_repo_info(owner, repo)


def test_get_download_count_success(github_helper):
    owner = "test_owner"
    repo = "test_repo"
    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {"Authorization": "token test_token"}

    mockito.when(requests).get(releases_url, headers=headers, params={"page": 1, "per_page": 100}).thenReturn(
        mockito.mock(
            {"status_code": 200, "json": lambda: [{"assets": [{"download_count": 10}, {"download_count": 11}]}]}
        )
    )
    mockito.when(requests).get(releases_url, headers=headers, params={"page": 2, "per_page": 100}).thenReturn(
        mockito.mock({"status_code": 200, "json": lambda: []})
    )

    download_count = github_helper._GitHubMetricsHelper__get_download_count(owner, repo)

    assert download_count == 21


def test_get_download_count_failure(github_helper):
    owner = "test_owner"
    repo = "test_repo"
    releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {"Authorization": "token test_token"}

    mockito.when(requests).get(releases_url, headers=headers, params={"page": 1, "per_page": 100}).thenReturn(
        mockito.mock({"status_code": 404})
    )

    with pytest.raises(GitHubException):
        github_helper._GitHubMetricsHelper__get_download_count(owner, repo)
