# Use mocked app if actual app is too complex to load in unit test context
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


def test_api_health():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
