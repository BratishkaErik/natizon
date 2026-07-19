<!--
style: Google Developer Documentation Style Guide
reason: Concise reference for ZON↔Python type conversions, edge cases, and configuration — focused on API-facing behavior.
doc-type: reference
audience: Python developers using natizon to parse or produce ZON data.
-->

# ZON ↔ Python Type Mapping

This reference documents how `natizon.loads()` maps ZON types to Python types, how
`natizon.dumps()` maps Python types to ZON output, and the edge cases, configuration
knobs, and roundtrip limitations that govern each conversion.

---

## `loads()`: ZON → Python

### Primitives and Literals

| ZON Type | ZON Example | Python Type | Python Value | Notes |
|---|---|---|---|---|
| **Null** | `null` | `NoneType` | `None` | |
| **Boolean** | `true`, `false` | `bool` | `True`, `False` | |
| **Integer** | `42`, `0x2A` | `int` | `42` | Negative zero (`-0`) is **rejected** with `ValueError`. |
| **Float** | `3.14`, `inf`, `nan` | `float` | `3.14` | `-nan` is **rejected** by the grammar. |
| **Char Literal** | `'a'` | `int` | `97` | ⚠️ **Does not roundtrip:** serializes back as an integer, not a char literal. Incomplete hex escapes (`'\x7'`) and invalid Unicode hex (`'\u{G}'`) are rejected. |
| **String** | `"Hello"` | `str` | `"Hello"` | Non-printable ASCII control bytes (0x00–0x1F) are accepted. Embedded null bytes are **allowed** in strings. |
| **Multiline String** | `\\Line 1` | `str` | `"Line 1"` | Strips the `\\` prefix and `\r` from each line; joins lines with `\n`. |
| **Enum Literal** | `.linux` | `str` | `"linux"` | ⚠️ **Does not roundtrip as an enum literal:** serializes back as `"linux"`. To preserve the ZON enum literal form, convert to an `Enum` subclass member before calling `dumps()`. |
| **Quoted Identifier** | `.@"complex-key!"` | `str` | `"complex-key!"` | Null bytes (`\x00`) in the identifier are **rejected** with `ValueError`. An empty quoted identifier (`.@""`) is valid and parses to key `""`. |

### Structures and Containers

| ZON Type | ZON Example | Python Type | Python Value | Notes |
|---|---|---|---|---|
| **Array** | `.{ 1, 2, 3 }` | `list` | `[1, 2, 3]` | Parses as a `tuple` when `use_tuples=True`. |
| **Struct** | `.{ .x = 1 }` | `dict` | `{"x": 1}` | Duplicate field names raise `ValueError`. Non-empty structs with key-value pairs are unambiguous. |
| **Empty Container** | `.{}` | `dict` or `list` or `tuple` | `{}` / `[]` / `()` | Controlled by `empty_mode` (default: `EmptyContainerMode.DICT` → `{}`). With `EmptyContainerMode.SEQUENCE`, returns `[]` (or `()` when `use_tuples=True`). ⚠️ **Ambiguous roundtrip:** an empty ZON array serializes to `.{}`, which under default settings parses back as `{}`. |

> **Parser leniency note:** `natizon` accepts Zig keywords (e.g., `if`, `fn`) as unquoted identifiers
> during parsing — more lenient than `std.zon` but intentional for consuming real-world data. When
> serializing via `dumps()`, these are always normalized to the quoted form (`.@"if"`, `.@"fn"`).

### Configuration

`loads()` accepts two parameters to control disambiguation of ambiguous ZON structures:

- **`use_tuples`** (`bool`, default `False`): When `True`, ZON arrays (e.g., `.{ 1, 2, 3 }`) are
  parsed as Python `tuple` instead of `list`. Affects non-empty arrays and empty containers when
  `empty_mode` is `SEQUENCE`.
- **`empty_mode`** (`EmptyContainerMode`, default `EmptyContainerMode.DICT`): Determines how the
  empty container `.{}` is interpreted.
  - `DICT` (default): returns an empty Python `dict` — suitable when the expected payload is a struct.
  - `SEQUENCE`: returns an empty `list` (or `tuple` if `use_tuples=True`) — suitable when the
    expected payload is an array.

