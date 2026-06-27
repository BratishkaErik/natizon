import pytest

from natizon import EmptyContainerMode, loads


@pytest.mark.parametrize(
    "zon_expr",
    [
        ".{}",
        ".{ }",
        ".{\n\n}",
    ],
    ids=["compact", "spaced", "newlines"],
)
def test_empty_struct(zon_expr: str):
    assert loads(zon_expr) == {}


@pytest.mark.parametrize(
    "zon_expr, use_tuples, empty_mode, expected",
    [
        # Checking `use_tuple` effect
        (".{1,2,3}", True, EmptyContainerMode.DICT, (1, 2, 3)),
        (".{1,2,3}", True, EmptyContainerMode.SEQUENCE, (1, 2, 3)),
        (".{1,2,3}", False, EmptyContainerMode.DICT, [1, 2, 3]),
        (".{1,2,3}", False, EmptyContainerMode.SEQUENCE, [1, 2, 3]),
        # Checking `EmptyContainerMode` effect
        (".{}", True, EmptyContainerMode.DICT, {}),
        (".{}", False, EmptyContainerMode.DICT, {}),
        (".{}", True, EmptyContainerMode.SEQUENCE, ()),
        (".{}", False, EmptyContainerMode.SEQUENCE, []),
    ],
    ids=[
        #
        "array_tuple_dict",
        "array_tuple_seq",
        "array_list_dict",
        "array_list_seq",
        #
        "empty_tuple_dict",
        "empty_list_dict",
        "empty_tuple_seq",
        "empty_list_seq",
    ],
)
def test_parser_options(
    zon_expr: str, use_tuples: bool, empty_mode: EmptyContainerMode, expected
):
    """Tests the effects of parser `loads()` parameters."""

    assert loads(zon_expr, use_tuples=use_tuples, empty_mode=empty_mode) == expected


@pytest.mark.parametrize(
    "zon_expr, expected_list",
    [
        (r".{ 10, 20, 30 }", [10, 20, 30]),
        (r".{ true, null, .missing }", [True, None, "missing"]),
        (r".{ 99, }", [99]),
    ],
    ids=["standard_elements", "mixed_types", "trailing_comma"],
)
def test_array_struct(zon_expr: str, expected_list: list):
    assert loads(zon_expr) == expected_list


@pytest.mark.parametrize(
    "zon_expr, expected_dict",
    [
        (
            r".{ .enable_logging = true, .retries = 3 }",
            {"enable_logging": True, "retries": 3},
        ),
        (
            r'.{ .@"complex-key!" = "data", }',
            {"complex-key!": "data"},
        ),
    ],
    ids=["standard_keys", "quoted_complex_key"],
)
def test_keyed_struct(zon_expr: str, expected_dict: dict):
    assert loads(zon_expr) == expected_dict


def test_nested_struct_composition():
    """Tests a realistic mix of arrays, dicts, strings, and enums inside a struct."""
    zon_expr = r"""
    .{
        .package_name = "network_tools",
        .version = "2.1.0",
        .supported_platforms = .{ .linux, .macos, .windows },
        .dependencies = .{
            .lib_a = .{ .url = "https://server.com/a.tar" },
            .lib_b = .{ .path = "../local_b" }
        }
    }
    """
    expected_structure = {
        "package_name": "network_tools",
        "version": "2.1.0",
        "supported_platforms": ["linux", "macos", "windows"],
        "dependencies": {
            "lib_a": {"url": "https://server.com/a.tar"},
            "lib_b": {"path": "../local_b"},
        },
    }
    assert loads(zon_expr) == expected_structure
