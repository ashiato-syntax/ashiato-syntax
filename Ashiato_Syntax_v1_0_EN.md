# Ashiato Syntax v1.0 — Freeze Compact
## English Specification

**Status:** Draft / v1.0 Freeze Candidate

---

# 1. Basic Form

Ashiato Syntax is enclosed by the following Unicode delimiters.

```text
⟦ ... ⟧
```

The basic form is as follows.

```text
⟦as:1,g:<geohash>[,<field>...]⟧
```

Example:

```text
⟦as:1,g:9q8yyk⟧
```

---

# 2. Fixed Header

Every Ashiato Syntax v1.0 string must begin with the following fixed header.

```text
as:1
```

`as:1` indicates Major Version 1 of Ashiato Syntax.

`as:1` and `g:<geohash>` are treated as the fixed header.

```text
⟦
  as:1
  ,
  g:<geohash>
  ,
  ...
⟧
```

`as` and `g` are mandatory, and their order is fixed.

---

# 3. Logical Model of Fields

The logical structure of Ashiato Syntax is very simple.

```text
Active = AND(fields)

Field = OR(values)
```

In other words,

- Fields are combined with AND
- Multiple values within the same field are combined with OR

For example,

```text
d:0101.0505,w:67
```

means

```text
(Jan 1 OR May 5)
AND
(Saturday OR Sunday)
```

Therefore,

```text
d:0101.0505,w:67,t:uo-a0
```

means

```text
(Jan 1 OR May 5)
AND
(Saturday OR Sunday)
AND
(18:00–06:00)
```

Ashiato Syntax v1.0 does not support arbitrary Boolean expressions or parenthesized logical expressions.

---

# 4. Location Field: g

## Format

```text
g:<geohash>
```

`g` uses a standard Geohash.

Example:

```text
g:9q8yyk
```

A Geohash represents a **Geohash Cell**, not a single precise point.

Therefore,

```text
g:9q8yyk
```

means "that Geohash Cell," not one exact coordinate.

---

## Geohash Specification

Ashiato Syntax does not define its own latitude/longitude encoding scheme.

Interpretation of `g` follows the standard Geohash specification.

The Geohash alphabet is as follows.

```text
0123456789bcdefghjkmnpqrstuvwxyz
```

Uppercase letters are not used.

---

## Geohash Length

In v1.0, the Geohash length is

```text
1–12 characters
```

Geohash length is verified by Semantic Validation, not by the Syntax Grammar.

Approximate cell sizes are as follows.

| Length | Approx. Cell Size |
|---:|---:|
| 5 | several km |
| 6 | ~1 km |
| 7 | ~100 m |
| 8 | tens of meters |
| 9 | several meters |
| 10 | ~1 m |

These are approximate values; actual cell dimensions vary with latitude.

---

## Distance Matching

Ashiato Syntax does not specify how to determine distance between `g` and the current location.

For example, a client may adopt:

- whether the current location is inside the Geohash Cell
- whether the distance to the cell is within a threshold
- whether the distance to the cell center is within a threshold
- a custom judgment that accounts for GPS accuracy

All of these are the responsibility of the Client/Application.

---

# 5. UTC Offset Field: z

## Format

```text
z:<signed-base36>
```

`z` expresses a fixed UTC Offset in minutes.

`z` is not an IANA Time Zone.

For example,

```text
z:+f0
```

means

```text
UTC+09:00
```

Time Zone identifiers such as `Asia/Tokyo` are not used.

---

## Fixed UTC Offset

`z` is a fixed value, not a Time Zone that changes depending on the moment of evaluation.

Therefore,

```text
z:+f0
```

always means UTC+09:00.

DST and political Time Zone rules are not applied.

---

## Value Range

In v1.0, the allowed range is

```text
-1440 <= z <= +1440
```

This is not intended as a fully compatible representation of an IANA Time Zone or an ISO 8601 Time Zone Offset.

`z` in Ashiato v1.0 is defined as its own value type: a **fixed UTC Offset expressed in minutes**.

v1.0 does not validate the offset value for general Time Zone plausibility; it is treated simply as an integer in the range `-1440`–`+1440`.

---

## Signed Base36

`z` is expressed as signed Base36.

- Positive → `+`
- Negative → `-`
- Zero → unsigned

Examples:

```text
0     → 0
540   → +f0
-300  → -8c
```

