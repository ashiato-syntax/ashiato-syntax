#!/usr/bin/env python3

from pathlib import Path
import csv
import json

BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"

TZDB_VERSION = "2026c"
DICTIONARY_VERSION = 1


def base36_encode(n: int) -> str:
    if n < 0:
        raise ValueError("index must be non-negative")

    if n == 0:
        return "0"

    chars = []
    while n:
        n, remainder = divmod(n, 36)
        chars.append(BASE36[remainder])

    return "".join(reversed(chars))


def read_zone1970(path: Path) -> list[str]:
    tzids = []

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        # Comments and empty lines
        if not line or line.startswith("#"):
            continue

        fields = line.split("\t")

        if len(fields) < 3:
            raise ValueError(f"Invalid zone1970.tab line: {line}")

        tzid = fields[2]

        if not tzid:
            raise ValueError(f"Empty TZID: {line}")

        tzids.append(tzid)

    return sorted(set(tzids))


def main():
    source = Path(f"tz-resources/tzdb-{TZDB_VERSION}/zone1970.tab")
    output_dir = Path("tz-dictionary/v1")

    output_dir.mkdir(parents=True, exist_ok=True)

    tzids = read_zone1970(source)

    entries = []

    for index, tzid in enumerate(tzids):
        entries.append({
            "index": index,
            "id": base36_encode(index),
            "tzid": tzid,
        })

    assert len(tzids) == len(set(tzids))
    assert tzids == sorted(tzids)
    assert entries[0]["index"] == 0
    assert entries[0]["id"] == "0"
    assert entries[-1]["index"] == len(entries) - 1
    assert len(entries) <= 36 * 36

    # CSV
    csv_path = output_dir / "dictionary.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "id", "tzid"])

        for entry in entries:
            writer.writerow([
                entry["index"],
                entry["id"],
                entry["tzid"],
            ])

    # JSON
    json_path = output_dir / "dictionary.json"

    data = {
        "dictionary_version": DICTIONARY_VERSION,
        "iana_tzdb": TZDB_VERSION,
        "source": "zone1970.tab",
        "index_base": 0,
        "encoding": "Ashiato Base36",
        "entries": entries,
    }

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"IANA TZDB: {TZDB_VERSION}")
    print(f"Entries:    {len(entries)}")
    print(f"Max index:  {len(entries) - 1}")
    print(f"Max ID:     {base36_encode(len(entries) - 1)}")
    print(f"CSV:        {csv_path}")
    print(f"JSON:       {json_path}")


if __name__ == "__main__":
    main()
