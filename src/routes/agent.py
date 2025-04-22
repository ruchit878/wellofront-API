from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import Agent, get_db
from src.schemas import AgentRequest, AgentRequestBody

router = APIRouter()

@router.post("/", summary="Create agent with knowledge & integrations (legacy)")
def create_agent_with_knowledge(body: AgentRequestBody, db: Session = Depends(get_db)):
    agent_data = body.agent
    db_agent = Agent(**agent_data.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/{agent_id}", summary="Get agent by ID")
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.identity == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", summary="Update agent by ID")
def update_agent(agent_id: int, payload: AgentRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.identity == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for k, v in payload.dict().items():
        setattr(agent, k, v)
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/{agent_id}", summary="Delete agent by ID")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.identity == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully"}
