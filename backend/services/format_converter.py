import base64
import io
import json
from typing import Any, Dict, List, Tuple
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd
import yaml


class FormatConverter:
    @staticmethod
    def convert_to_format(data: List[Dict[str, Any]], format_type: str, topic: str) -> Tuple[str, str, str]:
        """Convert data to specified format and return (content, filename, content_type)"""
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

        if format_type == "JSON":
            content = json.dumps(data, indent=2, default=str)
            return content, f"{topic}_data_{timestamp}.json", "application/json"

        elif format_type == "CSV":
            df = pd.DataFrame(data)
            content = df.to_csv(index=False)
            return content, f"{topic}_data_{timestamp}.csv", "text/csv"

        elif format_type == "TSV":
            df = pd.DataFrame(data)
            content = df.to_csv(index=False, sep='\t')
            return content, f"{topic}_data_{timestamp}.tsv", "text/tab-separated-values"

        elif format_type == "YAML":
            # For better readability, you can also format it as a dictionary of records
            if isinstance(data, list) and len(data) > 0:
                # Option 1: Keep as list but with better formatting
                content = yaml.dump(
                    data, 
                    default_flow_style=False, 
                    allow_unicode=True,
                    indent=2,
                    width=1000,              # Prevent line wrapping
                    sort_keys=False,
                    explicit_end = False,
                    explicit_start = False
                )
            else:
                content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
            return content, f"{topic}_data_{timestamp}.yaml", "application/x-yaml"

        elif format_type == "XML":
            root = Element("data")
            for i, record in enumerate(data):
                item = SubElement(root, "record", id=str(i+1))
                for key, value in record.items():
                    field = SubElement(item, key)
                    field.text = str(value)

            rough_string = tostring(root, 'unicode')
            reparsed = minidom.parseString(rough_string)
            content = reparsed.toprettyxml(indent="  ")
            return content, f"{topic}_data_{timestamp}.xml", "application/xml"

        elif format_type == "Parquet":
            df = pd.DataFrame(data)
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            content = base64.b64encode(buffer.getvalue()).decode()
            return content, f"{topic}_data_{timestamp}.parquet", "application/octet-stream"

        else:
            # Default to JSON for unsupported formats
            content = json.dumps(data, indent=2, default=str)
            return content, f"{topic}_data_{timestamp}.json", "application/json"
