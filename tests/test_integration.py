from fastapi.testclient import TestClient
from main import app

def test_integration_crud():
    client = TestClient(app)
    payload = {"client_id":1,"status":"connected","config":"{}","type":"crm","connected_at":"2025-04-20T00:00:00Z"}
    res = client.post("/integration/", json=payload)
    assert res.status_code == 200
    iid = res.json()["identity"]
    get_res = client.get(f"/integration/{iid}")
    assert get_res.status_code == 200
    del_res = client.delete(f"/integration/{iid}")
    assert del_res.status_code == 200
