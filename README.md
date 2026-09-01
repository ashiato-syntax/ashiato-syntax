English | [日本語](./README_JP.md)

# Ashiato Syntax

**A lightweight, deterministic syntax for declaratively expressing location and time.**

With a short string like `⟦as:1,g:9q8yyk,d:0101,t:uo-a0⟧`, you can embed conditions — a specific place, a specific period, a specific weekday, a specific time of day — directly inside text.

> **Status:** Draft / v1.0 Freeze Candidate
> The specification is still in Draft stage prior to Freeze. Breaking changes may still occur.

---

## What Is This

Ashiato Syntax is a small text syntax for location and time conditions, intended for use cases such as:

- Embedding "visible / active only at this place and time" conditions inside social posts or messages
- Location- and time-triggered game mechanics (footprint-style)
- Embedding in QR codes or URLs to distribute time-limited or place-limited content
- Associating posts with a specific service, event, project, or other application context

The name "Ashiato" comes from the Japanese word for "footprint" (足跡).

### Example

```text
⟦as:1,g:9q8yyk⟧
```

This is the minimal form, representing "being within Geohash Cell `9q8yyk`."

```text
⟦as:1,g:9q8yyk,z:+f0,d:0101,w:67,t:uo-a0⟧
```

This is Active when all of the following conditions are satisfied:

- inside the Geohash Cell `9q8yyk`
- in local time at UTC+09:00
- on January 1, and
- Saturday or Sunday, and
- between 18:00 and 06:00 the next day

## Application Context

Ashiato Syntax is not tied to any particular service or use case.

An Ashiato can optionally be associated with an Application Context using the `c` field:

```text
⟦as:1,c:VQX8h3QvT9m7k2LxP0aBcQ,g:9q8yyk⟧
```

The c field identifies an Application Context by UUID. An Application Context may represent a service, event, project, campaign, or any other application-specific context.

The c field is optional:

If c is omitted, the Ashiato is a generic, context-independent Ashiato.
If c is present, the Ashiato belongs to the specified Application Context.

Application Contexts are not registered, issued, or managed by Ashiato Syntax. Any service, event organizer, project, or other party can generate and use its own UUID.

The UUID is represented compactly in the syntax as a 128-bit UUID encoded as unpadded Base64url (22 characters).

The leading field order is fixed as as → [c] → g. Fields after g may appear in any order when parsing.

## Design Principles

- **A simple logical model**: fields are combined with AND, multiple values within a field are combined with OR. Arbitrary Boolean expressions or parentheses are not supported.
- **Separation of Syntax and Semantics**: syntactic validation via ABNF is clearly separated from Semantic Validation (validity checks on values).
- **A deterministic Canonical Form**: Ashiato values with the same meaning always normalize to the same Canonical String (guaranteeing Idempotence, Semantic Preservation, and Determinism).
- **Extensible**: Extension Fields in the form `x-<namespace>-<name>` let you add custom fields without breaking the standard specification.
- **Contextual but decentralized**: Application Contexts can distinguish different services, events, and projects without requiring centralized registration.

## Specification

See the full specification here:

- [Ashiato Syntax v1.0 — (English Specification)](./Ashiato_Syntax_v1_0_EN.md)
- [Ashiato Syntax v1.0 — 日本語仕様書）](./Ashiato_Syntax_v1_0_JP.md)

The specification includes the ABNF grammar, Semantic Validation rules, Canonicalization rules, the Reference Evaluation Algorithm, and a full set of Test Vectors.

## Non-Goals (Out of Scope for v1.0)

Ashiato Syntax is purely a syntax for expressing location and time conditions. The following are not specified and are left to the responsibility of the implementation (the application side):

- Distance calculation, discovery radius, GPS accuracy
- Game mechanics such as ownership, claiming, scoring, cooldowns, anti-cheat
- Server API, database schema, SNS API
- Arbitrary Boolean expressions
- Issuing, registering, or managing Application Contexts

See the "Non-Goals" section of the specification for the full list.

## Test Vectors

The Test Vectors in the specification (covering boundary values, Canonicalization, and error cases) can be used directly to verify conformance of implementations in any language.

## Contributing

Issues and Pull Requests are welcome. In particular, the following kinds of feedback are appreciated:

- Pointing out ambiguities or inconsistencies in the specification
- Reference implementations in any language (TypeScript, Rust, Go, Python, etc.)
- Additional Test Vectors

Since v1.0 is a Freeze Candidate, please discuss any backward-incompatible change proposals in an Issue first.

## License

The Ashiato Syntax specification and documentation are licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license.
