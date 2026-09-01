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
⟦as:1[,c:<context-uuid>],g:<geohash>[,<field>...]⟧
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

`as:1`, optional `c:<context-uuid>`, and `g:<geohash>` form the leading portion of the Syntax.

```text
⟦
  as:1
  [, c:<context-uuid>]
  ,
  g:<geohash>
  ,
  ...
⟧
```

`as` and `g` are mandatory. `c` is optional. If `c` is present, the leading order is fixed as `as → c → g`. If `c` is absent, it is `as → g`. Fields after `g` may appear in any order on input.

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
- `c`, when present, identifies the application context and is not a temporal/geographic condition

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

# 3.1 Application Context Field: `c`

## Format

```text
c:<context-id>
```

`c` is an identifier used to associate an Ashiato with a specific **Application Context**.

An Application Context may represent, for example:

- a specific service
- a specific event
- a project or campaign
- a specific application or activity
- any other context defined by the application using Ashiato

The value of `c` is treated as an **opaque identifier**.
Ashiato Syntax does not assign any meaning to the identifier itself.

---

## Character Set and Length

The value of `c` may contain only the following characters:

```text
0-9
a-z
```

Uppercase letters are not used.

The length is:

```text
1-22 characters
```

The maximum length of 22 characters allows implementations to use compact representations of identifiers such as 128-bit values.
However, Ashiato Syntax does **not** require `c` to be a UUID.

---

## Generation and Uniqueness

Ashiato Syntax does not define how an Application Context Identifier is generated.

An application may use any method that provides the required level of uniqueness within its intended scope.

For example, an application may use a short random identifier such as:

```text
c:7k3m9x
```

or an identifier derived from a 128-bit random value using an application-defined representation, such as:

```text
c:VQX8h3QvT9m7k2LxP0aBcQ
```

UUIDs may be used, but `c` is not limited to UUIDs.

Ashiato Syntax does not register, issue, reserve, or globally manage Application Contexts.

Therefore, an event organizer, service provider, project operator, or other party can independently generate and use its own `c` values.

The scope in which collisions must be avoided, and the method used to achieve the required uniqueness, are the responsibility of the application.

---

## Canonical Form

`c` is written directly as its value using only lowercase `0-9a-z` characters.

Ashiato Syntax does not require the `c` value to be transformed using any particular encoding scheme.

For example:

```text
c:7k3m9x
```

represents the `c` value `7k3m9x` directly.

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

## Numeric Encoding

Ashiato Syntax uses Base36 encoding for numeric values in some fields instead of representing them directly as decimal numbers.

Base36 uses the following 36 characters:

```text
0 1 2 3 4 5 6 7 8 9
a b c d e f g h i j k l m n o p q r s t u v w x y z
```

When a field specifies Base36 encoding, its numeric value is converted to Base36 and written using lowercase `a-z`. For example:

```text
35  → z
36  → 10
140 → 3w
```

Each field definition explicitly states whether Base36 encoding is used. Fields that do not specify Base36 follow their respective field definitions.

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

`z` does not use Time Zone identifiers such as `Asia/Tokyo`.

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

# 6. IANA Time Zone Field: tz

## Format

```text
tz:<base36-index>
```

`tz` references an IANA Time Zone Database (TZDB) Time Zone Identifier through the Ashiato TZ Dictionary.

The value of `tz` is not the TZID itself. It is the dictionary's 0-based index represented as an unsigned Base36 value.

Example:

```text
tz:5w
```

This references the IANA TZID corresponding to that index in the Ashiato TZ Dictionary. The actual TZID represented by `5w` is determined by the TZ Dictionary Version associated with the Syntax Version.

Uppercase letters are not used.

---

## Ashiato TZ Dictionary

Ashiato v1.0 uses the following dictionary.

```text
Ashiato TZ Dictionary v1
    = IANA TZDB 2026c
```

The dictionary's source set consists of the Time Zone Identifiers listed in `zone1970.tab` from IANA TZDB 2026c. Aliases provided through `Link` or `backward` are not included.

