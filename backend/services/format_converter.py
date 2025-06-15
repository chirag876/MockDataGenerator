import base64
import configparser
import io
import json
from typing import Any, Dict, List, Tuple
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd
import toml
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
        
        elif format_type == "YAML":
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            return content, f"{topic}_data_{timestamp}.yaml", "application/x-yaml"
        
        elif format_type == "TOML":
            # TOML works better with dict structure
            toml_data = {"data": data}
            content = toml.dumps(toml_data)
            return content, f"{topic}_data_{timestamp}.toml", "application/toml"
        
        elif format_type == "INI":
            config = configparser.ConfigParser()
            for i, record in enumerate(data):
                section_name = f"record_{i+1}"
                config[section_name] = {str(k): str(v) for k, v in record.items()}
            
            output = io.StringIO()
            config.write(output)
            content = output.getvalue()
            return content, f"{topic}_data_{timestamp}.ini", "text/plain"
        
        elif format_type == "Parquet":
            df = pd.DataFrame(data)
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            content = base64.b64encode(buffer.getvalue()).decode()
            return content, f"{topic}_data_{timestamp}.parquet", "application/octet-stream"
        
        elif format_type == "Feather":
            df = pd.DataFrame(data)
            buffer = io.BytesIO()
            df.to_feather(buffer)
            content = base64.b64encode(buffer.getvalue()).decode()
            return content, f"{topic}_data_{timestamp}.feather", "application/octet-stream"
        
        else:
            # Default to JSON for unsupported formats
            content = json.dumps(data, indent=2, default=str)
            return content, f"{topic}_data_{timestamp}.json", "application/json"