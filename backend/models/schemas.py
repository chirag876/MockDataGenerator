from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FormatEnum(str, Enum):
    JSON = "JSON"
    CSV = "CSV"
    TSV = "TSV"
    YAML = "YAML"
    XML = "XML"
    PARQUET = "Parquet"
    AVRO = "Avro"
    PROTOBUF = "Protobuf"


class DataRequest(BaseModel):
    topic: str
    format: FormatEnum
    num_records: int = Field(default=100, le=1000, ge=1)
    custom_fields: Optional[List[str]] = None
    seed: Optional[int] = None


class TopicInfo(BaseModel):
    name: str
    description: str
    fields: List[str]


class DataResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None
    content_type: str = "application/json"