Identifiers in the dictionary are ordered by ASCII lexicographic order, with the first entry assigned index `0`. Each dictionary index is encoded as an unsigned Base36 value for use as the `tz` field value.

Conceptually:

```text
TZID
  ↓
Ashiato TZ Dictionary v1
  ↓
0-based index
  ↓
unsigned Base36
```

The dictionary is fixed together with the Ashiato Syntax Version. Future updates to IANA TZDB must not modify the index-to-TZID mapping of Ashiato TZ Dictionary v1.

If a new dictionary is introduced, the existing dictionary must not be modified; a new Dictionary Version is defined instead. For example, a future Syntax Version may adopt TZ Dictionary v2 as an independent dictionary.

---

## Dictionary Immutability

Once an Ashiato TZ Dictionary Version has been published, its index-to-TZID mapping must not change.

If an IANA TZDB identifier is later changed to a Link to another TZID, or otherwise ceases to be a canonical zone, the mapping in a previously frozen Ashiato TZ Dictionary must remain unchanged.

An index that has been removed or is otherwise no longer needed must not be reassigned to another TZID.

Therefore, if a `tz` value in v1 corresponds to a particular TZID, that correspondence does not change as a result of future IANA TZDB updates.

---

## Generation and Distribution of the Dictionary

Ashiato TZ Dictionary v1 is mechanically generated from `zone1970.tab` in IANA TZDB 2026c. The generation procedure is as follows.

1. From each data line of `zone1970.tab` (excluding comment lines starting with `#` and blank lines), extract the 3rd column (the Time Zone Identifier).
2. Sort the extracted identifiers in ASCII lexicographic order.
3. Assign a 0-based index to each identifier according to the sorted order.
4. Encode each index as unsigned Base36.

When generated this way from `zone1970.tab` in IANA TZDB 2026c, Ashiato TZ Dictionary v1 contains **312 entries**, with the maximum index being `8n` in Base36 (311 in decimal). This leaves ample headroom below the capacity of 2-character Base36 (1,296 entries).

The authoritative source for generation is the official IANA TZDB release (`https://data.iana.org/time-zones/releases/`). Mirrors such as GitHub may be used only for the convenience of the generation process.

The generation script and the resulting Ashiato TZ Dictionary v1 data files (`dictionary.csv` / `dictionary.json`) are published separately from this specification, in the repository under `tz-dictionary/v1/`. Implementations must treat this distribution as the authoritative source for Ashiato TZ Dictionary v1.

---

## Base36 Representation

`tz` uses the existing Ashiato Base36 representation. No sign is used, and leading zeros are removed in Canonical Form.

If the dictionary index is 0:

```text
tz:0
```

If the dictionary index is 35:

```text
tz:z
```

If the dictionary index is 36:

```text
tz:10
```

If the v1 dictionary contains at most 1296 entries, all `tz` values can be represented in at most 2 characters. The Syntax Grammar nevertheless does not fix `tz` to exactly 2 characters.

---

## Determinism of TZID and Time Zone Rules

The Ashiato TZ Dictionary fixes the mapping from a `tz` index to an IANA TZID.

```text
tz index → IANA TZID
```

This mapping is deterministic as long as the Dictionary Version is fixed.

However, resolving an IANA TZID to the UTC Offset at a particular instant depends on the TZDB / tzdata Version used by the Evaluator. Ashiato v1.0 does not guarantee that the result of resolving a TZID to UTC Offset or Time Zone Rules remains unchanged across future tzdata versions.

Therefore, `tz` is a reference to an IANA Time Zone Identifier intended to follow future IANA Time Zone Rule changes; it does not represent a fixed UTC Offset.

---

## Mutual Exclusion with `z`

`z` and `tz` must not be specified together.

```text
z  = fixed UTC Offset
tz = IANA Time Zone reference
```

They represent different methods of resolving the local datetime.

For example,

