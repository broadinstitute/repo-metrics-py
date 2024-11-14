from typing import List

import json

from .output_type import OutputType

class OutputConfig:
    """
    Configuration defining what fields to include in the output
    """

    just_metrics_config = {
        "github_fields": [
            "forks",
            "open_issues",
            "watchers",
            "stargazers_count",
            "subscribers_count",
            "download_count",
        ],
        "dockerhub_fields": [
            "star_count",
            "pull_count",
        ],
    }

    def __init__(self, github_fields: List[str] | None = None, dockerhub_fields: List[str] | None = None):
        self.github_fields = github_fields
        self.dockerhub_fields = dockerhub_fields
    
    @staticmethod
    def just_metrics():
        return OutputConfig(
            github_fields=OutputConfig.just_metrics_config["github_fields"],
            dockerhub_fields=OutputConfig.just_metrics_config["dockerhub_fields"],
        )
    
    @staticmethod
    def everything():
        return OutputConfig(
            github_fields=None,
            dockerhub_fields=None,
        )
    
    @staticmethod
    def load_from_json_file(path: str):
        """
        Loads the configuration from a json file

        :param path: The path to the json file
        :return: The configuration
        """
        with open(path, 'r') as f:
            data = json.load(f)
            return OutputConfig(
                github_fields=data.get("github_fields", None),
                dockerhub_fields=data.get("dockerhub_fields", None),
            )
