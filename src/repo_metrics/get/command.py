from datetime import datetime
import logging

import click

from repo_metrics.metrics import DockerHubMetricsHelper, GitHubMetricsHelper
from repo_metrics.output import OutputConfig, Output, OutputType, CsvOutput, JsonOutput, preprocess

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
@click.option(
    "--config",
    "-c",
    type=str,
    default="just_metrics",
    help="Configuration to use. Use 'just_metrics' for just metrics that change over time, 'everything' for all available fields from the APIs, or a path to a json file with a custom configuration.",
)
def main(github_repo, dockerhub_repo, output, output_format, append, include_timestamp, config):
    """
    Get metrics for the specified repository
    """
    if config == "just_metrics":
        config = OutputConfig.just_metrics()
    elif config == "everything":
        config = OutputConfig.everything()
    else:
        config = OutputConfig.load_from_json_file(config)

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
        # Filter the fields if specified
        if config.github_fields:
            github_data = preprocess.filter(github_data, config.github_fields)
        data_to_print.append(github_data)
        data_to_print_labels.append("github")

    if dockerhub_repo:
        owner, repo = dockerhub_repo.split("/")
        helper = DockerHubMetricsHelper()
        dockerhub_data = helper.get_repo_info(owner, repo)
        # Filter the fields if specified
        if config.dockerhub_fields:
            dockerhub_data = preprocess.filter(dockerhub_data, config.dockerhub_fields)
        data_to_print.append(dockerhub_data)
        data_to_print_labels.append("dockerhub")
    

    repo_info = preprocess.merge(data_to_print, data_to_print_labels)

    output_writer: Output = None
    if output_format == "csv":
        output_writer = CsvOutput(output, append)
    else:
        output_writer = JsonOutput(output)

    output_writer.write(repo_info)