```text
⟦as:1,g:9q8yyk,z:+f0,tz:0⟧
```

is a Semantic Validation Error.

If neither `z` nor `tz` is specified, the base Offset for local datetime generation is `0` (UTC).

---

# 7. Absolute Time: s / e

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

`s` and `e` are treated as **non-negative integers**. Their Syntax values are lowercase Base36 representations of those Unix-minute integers.

Therefore,

```text
s >= 0
e >= 0
```

must hold.

v1.0 sets no upper bound on `s` / `e`.

In the ABNF, `s` / `e` are written as `base36`, but the Semantic Model treats them as integer values.

---

# 8. Evaluation of s

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

# 9. Evaluation of e

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

# 10. When Both s and e Are Present

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

# 11. d: Month-Day Field

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

The year used to determine leap years is the year of the `local_datetime` generated by `z` or `tz`.

The Gregorian Calendar is used.

---

# 12. w: Weekday Field

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

# 13. t: Time-of-Day Field

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

# 14. local_minute_of_day

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

# 15. Evaluation of t

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

# 16. Midnight Crossing in t

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

To express a single continuous span that crosses a `d` (or `w`) boundary together with `t` — for example, "18:00 on January 1 through 06:00 on January 2" — use the `o` field described in the next chapter.

---

# 17. o: Overnight Modifier Field

## Format

```text
o:1
```

`o` is a Modifier Field that qualifies `t`; it cannot exist on its own.

`o:1` means

```text
the t interval is a single, continuous overnight interval
running from the start-side calendar day into the end-side calendar day
```

The only value `o` currently takes is `1`; in v1.0, `o` is effectively a Boolean field.

---

## Semantics: Reinterpreting the Wrap-Around

As described in Chapter 16, a wrap-around `t` (where `start > end`), such as `t:uo-a0`, is interpreted — without `o` — as

```text
00:00–06:00 OR 18:00–24:00
on the same calendar day
```

Adding `o:1` changes this interpretation to

```text
from 18:00 on the start-side calendar day
through 06:00 on the end-side calendar day,
as a single continuous interval
```

That is, `o` is a modifier that

```text
converts a wrap-around interval from
"an OR within the same day" into "a continuous overnight interval"
```

Example:

```text
⟦as:1,g:9q8yyk,d:0101,t:uo-a0⟧
```

means

```text
Jan 1, 00:00–06:00 OR Jan 1, 18:00–24:00
```

whereas

```text
⟦as:1,g:9q8yyk,d:0101,t:uo-a0,o:1⟧
```

means

```text
Jan 1, 18:00 → Jan 2, 06:00
```

---

## Combining o with d / w

`o:1` is used together with `d` or `w`.

```text
d:0101,t:uo-a0,o:1
```

means

```text
start date = Jan 1
end date   = Jan 2
```

```text
w:5,t:uo-a0,o:1
```

means

```text
start weekday = Friday
end weekday   = Saturday
```

expressing "every Friday 18:00 through Saturday 06:00."

When `d` has multiple values, `o:1` is applied independently to each value.

```text
d:0101.0505,t:uo-a0,o:1
```

means

```text
(Jan 1, 18:00 → Jan 2, 06:00) OR (May 5, 18:00 → May 6, 06:00)
```

---

## Evaluation Model: effective_date / effective_weekday

When `o:1` is present, evaluating `d` and `w` does not use `local_date` / `local_weekday` directly. Instead, it uses derived values called **effective_date** and **effective_weekday**, defined as follows.

```text
if o == 1:
    if local_minute_of_day < t.start:
        effective_date    = local_date - 1 day
        effective_weekday = local_weekday - 1 (mod 7)
    else:
        effective_date    = local_date
        effective_weekday = local_weekday
else:
    # tz is resolved through the Syntax Version's Ashiato TZ Dictionary.
    # z and tz are mutually exclusive; if neither is present, z = 0 (UTC).
    effective_date    = local_date
    effective_weekday = local_weekday
```

