# natizon

`natizon` (short for "native-ZON") is a pure Python parser and serializer for
[ZON (Zig Object Notation)](https://ziglang.org/documentation/0.16.0/std/#std.zon). Built on top of
[Lark](https://github.com/lark-parser/lark), it provides a familiar, `json`-like interface for decoding ZON strings
directly into Python data structures, and for encoding Python data structures back into ZON text.
It relies strictly on standard Python types, without AST wrappers and so on.

> [!NOTE]
> `natizon` is slightly more lenient than the official `std.zon` parser. This
> flexibility is intentional, making it easier to consume and work with data
> in Python environments.
>
> For example, you can safely parse ZON containing
> unquoted keywords like `if` or `fn`, but `dumps()` will always normalize
> these to `.@"if"` and `.@"fn"` to guarantee strict compatibility.

## Installation

```shell
pip install natizon
```

or:

```shell
uv add natizon
```

## Usage

`natizon` exposes `loads()` and `dumps()` functions that work similarly to the standard library's `json` module.

> [!TIP]
> **Looking to parse `build.zig.zon`?**
>
> Check out this Python script for
> [Parsing and validating build.zig.zon](https://gist.github.com/BratishkaErik/8ec576586ebca98f222e8e7c2bf3d98b)
> to see how to:
> * load Zig 0.16 package metadata using `natizon`,
> * validate fields with `Pydantic`,
> * and print a pretty JSON dump using `Rich`.

### Parsing

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

### Serialization

You can serialize standard Python objects back into ZON text using `dumps()`:

```python
from enum import Enum
from natizon import dumps


class Difficulty(Enum):
    EASY = "easy"
    HARD = "hard"


game_config = {
    "title": "Neon Dash",
    "difficulty": Difficulty.HARD,
    "player_stats": {"level": 10, "xp": 1500},
}

zon_string = dumps(game_config, indent=2)
print(zon_string)
```

Output:

<!--pytest-codeblocks:expected-output-->

```zig
.{
  .title = "Neon Dash",
  .difficulty = .HARD,
  .player_stats = .{
    .level = 10,
    .xp = 1500,
  },
}
```

> [!NOTE]
> While `loads()` and `dumps()` are designed to be compatible, some ZON-specific constructs do not roundtrip exactly:
> * **Enum literals** (e.g., `.linux`) are parsed into Python strings and will serialize back as quoted strings
    (`"linux"`). If you want to preserve them as ZON Enum literals, convert them to your `Enum` subclass member
    (e.g.,`Color.RED`) instead.
> * **Enum flags** (`enum.Flag`, `enum.IntFlag`) are not serializable, as their bitwise nature lacks a canonical ZON
    representation. To include them in your output, convert them to a standard `Enum` tag, integer, or array first.
> * **Char literals** (e.g., `'a'`) are parsed into Python integers and will serialize back as integers (`97`).
> * **Empty arrays** (`[]`) serialize to `.{}`, which `loads()` parses as an empty dict by default. Use
    `EmptyContainerMode.SEQUENCE` if you need them to parse back as lists/tuples.

## Advanced Usage

### Validation

`dumps()` automatically validates your data before serialization. However, if you need to check if an object is
serializable without triggering the full serialization process, you can use `validate_zon_serializable()`:

```python
from natizon import validate_zon_serializable

user_settings = {
    "theme": "dark",
    "font_size": 14,
    "notifications": True,
}

# Raises TypeError if the object is not serializable,
# or ValueError if a circular reference is detected.
try:
    validate_zon_serializable(user_settings)
    print("Data is valid!")
except (TypeError, ValueError) as e:
    print(f"Validation failed: {e}")
```

### Custom Serialization

If you have custom classes that you want to serialize into ZON, you can implement the `ZonEncodable` protocol. Simply
define a `to_zon()` method that returns a `ZonSerializable` type.

```python
from dataclasses import dataclass
from natizon import dumps, ZonSerializable


@dataclass
class ByteSize:
    bytes: int

    def to_zon(self) -> ZonSerializable:
        return f"{self.bytes}B"


data = {
    "cache_limit": ByteSize(1024),
    "buffer_size": ByteSize(2048),
}

print(dumps(data, indent=2))
```

Output:

<!--pytest-codeblocks:expected-output-->

```zig
.{
  .cache_limit = "1024B",
  .buffer_size = "2048B",
}
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

* **`use_tuples`** (`bool`, default `False`): If `True`, parses ZON arrays (e.g., `.{ 1, 2, 3 }`) as Python `tuple`s
  instead of `list`s.
* **`empty_mode`** (`EmptyContainerMode`, default `EmptyContainerMode.DICT`): Controls whether an empty container `.{}`
  becomes an empty dictionary (`{}`) or an empty sequence (`[]` / `()`).

```python
from natizon import EmptyContainerMode, loads

data = loads(".{}", use_tuples=True, empty_mode=EmptyContainerMode.SEQUENCE)
print(data)  # Output: ()
```

## Python to ZON Type Mapping

When you pass a Python object to `natizon.dumps()`, it is converted to its natural ZON representation.

| Python Type    | Python Value     | ZON Output        | Notes                                                                                                  |
|:---------------|:-----------------|:------------------|:-------------------------------------------------------------------------------------------------------|
| `NoneType`     | `None`           | `null`            |                                                                                                        |
| `bool`         | `True`, `False`  | `true`, `false`   |                                                                                                        |
| `int`          | `42`, `-7`       | `42`, `-7`        |                                                                                                        |
| `float`        | `3.14`           | `3.14`            | `nan`, `inf`, and `-inf` are serialized as ZON keywords.                                               |
| `str`          | `"hello\nworld"` | `"hello\\nworld"` | Special characters are escaped; output is always a quoted string.                                      |
| `Enum`         | `Color.RED`      | `.RED`            | Maps to ZON Enum Literals using the member **name**.                                                   |
| `Sequence`     | `[1, 2, 3]`      | `.{ 1, 2, 3 }`    | Maps all `Sequence` types (e.g., `list`, `tuple`, `deque`, `range`).                                   |
| `Mapping`      | `{"x": 1}`       | `.{ .x = 1 }`     | Keys become ZON identifiers; non-plain keys use `.@"..."` syntax.                                      |
| `ZonEncodable` | `obj.to_zon()`   | *Variable*        | **Custom:** User defines the serialization (can return any supported type above, e.g., `str`, `dict`). |

**Note:** For `Mapping` types, only string keys are supported. Non-string keys will result in a `TypeError`.

### Configuration

* **`indent`** (`int | str | None`, default `None`): If a non-negative integer, indents with that many spaces per level.
  If a string (like `"\t"`), uses that string to indent each level. If `None`, outputs a compact, single-line
  representation.
* **`sort_keys`** (`bool`, default `False`): If `True`, dictionary keys are output in sorted order.

## License

This project is licensed under the Apache License 2.0. See the [LICENSES](LICENSES) directory for the full license
text.