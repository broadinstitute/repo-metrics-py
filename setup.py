from io import open

from setuptools import find_packages, setup

# following src dir layout according to
# https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
version = "0.0.1"
setup(
    name="repo_metrics",
    version=version,
    description="CLI tool for retreiving and storing metrics for your code project",
    author="Kevin Lydon",
    author_email="klydon@broadinstitute.org",
    license="BSD 3-Clause",
    long_description=open("README.md").read(),
    install_requires="""
    click
    requests
    python-dotenv
    pyjwt
    """.split(
        "\n"
    ),
    tests_require=["coverage", "pytest"],
    python_requires=">=3.10",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD 3-Clause",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["repo_metrics=repo_metrics.__main__:main_entry"]},
    include_package_data=True,
)
