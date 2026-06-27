"""Check that basic features work.

Catch cases where e.g. files are missing so the import doesn't work. For natizon,
it is especially important to check that the .lark grammar files are successfully
included in the built distribution.
"""

import sys

from natizon import loads


def _check_parse() -> None:
    """Parse a representative ZON string and verify the result."""
    zon_expr = r"""
    .{
        .package_name = "natizon",
        .version = 1,
        .platforms = .{ .linux, .windows }
    }
    """

    expected = {
        "package_name": "natizon",
        "version": 1,
        "platforms": ["linux", "windows"],
    }

    # If the grammar file is missing, loads() will raise a ZonInternalError
    result = loads(zon_expr)

    if result != expected:
        msg = f"Unexpected parse result.\nExpected: {expected}\nGot: {result}"
        raise ValueError(msg)


def main() -> None:
    try:
        _check_parse()
    except Exception as e:
        sys.stderr.write(f"Smoke test failed with exception: {e}\n")
        sys.exit(1)
    else:
        sys.stdout.write(
            "Smoke test succeeded: Package imported and ZON parsed correctly.\n"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
