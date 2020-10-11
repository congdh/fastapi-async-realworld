from httpx import Response


def assert_error_response(response: Response, status_code: int, detail: str):
    assert response.status_code == status_code
    assert "detail" in response.json()
    assert response.json()["detail"] == detail