`d` is evaluated against the Month-Day of `effective_date`; `w` is evaluated against `effective_weekday`.

In other words, `o:1` does not simply extend the `t` interval — it is an extension to the Evaluation Algorithm itself, which shifts the effective date used for `d` / `w` matching back by one day, but only for instants on the small-hours side (before `t.start`).

As a result, `d:0101,t:uo-a0,o:1` does not match "Jan 1, 00:00–06:00" (during that span, `effective_date` is Dec 31). This is the opposite of the behavior without `o` (where that same span matches via OR semantics).

```text
# without o: d:0101,t:uo-a0
Jan 1, 03:00 → Match   (OR semantics)
Jan 1, 20:00 → Match

# with o: d:0101,t:uo-a0,o:1
Jan 1, 03:00 → No Match  (treated as the night of Dec 31)
Jan 1, 20:00 → Match
Jan 2, 03:00 → Match     (treated as a continuation of Jan 1's night)
```

---

## Semantic Validation

`o` is subject to the following constraints.

- If `o:1` is present, `t` is mandatory. If `o:1` is present without `t`, this is a Semantic Validation Error.
- If `o:1` is present, `t` must be a wrap-around interval (`t.start > t.end`). If `o:1` is present while `t.start <= t.end`, this is a Semantic Validation Error. Allowing the same meaning to be expressed in more than one way would break the uniqueness of Canonical Form, so this is treated as a prohibition rather than an ambiguity to be resolved.
- `o` is one of the standard fields, and per the rule in Chapter 20 (Field Duplication), must not appear more than once within the same Syntax.

---

# 18. Generating the Local Datetime

The Local Datetime used to evaluate `d`, `w`, and `t` is generated using either `z` or `tz`.

When `z` is present, the fixed UTC Offset is applied.

```text
local_datetime = utc_datetime + z
```

When `tz` is present, the `tz` value is resolved to an IANA TZID through the Ashiato TZ Dictionary, and the Evaluator generates the Local Datetime according to the Time Zone Rules in the TZDB / tzdata it uses.

Because `z` and `tz` are mutually exclusive, they are never applied together.

The Local Datetime produced through `tz` depends on the TZDB / tzdata Version used by the Evaluator.

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
d / w / t → Local Datetime generated by z or tz
```

Neither `z` nor `tz` is applied to `s` or `e`.

When `o:1` is present, `d` / `w` evaluation does not use `local_date` / `local_weekday` directly; it uses the `effective_date` / `effective_weekday` defined in Chapter 17.

---

# 19. Semantic Model

The Parser converts the string into a Semantic Model such as the following.

Conceptual model:

```text
Ashiato {
    version: 1
    context_uuid: Optional<UUID>
    geohash: Geohash
    utc_offset_minutes: Optional<Integer>
    timezone_index: Optional<Integer>
    start_unix_minute: Optional<Integer>
    end_unix_minute: Optional<Integer>
    dates: Optional<Set<MonthDay>>
    weekdays: Optional<Set<Weekday>>
    time_range: Optional<TimeRange>
    overnight: Boolean
    extensions: ExtensionMap
}
```

---

# 20. Field Duplication

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

# 21. Extension Field

Fields not defined in v1.0 are treated as Extension Fields.

Example:

```text
x-example-test:foo
```

Extension Fields are not semantically interpreted by the v1 evaluator.

---

# 22. Extension Namespace

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

# 23. Extensions and Standard Field Names

An Extension Key must not be identical to any of the v1.0 standard field names.

Standard fields:

```text
as
g
c
z
tz
s
e
d
w
t
o
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

# 24. Semantics of Extensions

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

# 25. Preservation of Unknown Extensions

The Parser preserves any recognized Extension Field in the Semantic Model.

The Canonical Serializer must always output any Extension Field that is preserved.

Therefore, when

```text
⟦as:1,g:9q8yyk,x-example-test:foo⟧
```

