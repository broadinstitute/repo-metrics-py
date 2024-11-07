import logging

import click

from repo_metrics.metrics import DockerHubMetricsHelper, GitHubMetricsHelper
from repo_metrics.output import JsonOutput

LOGGER = logging.getLogger(__name__)


@click.command(name="get")
@click.option(
    "--owner",
    required=True,
    type=str,
    help="The owner of the repository",
)
@click.option(
    "--repo",
    required=True,
    type=str,
    help="The name of the repository",
)
@click.option(
    "--output",
    type=str,
    default="/dev/stdout",
    help="The output file",
)
def main(owner, repo, output):
    """
    Get metrics for the specified repository
    """
    helper = GitHubMetricsHelper()
    repo_info = helper.get_repo_info(owner, repo)
    output = JsonOutput(output)
    output.write(repo_info)