`+0` and `-0` may be syntactically accepted, but the Semantic Value is 0.

In Canonical Form, `z` is omitted when it is 0.

---

## Default Value

If `z` is omitted, its value is `0`.

Therefore,

```text
⟦as:1,g:9q8yyk⟧
```

and

```text
⟦as:1,g:9q8yyk,z:0⟧
```

are semantically equivalent.

In Canonical Form, `z:0` is omitted.

---

# 6. Absolute Time: s / e

## Overview

`s` and `e` express an absolute validity period.

```text
s:<unix-minute>
e:<unix-minute>
```

The values used here are not raw Unix Timestamp seconds, but

**integer minutes elapsed since the Unix epoch**.

Definition:

```text
unix_minute = floor(unix_time_seconds / 60)
```

---

## UTC Basis

`s` and `e` are always interpreted as UTC-based Unix Minutes.

`z` is not applied to the interpretation of `s` or `e`.

Therefore, given

```text
z:+f0,s:100,e:200
```

the following holds:

```text
s/e → UTC-based Unix Minute
z    → applied only to the local datetime for d/w/t
```

## Value Range

`s` and `e` are treated as **non-negative integers**.

Therefore,

```text
s >= 0
e >= 0
```

must hold.

v1.0 sets no upper bound on `s` / `e`.

In the ABNF, `s` / `e` are written as `base36`, but the Semantic Model treats them as integer values.

---

# 7. Evaluation of s

When only `s` is present, it is Active when

```text
s <= current_unix_minute
```

holds.

Example:

```text
⟦as:1,g:9q8yyk,s:100⟧
```

| current_unix_minute | Result |
|---:|---|
| 99 | No Match |
| 100 | Match |
| 101 | Match |

---

# 8. Evaluation of e

When only `e` is present, it is Active when

```text
current_unix_minute < e
```

holds.

Example:

```text
⟦as:1,g:9q8yyk,e:200⟧
```

| current_unix_minute | Result |
|---:|---|
| 199 | Match |
| 200 | No Match |
| 201 | No Match |

---

# 9. When Both s and e Are Present

When both `s` and `e` are present, the condition is

```text
s <= current_unix_minute < e
```

That is, a half-open interval

```text
[s, e)
```

When both `s` and `e` are present,

```text
s < e
```

must hold.

Therefore,

```text
s:100,e:200
```

is valid, but

```text
s:200,e:100
```

is a Semantic Validation Error.

Likewise,

```text
s:100,e:100
```

is also invalid.

---

# 10. d: Month-Day Field

## Format

```text
d:<month-day>[.<month-day>...]
```

Example:

```text
d:0101
```

```text
d:0101.0505
```

Expressed in `MMDD` format.

---

## OR Semantics

Multiple values within the same `d` field are combined with OR.

```text
d:0101.0505
```

means

```text
January 1 OR May 5
```

---

## Calendar Validation

The syntactic form of `d` is `4DIGIT`.

Whether the value forms a real calendar month/day is verified by Semantic Validation.

For example:

| Input | Valid | Match |
|---|---|---|
| `d:0101` | Yes | January 1 only |
| `d:0231` | No | — |
| `d:1332` | No | — |
| `d:0229` | Yes | February 29 in leap years only |

`d:0229` is a valid condition, but it does not match in non-leap years.

The year used to determine leap years is the year of the `local_datetime` produced by applying `z`.

The Gregorian Calendar is used.

---

# 11. w: Weekday Field

## Format

```text
w:<weekday-value>
```

Weekdays are expressed as follows.

```text
1 = Monday
2 = Tuesday
3 = Wednesday
4 = Thursday
5 = Friday
6 = Saturday
7 = Sunday
```

---

## OR Semantics

For example,

```text
w:67
```

means

```text
Saturday OR Sunday
```

`w` is not a Base36 encoding.

`6` and `7` each represent the weekday number directly.

---

## Validation

Each character of `w` must be one of `1`–`7`.

Duplicate weekdays are allowed; Canonicalization removes duplicates.

Therefore,

```text
w:67
```

is valid.

```text
w:667
```

is also valid, and in Canonical Form becomes

```text
w:67
```

Since both `d` and `w` carry set semantics, duplicate values are permitted on input and normalized during Canonicalization.

---

# 12. t: Time-of-Day Field

## Format

```text
t:<start>-<end>
```

`t` expresses a single interval of local time-of-day.

Example:

