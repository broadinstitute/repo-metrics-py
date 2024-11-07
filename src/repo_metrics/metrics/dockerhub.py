import requests

class DockerHubMetricsHelper:
    def __init__(self):
        pass

    def get_repo_info(self, owner: str, repo: str) -> dict:
        """
        Get info for the specified dockerhub repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: A dictionary containing the repository info
        """
        url = f'https://hub.docker.com/v2/repositories/{org}/{repo}'
        response = requests.get(url, headers=headers)
        return response.json()
