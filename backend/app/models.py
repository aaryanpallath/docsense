from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)

    vendor = Column(String, nullable=True)
    date = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    line_items = Column(JSON, nullable=True)

    corrected = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
