import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.deps_auth import get_current_user
from app.deps_org import get_current_org_id
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage"))


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    org_id: int = Depends(get_current_org_id),
):
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(status_code=415, detail="tipo_de_arquivo_invalido")

    doc = Document(
        organization_id=org_id,
        owner_id=user.id,
        filename=file.filename or "documento.pdf",
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    org_dir = STORAGE_DIR / str(org_id)
    org_dir.mkdir(parents=True, exist_ok=True)
    filepath = org_dir / f"{doc.id}.pdf"

    content = await file.read()
    filepath.write_bytes(content)

    return {"id": doc.id, "filename": doc.filename, "status": doc.status}


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org_id),
):
    docs = (
        db.query(Document)
        .filter(Document.organization_id == org_id)
        .order_by(Document.id.desc())
        .limit(50)
        .all()
    )
    return [{"id": d.id, "filename": d.filename, "status": d.status, "created_at": d.created_at} for d in docs]


@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_current_org_id),
):
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.organization_id == org_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="documento_nao_encontrado")

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "extracted_text": doc.extracted_text,
        "created_at": doc.created_at,
    }
