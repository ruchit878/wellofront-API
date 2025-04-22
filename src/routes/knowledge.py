from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import Knowledge, get_db
from src.schemas import KnowledgeRequest
from src.storage.blob import upload_file_to_blob

router = APIRouter()

@router.post("/", summary="Create knowledge file entry")
def create_knowledge(entry: KnowledgeRequest, db: Session = Depends(get_db)):
    file_url = entry.file_url
    if entry.file_blob_base64:
        file_url = upload_file_to_blob(entry.file_blob_base64, entry.file_name)
    db_knowledge = Knowledge(
        client_id=entry.client_id,
        agent_id=entry.agent_id,
        file_name=entry.file_name,
        file_type=entry.file_type,
        file_size=entry.file_size,
        file_url=file_url,
        upload_date=entry.upload_date,
    )
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    return db_knowledge

@router.get("/{knowledge_id}", summary="Get knowledge file by ID")
def read_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    k = db.query(Knowledge).filter(Knowledge.identity == knowledge_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
    return k

@router.delete("/{knowledge_id}", summary="Delete knowledge file by ID")
def delete_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    k = db.query(Knowledge).filter(Knowledge.identity == knowledge_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
    db.delete(k)
    db.commit()
    return {"message": "Knowledge deleted successfully"}
