from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    vendor: Optional[str] = None
    date: Optional[str] = None
    total_amount: Optional[float] = None
    category: Optional[str] = None
    corrected: bool
    created_at: datetime


class DocumentDetail(DocumentSummary):
    raw_text: Optional[str] = None
    line_items: Optional[list[dict[str, Any]]] = None
    updated_at: datetime


class DocumentUpdate(BaseModel):
    vendor: Optional[str] = None
    date: Optional[str] = None
    total_amount: Optional[float] = None
    category: Optional[str] = None
    line_items: Optional[list[dict[str, Any]]] = None
