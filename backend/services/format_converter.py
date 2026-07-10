"""
format_converter.py — Converts generated data into requested output formats

Supports:
  - Single table  : convert_to_format()        (backward-compatible)
  - Multi-table   : convert_multi_table()       (relational / domain output)

Formats: JSON, CSV, TSV, YAML, XML, Parquet
"""

from __future__ import annotations

import base64
import io
import json
import zipfile
from typing import Any, Dict, List, Tuple
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")


def _sanitize_xml_tag(tag: str) -> str:
    """XML tag names cannot have spaces or start with digits."""
    tag = tag.strip().replace(" ", "_")
    if tag and tag[0].isdigit():
        tag = f"_{tag}"
    return tag or "field"


def _to_json(data: List[Dict[str, Any]]) -> str:
    return json.dumps(data, indent=2, default=str)


def _to_csv(data: List[Dict[str, Any]], sep: str = ",") -> str:
    return pd.DataFrame(data).to_csv(index=False, sep=sep)


def _to_yaml(data: List[Dict[str, Any]]) -> str:
    return yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        indent=2,
        width=1000,
        sort_keys=False,
    )


def _to_xml(data: List[Dict[str, Any]], root_tag: str = "data") -> str:
    root = Element(root_tag)
    for i, record in enumerate(data):
        item = SubElement(root, "record", id=str(i + 1))
        for key, value in record.items():
            field = SubElement(item, _sanitize_xml_tag(key))
            field.text = str(value) if value is not None else ""
    rough   = tostring(root, "unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")


def _to_parquet_b64(data: List[Dict[str, Any]]) -> str:
    """Returns base64-encoded parquet bytes."""
    buf = io.BytesIO()
    pd.DataFrame(data).to_parquet(buf, index=False)
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------------------
# Single-table converter (backward-compatible)
# ---------------------------------------------------------------------------

class FormatConverter:

    @staticmethod
    def convert_to_format(
        data: List[Dict[str, Any]],
        format_type: str,
        topic: str,
    ) -> Tuple[str, str, str]:
        """
        Convert data to specified format.
        Returns (content, filename, content_type).
        Backward-compatible with existing /generate and /download endpoints.
        """
        ts    = _timestamp()
        fname = f"{topic}_data_{ts}"

        if format_type == "JSON":
            return _to_json(data), f"{fname}.json", "application/json"

        if format_type == "CSV":
            return _to_csv(data), f"{fname}.csv", "text/csv"

        if format_type == "TSV":
            return _to_csv(data, sep="\t"), f"{fname}.tsv", "text/tab-separated-values"

        if format_type == "YAML":
            return _to_yaml(data), f"{fname}.yaml", "application/x-yaml"

        if format_type == "XML":
            return _to_xml(data, root_tag=topic), f"{fname}.xml", "application/xml"

        if format_type == "Parquet":
            return _to_parquet_b64(data), f"{fname}.parquet", "application/octet-stream"

        # Fallback → JSON
        return _to_json(data), f"{fname}.json", "application/json"


# ---------------------------------------------------------------------------
# Multi-table converter (relational / domain / schema-driven)
# ---------------------------------------------------------------------------

class MultiTableFormatConverter:
    """
    Converts a dict of { table_name: [records] } into the requested format.

    Strategy per format:
      JSON    → single JSON object  { "table_name": [...], ... }
      CSV/TSV → ZIP archive with one file per table
      YAML    → single YAML document with table names as top-level keys
      XML     → single XML document with <table name="..."> sections
      Parquet → ZIP archive with one .parquet file per table
    """

    @staticmethod
    def convert(
        tables_data: Dict[str, List[Dict[str, Any]]],
        format_type: str,
        label: str = "export",
    ) -> Tuple[str, str, str]:
        """
        Convert multi-table data to the requested format.
        Returns (content, filename, content_type).

        For ZIP-based formats (CSV, TSV, Parquet), content is base64-encoded ZIP.
        For text formats (JSON, YAML, XML), content is a plain string.
        """
        ts    = _timestamp()
        fname = f"{label}_{ts}"

        if format_type == "JSON":
            content = json.dumps(tables_data, indent=2, default=str)
            return content, f"{fname}.json", "application/json"

        if format_type in ("CSV", "TSV"):
            sep = "\t" if format_type == "TSV" else ","
            ext = "tsv" if format_type == "TSV" else "csv"
            mime = "text/tab-separated-values" if format_type == "TSV" else "text/csv"
            zip_b64 = MultiTableFormatConverter._to_zip(
                tables_data,
                ext=ext,
                serializer=lambda data: _to_csv(data, sep=sep).encode("utf-8"),
            )
            return zip_b64, f"{fname}.zip", "application/zip"

        if format_type == "YAML":
            content = yaml.dump(
                tables_data,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
                width=1000,
                sort_keys=False,
            )
            return content, f"{fname}.yaml", "application/x-yaml"

        if format_type == "XML":
            content = MultiTableFormatConverter._to_multi_xml(tables_data)
            return content, f"{fname}.xml", "application/xml"

        if format_type == "Parquet":
            zip_b64 = MultiTableFormatConverter._to_zip(
                tables_data,
                ext="parquet",
                serializer=lambda data: MultiTableFormatConverter._parquet_bytes(data),
            )
            return zip_b64, f"{fname}.zip", "application/zip"

        # Fallback → JSON
        content = json.dumps(tables_data, indent=2, default=str)
        return content, f"{fname}.json", "application/json"

    # ── Internal helpers ──────────────────────────────────────────────────

    @staticmethod
    def _to_zip(
        tables_data: Dict[str, List[Dict[str, Any]]],
        ext: str,
        serializer,
    ) -> str:
        """Pack multiple table files into a ZIP, return base64-encoded string."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for table_name, records in tables_data.items():
                file_bytes = serializer(records)
                zf.writestr(f"{table_name}.{ext}", file_bytes)
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def _parquet_bytes(data: List[Dict[str, Any]]) -> bytes:
        buf = io.BytesIO()
        pd.DataFrame(data).to_parquet(buf, index=False)
        return buf.getvalue()

    @staticmethod
    def _to_multi_xml(tables_data: Dict[str, List[Dict[str, Any]]]) -> str:
        root = Element("dataset")
        for table_name, records in tables_data.items():
            table_el = SubElement(root, "table", name=_sanitize_xml_tag(table_name))
            for i, record in enumerate(records):
                row_el = SubElement(table_el, "record", id=str(i + 1))
                for key, value in record.items():
                    field_el      = SubElement(row_el, _sanitize_xml_tag(key))
                    field_el.text = str(value) if value is not None else ""
        rough = tostring(root, "unicode")
        return minidom.parseString(rough).toprettyxml(indent="  ")