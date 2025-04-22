# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- Table Models -----------------

class User(Base):
    __tablename__ = "Users"

    client_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    profile_picture = Column(String(512))
    provider = Column(String(50), nullable=False)
    access_token = Column(String(2048))
    refresh_token = Column(String(2048))
    expires_at = Column(DateTime)

    agents = relationship("Agent", backref="user", cascade="all, delete")
    integrations = relationship("Integration", backref="user", cascade="all, delete")

class Agent(Base):
    __tablename__ = "Agents"

    identity = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(255), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    agent_name = Column(String(255), nullable=False)
    agent_voice = Column(String(255), nullable=False)
    agent_role = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("Users.client_id", ondelete="CASCADE"), nullable=False)

    knowledge_files = relationship("Knowledge", backref="agent", cascade="all, delete")
    integrations = relationship("Integration", backref="agent", cascade="all, delete")

class Knowledge(Base):
    __tablename__ = "Knowledge"

    identity = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("Agents.identity", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("Users.client_id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), index=True, nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)
    file_url = Column(String(512))
    upload_date = Column(DateTime, default=datetime.utcnow)

class Integration(Base):
    __tablename__ = "Integrations"

    identity = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("Agents.identity", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("Users.client_id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(50))
    config = Column(String(1024))
    access_token = Column(String(2048))
    refresh_token = Column(String(2048))
    expires_at = Column(DateTime)
    connected_at = Column(DateTime)
