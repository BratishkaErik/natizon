"""Check that basic features work.

Catch cases where e.g. files are missing so the import doesn't work. For natizon,
it is especially important to check that the .lark grammar files are successfully
included in the built distribution.
"""

import sys

from natizon import loads  # noqa: F401


def main():
    # A representative ZON string testing structs, arrays, enums, strings, and ints
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

    try:
        # If the grammar file is missing, loads() will raise a ZonInternalError
        result = loads(zon_expr)

        if result == expected:
            print("Smoke test succeeded: Package imported and ZON parsed correctly.")
            sys.exit(0)
        else:
            print(
                f"Smoke test failed: Unexpected parse result.\nExpected: {expected}\nGot: {result}"
            )
            sys.exit(1)

    except Exception as e:
        print(f"Smoke test failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
