"""
Upload and document parsing routes for BiasharaIQ.
Handles file uploads, parsing, categorization, and transaction import.
"""

import json
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import cloudinary
import cloudinary.uploader

from core.database import get_db
from core.config import settings
from middleware.auth import get_current_user
from models.models import User, UploadedDocument, Transaction, TransactionType
from services.document_parser import parse_document, generate_batch_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["uploads"])

# Configure Cloudinary
if settings.CLOUDINARY_URL:
    cloudinary.config(url=settings.CLOUDINARY_URL)


# Pydantic models
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document (M-Pesa PDF, bank statement, CSV, or invoice).
    Parse it, categorize transactions, and save as pending_review.
    """
    try:
        # Read file
        file_bytes = await file.read()
        filename = file.filename or "upload"
        mime_type = file.content_type or "application/octet-stream"

        logger.info(f"[UPLOAD] User {current_user.id} uploading {filename} ({len(file_bytes)} bytes)")

        # Parse document
        transactions, doc_type = parse_document(file_bytes, filename, mime_type)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in document")

        logger.info(f"[UPLOAD] Parsed {len(transactions)} transactions from {doc_type}")

        # Upload file to Cloudinary
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
                logger.info(f"[UPLOAD] File stored at {storage_url}")
            except Exception as e:
                logger.warning(f"[UPLOAD] Cloudinary upload failed: {e}. Continuing without storage.")
                storage_url = f"local://{filename}"
        else:
            storage_url = f"local://{filename}"

        # Create batch ID and UploadedDocument record
        batch_id = generate_batch_id()

        doc_record = UploadedDocument(
            user_id=current_user.id,
            filename=filename,
            file_type=doc_type,
            storage_url=storage_url,
            transaction_count=len(transactions),
            batch_id=batch_id,
            status="confirmed",
            summary=json.dumps({"doc_type": doc_type, "transaction_count": len(transactions)}),
        )
        db.add(doc_record)
        db.flush()  # Get the ID

        # Create Transaction records directly as confirmed (no AI categorization)
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
        logger.info(f"[UPLOAD] Batch {batch_id} imported with {len(transactions)} confirmed transactions")

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
        logger.error(f"[UPLOAD] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


# ─────────────────────────────────────────────
# GET /uploads/preview/{batch} — preview pending transactions
# ─────────────────────────────────────────────

@router.get("/preview/{batch_id}")
async def preview_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return pending transactions from a batch for review.
    User can see categorization and decide to confirm or edit.
    """
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
            "parsed_at": doc.parsed_at.isoformat(),
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
# POST /uploads/confirm/{batch} — confirm and save batch
# ─────────────────────────────────────────────

@router.post("/confirm/{batch_id}")
async def confirm_batch(
    batch_id: str,
    request_body: ConfirmBatchRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirm a batch: mark transactions as "confirmed" and move to live.
    Optionally accept manual edits to categories/descriptions.
    """
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

    # Apply updates if provided
    updates = request_body.updates
    if updates:
        for tx in transactions:
            if tx.id in updates:
                update_data = updates[tx.id]
                if update_data.category:
                    tx.category = update_data.category
                if update_data.description:
                    tx.description = update_data.description

    # Mark all as confirmed
    for tx in transactions:
        tx.status = "confirmed"

    doc.status = "confirmed"

    db.commit()
    logger.info(f"[UPLOAD] Batch {batch_id} confirmed with {len(transactions)} transactions")

    return {
        "batch_id": batch_id,
        "status": "confirmed",
        "transaction_count": len(transactions),
    }


# ─────────────────────────────────────────────
# DELETE /uploads/cancel/{batch} — cancel/discard batch
# ─────────────────────────────────────────────

@router.delete("/cancel/{batch_id}")
async def cancel_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a pending batch: delete all pending_review transactions and the document record.
    """
    doc = db.query(UploadedDocument).filter(
        UploadedDocument.batch_id == batch_id,
        UploadedDocument.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Delete pending transactions
    db.query(Transaction).filter(
        Transaction.import_batch_id == batch_id,
        Transaction.status == "pending_review",
    ).delete()

    # Mark document as cancelled
    doc.status = "cancelled"
    db.commit()

    logger.info(f"[UPLOAD] Batch {batch_id} cancelled")

    return {"batch_id": batch_id, "status": "cancelled"}


# ─────────────────────────────────────────────
# GET /uploads/history — list past uploads
# ─────────────────────────────────────────────

@router.get("/history")
async def upload_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get upload history for the current user.
    """
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
            "parsed_at": doc.parsed_at.isoformat(),
            "summary": json.loads(doc.summary) if doc.summary else {},
        }
        for doc in docs
    ]
