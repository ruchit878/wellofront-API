from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import Integration, get_db
from src.schemas import IntegrationRequest

router = APIRouter()

@router.post("/", summary="Create integration entry")
def create_integration(entry: IntegrationRequest, db: Session = Depends(get_db)):
    db_integration = Integration(**entry.dict())
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    return db_integration

@router.get("/{integration_id}", summary="Get integration by ID")
def read_integration(integration_id: int, db: Session = Depends(get_db)):
    integ = db.query(Integration).filter(Integration.identity == integration_id).first()
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integ

@router.delete("/{integration_id}", summary="Delete integration by ID")
def delete_integration(integration_id: int, db: Session = Depends(get_db)):
    integ = db.query(Integration).filter(Integration.identity == integration_id).first()
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")
    db.delete(integ)
    db.commit()
    return {"message": "Integration deleted successfully"}
