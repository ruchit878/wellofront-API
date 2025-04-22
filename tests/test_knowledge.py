from fastapi.testclient import TestClient
from main import app

def test_knowledge_crud():
    client = TestClient(app)
    payload = {"file_name":"doc.pdf","file_type":"pdf","file_size":123,"file_url":None,"file_blob_base64":None,"client_id":1}
    res = client.post("/knowledge/", json=payload)
    assert res.status_code == 200
    kid = res.json()["identity"]
    get_res = client.get(f"/knowledge/{kid}")
    assert get_res.status_code == 200
    del_res = client.delete(f"/knowledge/{kid}")
    assert del_res.status_code == 200
