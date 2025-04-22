from fastapi.testclient import TestClient
from main import app

def test_create_and_read_agent():
    client = TestClient(app)
    payload = {"agent": {"agent_type":"inbound","campaign_name":"X","industry":"tech","company_name":"C","agent_name":"A","agent_voice":"V","agent_role":"sales","client_id":42},"knowledge":[],"integration":[]}
    res = client.post("/agent/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["identity"]
