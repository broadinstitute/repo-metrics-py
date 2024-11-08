from datetime import datetime
import logging

import click

from repo_metrics.metrics import DockerHubMetricsHelper, GitHubMetricsHelper
from repo_metrics.output import Output, CsvOutput, JsonOutput, preprocess

LOGGER = logging.getLogger(__name__)


@click.command(name="get")
@click.option(
    "--github-repo",
    "-gh",
    required=False,
    type=str,
    help="The github repository to get metrics for, in the form {owner}/{repo}",
)
@click.option(
    "--dockerhub-repo",
    "-dh",
    required=False,
    type=str,
    help="The dockerhub repository to get metrics for, in the form {owner}/{repo}",
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
    "--include-timestamp",
    "-t",
    is_flag=True,
    help="Include a timestamp in the output",
)
def main(github_repo, dockerhub_repo, output, output_format, append, include_timestamp):
    """
    Get metrics for the specified repository
    """
    data_to_print = []
    data_to_print_labels = []

    # Include the timestamp if set, with some clever labelling so I don't need to special case it
    if include_timestamp:
        data_to_print.append({"time": datetime.now().isoformat()})
        data_to_print_labels.append("date_and")

    if github_repo:
        owner, repo = github_repo.split("/")
        helper = GitHubMetricsHelper()
        github_data = helper.get_repo_info(owner, repo)
        data_to_print.append(github_data)
        data_to_print_labels.append("github")

    if dockerhub_repo:
        owner, repo = dockerhub_repo.split("/")
        helper = DockerHubMetricsHelper()
        dockerhub_data = helper.get_repo_info(owner, repo)
        data_to_print.append(dockerhub_data)
        data_to_print_labels.append("dockerhub")
    

    repo_info = preprocess.merge(data_to_print, data_to_print_labels)

    output_writer: Output = None
    if output_format == "csv":
        output_writer = CsvOutput(output, append)
    else:
        output_writer = JsonOutput(output)

    output_writer.write(repo_info)