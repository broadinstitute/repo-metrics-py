import os
import requests

class GitHubMetricsHelper:
    def __init__(self):
        # Get the GitHub API token from the environment variable
        token = os.getenv('GITHUB_TOKEN')
        self.token = token

    def get_repo_info(self, owner: str, repo: str) -> dict:
        """
        Get info for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: A dictionary containing the repository info
        """
        url = f'https://api.github.com/repos/{owner}/{repo}'
        headers = {'Authorization':f'token {self.token}'}
        response = requests.get(url, headers=headers)
        data = response.json()

        # Get the download count for the repository
        download_count = self.__get_download_count(owner, repo)
        data['download_count'] = download_count

        return data
    
    def __get_download_count(self, owner: str, repo: str) -> int:
        """
        Get the download count for the specified git repository

        :param owner: The owner of the repository
        :param repo: The name of the repository

        :return: The download count
        """
        url = f'https://api.github.com/repos/{owner}/{repo}/releases'
        headers = {'Authorization':f'token {self.token}'}

        # Paginate through the releases to get the download count
        page = 1
        download_count = 0
        while True:
            # Set the per_page parameter to 100 to get the maximum number of releases per page
            params = {'page': page, 'per_page': 100}
            response = requests.get(url, headers=headers, params=params)
            releases = response.json()
            
            for release in releases:
                for asset in release['assets']:
                    download_count += asset['download_count']
            
            # If there are no more releases, break out of the loop
            if not releases:
                break

            page += 1
        
        return download_count

