<!--
style: Microsoft Writing Style Guide
reason: Project landing page optimized for developer onboarding — friendly, task-oriented, progressive-disclosure flow that minimizes cognitive load.
doc-type: reference
audience: Python developers reading or writing ZON data from toolchains and build scripts
-->

# natizon

`natizon` is a pure Python parser and serializer for [ZON (Zig Object Notation)][zig-zon].
It converts ZON text directly into standard Python types, and serializes Python objects back
into valid ZON — all without intermediate AST objects or wrapper layers. Its API is modeled
after the standard library's `json` module, offering `loads()` and `dumps()` as the primary
entry points.

Built on [Lark][lark], the library handles the full ZON grammar, including structs, arrays,
enum literals, multiline strings, hexadecimal and float literals, and quoted identifiers.

> [!NOTE]
> `natizon` is intentionally a little more forgiving than Zig's own `std.zon` parser. This
> leniency makes it easier to consume real-world ZON data in Python without friction.
>
> For example, unquoted Zig keywords like `if` or `fn` parse just fine — but `dumps()` always
> normalizes them to `.@"if"` and `.@"fn"` for strict compatibility when you write back out.

## API Overview

| Function | Signature | Description |
|---|---|---|
| `loads` | `(zon_str, *, use_tuples=False, empty_mode=DICT) → dict` | Parse ZON string to Python dicts/lists. |
| `dumps` | `(obj, *, indent=None, sort_keys=False) → str` | Serialize Python object to ZON string. |
| `validate_zon_serializable` | `(obj) → None` | Validate an object is ZON-serializable; raises `TypeError` or `ValueError`. |

> [Full type mapping reference →][type-mapping]

## Installation

```shell
pip install natizon
```

Or:

```shell
uv add natizon
```

## Usage

`natizon` exposes `loads()` and `dumps()` functions that work similarly to the standard library's `json` module.

> [!TIP]
> **Looking to parse `build.zig.zon`?**
>
> Check out [this Python script][gist-build-zon] for parsing and validating `build.zig.zon`
> to see how to:
> * load Zig 0.16 package metadata using `natizon`,
> * validate fields with Pydantic,
> * and print a pretty JSON dump using Rich.

### Parsing

```python
import natizon

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
parsed_data = natizon.loads(zon_data)

print(parsed_data["package_name"])  # "network_tools"
print(parsed_data["supported_platforms"])  # ["linux", "macos", "windows"]
```

### Serialization

You can serialize standard Python objects back into ZON text using `dumps()`:

```python
from enum import Enum
import natizon


class Difficulty(Enum):
    EASY = "easy"
    HARD = "hard"


game_config = {
    "title": "Neon Dash",
    "difficulty": Difficulty.HARD,
    "player_stats": {"level": 10, "xp": 1500},
}

zon_string = natizon.dumps(game_config, indent=2)
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
>   (`"linux"`). If you want to preserve them as ZON Enum literals, convert them to your `Enum` subclass member
>   (e.g., `Color.RED`) instead.
> * **Enum flags** (`enum.Flag`, `enum.IntFlag`) are not serializable — their bitwise nature lacks a canonical ZON
>   representation. Convert them to a standard `Enum` tag, integer, or array before serialization.
> * **Char literals** (e.g., `'a'`) are parsed into Python integers and will serialize back as integers (`97`).
> * **Empty arrays** (`[]`) serialize to `.{}`, which `loads()` parses as an empty dict by default. Use
>   `EmptyContainerMode.SEQUENCE` if you need them to parse back as lists or tuples.

## Advanced Usage

### Validation

`dumps()` automatically validates your data before serialization. If you need to check whether an object is
serializable without triggering the full serialization process, use `validate_zon_serializable()`:

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

Implement the `ZonEncodable` protocol on your own classes by defining a `to_zon()` method that returns a
`ZonSerializable` type:

```python
from dataclasses import dataclass
import natizon
from natizon import ZonSerializable


@dataclass
class ByteSize:
    bytes: int

    def to_zon(self) -> ZonSerializable:
        return f"{self.bytes}B"


data = {
    "cache_limit": ByteSize(1024),
    "buffer_size": ByteSize(2048),
}

zon_string = natizon.dumps(data, indent=2)
print(zon_string)
```

Output:

<!--pytest-codeblocks:expected-output-->

```zig
.{
  .cache_limit = "1024B",
  .buffer_size = "2048B",
}
```

> [!IMPORTANT]
> If an object implements the `ZonEncodable` protocol, `dumps()` **always**
> prefers its `to_zon()` method over built-in serialization for that object's
> actual type. A subclass of `str`, `int`, or `Enum` that defines `to_zon()`
> is serialized as whatever `to_zon()` returns — not as a string, integer, or
> enum literal.

## License

This project is licensed under the Apache License 2.0. See the [LICENSES][licenses] directory for the full license text.

<!-- Reference-style links -->

[lark]: https://github.com/lark-parser/lark
[zig-zon]: https://ziglang.org/documentation/0.16.0/std/#std.zon
[gist-build-zon]: https://gist.github.com/BratishkaErik/8ec576586ebca98f222e8e7c2bf3d98b
[type-mapping]: docs/type-mapping.md
[licenses]: LICENSES