is parsed and then canonically serialized, `x-example-test:foo` must not disappear.

The fact that the v1 evaluator does not interpret the meaning of an Extension Field is a separate matter from removing it from the Canonical Model.

---

# 26. Extension Value

The Extension Value in v1.0 uses a restricted ASCII character format.

```text
extension-value =
    1*(ALPHA / DIGIT / "." / "-" / "+")
```

v1.0 does not define a specification for embedding URLs, JSON, arbitrary Unicode text, etc. directly as an Extension Value.

The internal meaning of an Extension Value is not the responsibility of the v1 evaluator.

---

# 27. ABNF

The following is the basic Syntax Grammar for v1.0. `c` may appear only between `as:1` and `g:<geohash>`. Fields after `g` may appear in any input order.

```abnf
ashiato =
    "⟦" "as:1" [ "," context-field ] "," "g:" geohash
    *( "," field )
    "⟧"

field =
      utc-offset-field
    / timezone-field
    / start-field
    / expiration-field
    / date-field
    / weekday-field
    / time-field
    / overnight-field
    / extension-field

context-field =
    "c:" uuid-base64url

uuid-base64url = 22base64url-char

base64url-char =
      ALPHA
    / DIGIT
    / "-"
    / "_"

utc-offset-field =
    "z:" signed-base36

timezone-field =
    "tz:" base36

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

overnight-field =
    "o:" "1"

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

# 28. Division of Responsibility Between ABNF and Semantic Validation

The ABNF defines only the form of the Syntax.

Being accepted by the ABNF does not mean passing Semantic Validation.

Semantic Validation verifies, for example, the following:

- Geohash length
- Geohash alphabet
- Geohash validity
- `c` encoding validity (exactly 22 unpadded Base64url characters representing 128 bits)
- Range of `z`
- `tz` index outside the range of the Ashiato TZ Dictionary
- `z` and `tz` both present
- Range of `s`/`e`
- `s < e`
- `t`'s start/end range
- `t`'s start == end
- Calendar validity of `d`
- Weekday values of `w`
- `o:1` present without `t`
- `o:1` present while `t` is not a wrap-around interval (`t.start <= t.end`)
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

# 29. Syntax Parse and Semantic Validation

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

# 30. Candidate Extraction

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

# 31. Nested Delimiters

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

# 32. Candidate Length Limit

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

# 33. Unicode Normalization

The delimiters of Ashiato Syntax are treated as literal Unicode code points.

```text
⟦
⟧
```

The Parser must not perform Unicode Normalization before parsing a Candidate.

Likewise, Canonicalization must not perform Unicode Normalization.

Comparison, Parsing, and Canonicalization of Ashiato Syntax do not treat strings that differ only after Unicode Normalization as identical.

---

# 34. Whitespace Policy

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

# 35. Version

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

# 36. Canonicalization

Canonicalization proceeds as

```text
Parse
→ Semantic Validation
→ Semantic Model
→ Canonical Serialization
```

The Canonical Serializer must always produce the same Canonical String for the same Semantic Model.

---

# 37. Canonical Form

The basic form of a Canonical Ashiato:

```text
⟦as:1[,c:<canonical-context-uuid>],g:<canonical-geohash>[,<canonical-field>...]⟧
```

Canonical Form guarantees the following.

1. `as:1` is always present
2. `g` is always present
3. `z:0` is omitted
4. `tz` uses unsigned Base36
5. Base36 is lowercase
6. Positive `z` values are prefixed with `+`
7. Negative `z` values are prefixed with `-`
8. `s`/`e`/`t` use unsigned Base36
9. Unnecessary leading zeros are removed
10. `d` values are sorted in ascending order
11. `w` values are sorted in ascending order
12. Duplicate `d`/`w` values are removed
13. Standard fields are output in a fixed order
14. Extension fields are preserved
15. Extension fields are output in a deterministic order
16. Unicode Normalization is not performed
17. No unnecessary whitespace is output

---

# 38. Canonical Numeric Representation

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

# 39. Canonical Field Order

The Canonical Order of standard fields is as follows.

```text
as
c
g
z
tz
s
e
d
w
t
o
```

`as`, `c`, and `g` form the leading portion of the Syntax. `c` is output only when present.

**Input order and Canonical Order are separate rules.** The Parser requires the leading order `as → [c] → g`, but accepts the Standard Fields and Extension Fields after `g` in any input order. The Canonical Serializer outputs the Semantic Model according to the Canonical Order above.

`o` qualifies `t`, so it is placed immediately after `t`.

Therefore,

```text
⟦as:1,g:9q8yyk,t:f0-uo,z:+f0,d:0101,s:2s⟧
```

becomes, in Canonical Form,

```text
⟦as:1,g:9q8yyk,z:+f0,s:2s,d:0101,t:f0-uo⟧
```

With `o:1` present, for example

```text
⟦as:1,g:9q8yyk,o:1,d:0101,t:uo-a0⟧
```

becomes, in Canonical Form,

```text
⟦as:1,g:9q8yyk,d:0101,t:uo-a0,o:1⟧
```

---

# 40. Canonical d

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

# 41. Canonical w

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

# 42. Canonical Extension

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

# 43. Semantic Equality

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

# 44. Privacy Considerations

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

When `tz` is used, the intended regional Time Zone Rules may also become inferable. Combining this further with `s`/`e` may make it possible to infer time-limited events, and so on.

Ashiato Syntax provides no automatic protection for such Location Privacy or Temporal Privacy.

Location and time information can, by design, become public information.

---

# 45. Server Communication

Ashiato Syntax neither requires nor prohibits transmitting the current location to a server. How location is acquired, compared, and transmitted is the responsibility of the Client/Application.

---

# 46. Non-Goals

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
- Multiple time ranges
- Arbitrary Boolean expressions
- Context registry or context ownership
- Context discovery or resolution
- Extension encoding such as URL / JSON / Markdown
- SNS-specific edit / quote / reply / repost features

---

# 47. Test Vectors

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

## IANA Time Zone

```text
⟦as:1,g:9q8yyk,tz:0⟧
```

Valid if index `0` exists in Ashiato TZ Dictionary v1. The value `0` refers to the first TZID in the frozen v1 dictionary.

The exact Local Datetime offset is determined by the Evaluator's TZDB / tzdata rules.

`z` and `tz` must not be specified together.

```text
⟦as:1,g:9q8yyk,z:+f0,tz:0⟧
```

Semantic Validation Error.

---

## Invalid: tz Index Out of Range

```text
⟦as:1,g:9q8yyk,tz:zz⟧
```

If `zz` represents an index beyond the number of entries (the total number of Canonical Zones) in Ashiato TZ Dictionary v1, this is a Semantic Validation Error.

As with `w:999`, this value matches the ABNF (`base36`) but is semantically invalid because it falls outside the dictionary's range.

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

## Application Context

```text
⟦as:1,c:VQX8h3QvT9m7k2LxP0aBcQ,g:9q8yyk⟧
```

Valid. The `c` value identifies an application context using a compact encoding of a 128-bit UUID.

`c` does not change the temporal active/inactive result. Applications MAY use it to select the relevant service, event, project, or other context.

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

## Application Context and Field Ordering

Generic Ashiato:

```text
⟦as:1,g:9q8yyk,d:0101⟧
```

Valid. Because `c` is absent, the Syntax itself is not associated with a particular application context.

Context-bound Ashiato:

```text
⟦as:1,c:VQX8h3QvT9m7k2LxP0aBcQ,g:9q8yyk,d:0101⟧
```

Valid.

The leading order `as → [c] → g` is also fixed on input. Fields after `g` may appear in any input order. For example, the following is parseable:

```text
⟦as:1,c:VQX8h3QvT9m7k2LxP0aBcQ,g:9q8yyk,t:f0-uo,d:0101,s:2s,z:+f0⟧
```

Canonical:

```text
⟦as:1,c:VQX8h3QvT9m7k2LxP0aBcQ,g:9q8yyk,z:+f0,s:2s,d:0101,t:f0-uo⟧
```

The following is invalid:

```text
⟦as:1,g:9q8yyk,c:VQX8h3QvT9m7k2LxP0aBcQ,d:0101⟧
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

