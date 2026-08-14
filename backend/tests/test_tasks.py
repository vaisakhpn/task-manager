from fastapi.testclient import TestClient


def get_auth_headers(client: TestClient, email: str) -> dict[str, str]:
    client.post("/auth/register", json={"email": email, "password": "password123"})
    login_res = client.post("/auth/login", data={"username": email, "password": "password123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_tasks(client: TestClient):
    headers = get_auth_headers(client, "taskuser@example.com")

    # Create task
    create_res = client.post(
        "/tasks/add",
        json={"title": "Pytest Task", "description": "Testing FastAPI"},
        headers=headers,
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["title"] == "Pytest Task"
    assert data["description"] == "Testing FastAPI"

    # List tasks
    list_res = client.get("/tasks/list", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert len(list_data["items"]) == 1


def test_bola_security_isolation(client: TestClient):
    headers_a = get_auth_headers(client, "user_a@example.com")
    headers_b = get_auth_headers(client, "user_b@example.com")

    # User A creates a task
    task_a = client.post(
        "/tasks/add",
        json={"title": "User A Private Task"},
        headers=headers_a,
    ).json()

    task_id = task_a["id"]

    # User B attempts to access User A's task -> Must return 404
    get_res = client.get(f"/tasks/show/{task_id}", headers=headers_b)
    assert get_res.status_code == 404

    # User B attempts to update User A's task -> Must return 404
    patch_res = client.patch(
        f"/tasks/update/{task_id}",
        json={"title": "Hacked Title"},
        headers=headers_b,
    )
    assert patch_res.status_code == 404

    # User B attempts to delete User A's task -> Must return 404
    del_res = client.delete(f"/tasks/delete/{task_id}", headers=headers_b)
    assert del_res.status_code == 404
