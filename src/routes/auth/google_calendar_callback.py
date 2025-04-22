from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src.schemas import CalendarCodeExchangeRequest, IntegrationRequest
from src.models import Integration, get_db
from src.lib.oauth_helpers import exchange_code_to_tokens
from src.lib.crypto import encrypt

router = APIRouter()

@router.post("/calendar/callback", response_model=IntegrationRequest)
def google_calendar_callback(payload: CalendarCodeExchangeRequest, db: Session = Depends(get_db)):
    tokens = exchange_code_to_tokens(
        code=payload.code,
        verifier=payload.verifier,
        redirect_uri="http://localhost:8000/integrations/google/calendar/callback"
    )
    integ = db.query(Integration).filter(
        Integration.client_id == payload.client_id,
        Integration.agent_id == payload.agent_id,
        Integration.type == "google-calendar"
    ).first()
    if not integ:
        integ = Integration(
            client_id=payload.client_id,
            agent_id=payload.agent_id,
            type="google-calendar",
            connected_at=datetime.utcnow().isoformat()
        )
        db.add(integ)
    integ.access_token = encrypt(tokens["access_token"])
    integ.refresh_token = encrypt(tokens["refresh_token"])
    integ.expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
    integ.status = "connected"
    db.commit()
    db.refresh(integ)
    return IntegrationRequest(**integ.__dict__)