```python
import natizon
from natizon import EmptyContainerMode

result = natizon.loads(".{}", use_tuples=True, empty_mode=EmptyContainerMode.SEQUENCE)
print(result)  # ()
```

---

## `dumps()`: Python → ZON

### Primitives and Collections

| Python Type | Python Value | ZON Output | Notes                                                                                                                                                                          |
|---|---|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `NoneType` | `None` | `null` |                                                                                                                                                                                |
| `bool` | `True`, `False` | `true`, `false` |                                                                                                                                                                                |
| `int` | `42`, `-7` | `42`, `-7` |                                                                                                                                                                                |
| `float` | `3.14`, `nan`, `inf` | `3.14`, `nan`, `inf` | `nan`, `inf`, and `-inf` map to ZON float keywords.                                                                                                                            |
| `str` | `"hello\nworld"` | `"hello\nworld"` | Strings are properly escaped.                                                                    |
| `Enum` (subclasses of `Enum`, `IntEnum`, `StrEnum`) | `Color.RED` | `.RED` | Uses the member **name**, not its value.                                                                                                                                       |
| **`enum.Flag`, `enum.IntFlag`** | *(any value)* | *(not serializable)* | ❌ **Rejected** with `TypeError`: *"Flag/IntFlag serialization is ambiguous"*. Convert to a standard `Enum`, integer, or array before serialization.                            |
| `Sequence` (`list`, `tuple`, `deque`, `range`, `bytearray`, `UserList`, `namedtuple`) | `[1, 2, 3]` | `.{ 1, 2, 3 }` | Empty sequences produce `.{}`. ⚠️ **Ambiguous roundtrip:** see empty container note above.                                                                                     |
| `Mapping` (`dict`, `MappingProxyType`, `ChainMap`, `Counter`) | `{"x": 1}` | `.{ .x = 1 }` | Non-string keys raise `TypeError`.                                                                                                                                             |
| **`ZonEncodable`** (protocol with `to_zon()`) | `obj.to_zon()` | *(varies)* | ⚠️ **Takes precedence** over all built-in type handlers — a subclass of `str`, `int`, or `Enum` that implements `to_zon()` uses the protocol result, not the built-in mapping. |

### Identifier Formatting Rules

When serializing `Mapping` keys and `Enum` member names, `dumps()` formats them as ZON identifiers:
- If escaping is needed (special characters, Zig keywords) → `.@"..."` syntax.
- Otherwise → `.name` syntax.

> **Non-string keys:** `Mapping` types with non-string keys raise `TypeError`:
> *"ZON dictionary keys must be strings, found \<type\>"*.

### Validation

| Condition | Error Type |
|---|---|
| `enum.Flag` / `enum.IntFlag` member | `TypeError` |
| Non-string `Mapping` key | `TypeError` |
| Unserializable type | `TypeError` |
| Circular reference | `ValueError` |
| Negative `indent` value | `ValueError` |

Use `natizon.validate_zon_serializable()` to check without producing output.

### Configuration

`dumps()` accepts two parameters:

- **`indent`** (`int | str | None`, default `None`): Controls output formatting.
  - Non-negative integer: indents each level with that many spaces.
  - String (e.g., `"\t"`): used verbatim as the indent per level.
  - `None`: produces compact, single-line output.
- **`sort_keys`** (`bool`, default `False`): When `True`, `Mapping` keys are output in sorted order.

---

## Roundtrip Compatibility

These constructs do not roundtrip unchanged:

| Construct | `loads()` result | `dumps()` result | Workaround |
|---|---|---|---|
| Enum literal (`.linux`) | `str` `"linux"` | `"linux"` (quoted string) | Convert to an `Enum` subclass member before calling `dumps()`. |
| Char literal (`'a'`) | `int` `97` | `97` (integer) | Manually format as `'a'` post-serialization if needed. |
| Empty array → `.{}` (as ZON input) | `dict` `{}` (default) | `.{}` (looks like empty struct) | Use `EmptyContainerMode.SEQUENCE` when calling `loads()`. |
| ZON keywords as identifiers | Accepted | `.@"keyword"` | Output is spec-compliant — no real loss. |
