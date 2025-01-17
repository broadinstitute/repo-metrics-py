"""
Defines a command for getting traffic data for a specific GitHub repository
"""

import logging

import click

from repo_metrics.metrics import GitHubMetricsHelper
from repo_metrics.output import CsvOutput, JsonOutput, Output

LOGGER = logging.getLogger(__name__)


@click.command(name="github_traffic_stats")
@click.option(
    "--github-repo",
    "-gh",
    required=False,
    type=str,
    help="The GitHub repository to get traffic stats for, in the form {owner}/{repo}",
)
@click.option(
    "--output",
    "-o",
    type=str,
    default="/dev/stdout",
    help="The output file",
)
@click.option(
    "--output-format",
    "-of",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="The output format",
)
@click.option(
    "--append",
    "-a",
    is_flag=True,
    help="Append to the output file, if the selected format supports it",
)
@click.option(
    "--only-yesterday",
    "-oy",
    is_flag=True,
    help="Only include the data for yesterday (by default includes all available data for the last 14 days)",
)
def main(
    github_repo: str,
    output: str,
    output_format: str,
    append: bool,
    only_yesterday: bool,
):
    """
    Get the traffic data for a specific GitHub repository
    """
    owner, repo = github_repo.split("/")
    helper = GitHubMetricsHelper()
    data = helper.get_repo_traffic(owner, repo, only_yesterday)

    output_writer: Output = None
    if output_format == "json":
        output_writer = JsonOutput(output, append)
    else:
        output_writer = CsvOutput(output, append)

    output_writer.write(data)
