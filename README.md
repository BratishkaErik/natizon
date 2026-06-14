# natizon

`natizon` (short for "native-ZON") is a pure Python parser for
[ZON (Zig Object Notation)](https://ziglang.org/documentation/0.16.0/std/#std.zon). Built on top of
[Lark](https://github.com/lark-parser/lark), it provides a familiar, `json`-like interface for decoding ZON strings
directly into Python data structures: like dictionaries, lists, strings, booleans, and numbers.
It relies strictly on standard Python types, without AST wrappers and so on.

> [!NOTE]
> `natizon` is slightly more lenient than the official `std.zon` parser. This flexibility is intentional,
> making it easier to consume and work with data in Python environments.

## Installation

```shell
pip install natizon
```

or:

```shell
uv add natizon
```

## Usage

`natizon` exposes a `loads()` function that works similarly to the standard library's `json.loads()`.

> [!TIP]
> **Looking to parse `build.zig.zon`?**
>
> Check out this Python script for
> [Parsing and validating build.zig.zon](https://gist.github.com/BratishkaErik/8ec576586ebca98f222e8e7c2bf3d98b)
> to see how to:
> * load Zig 0.16 package metadata using `natizon`,
> * validate fields with `Pydantic`,
> * and print a pretty JSON dump using `Rich`.

```python
from natizon import loads

zon_data = r"""
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

# Parses directly into standard Python dicts and lists
parsed_data = loads(zon_data)

print(parsed_data["package_name"])  # "network_tools"
print(parsed_data["supported_platforms"])  # ["linux", "macos", "windows"]
```

## ZON to Python Type Mapping

When you pass a ZON string to `natizon.loads()`, the parser automatically converts ZON primitives and structures into
their closest Python types.

Here's breakdown:

### Primitives and Literals

| ZON Type              | ZON Example          | Python Type | Python Value     | Notes                                                          |
|:----------------------|:---------------------|:------------|:-----------------|:---------------------------------------------------------------|
| **Null**              | `null`               | `NoneType`  | `None`           |                                                                |
| **Boolean**           | `true`, `false`      | `bool`      | `True`, `False`  |                                                                |
| **Integer**           | `42`, `0x2A`         | `int`       | `42`             |                                                                |
| **Float**             | `3.14`, `inf`, `nan` | `float`     | `3.14`           | Supports ZON-specific keywords: `nan` and `inf`.               |
| **Char Literal**      | `'a'`                | `int`       | `97`             | Evaluates to the integer Unicode code point.                   |
| **String**            | `"Hello"`            | `str`       | `"Hello"`        | Handles standard escapes and Unicode `\u{...}`.                |
| **Multiline String**  | `\\Line 1`           | `str`       | `"Line 1"`       | Strips the `\\` prefix and joins multiple lines with newlines. |
| **Enum Literal**      | `.linux`             | `str`       | `"linux"`        | Parsed simply as strings.                                      |
| **Quoted Identifier** | `.@"complex-key!"`   | `str`       | `"complex-key!"` | Slices off the `@` prefix and evaluates the string.            |

### Structures and Containers

| ZON Type            | ZON Example    | Python Type | Python Value | Notes                                                          |
|:--------------------|:---------------|:------------|:-------------|:---------------------------------------------------------------|
| **Array**           | `.{ 1, 2, 3 }` | `list`      | `[1, 2, 3]`  | Parses as a `tuple` if `use_tuples=True` is set.               |
| **Struct**          | `.{ .x = 1 }`  | `dict`      | `{"x": 1}`   | Raises `ValueError` if duplicate field names are encountered.  |
| **Empty Container** | `.{}`          | `dict`      | `{}`         | Parses using Array rules if `empty_mode` is set to `SEQUENCE`. |

### Configuration

You can customize how `natizon` handles specific ZON structures:

* **`use_tuples`** (`bool`, default `False`): If `True`, parses ZON arrays (e.g., `.{ 1, 2, 3 }`) as Python `tuple`s
  instead of `list`s.
* **`empty_mode`** (`EmptyContainerMode`, default `EmptyContainerMode.DICT`): Controls whether an empty container `.{}`
  becomes an empty dictionary (`{}`) or an empty sequence (`[]` / `()`).

```python
from natizon import loads, EmptyContainerMode

data = loads(".{}", use_tuples=True, empty_mode=EmptyContainerMode.SEQUENCE)
print(data)  # Output: ()
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSES](LICENSES) directory for the full license
text.