```text
t:f0-uo
```

means

```text
09:00 <= local_time < 18:00
```

---

# 13. local_minute_of_day

Evaluation of `t` uses

```text
local_minute_of_day = hour * 60 + minute
```

The range is

```text
0 <= local_minute_of_day <= 1439
```

Examples:

```text
00:00 → 0
06:00 → 360
09:00 → 540
18:00 → 1080
23:59 → 1439
```

---

# 14. Evaluation of t

Semantic Validation verifies that `t`'s `start` and `end` each satisfy

```text
0 <= start <= 1439
0 <= end <= 1439
```

Therefore, the value of `t` must fall within one day's time range.

`t` is evaluated as an interval on a 24-hour circular ring.

### start < end

```text
match =
    start <= local_minute_of_day < end
```

### start > end

```text
match =
    local_minute_of_day >= start
    OR
    local_minute_of_day < end
```

### start == end

```text
invalid
```

`start == end` does not mean "24 hours."

A full 24-hour, unconditional time range can only be expressed by omitting `t`.

---

# 15. Midnight Crossing in t

For example,

```text
t:uo-a0
```

means

```text
18:00–24:00
OR
00:00–06:00
```

This means "until 06:00 the next day," but it does not automatically roll the calendar date / weekday evaluated for `d` and `w` over to the next day.

Each instant is evaluated independently, using the local datetime at that instant.

Therefore,

```text
d:0101,t:uo-a0
```

matches when the local datetime satisfies, on January 1's local datetime,

```text
18:00–24:00
OR
00:00–06:00
```

00:00–06:00 on January 2 is not treated as "the night of January 1."

---

# 16. Generating the Local Datetime

The Local Datetime used to evaluate `d`, `w`, and `t` is generated by applying `z` to the UTC time.

Conceptually,

```text
local_datetime = utc_datetime + z
```

From this,

```text
local_date
local_weekday
local_minute_of_day
```

are derived.

The fields to be evaluated are as follows.

```text
d → local_date
w → local_weekday
t → local_minute_of_day
```

Important:

```text
s / e → UTC Unix Minute
d / w / t → Local Datetime after applying z
```

`z` must not be applied to `s` or `e`.

---

# 17. Semantic Model

The Parser converts the string into a Semantic Model such as the following.

Conceptual model:

```text
Ashiato {
    version: 1
    geohash: Geohash
    utc_offset_minutes: Integer
    start_unix_minute: Optional<Integer>
    end_unix_minute: Optional<Integer>
    dates: Optional<Set<MonthDay>>
    weekdays: Optional<Set<Weekday>>
    time_range: Optional<TimeRange>
    extensions: ExtensionMap
}
```

---

# 18. Field Duplication

In v1.0, a standard field must not appear more than once within the same Syntax.

For example,

```text
⟦as:1,g:9q8yyk,z:+f0,z:+f0⟧
```

is invalid.

However, duplication of values within the same field is treated as a separate issue.

For example,

```text
d:0101.0101
```

is parseable, and Canonicalization removes the duplicate.

In other words,

```text
Field duplicate
```

and

```text
Value duplicate
```

are different things.

---

# 19. Extension Field

Fields not defined in v1.0 are treated as Extension Fields.

Example:

```text
x-example-test:foo
```

Extension Fields are not semantically interpreted by the v1 evaluator.

---

# 20. Extension Namespace

An Extension Key must always take the following form.

```text
x-<namespace>-<name>
```

`x-` is the Extension identifier reserved by Ashiato.

`<namespace>` is a namespace identifying the provider of the extension (an organization, application, project, etc.), and `<name>` is the extension name within that namespace.

`<namespace>` and `<name>` must consist only of `a-z`, `0-9`, and `-`, and each must be at least one character. Uppercase letters (`A-Z`) must not be used.

For example, the following are valid Extension Keys.

```text
x-acme-theme
x-acme-color
x-myapp-location-mode
x-org-example-theme
```

The boundary between `<namespace>` and `<name>` is the **last** `-` in the Key. Therefore, `x-org-example-theme` is interpreted as namespace `org-example`, name `theme`.

The `x-` prefix is not merely a recommendation; it is required for all Extension Keys in v1.0.

Therefore, the following do not satisfy the Extension Key format.

```text
color
acme-color
x-color
```

---

# 21. Extensions and Standard Field Names

An Extension Key must not be identical to any of the v1.0 standard field names.

