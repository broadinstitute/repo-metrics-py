"""
Defines and sets the settings that may need to be retrieved from the environment or w/e.
"""

import os


class Settings:
    """
    A class to store settings for the application
    """

    def __init__(self):
        """
        Initialize the settings
        """
        # Get the GitHub config info from the environment variable
        self.github_token: str | None = os.getenv("GITHUB_TOKEN")
        self.github_app_client_id: str | None = os.getenv("GITHUB_APP_CLIENT_ID")
        # Github app private key is in a file, so we need to read it
        self.github_app_private_key: str | None = None
        private_key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
        if private_key_path:
            with open(private_key_path, "r") as f:
                self.github_app_private_key = f.read()

    def get_github_token(self) -> str:
        """
        Get the GitHub API token

        :return: The GitHub API token
        """
        return self.github_token

    def get_github_app_client_id(self) -> str:
        """
        Get the GitHub App client ID, needed for API calls made as a GitHub App (since some API
        endpoints can only be accessed by Apps)

        :return: The GitHub App client ID
        """
        return self.github_app_client_id

    def get_github_app_private_key(self) -> str:
        """
        Get the path to the private key, needed for API calls made as a GitHub App (since some API
        endpoints can only be accessed by Apps)

        :return: The path to the private key file
        """
        return self.github_app_private_key
