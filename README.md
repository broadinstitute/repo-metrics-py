# Repo Metrics
This is a tool for retrieving metrics for a project from a few different places (currently just GitHub and DockerHub, but more to come later).

Current version: 0.0.1

## Installation

    pip install .

## Usage

Currently, the only command for the tool is `get`.  For example:

    repo_metrics get -gh broadinstitute/gatk

Running the command above will retrieve metrics from the GATK GitHub repo, and write a selection of them to stdout as JSON.

### Sources

Two sources of data are currently supported: GitHub and DockerHub.  It is possible to retrieve data from both in one command:

    repo_metrics get -gh broadinstitute/gatk -dh broadinstitute/gatk

When retrieving data for both, the keys for each value will be prefixed with the name of the source.

#### Private GitHub repos

It is possible to retrieve metrics from private GitHub repos by setting the `GITHUB_TOKEN` environment variable with a GitHub API token corresponding to an account that has access to that repo.

### Output formats

Two output are currently supported: JSON and CSV.  JSON is the default output format.  Output format is specified using the `-of` option:

    repo_metrics get -gh broadinstitute/gatk -of csv -o output.csv

You can also use the `-a` option with CSV output to append to the specified file.

### Output config

The GitHub and DockerHub APIs both provide a lot of information that you mostly probably don't want to record over and over again.  The tool provides functionality for filtering what values will actually be written to the output.  You can provide a custom config for what values to include using a JSON file like this:

    repo_metrics get -gh broadinstitute/gatk -dh broadinstitute/gatk -c config.json

where the contents of the config.json file are:

    {
        "github_fields": [
            "forks",
            "open_issues",
            "watchers",
            "stargazers_count",
            "subscribers_count",
            "download_count"
        ],
        "dockerhub_fields": [
            "star_count",
            "pull_count"
        ]
    }

There are also two built-in configurations that can be used without a file.  The default (`just_metrics`) matches the configuration above.  The other option is `everything`, which will give you every field for every specified source.

    repo_metrics get -gh broadinstitute/gatk -dh broadinstitute/gatk -c everything

### Timestamps

The tool can also include a timestamp in the output using the `-t` flag.  This will be prepended to the output with the key `date_and_time`.

## Development

To do development in this codebase, the python3 development package must
be installed.

After installation the development environment can be set up by
the following commands:

    python3 -mvenv venv
    . venv/bin/activate
    pip install -r dev-requirements.txt
    pip install -e .

### Linting files

    # run all linting commands
    tox -e lint

    # reformat all project files
    black src tests setup.py

    # sort imports in project files
    isort -rc src tests setup.py

    # check pep8 against all project files
    flake8 src tests setup.py

    # lint python code for common errors and codestyle issues
    pylint src

### Tests

    # run all linting and test
    tox

    # run only (fast) unit tests
    tox -e unit

    # run only linting
    tox -e lint

Note: If you run into "module not found" errors when running tox for testing, verify the modules are listed in test-requirements.txt and delete the .tox folder to force tox to refresh dependencies.

### Versioning

We use `bumpversion` to maintain version numbers.
*DO NOT MANUALLY EDIT ANY VERSION NUMBERS.*

Our versions are specified by a 3 number semantic version system (https://semver.org/):

	major.minor.patch

To update the version with bumpversion do the following:

`bumpversion PART` where PART is one of:
- major
- minor
- patch

This will increase the corresponding version number by 1.

