#!/usr/bin/env python3
import json
from pathlib import Path

INPUT = Path("globe-data-output-5.json")
OUTPUT = Path("globe-data-null-countries-5.json")

KEYS_TO_CHECK = [
    "latest_year",
    "total_external_debt_usd",
    "debt_per_capita_usd",
    "debt_pct_gdp",
    "debt_concept",
    "data_source",
    "data_vintage",
]


def has_null(item: dict) -> bool:
    for k in KEYS_TO_CHECK:
        if item.get(k) is None:
            return True
    return False


def main():
    data = json.loads(INPUT.read_text())
    items = data.get("items", [])

    null_items = [it for it in items if has_null(it)]

    out = {"item_count": len(null_items), "items": null_items}
    OUTPUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"Found {len(null_items)} countries with nulls. Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