## Overnight: d + t + o

```text
# without o: d:0101,t:uo-a0
⟦as:1,g:9q8yyk,d:0101,t:uo-a0⟧
```

```text
Jan 1, 00:00–06:00 OR Jan 1, 18:00–24:00
```

```text
# with o: d:0101,t:uo-a0,o:1
⟦as:1,g:9q8yyk,d:0101,t:uo-a0,o:1⟧
```

```text
Jan 1, 18:00 → Jan 2, 06:00
```

Results:

```text
Jan 1, 03:00 → No Match  (for d:0101,t:uo-a0,o:1; treated as the night of Dec 31)
Jan 1, 20:00 → Match
Jan 2, 03:00 → Match     (treated as a continuation of Jan 1's night)
Jan 2, 07:00 → No Match
```

---

## Overnight: w + t + o

```text
⟦as:1,g:9q8yyk,w:5,t:uo-a0,o:1⟧
```

Meaning:

```text
Every Friday, 18:00 → Saturday, 06:00
```

---

## Overnight: Multiple d Values

```text
⟦as:1,g:9q8yyk,d:0101.0505,t:uo-a0,o:1⟧
```

Meaning:

```text
(Jan 1, 18:00 → Jan 2, 06:00) OR (May 5, 18:00 → May 6, 06:00)
```

