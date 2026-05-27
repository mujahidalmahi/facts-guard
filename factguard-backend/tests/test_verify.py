from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.verify.create_claim", return_value="claim-123")
@patch("app.api.verify.process_claim", new_callable=AsyncMock)
def test_verify_returns_job_id(mock_process, mock_create):
    resp = client.post("/verify", json={"claim": "The Earth is round"})
    assert resp.status_code == 202
    assert "jobId" in resp.json()


def test_verify_rejects_short_claim():
    resp = client.post("/verify", json={"claim": "hi"})
    assert resp.status_code == 422


@patch("app.api.verify.get_job_result", new_callable=AsyncMock)
def test_verify_result_processing(mock_get_result):
    mock_get_result.return_value = None
    resp = client.get("/result/some-job-id")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "processing"
    assert data["jobId"] == "some-job-id"


@patch("app.api.verify.get_job_result", new_callable=AsyncMock)
def test_verify_result_done(mock_get_result):
    mock_get_result.return_value = {
        "verdict": "True",
        "confidence": "High",
        "summary": "Test",
        "sources": [],
    }
    resp = client.get("/result/some-job-id")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    assert "Cache-Control" in resp.headers
