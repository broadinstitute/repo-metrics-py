"""
Defines functions for filtering and merging metrics data so it is ready to be handled by the
output classes
"""

from typing import List

def filter(data: dict, fields: List[str] | None) -> dict:
    """
    Filter the data dictionary to only include the fields specified in the fields list

    :param data: The data dictionary
    :param fields: The list of fields to include

    :return: The filtered data dictionary (or the original data dictionary if fields is empty)
    """
    if not fields:
        return data
    return {field: data[field] for field in fields if field in data}

def merge(data: List[dict], labels: List[str] | None) -> dict:
    """
    Merge the data dictionaries in the data list into a single dictionary

    :param data: The list of data dictionaries
    :param labels: The optional list of labels to use for the keys in the merged dictionary

    :return: The merged data dictionary
    """
    merged_data = {}
    for i, data_dict in enumerate(data):
        for key, value in data_dict.items():
            if labels:
                merged_data[f"{labels[i]}_{key}"] = value
            else:
                merged_data[key] = value
    return merged_data

def flatten(data: dict, prefix: str = "") -> dict:
    """
    Flatten the data dictionary so it only contains scalar values

    :param data: The data dictionary

    :return: The flattened data dictionary
    """
    flattened_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            flattened_data.update(flatten(value, f"{prefix}{key}."))
        else:
            flattened_data[prefix + key] = value
    return flattened_data