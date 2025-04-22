# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from typing       import Optional
from typing       import Literal


# ----------------- Request Schemas -----------------

class KnowledgeRequest(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    file_url: Optional[str] = None
    file_blob_base64: Optional[str] = None
    client_id: int
    agent_id: Optional[int] = None
    upload_date: Optional[datetime] = None

class AgentRequest(BaseModel):
    agent_type: str
    campaign_name: str
    industry: str
    company_name: str
    agent_name: str
    agent_voice: str
    agent_role: str
    client_id: int

class IntegrationRequest(BaseModel):
    client_id: int
    status: str
    config: str
    type: str
    connected_at: str
    agent_id: Optional[int] = None

class AgentRequestBody(BaseModel):
    agent: AgentRequest
    knowledge: List[KnowledgeRequest]
    integration: List[IntegrationRequest]

# PKCE Google login request + response
class GooglePKCERequest(BaseModel):
    code: str
    verifier: str

class GoogleLoginResponse(BaseModel):
    client_id: int
    message: str
    full_name: str
    email: str
    profile_picture: Optional[str] = None
    provider: str

class GoogleProfileRequest(BaseModel):
    full_name:       str
    email:           str
    profile_picture: Optional[str] = None
    provider:        Literal["google"]
    access_token:    str


# ----------------- Response Schemas -----------------
# (you may add more response models below as needed)



# from pydantic import BaseModel
# from typing import Optional, List
# from datetime import datetime

# class KnowledgeRequest(BaseModel):
#     file_name: str
#     file_type: str
#     file_size: int
#     file_url: Optional[str] = None
#     file_blob_base64: Optional[str] = None
#     client_id: int
#     agent_id: Optional[int] = None
#     upload_date: Optional[datetime] = None

# class AgentRequest(BaseModel):
#     agent_type: str
#     campaign_name: str
#     industry: str
#     company_name: str
#     agent_name: str
#     agent_voice: str
#     agent_role: str
#     client_id: int

# class IntegrationRequest(BaseModel):
#     client_id: int
#     status: str
#     config: Optional[str] = None
#     access_token: Optional[str] = None
#     refresh_token: Optional[str] = None
#     expires_at: Optional[datetime] = None
#     type: str
#     connected_at: str
#     agent_id: Optional[int] = None

# class AgentRequestBody(BaseModel):
#     agent: AgentRequest
#     knowledge: List[KnowledgeRequest]
#     integration: List[IntegrationRequest]

# class GoogleLoginRequest(BaseModel):
#     full_name: str
#     email: str
#     profile_picture: Optional[str] = None
#     provider: str

# class GoogleLoginResponse(BaseModel):
#     client_id: int
#     message: str
#     access_token: Optional[str] = None
#     refresh_token: Optional[str] = None
#     expires_at: Optional[datetime] = None

# class CodeExchangeRequest(BaseModel):
#     code: str
#     verifier: str

# class CalendarCodeExchangeRequest(BaseModel):
#     code: str
#     verifier: str
#     client_id: int
#     agent_id: int
