from natizon import loads


def test_comments_and_whitespace_are_ignored():
    """Check that comments are ignored everywhere."""
    zon_expr = """
    // This is a file header comment
    .{
        // Comment before a key
        .version = "1.0.0", // Inline comment after a value

        // Blank lines and heavy indentation below
            .deps = .{
                1, // trailing comma comment
            }
    }
    """
    expected = {"version": "1.0.0", "deps": [1]}
    assert loads(zon_expr) == expected


def test_deep_nesting_does_not_break_parser():
    """
    Stress tests the AST depth limits for parsing highly nested ZON structures.
    Creates 20 levels of nested empty/single-element structs.
    """
    nest_depth = 20

    # Creates: .{ .{ .{ ... "deep" ... } } }
    zon_expr = (".{" * nest_depth) + '"deep"' + ("}" * nest_depth)

    result = loads(zon_expr)

    # Traverse to the bottom of the nesting
    for _ in range(nest_depth):
        assert isinstance(result, list)
        assert len(result) == 1
        result = result[0]

    assert result == "deep"


def test_empty_string_keys():
    """Tests the edge case of using an empty string as a quoted identifier."""
    zon_expr = r'.{ .@"" = "empty key" }'
    assert loads(zon_expr) == {"": "empty key"}