Standard fields:

```text
as
g
z
s
e
d
w
t
```

These are never treated as Extension Fields.

## Duplicate Extension Keys

An Extension Key, too, must appear at most once within a single Syntax.

For example,

```text
⟦as:1,g:9q8yyk,x-example-test:foo,x-example-test:bar⟧
```

is a Semantic Validation Error.

Duplication of an Extension Key is not interpreted as a MultiMap-like semantic in which one key holds multiple values.

---

# 22. Semantics of Extensions

An Extension Field is part of the Semantic Model.

Therefore,

```text
x-example-test:foo
```

and

```text
x-example-test:bar
```

differ as Semantic Models.

The fact that the v1 evaluator does not interpret their meaning does not mean the two are identical as Semantic Models.

---

# 23. Preservation of Unknown Extensions

The Parser preserves any recognized Extension Field in the Semantic Model.

The Canonical Serializer must always output any Extension Field that is preserved.

Therefore, when

```text
⟦as:1,g:9q8yyk,x-example-test:foo⟧
```

is parsed and then canonically serialized, `x-example-test:foo` must not disappear.

The fact that the v1 evaluator does not interpret the meaning of an Extension Field is a separate matter from removing it from the Canonical Model.

---

# 24. Extension Value

The Extension Value in v1.0 uses a restricted ASCII character format.

```text
extension-value =
    1*(ALPHA / DIGIT / "." / "-" / "+")
```

v1.0 does not define a specification for embedding URLs, JSON, arbitrary Unicode text, etc. directly as an Extension Value.

The internal meaning of an Extension Value is not the responsibility of the v1 evaluator.

---

# 25. ABNF

The following is the basic Syntax Grammar for v1.0.

```abnf
ashiato =
    "⟦" "as:1" "," "g:" geohash
    *("," field)
    "⟧"

field =
      utc-offset-field
    / start-field
    / expiration-field
    / date-field
    / weekday-field
    / time-field
    / extension-field

utc-offset-field =
    "z:" signed-base36

start-field =
    "s:" base36

expiration-field =
    "e:" base36

date-field =
    "d:" month-day
    *("." month-day)

weekday-field =
    "w:" weekday-value

time-field =
    "t:" base36 "-" base36

signed-base36 =
    ["+" / "-"] base36

base36 =
    1*(DIGIT / %x61-7A)

month-day =
    4DIGIT

weekday-value =
    1*7DIGIT

geohash =
    1*geohash-char

geohash-char =
      DIGIT
    / %x62-68    ; b-h
    / %x6A-6B    ; j-k
    / %x6D-6E    ; m-n
    / %x70-7A    ; p-z

extension-field =
    extension-key ":" extension-value

extension-key =
    "x-" extension-namespace "-" extension-name

extension-namespace =
    1*(%x61-7A / DIGIT / "-")

extension-name =
    1*(%x61-7A / DIGIT / "-")

extension-value =
    1*(ALPHA / DIGIT / "." / "-" / "+")
```

> **Extension Key splitting rule:** Because both `<namespace>` and `<name>` may contain `-` in the ABNF, the split position of an Extension Key is not uniquely determined by the ABNF alone. In v1.0, the string following `x-` is **split at the last `-`**, with everything before it treated as `<namespace>` and everything after it as `<name>`.
>
> For example, `x-org-example-theme` is interpreted as namespace=`org-example`, name=`theme`. This rule is a supplementary Syntax Interpretation Rule to the ABNF, and implementations must follow it.

---

# 26. Division of Responsibility Between ABNF and Semantic Validation

The ABNF defines only the form of the Syntax.

Being accepted by the ABNF does not mean passing Semantic Validation.

Semantic Validation verifies, for example, the following:

- Geohash length
- Geohash alphabet
- Geohash validity
- Range of `z`
- Range of `s`/`e`
- `s < e`
- `t`'s start/end range
- `t`'s start == end
- Calendar validity of `d`
- Weekday values of `w`
- Duplication of standard fields
- Format of Extension Keys
- Duplication of Extension Keys
- Collision between Extension Keys and standard field names

Therefore, a value such as

```text
w:999
```

which matches the ABNF but is semantically invalid, results in a Semantic Validation Error.

---

# 27. Syntax Parse and Semantic Validation

The processing model is as follows.

