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
        # Get the GitHub API token from the environment variable
        self.github_token = os.getenv('GITHUB_TOKEN')

    def get_github_token(self) -> str:
        """
        Get the GitHub API token

        :return: The GitHub API token
        """
        return self.github_token