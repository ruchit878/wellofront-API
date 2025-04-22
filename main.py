# main.py

import os
import base64
import uuid
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from mangum import Mangum

# HTTP client for token exchange if ever needed
import requests
from jose import jwt  # for PKCE flow, not used here

from models import Agent, Knowledge, Integration, User, get_db, Base, engine
from schemas import (
    AgentRequestBody,
    KnowledgeRequest,
    IntegrationRequest,
    GoogleProfileRequest,   # <— NEW
    GoogleLoginResponse,
)
from azure.storage.blob import BlobServiceClient
from lib.crypto import encrypt

# -------------------- Load Environment --------------------
load_dotenv()

# -------------------- Azure Blob Setup --------------------
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME   = os.getenv("AZURE_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client     = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

# -------------------- Database Setup --------------------
Base.metadata.create_all(bind=engine)

# -------------------- FastAPI Init --------------------
app     = FastAPI()
handler = Mangum(app)

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Helpers --------------------
def upload_file_to_blob(file_base64: str, file_name: str) -> str:
    """
    Upload a base64-encoded file to Azure Blob Storage and return its URL.
    """
    data      = base64.b64decode(file_base64)
    blob_name = f"{uuid.uuid4()}_{file_name}"
    blob      = container_client.get_blob_client(blob_name)
    blob.upload_blob(data, overwrite=True)
    return (
        f"https://"
        f"{blob_service_client.account_name}.blob.core.windows.net/"
        f"{AZURE_CONTAINER_NAME}/{blob_name}"
    )


# -------------------- Endpoints --------------------

@app.post("/agent/")
def create_agent_with_knowledge(
    body: AgentRequestBody,
    db:   Session = Depends(get_db),
):
    """
    Create an Agent along with its Knowledge files and Integrations.
    """
    # 1) Save Agent
    db_agent = Agent(**body.agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    agent_id = db_agent.identity

    # 2) Save Knowledge entries
    for k in body.knowledge:
        url = k.file_url or upload_file_to_blob(k.file_blob_base64, k.file_name)
        db.add(
            Knowledge(
                client_id   = body.agent.client_id,
                agent_id    = agent_id,
                file_name   = k.file_name,
                file_type   = k.file_type,
                file_size   = k.file_size,
                file_url    = url,
                upload_date = k.upload_date or datetime.utcnow(),
            )
        )

    # 3) Save Integrations
    for i in body.integration:
        db.add(
            Integration(
                client_id    = body.agent.client_id,
                agent_id     = agent_id,
                type         = i.type,
                status       = i.status,
                config       = i.config,
                connected_at = i.connected_at,
            )
        )

    db.commit()
    return {
        "agent":        db_agent,
        "knowledge":    [k.file_name for k in body.knowledge],
        "integrations": [i.type for i in body.integration],
        "agent_id":     agent_id,
    }


@app.post("/auth/google", response_model=GoogleLoginResponse)
def google_profile_login(
    payload: GoogleProfileRequest,
    db:      Session = Depends(get_db),
):
    """
    Accepts a Google user profile + access_token from the front end,
    upserts the User, encrypts & stores access_token, and returns client_id.
    """
    # 1) Compute expiry (implicit flow tokens usually expire in 3600s)
    expires_at = datetime.utcnow() + timedelta(seconds=3600)

    # 2) Upsert User record
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            full_name       = payload.full_name,
            email           = payload.email,
            profile_picture = payload.profile_picture,
            provider        = payload.provider,
            access_token    = encrypt(payload.access_token),
            refresh_token   = "",           # no refresh_token in implicit flow
            expires_at      = expires_at,
        )
        db.add(user)
    else:
        # update existing row
        user.full_name       = payload.full_name
        user.profile_picture = payload.profile_picture
        user.access_token    = encrypt(payload.access_token)
        user.expires_at      = expires_at

    db.commit()

    # 3) Return extended login response
    return GoogleLoginResponse(
        client_id       = user.client_id,
        message         = "Logged in successfully.",
        full_name       = user.full_name,
        email           = user.email,
        profile_picture = user.profile_picture,
        provider        = user.provider,
    )



# import os
# import base64
# import uuid
# from datetime import datetime, timedelta

# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from mangum import Mangum

# from models import Agent, Knowledge, Integration, User, get_db, Base, engine
# from schemas import (
#     AgentRequestBody,
#     KnowledgeRequest,
#     IntegrationRequest,
#     GoogleLoginRequest,
#     GoogleLoginResponse,
#     CodeExchangeRequest,
#     CalendarCodeExchangeRequest,
# )
# from azure.storage.blob import BlobServiceClient
# from lib.crypto import encrypt, decrypt
# from lib.oauth_helpers import exchange_code_to_tokens

# # -------------------- Azure Blob Setup --------------------
# load_dotenv()
# AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

# blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
# container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

# # -------------------- DB Table Creation --------------------
# Base.metadata.create_all(bind=engine)

# # -------------------- FastAPI Init --------------------
# app = FastAPI()
# handler = Mangum(app)

# # -------------------- CORS --------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------------- Helpers --------------------
# def upload_file_to_blob(file_base64: str, file_name: str) -> str:
#     file_content = base64.b64decode(file_base64)
#     blob_name = f"{uuid.uuid4()}_{file_name}"
#     blob_client = container_client.get_blob_client(blob_name)
#     blob_client.upload_blob(file_content, overwrite=True)
#     return f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_name}"

# # -------------------- Create Agent with Knowledge & Integration --------------------
# @app.post("/agent/")
# def create_agent_with_knowledge(body: AgentRequestBody, db: Session = Depends(get_db)):
#     agent_data = body.agent
#     knowledge_items = body.knowledge
#     integration_items = body.integration

#     # Step 1: Save agent and get agent_id
#     db_agent = Agent(**agent_data.dict())
#     db.add(db_agent)
#     db.commit()
#     db.refresh(db_agent)
#     agent_id = db_agent.identity

#     # Step 2: Save knowledge files
#     saved_knowledge = []
#     for k in knowledge_items:
#         file_url = k.file_url
#         if k.file_blob_base64:
#             file_url = upload_file_to_blob(k.file_blob_base64, k.file_name)
#         db_knowledge = Knowledge(
#             client_id=agent_data.client_id,
#             agent_id=agent_id,
#             file_name=k.file_name,
#             file_type=k.file_type,
#             file_size=k.file_size,
#             file_url=file_url,
#             upload_date=k.upload_date or datetime.utcnow(),
#         )
#         db.add(db_knowledge)
#         saved_knowledge.append(db_knowledge)

#     # Step 3: Save legacy integrations (non-OAuth)
#     saved_integrations = []
#     for i in integration_items:
#         db_integration = Integration(
#             client_id=agent_data.client_id,
#             agent_id=agent_id,
#             type=i.type,
#             status=i.status,
#             config=i.config or "",
#             connected_at=i.connected_at,
#         )
#         db.add(db_integration)
#         saved_integrations.append(db_integration)

#     db.commit()
#     return {
#         "agent": db_agent,
#         "knowledge": [k.file_name for k in saved_knowledge],
#         "integrations": [i.type for i in saved_integrations],
#         "agent_id": agent_id,
#     }

# # -------------------- OAuth Login Callback --------------------
# @app.post("/auth/google/callback", response_model=GoogleLoginResponse)
# def google_oauth_callback(payload: CodeExchangeRequest, db: Session = Depends(get_db)):
#     tokens = exchange_code_to_tokens(
#         code=payload.code,
#         verifier=payload.verifier,
#         redirect_uri=os.getenv("GOOGLE_LOGIN_REDIRECT_URI"),
#     )
#     user = db.query(User).filter(User.email == tokens["email"]).first()
#     if not user:
#         user = User(
#             full_name=tokens["name"],
#             email=tokens["email"],
#             profile_picture=tokens["picture"],
#             provider="google",
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#     user.access_token = encrypt(tokens["access_token"])
#     user.refresh_token = encrypt(tokens["refresh_token"])
#     user.expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
#     db.commit()
#     return GoogleLoginResponse(
#         client_id=user.client_id,
#         message="Logged in successfully.",
#         access_token=tokens["access_token"],
#         refresh_token=tokens["refresh_token"],
#         expires_at=user.expires_at,
#     )

# # -------------------- OAuth Calendar Callback --------------------
# @app.post("/integrations/google/calendar/callback", response_model=IntegrationRequest)
# def google_calendar_callback(payload: CalendarCodeExchangeRequest, db: Session = Depends(get_db)):
#     tokens = exchange_code_to_tokens(
#         code=payload.code,
#         verifier=payload.verifier,
#         redirect_uri=os.getenv("GOOGLE_CALENDAR_REDIRECT_URI"),
#     )
#     integ = db.query(Integration).filter(
#         Integration.client_id == payload.client_id,
#         Integration.agent_id == payload.agent_id,
#         Integration.type == "google-calendar",
#     ).first()
#     if not integ:
#         integ = Integration(
#             client_id=payload.client_id,
#             agent_id=payload.agent_id,
#             type="google-calendar",
#             connected_at=datetime.utcnow().isoformat(),
#         )
#         db.add(integ)
#     integ.access_token = encrypt(tokens["access_token"])
#     integ.refresh_token = encrypt(tokens["refresh_token"])
#     integ.expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
#     integ.status = "connected"
#     db.commit()
#     db.refresh(integ)
#     return integ