```text
Input
  ↓
Candidate Extraction
  ↓
Syntax Parse
  ↓
Semantic Validation
  ↓
Semantic Model
  ↓
Evaluation
```

When performing Canonicalization,

```text
Semantic Model
  ↓
Canonical Serialization
```

is added.

---

# 28. Candidate Extraction

An Ashiato Candidate begins with

```text
⟦
```

and extends to the first

```text
⟧
```

that appears afterward; together these delimit one Candidate.

A Candidate must have both `⟦` and `⟧`.

If `⟦` exists but is not followed by a corresponding `⟧`, that Candidate is an invalid candidate.

In this case, everything up to the end of the input is treated as an unclosed Candidate, and any `⟦` appearing inside that unclosed Candidate must not be treated as the start of a new Candidate.

Example:

```text
foo ⟦as:1,g:9q8yyk⟧ bar
```

Here,

```text
⟦as:1,g:9q8yyk⟧
```

is the Candidate.

Example of an unclosed Candidate:

```text
foo ⟦as:1,g:9q8yyk bar
```

Here, the Candidate is an invalid candidate.

---

# 29. Nested Delimiters

A `⟦` that appears while a Candidate is open must not be recursively treated as the start of a new Candidate.

For example,

```text
⟦foo⟦as:1,g:9q8yyk⟧
```

Here,

```text
⟦foo⟦as:1,g:9q8yyk⟧
```

is treated as a single Candidate in its entirety, and results in a Syntax Error.

If another `⟦` appears afterward, the Extractor continues its search for the next Candidate as usual.

---

# 30. Candidate Length Limit

The maximum length of a Candidate is

```text
4096 Unicode code points
```

This limit includes both

```text
⟦
```

and

```text
⟧
```

It is counted in Unicode code points, not UTF-16 code units.

A Candidate that exceeds this limit is treated as an invalid candidate.

---

# 31. Unicode Normalization

The delimiters of Ashiato Syntax are treated as literal Unicode code points.

```text
⟦
⟧
```

The Parser must not perform Unicode Normalization before parsing a Candidate.

Likewise, Canonicalization must not perform Unicode Normalization.

Comparison, Parsing, and Canonicalization of Ashiato Syntax do not treat strings that differ only after Unicode Normalization as identical.

---

# 32. Whitespace Policy

Whitespace is not permitted anywhere in Ashiato Syntax.

If whitespace exists at any position in the Syntax — immediately before/after a delimiter, between fields, around a comma, or inside a field's value — that Candidate is invalid as v1.0 Syntax.

For example, all of the following are invalid.

```text
⟦ as:1,g:9q8yyk⟧
⟦as:1, g:9q8yyk⟧
⟦as:1,g:9q8yyk ⟧
```

Ashiato Syntax has no whitespace in Canonical Form.

---

# 33. Version

v1.0 supports only

```text
as:1
```

A v1 parser must not interpret

```text
⟦as:2,g:9q8yyk⟧
```

as v1 Syntax.

An API implementation may distinguish between error categories such as

```text
SYNTAX_ERROR
UNSUPPORTED_VERSION
```

but this specification does not mandate any particular error classification.

---

# 34. Canonicalization

Canonicalization proceeds as

```text
Parse
→ Semantic Validation
→ Semantic Model
→ Canonical Serialization
```

The Canonical Serializer must always produce the same Canonical String for the same Semantic Model.

---

# 35. Canonical Form

The basic form of a Canonical Ashiato:

```text
⟦as:1,g:<canonical-geohash>[,<canonical-field>...]⟧
```

Canonical Form guarantees the following.

1. `as:1` is always present
2. `g` is always present
3. `z:0` is omitted
4. Base36 is lowercase
5. Positive `z` values are prefixed with `+`
6. Negative `z` values are prefixed with `-`
7. `s`/`e`/`t` use unsigned Base36
8. Unnecessary leading zeros are removed
9. `d` values are sorted in ascending order
10. `w` values are sorted in ascending order
11. Duplicate `d`/`w` values are removed
12. Standard fields are output in a fixed order
13. Extension fields are preserved
14. Extension fields are output in a deterministic order
15. Unicode Normalization is not performed
16. No unnecessary whitespace is output

---

# 36. Canonical Numeric Representation

## z

`z` is signed Base36.

```text
+540 → +f0
-300 → -8c
0    → z field omitted
+0   → z field omitted
-0   → z field omitted
```

---

## s / e / t

`s`, `e`, and `t` are unsigned Base36.

