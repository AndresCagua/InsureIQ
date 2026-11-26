"""Reproducible download and conversion of the public Zenodo fraud benchmark."""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_URL = "https://zenodo.org/api/records/13381118/files/US%20Insurance%20Claims%20Data.xlsx/content"
SOURCE_PAGE = "https://zenodo.org/records/13381118"
SOURCE_LICENSE = "CC BY 4.0"
EXPECTED_MD5 = "ef6015e47bc8fb3b8c1b9e51f2f64ef7"
_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall(f"{_NS}si"):
        values.append("".join(node.text or "" for node in item.iter(f"{_NS}t")))
    return values


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    value = cell.find(f"{_NS}v")
    text = "" if value is None else value.text or ""
    if cell.get("t") == "s":
        return shared[int(text)]
    return text


def xlsx_to_csv(source: Path, destination: Path) -> int:
    """Convert the first worksheet of the public XLSX to CSV without extra engines."""
    with zipfile.ZipFile(source) as archive:
        shared = _shared_strings(archive)
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = sheet.findall(f".//{_NS}row")
        if not rows:
            raise ValueError("El workbook público no contiene filas")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            header = [_cell_value(cell, shared) for cell in rows[0].findall(f"{_NS}c")]
            header = [name for name in header if name and name != "_c39"]
            writer.writerow(header)
            for row in rows[1:]:
                values = [_cell_value(cell, shared) for cell in row.findall(f"{_NS}c")]
                writer.writerow(values[: len(header)])
    return len(rows) - 1


def download_fraud_benchmark(raw_dir: Path, processed_dir: Path) -> dict[str, object]:
    """Download, verify, convert and register the Zenodo benchmark."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "auto_insurance_claims_zenodo_13381118.xlsx"
    request = Request(SOURCE_URL, headers={"User-Agent": "InsureIQ/1.0"})
    with urlopen(request, timeout=120) as response, raw_path.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    md5 = hashlib.md5(raw_path.read_bytes()).hexdigest()
    if md5 != EXPECTED_MD5:
        raise ValueError(f"Checksum MD5 inesperado: {md5}")
    csv_path = processed_dir / "public_vehicle_fraud_benchmark.csv"
    rows = xlsx_to_csv(raw_path, csv_path)
    frame_metadata = {
        "source_name": "Auto Insurance Claims",
        "source_url": SOURCE_URL,
        "source_page": SOURCE_PAGE,
        "doi": "10.5281/zenodo.13381118",
        "license": SOURCE_LICENSE,
        "retrieval_date": "2026-11-26",
        "sha256": sha256,
        "md5": md5,
        "rows": rows,
        "target_source_column": "fraud_reported",
        "target_column": "fraud",
        "target_mapping": {"Y": 1, "N": 0},
        "limitation": (
            "Benchmark publicado; no representa validación ecuatoriana ni "
            "rendimiento productivo."
        ),
    }
    source_file = csv_path.open(newline="", encoding="utf-8")
    target_file = (processed_dir / "_target.csv").open(
        "w", newline="", encoding="utf-8"
    )
    with source_file as source, target_file as target:
        reader = csv.DictReader(source)
        fieldnames = [
            "fraud" if name == "fraud_reported" else name
            for name in reader.fieldnames or []
        ]
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            row["fraud"] = "1" if row.pop("fraud_reported") == "Y" else "0"
            writer.writerow(row)
    csv_path.unlink()
    (processed_dir / "public_vehicle_fraud_benchmark.csv").write_text(
        (processed_dir / "_target.csv").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (processed_dir / "_target.csv").unlink()
    (processed_dir / "public_vehicle_fraud_benchmark_metadata.json").write_text(
        json.dumps(frame_metadata, indent=2), encoding="utf-8"
    )
    return frame_metadata
