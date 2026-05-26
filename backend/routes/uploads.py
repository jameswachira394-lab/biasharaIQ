"""
Upload and document parsing routes for BiasharaIQ.
Handles file uploads, parsing, categorization, and transaction import.
"""

import json
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import cloudinary
import cloudinary.uploader

from core.database import get_db
from core.config import settings
from middleware.auth import get_current_user
from models.models import User, UploadedDocument, Transaction, TransactionType
from services.document_parser import parse_document, generate_batch_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["uploads"])

if settings.CLOUDINARY_URL:
    cloudinary.config(url=settings.CLOUDINARY_URL)


class TransactionUpdate(BaseModel):
    category: str = None
    description: str = None


class ConfirmBatchRequest(BaseModel):
    updates: dict[int, TransactionUpdate] = {}


# ─────────────────────────────────────────────
# POST /uploads/document — upload and parse
# ─────────────────────────────────────────────

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    phone: Optional[str] = Form(None),   # M-Pesa phone number for password-protected PDFs
    password: Optional[str] = Form(None), # explicit password for bank PDFs
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document (M-Pesa PDF, bank statement, CSV, or invoice).
    For M-Pesa PDFs, pass the subscriber's phone number as `phone` (e.g. 0712345678).
    Parse it, categorize transactions, and save as confirmed.
    """
    try:
        file_bytes = await file.read()
        filename = file.filename or "upload"
        mime_type = file.content_type or "application/octet-stream"

        logger.info(
            "[UPLOAD] User %s uploading %s (%d bytes), phone_hint=%s",
            current_user.id, filename, len(file_bytes), bool(phone)
        )

        # Parse document — pass phone so M-Pesa PDFs can be unlocked
        try:
            transactions, doc_type = parse_document(
                file_bytes, filename, mime_type,
                phone=phone,
                password=password or "",
            )
        except ValueError as e:
            # Surface friendly errors (wrong password, no transactions, etc.)
            raise HTTPException(status_code=422, detail=str(e))

        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in document")

        logger.info("[UPLOAD] Parsed %d transactions from %s", len(transactions), doc_type)

        # Upload to Cloudinary
        storage_url = ""
        if settings.CLOUDINARY_URL:
            try:
                upload_result = cloudinary.uploader.upload(
                    file_bytes,
                    resource_type="auto",
                    folder=f"biasharaiq/{current_user.id}",
                    public_id=filename,
                )
                storage_url = upload_result["secure_url"]
                logger.info("[UPLOAD] File stored at %s", storage_url)
            except Exception as e:
                logger.warning("[UPLOAD] Cloudinary upload failed: %s. Continuing.", e)
                storage_url = f"local://{filename}"
        else:
            storage_url = f"local://{filename}"

        batch_id = generate_batch_id()
        now = datetime.utcnow()

        doc_record = UploadedDocument(
            user_id=current_user.id,
            filename=filename,
            file_type=doc_type,
            storage_url=storage_url,
            transaction_count=len(transactions),
            batch_id=batch_id,
            status="confirmed",
            parsed_at=now,          # ← always set explicitly
            created_at=now,
            summary=json.dumps({"doc_type": doc_type, "transaction_count": len(transactions)}),
        )
        db.add(doc_record)
        db.flush()

        for tx_data in transactions:
            tx = Transaction(
                user_id=current_user.id,
                amount=tx_data["amount"],
                type=TransactionType(tx_data["type"]),
                category="Uncategorized",
                date=datetime.fromisoformat(tx_data["date"]),
                description=tx_data["description"],
                source=tx_data["source"],
                import_batch_id=batch_id,
                status="confirmed",
            )
            db.add(tx)

        db.commit()
        logger.info("[UPLOAD] Batch %s imported with %d confirmed transactions", batch_id, len(transactions))

        return {
            "batch_id": batch_id,
            "document_id": doc_record.id,
            "doc_type": doc_type,
            "transaction_count": len(transactions),
            "status": "confirmed",
            "message": f"Successfully imported {len(transactions)} transactions",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("[UPLOAD] Unexpected error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


# ─────────────────────────────────────────────
# GET /uploads/preview/{batch_id}
# ─────────────────────────────────────────────

@router.get("/preview/{batch_id}")
async def preview_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(UploadedDocument).filter(
        UploadedDocument.batch_id == batch_id,
        UploadedDocument.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Batch not found")

    transactions = db.query(Transaction).filter(
        Transaction.import_batch_id == batch_id,
        Transaction.user_id == current_user.id,
        Transaction.status == "pending_review",
    ).all()

    return {
        "batch_id": batch_id,
        "document": {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "parsed_at": doc.parsed_at.isoformat() if doc.parsed_at else None,
        },
        "summary": json.loads(doc.summary) if doc.summary else {},
        "transactions": [
            {
                "id": tx.id,
                "date": tx.date.isoformat(),
                "description": tx.description,
                "amount": tx.amount,
                "type": tx.type.value,
                "category": tx.category,
                "source": tx.source,
            }
            for tx in transactions
        ],
    }


# ─────────────────────────────────────────────
# POST /uploads/confirm/{batch_id}
# ─────────────────────────────────────────────

@router.post("/confirm/{batch_id}")
async def confirm_batch(
    batch_id: str,
    request_body: ConfirmBatchRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(UploadedDocument).filter(
        UploadedDocument.batch_id == batch_id,
        UploadedDocument.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Batch not found")

    transactions = db.query(Transaction).filter(
        Transaction.import_batch_id == batch_id,
        Transaction.user_id == current_user.id,
    ).all()

    updates = request_body.updates
    if updates:
        for tx in transactions:
            if tx.id in updates:
                update_data = updates[tx.id]
                if update_data.category:
                    tx.category = update_data.category
                if update_data.description:
                    tx.description = update_data.description

    for tx in transactions:
        tx.status = "confirmed"

    doc.status = "confirmed"
    db.commit()
    logger.info("[UPLOAD] Batch %s confirmed with %d transactions", batch_id, len(transactions))

    return {
        "batch_id": batch_id,
        "status": "confirmed",
        "transaction_count": len(transactions),
    }


# ─────────────────────────────────────────────
# DELETE /uploads/cancel/{batch_id}
# ─────────────────────────────────────────────

@router.delete("/cancel/{batch_id}")
async def cancel_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(UploadedDocument).filter(
        UploadedDocument.batch_id == batch_id,
        UploadedDocument.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Batch not found")

    db.query(Transaction).filter(
        Transaction.import_batch_id == batch_id,
        Transaction.status == "pending_review",
    ).delete()

    doc.status = "cancelled"
    db.commit()
    logger.info("[UPLOAD] Batch %s cancelled", batch_id)

    return {"batch_id": batch_id, "status": "cancelled"}


# ─────────────────────────────────────────────
# GET /uploads/history
# ─────────────────────────────────────────────

@router.get("/history")
async def upload_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(UploadedDocument).filter(
        UploadedDocument.user_id == current_user.id,
    ).order_by(UploadedDocument.created_at.desc()).all()

    return [
        {
            "id": doc.id,
            "batch_id": doc.batch_id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "transaction_count": doc.transaction_count,
            "status": doc.status,
            "parsed_at": doc.parsed_at.isoformat() if doc.parsed_at else None,
            "summary": json.loads(doc.summary) if doc.summary else {},
        }
        for doc in docs
    ]