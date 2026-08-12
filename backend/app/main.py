import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import extraction, models, schemas
from .database import Base, engine, get_db

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents", response_model=schemas.DocumentDetail)
async def create_document(
    file: Optional[UploadFile] = File(default=None),
    text: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide a file or raw text")

    if file:
        filename = file.filename or "upload"
        content = await file.read()

        stored_name = f"{uuid.uuid4().hex}-{filename}"
        (UPLOAD_DIR / stored_name).write_bytes(content)

        content_type = file.content_type or ""
        if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
            raw_text = extraction.extract_pdf_text(content)
            fields = extraction.extract_from_text(raw_text)
        elif content_type.startswith("image/"):
            fields = extraction.extract_from_image(content, content_type)
            raw_text = None
        else:
            raw_text = content.decode("utf-8", errors="ignore")
            fields = extraction.extract_from_text(raw_text)
    else:
        filename = "pasted-text.txt"
        raw_text = text
        fields = extraction.extract_from_text(raw_text)

    document = models.Document(
        filename=filename,
        raw_text=raw_text,
        vendor=fields.get("vendor"),
        date=fields.get("date"),
        total_amount=fields.get("total_amount"),
        category=fields.get("category"),
        line_items=fields.get("line_items"),
        corrected=False,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@app.get("/documents", response_model=list[schemas.DocumentSummary])
def list_documents(db: Session = Depends(get_db)):
    return db.query(models.Document).order_by(models.Document.created_at.desc()).all()


@app.get("/documents/{document_id}", response_model=schemas.DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.patch("/documents/{document_id}", response_model=schemas.DocumentDetail)
def update_document(
    document_id: int, update: schemas.DocumentUpdate, db: Session = Depends(get_db)
):
    document = db.get(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    document.corrected = True

    db.commit()
    db.refresh(document)
    return document