No sign is used.

For example,

```text
100 decimal → 2s
200 decimal → 5k
540 decimal → f0
1080 decimal → uo
```

Therefore, the Canonical Form of

```text
s:100
```

is

```text
s:2s
```

---

# 37. Canonical Field Order

The Canonical Order of standard fields is as follows.

```text
z
s
e
d
w
t
```

Therefore,

```text
⟦as:1,g:9q8yyk,t:f0-uo,z:+f0,d:0101,s:2s⟧
```

becomes, in Canonical Form,

```text
⟦as:1,g:9q8yyk,z:+f0,s:2s,d:0101,t:f0-uo⟧
```

---

# 38. Canonical d

Values of `d` are

1. deduplicated
2. sorted in numeric MMDD order

For example,

```text
d:0505.0101.0505
```

becomes

```text
d:0101.0505
```

---

# 39. Canonical w

Values of `w` are permitted to contain duplicates on input.

During Canonicalization, they are

1. deduplicated
2. sorted in numeric ascending order

For example,

```text
w:765
```

becomes

```text
w:567
```

---

# 40. Canonical Extension

Extension Fields are preserved in the Semantic Model and must always be output in Canonical Form.

Canonicalization must not alter the namespace/name of an Extension Key.

Extension Keys are ordered deterministically.

v1.0 uses ASCII lexicographic order.

Since v1.0 does not interpret the meaning of an Extension Value, no semantic transformation is performed on it.

Therefore,

```text
x-example-test:FOO
```

must not be converted to

```text
x-example-test:foo
```

Extension Values are case-sensitive.

---

# 41. Semantic Equality

Two Ashiato values are considered identical under Semantic Equality when the results of their Canonical Serialization are identical.

That is,

```text
Canonical(A) == Canonical(B)
```

implies

```text
A == B
```

Extension Fields participate in Semantic Equality because they are part of the Semantic Model.

For example,

```text
⟦as:1,g:9q8yyk,x-example-test:foo⟧
```

and

```text
⟦as:1,g:9q8yyk,x-example-test:bar⟧
```

differ under Semantic Equality.

---

# 42. Privacy Considerations

Ashiato Syntax expresses location and time conditions as a public string.

Therefore, if a user combines a high-precision Geohash with a time condition, not only location but also temporal patterns may become inferable by third parties.

For example,

```text
⟦as:1,g:<high-precision-geohash>,z:+f0,d:0101,t:uo-a0⟧
```

discloses:

- a specific location
- UTC+09:00
- January 1 every year
- a local time condition equivalent to 18:00–06:00 the next day

Combining this further with `s`/`e` may make it possible to infer time-limited events, and so on.

Ashiato Syntax provides no automatic protection for such Location Privacy or Temporal Privacy.

Location and time information can, by design, become public information.

---

# 43. Server Communication

Ashiato Syntax neither requires nor prohibits transmitting the current location to a server. How location is acquired, compared, and transmitted is the responsibility of the Client/Application.

---

# 44. Non-Goals

v1.0 does not specify any of the following.

- Distance calculation
- Discovery radius
- GPS accuracy
- Geolocation permission
- Ownership
- Claiming
- Scoring
- Cooldowns
- Anti-cheat
- Game mechanics
- Server API
- Database schema
- SNS API
- IANA Time Zone
- DST rules
- Multiple time ranges
- Arbitrary Boolean expressions
- Extension encoding such as URL / JSON / Markdown
- SNS-specific edit / quote / reply / repost features

---

# 45. Test Vectors

The following are examples of v1.0 Reference Test Vectors.

## Basic

```text
⟦as:1,g:9q8yyk⟧
```

Valid.

---

## Zero Offset

```text
⟦as:1,g:9q8yyk,z:0⟧
```

Valid.

Canonical Form:

```text
⟦as:1,g:9q8yyk⟧
```

---

## Absolute Start

```text
⟦as:1,g:9q8yyk,s:2s⟧
```

`current_unix_minute = 100`

→ Match

`current_unix_minute = 99`

→ No Match

---

## Invalid Absolute Interval

```text
⟦as:1,g:9q8yyk,s:5k,e:2s⟧
```

Semantic Validation Error.

---

## Cross-Midnight Time Range

