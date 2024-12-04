"""
Defines a command for getting the download stats for a github repository
"""

import logging
from datetime import datetime

import click

from repo_metrics.metrics import GitHubMetricsHelper
from repo_metrics.output import CsvOutput, JsonOutput, Output, OutputConfig, OutputType, preprocess

LOGGER = logging.getLogger(__name__)

@click.command(name="github_download_stats")
@click.option(
    "--github-repo",
    "-gh",
    required=False,
    type=str,
    help="The github repository to get download stats for, in the form {owner}/{repo}",
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
    type=click.Choice([o.value for o in OutputType]),
    default=OutputType.JSON.value,
    help="The output format",
)
@click.option(
    "--append",
    "-a",
    is_flag=True,
    help="Append to the output file, if the selected format supports it",
)
@click.option(
    "--include-timestamp",
    "-t",
    is_flag=True,
    help="Include a timestamp in the output",
)
def main(
    github_repo: str,
    output: str,
    output_format: str,
    append: bool,
    include_timestamp: bool,
):
    """
    Get the download stats for a github repository
    """

    data_to_print = []
    data_to_print_labels = []

    # Include the timestamp if set, with some clever labelling so I don't need to special case it
    if include_timestamp:
        data_to_print.append({"time": datetime.now().isoformat()})
        data_to_print_labels.append("date_and_")

    # Get the owner and repo from the github_repo string
    owner, repo = github_repo.split("/")
    helper = GitHubMetricsHelper()
    github_data = helper.get_release_download_counts(owner, repo)
    data_to_print.append(github_data)
    data_to_print_labels.append("")

    output_data = preprocess.merge(data_to_print, data_to_print_labels)

    output_writer: Output = None
    if output_format == "csv":
        output_writer = CsvOutput(output, append)
    else:
        output_writer = JsonOutput(output)

    output_writer.write(output_data)