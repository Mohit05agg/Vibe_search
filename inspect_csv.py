from __future__ import annotations

import csv
from pathlib import Path
from pprint import pprint


def preview_csv(path: Path, sample_size: int = 5) -> None:
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for _ in range(sample_size):
            try:
                rows.append(next(reader))
            except StopIteration:
                break

    print("Columns:", reader.fieldnames)
    for idx, row in enumerate(rows, 1):
        print(f"\nRow {idx}:")
        pprint(row)


if __name__ == "__main__":
    csv_path = Path("products_export_20250916_071707.csv")
    preview_csv(csv_path)




