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

    return response.json()["public_id"]


def create_project(client, token, organization_public_id):

    response = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend API",
            "description": "Project",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 201

    return response.json()["public_id"]


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

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    response = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Implement API"


def test_list_tasks(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/projects/{project_public_id}/tasks",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_task(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    created = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    task_public_id = created.json()["public_id"]

    response = client.put(
        f"/api/v1/projects/tasks/{task_public_id}",
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

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    created = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    task_public_id = created.json()["public_id"]

    response = client.delete(
        f"/api/v1/projects/{project_public_id}/tasks/{task_public_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204


def test_create_task_invalid_project(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/11111111-1111-1111-1111-111111111111/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_update_nonexistent_task(client):

    token = get_token(client)

    response = client.put(
        "/api/v1/projects/tasks/11111111-1111-1111-1111-111111111111",
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

    fake_project_id = "11111111-1111-1111-1111-111111111111"
    fake_task_id = "22222222-2222-2222-2222-222222222222"

    response = client.delete(
        f"/api/v1/projects/{fake_project_id}/tasks/{fake_task_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_restore_task(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    task = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    ).json()

    client.delete(
        f"/api/v1/projects/{project_public_id}/tasks/{task['public_id']}",
        headers=auth_header(token),
    )

    response = client.post(
        f"/api/v1/projects/tasks/{task['public_id']}/restore",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["public_id"] == task["public_id"]


def test_restore_active_task(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    task = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    ).json()

    response = client.post(
        f"/api/v1/projects/tasks/{task['public_id']}/restore",
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_restore_missing_task(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/tasks/11111111-1111-1111-1111-111111111111/restore",
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_archive_task(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    task = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    ).json()

    response = client.post(
        f"/api/v1/projects/tasks/{task['public_id']}/archive",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["is_archived"] is True


def test_archive_missing_task(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/tasks/11111111-1111-1111-1111-111111111111/archive",
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_archive_task_twice(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    task = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    ).json()

    client.post(
        f"/api/v1/projects/tasks/{task['public_id']}/archive",
        headers=auth_header(token),
    )

    response = client.post(
        f"/api/v1/projects/tasks/{task['public_id']}/archive",
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_unarchive_active_task(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project_public_id = create_project(
        client,
        token,
        organization_public_id,
    )

    task = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    ).json()

    response = client.post(
        f"/api/v1/projects/tasks/{task['public_id']}/unarchive",
        headers=auth_header(token),
    )

    assert response.status_code == 400