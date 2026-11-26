"""Download and summarize the public Iowa crash dataset."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_URL = "https://idh-be.iowa.gov/api/v1/datasets/13/rows.csv"
SOURCE_NAME = "Iowa Data Hub — Vehicle Crashes in Iowa"
SOURCE_LICENSE = "CC BY 4.0"


def download_iowa_crashes(raw_dir: Path, processed_dir: Path) -> dict[str, object]:
    """Download the official archive and create BI-friendly public summaries."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    archive_path = raw_dir / "iowa_vehicle_crashes_13.zip"
    request = Request(SOURCE_URL, headers={"User-Agent": "InsureIQ/1.0"})
    with urlopen(request, timeout=180) as response, archive_path.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            target.write(chunk)

    monthly: Counter[tuple[str, str]] = Counter()
    severity: Counter[tuple[str, str]] = Counter()
    county: Counter[tuple[str, str]] = Counter()
    rows = 0
    with zipfile.ZipFile(archive_path) as archive:
        members = [name for name in archive.namelist() if name.endswith(".csv")]
        with (processed_dir / "public_iowa_crashes_sample.csv").open(
            "w", newline="", encoding="utf-8"
        ) as sample_file:
            sample_writer = None
            for member in members:
                with archive.open(member) as binary:
                    text = io.TextIOWrapper(binary, encoding="utf-8-sig", newline="")
                    reader = csv.DictReader(text)
                    if sample_writer is None:
                        sample_writer = csv.DictWriter(
                            sample_file, fieldnames=reader.fieldnames or []
                        )
                        sample_writer.writeheader()
                    for row in reader:
                        rows += 1
                        crash_on = row.get("crash_on", "")[:7]
                        severity_name = row.get("crash_severity", "Unknown") or "Unknown"
                        county_name = row.get("county_name", "Unknown") or "Unknown"
                        monthly[(crash_on, severity_name)] += 1
                        severity[(severity_name, "crashes")] += 1
                        county[(county_name, "crashes")] += 1
                        if rows <= 50000:
                            sample_writer.writerow(row)

    summary_path = processed_dir / "public_iowa_crashes_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["dimension", "category", "period", "crashes"])
        writer.writeheader()
        for (period, category), count in sorted(monthly.items()):
            writer.writerow(
                {
                    "dimension": "month_severity",
                    "category": category,
                    "period": period,
                    "crashes": count,
                }
            )
        for (category, _), count in sorted(severity.items()):
            writer.writerow(
                {
                    "dimension": "severity",
                    "category": category,
                    "period": "",
                    "crashes": count,
                }
            )
        for (category, _), count in sorted(county.items()):
            writer.writerow(
                {
                    "dimension": "county",
                    "category": category,
                    "period": "",
                    "crashes": count,
                }
            )

    metadata = {
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "license": SOURCE_LICENSE,
        "downloaded_rows": rows,
        "raw_archive": str(archive_path),
        "summary": str(summary_path),
        "sample_rows": min(rows, 50000),
        "is_insurance_claim_data": False,
        "limitation": "Public vehicle crashes are a safety/risk proxy, not insurance claims.",
    }
    (processed_dir / "public_iowa_crashes_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return metadata