```text
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

Meaning:

```text
18:00–24:00
OR
00:00–06:00
```

Boundaries:

```text
1079 → No Match
1080 → Match
1439 → Match
0    → Match
359  → Match
360  → No Match
```

---

## Invalid Zero-Length Time

```text
⟦as:1,g:9q8yyk,t:0-0⟧
```

Semantic Validation Error.

---

## Month-Day

```text
⟦as:1,g:9q8yyk,d:0101.0505⟧
```

Meaning:

```text
January 1 OR May 5
```

---

## Combined Recurring Conditions

```text
⟦as:1,g:9q8yyk,z:+f0,d:0101,w:67,t:uo-a0⟧
```

Meaning:

```text
local date = January 1
AND
local weekday = Saturday OR Sunday
AND
local time = 18:00–06:00
```

---

## Leap Day

```text
⟦as:1,g:9q8yyk,d:0229⟧
```

Valid.

Leap year:

→ Match

Non-leap year:

→ No Match

---

## Invalid Calendar Date

```text
⟦as:1,g:9q8yyk,d:0231⟧
```

Semantic Validation Error.

---

## Extension

```text
⟦as:1,g:9q8yyk,x-example-test:foo⟧
```

Valid.

The v1 evaluator does not interpret the meaning of `x-example-test`.

Canonical Serialization preserves `x-example-test:foo`.

---

## Canonical z

Input:

```text
⟦as:1,g:9q8yyk,z:+000f0⟧
```

Canonical:

```text
⟦as:1,g:9q8yyk,z:+f0⟧
```

---

## Canonical Zero z

Input:

```text
⟦as:1,g:9q8yyk,z:-0⟧
```

Canonical:

```text
⟦as:1,g:9q8yyk⟧
```

---

## Canonical s/e

Input:

```text
⟦as:1,g:9q8yyk,s:0002s,e:0005k⟧
```

Canonical:

```text
⟦as:1,g:9q8yyk,s:2s,e:5k⟧
```

---

## Canonical d

Input:

```text
⟦as:1,g:9q8yyk,d:0505.0101.0505⟧
```

Canonical:

```text
⟦as:1,g:9q8yyk,d:0101.0505⟧
```

---

## Canonical w

Input:

```text
⟦as:1,g:9q8yyk,w:765⟧
```

Canonical:

```text
⟦as:1,g:9q8yyk,w:567⟧
```

---

## Duplicate w Values

Input:

```text
⟦as:1,g:9q8yyk,w:667⟧
```

Valid.

Canonical:

```text
⟦as:1,g:9q8yyk,w:67⟧
```

---

## Field Ordering

Input:

```text
⟦as:1,g:9q8yyk,t:f0-uo,d:0101,s:2s,z:+f0⟧
```

Canonical:

```text
⟦as:1,g:9q8yyk,z:+f0,s:2s,d:0101,t:f0-uo⟧
```

---

## Cross-Midnight Boundary

```text
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

```text
1079 → No Match
1080 → Match
1439 → Match
0    → Match
359  → Match
360  → No Match
```

---

## Duplicate Extension Key

Input:

```text
⟦as:1,g:9q8yyk,x-example-test:foo,x-example-test:bar⟧
```

Semantic Validation Error.

An Extension Key must not appear more than once within a single Syntax.

---

# 46. Reference Evaluation Algorithm

A conceptual Evaluation can be implemented as follows.

```text
evaluate(ashiato, current_utc_datetime):

    current_unix_minute =
        floor(current_unix_time_seconds / 60)

    if s exists and current_unix_minute < s:
        return false

    if e exists and current_unix_minute >= e:
        return false

    local_datetime =
        current_utc_datetime + z

    if d exists:
        if local_month_day not in d:
            return false

    if w exists:
        if local_weekday not in w:
            return false

    if t exists:
        start = t.start
        end   = t.end
        minute = local_minute_of_day

        if start == end:
            invalid

        if start < end:
            if not (start <= minute < end):
                return false

        if start > end:
            if not (minute >= start or minute < end):
                return false

    return true
```

The v1 evaluator ignores Extension Fields.

---

# 47. Required Properties of Canonicalization

The Canonical Serializer must satisfy the following.

### Idempotence

```text
Canonical(Canonical(x))
=
Canonical(x)
```

### Semantic Preservation

```text
Parse(x)
```

and

```text
Parse(Canonical(x))
```

produce the same Semantic Model.

### Determinism

For the same Semantic Model,

```text
Serialize(model)
```

always returns the same string.

---
