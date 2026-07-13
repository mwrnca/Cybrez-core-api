from tests.test_organizations import (
    auth_header,
    get_token,
    organization_payload,
)


def create_organization(client, token):

    response = client.post(
        "/api/v1/organizations",
        json=organization_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_project(client, token, organization_id):

    response = client.post(
        f"/api/v1/projects/{organization_id}",
        json={
            "name": "Backend API",
            "description": "Project",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 201

    return response.json()["id"]


def task_payload(
    title="Implement API",
    description="Write backend",
):
    return {
        "title": title,
        "description": description,
        "status": "todo",
        "priority": "medium",
        "assignee_id": None,
        "due_date": None,
    }


def test_create_task(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    project_id = create_project(
        client,
        token,
        organization_id,
    )

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Implement API"


def test_list_tasks(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    project_id = create_project(
        client,
        token,
        organization_id,
    )

    client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_task(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    project_id = create_project(
        client,
        token,
        organization_id,
    )

    created = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    task_id = created.json()["id"]

    response = client.put(
        f"/api/v1/projects/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated",
            "status": "in_progress",
            "priority": "high",
            "assignee_id": None,
            "due_date": None,
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["status"] == "in_progress"


def test_delete_task(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    project_id = create_project(
        client,
        token,
        organization_id,
    )

    created = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    task_id = created.json()["id"]

    response = client.delete(
        f"/api/v1/projects/tasks/{task_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204


def test_create_task_invalid_project(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/9999/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_update_nonexistent_task(client):

    token = get_token(client)

    response = client.put(
        "/api/v1/projects/tasks/9999",
        json={
            "title": "Test",
            "description": "Test",
            "status": "todo",
            "priority": "medium",
            "assignee_id": None,
            "due_date": None,
        },
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_delete_nonexistent_task(client):

    token = get_token(client)

    response = client.delete(
        "/api/v1/projects/tasks/9999",
        headers=auth_header(token),
    )

    assert response.status_code == 404