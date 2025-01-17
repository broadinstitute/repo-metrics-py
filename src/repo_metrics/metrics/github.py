import datetime
import logging
import time

import jwt
import requests

from ..settings import Settings


class GitHubException(Exception):
    pass


LOGGER = logging.getLogger(__name__)


class GitHubMetricsHelper:
    """
    A helper class for getting metrics from the GitHub API
    """

    def __init__(self):
        # Get the GitHub API token from the environment variable (if there is one)
        token = Settings().get_github_token()
        self.token: str | None = token

    def get_repo_info(self, owner: str, repo: str) -> dict:
        """
        Get info for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: A dictionary containing the repository info
        """
        url = f"https://api.github.com/repos/{owner}/{repo}"
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            headers = {}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise GitHubException(f"Failed to get info for {owner}/{repo}")
        data = response.json()

        # Get the download count for the repository
        download_count = self.__get_download_count(owner, repo)
        data["download_count"] = download_count

        return data

    def get_release_download_counts(self, owner: str, repo: str) -> dict:
        """
        Get download counts for all releases in the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: A dictionary containing the download counts for each release
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            headers = {}

        release_download_counts = {}

        # Paginate through the releases to get the download counts
        page = 1
        while True:
            # Set the per_page parameter to 100 to get the maximum number of releases per page
            params = {"page": page, "per_page": 100}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubException(f"Failed to get info for {owner}/{repo}")
            releases = response.json()

            # If there are no more releases, break out of the loop
            if not releases:
                break

            for release in releases:
                release_name = release["tag_name"]
                download_count = 0
                for asset in release["assets"]:
                    download_count += asset["download_count"]
                release_download_counts[release_name] = download_count

            page += 1

        return release_download_counts

    def __get_download_count(self, owner: str, repo: str) -> int:
        """
        Get the download count for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: The download count
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            headers = {}

        # Paginate through the releases to get the download count
        page = 1
        download_count = 0
        while True:
            # Set the per_page parameter to 100 to get the maximum number of releases per page
            params = {"page": page, "per_page": 100}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubException(f"Failed to get info for {owner}/{repo}")
            releases = response.json()

            # If there are no more releases, break out of the loop
            if not releases:
                break

            for release in releases:
                for asset in release["assets"]:
                    download_count += asset["download_count"]

            page += 1

        return download_count

    def get_repo_traffic(self, owner: str, repo: str, only_yesterday: bool = False) -> list[dict]:
        """
        Get the traffic data for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository
        :param only_yesterday: Whether to only get the traffic data for yesterday

        :return: A dictionary containing the traffic data

        :raises GitHubException: If any requests fail or if the data returned by the requests is
        not as expected
        """
        # Generate a JWT for the GitHub App that we'll make the requests as
        jwt = self.__create_github_app_jwt()
        # Get the installation id for the app installation on the repository
        installation_id = self.__get_installation_id(owner, repo, jwt)
        # Get an app installation access token which we'll use to make the requests
        token = self.__get_installation_access_token(installation_id, jwt)
        # Get the clones for the past two weeks
        clones = self.__get_traffic_clones(owner, repo, token)
        # Get the views for the past two weeks
        views = self.__get_traffic_views(owner, repo, token)
        # Combine the clones and views data into a dictionary keyed by timestamp
        traffic_data = {}
        for clone in clones["clones"]:
            timestamp = clone["timestamp"]
            traffic_data[timestamp] = {"clones": clone["count"], "unique clones": clone["uniques"]}
        for view in views["views"]:
            timestamp = view["timestamp"]
            if timestamp in traffic_data:
                traffic_data[timestamp]["views"] = view["count"]
                traffic_data[timestamp]["unique views"] = view["uniques"]
            else:
                traffic_data[timestamp] = {"views": view["count"], "unique views": view["uniques"]}

        if only_yesterday:
            # Get a timestamp for yesterday at midnight so we can check for it in the traffic data
            today = datetime.datetime.now(datetime.timezone.utc)
            midnight = datetime.datetime.combine(today, datetime.time.min)
            yesterday = midnight - datetime.timedelta(days=1)
            yesterday_formatted = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")
            # Check if the traffic data contains data for yesterday
            if yesterday_formatted not in traffic_data:
                raise GitHubException("Traffic data for yesterday not found")
            # Filter out all the data except for yesterday
            traffic_data = {yesterday_formatted: traffic_data[yesterday_formatted]}

        # Format the traffic data so it's a list of objects
        traffic_data = [{"timestamp": timestamp, **data} for timestamp, data in traffic_data.items()]

        return traffic_data

    def __create_github_app_jwt(self):
        """
        Creates a JWT for interacting with the GitHub API as a GitHub App
        """
        client_id = Settings().get_github_app_client_id()
        private_key = Settings().get_github_app_private_key()

        if not client_id or not private_key:
            raise GitHubException("GitHub App client ID or private key not found")

        payload = {
            # Issued at time
            "iat": int(time.time()),
            # JWT expiration time (10 minutes maximum)
            "exp": int(time.time()) + 600,
            # GitHub App's client ID
            "iss": client_id,
        }

        return jwt.encode(payload, private_key, algorithm="RS256")

    def __get_installation_id(self, owner, repo, jwt):
        """
        Get the installation ID for the app installation on the specified repo

        :param owner: The owner of the repository
        :param repo: The name of the repository
        :param jwt: The JWT for the GitHub App

        :return: The installation ID

        :raises GitHubException: If the request fails
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/installation"
        if self.token:
            headers = {"Authorization": f"Bearer {jwt}"}
        else:
            headers = {}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise GitHubException(f"Failed to get installation ID for {owner}/{repo}. Response: {response.text}")
        data = response.json()

        return data["id"]

    def __get_installation_access_token(self, installation_id, jwt):
        """
        Get an installation access token for the specified app installation

        :param installation_id: The ID of the app installation
        :param jwt: The JWT for the GitHub App

        :return: The installation access token

        :raises GitHubException: If the request fails
        """
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        if self.token:
            headers = {"Authorization": f"Bearer {jwt}"}
        else:
            headers = {}
        response = requests.post(url, headers=headers)
        if response.status_code != 201:
            raise GitHubException(
                f"Failed to get installation access token for {installation_id}. Response: {response.text}"
            )
        data = response.json()

        return data["token"]

    def __get_traffic_clones(self, owner: str, repo: str, token: str) -> dict:
        """
        Get the traffic clones for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository
        :param token: The installation access token

        :return: A dictionary containing the traffic clones data

        :raises GitHubException: If the request fails
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/traffic/clones"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise GitHubException(f"Failed to get traffic clones for {owner}/{repo}. Response: {response.text}")
        data = response.json()

        return data

    def __get_traffic_views(self, owner: str, repo: str, token: str) -> dict:
        """
        Get the traffic views for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository
        :param token: The installation access token

        :return: A dictionary containing the traffic views data

        :raises GitHubException: If the request fails
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/traffic/views"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise GitHubException(f"Failed to get traffic views for {owner}/{repo}. Response: {response.text}")
        data = response.json()

        return data
