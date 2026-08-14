from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "pytest_register@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "pytest_register@example.com"
    assert "id" in data


def test_login_user(client: TestClient):
    # 1. Register user
    client.post(
        "/auth/register",
        json={"email": "pytest_login@example.com", "password": "testpassword123"},
    )

    # 2. Login
    response = client.post(
        "/auth/login",
        data={"username": "pytest_login@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "pytest_wrong@example.com", "password": "correctpassword"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "pytest_wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
