from repo_metrics.output.preprocess import filter, flatten, merge


def test_filter_empty_fields():
    data = {"name": "test", "value": 123}
    fields = []
    result = filter(data, fields)
    assert result == data


def test_filter_non_empty_fields():
    data = {"name": "test", "value": 123, "description": "example"}
    fields = ["name", "value"]
    result = filter(data, fields)
    expected = {"name": "test", "value": 123}
    assert result == expected


def test_filter_non_existing_fields():
    data = {"name": "test", "value": 123}
    fields = ["non_existing_field"]
    result = filter(data, fields)
    expected = {}
    assert result == expected


def test_filter_mixed_fields():
    data = {"name": "test", "value": 123, "description": "example"}
    fields = ["name", "non_existing_field"]
    result = filter(data, fields)
    expected = {"name": "test"}
    assert result == expected


def test_merge_without_labels():
    data = [{"name": "test1", "value": 123}, {"name": "test2", "value": 456}]
    result = merge(data, None)
    expected = {"name": "test2", "value": 456}
    assert result == expected


def test_merge_with_labels():
    data = [{"name": "test1", "value": 123}, {"name": "test2", "value": 456}]
    labels = ["first", "second"]
    result = merge(data, labels)
    expected = {"first_name": "test1", "first_value": 123, "second_name": "test2", "second_value": 456}
    assert result == expected


def test_flatten_simple():
    data = {"name": "test", "value": 123}
    result = flatten(data)
    expected = {"name": "test", "value": 123}
    assert result == expected


def test_flatten_nested():
    data = {"name": "test", "details": {"value": 123, "description": "example"}}
    result = flatten(data)
    expected = {"name": "test", "details.value": 123, "details.description": "example"}
    assert result == expected


def test_flatten_deeply_nested():
    data = {"name": "test", "details": {"value": 123, "more_details": {"description": "example"}}}
    result = flatten(data)
    expected = {"name": "test", "details.value": 123, "details.more_details.description": "example"}
    assert result == expected