---

## Overnight: Crossing the Year Boundary

```text
⟦as:1,g:9q8yyk,d:1231,t:uo-a0,o:1⟧
```

Meaning:

```text
Dec 31, 18:00 → Jan 1, 06:00
```

Results:

```text
Dec 31, 20:00 → Match
Jan 1,  03:00 → Match   (treated as a continuation of Dec 31's night)
Jan 1,  07:00 → No Match
```

---

## Invalid: o Present Without t

```text
⟦as:1,g:9q8yyk,d:0101,o:1⟧
```

Semantic Validation Error.

`t` is mandatory whenever `o:1` is present.

---

## Invalid: o Present but t Is Not a Wrap-Around

```text
⟦as:1,g:9q8yyk,t:f0-uo,o:1⟧
```

Semantic Validation Error.

Whenever `o:1` is present, `t.start > t.end` (a wrap-around interval) is required.

---

# 48. Reference Evaluation Algorithm

A conceptual Evaluation can be implemented as follows.

```text
evaluate(ashiato, current_utc_datetime):

    current_unix_minute =
        floor(current_unix_time_seconds / 60)

    if s exists and current_unix_minute < s:
        return false

    if e exists and current_unix_minute >= e:
        return false

    if tz exists:
        local_datetime = resolve_iana_timezone(
            current_utc_datetime, tz, evaluator_tzdb
        )
    else:
        local_datetime = current_utc_datetime + z

    effective_date    = local_date
    effective_weekday = local_weekday

    if o == 1:
        # By the Semantic Validation of o:1, t is guaranteed to exist
        # here and to be a wrap-around interval (t.start > t.end)
        if local_minute_of_day < t.start:
            effective_date    = local_date - 1 day
            effective_weekday = local_weekday - 1 (mod 7)

    if d exists:
        if effective_month_day not in d:
            return false

    if w exists:
        if effective_weekday not in w:
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

`o:1` does not extend the `t` interval. It is an extension to the Evaluation Algorithm itself: it shifts the effective date used for `d` / `w` matching (`effective_date` / `effective_weekday`) back by one day, but only for instants on the small-hours side (`local_minute_of_day < t.start`).

The v1 evaluator ignores Extension Fields.

---

# 49. Required Properties of Canonicalization

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
