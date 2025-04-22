from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src.schemas import CodeExchangeRequest, GoogleLoginResponse
from src.models import User, get_db
from src.lib.oauth_helpers import exchange_code_to_tokens
from src.lib.crypto import encrypt

router = APIRouter()

@router.post("/callback", response_model=GoogleLoginResponse)
def google_login_callback(payload: CodeExchangeRequest, db: Session = Depends(get_db)):
    tokens = exchange_code_to_tokens(
        code=payload.code,
        verifier=payload.verifier,
        redirect_uri="http://localhost:8000/auth/google/callback"
    )
    user = db.query(User).filter(User.email == tokens["email"]).first()
    if not user:
        user = User(
            full_name=tokens["name"],
            email=tokens["email"],
            profile_picture=tokens["picture"],
            provider="google"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    user.access_token = encrypt(tokens["access_token"])
    user.refresh_token = encrypt(tokens["refresh_token"])
    user.expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
    db.commit()
    return GoogleLoginResponse(
        client_id=user.client_id,
        message="Logged in successfully",
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_at=user.expires_at
    )
