from tests.test_organizations import (
    auth_header,
    get_token,
    organization_payload,
)
from tests.test_tasks import task_payload


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
            "name": "Comments project",
            "description": "Comment tests",
        },
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.json()["public_id"]


def create_task(client, token, project_public_id):
    response = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json=task_payload(),
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.json()


def test_comment_crud_uses_public_ids(client):
    token = get_token(client)

    organization_public_id = create_organization(client, token)
    project_public_id = create_project(client, token, organization_public_id)
    task = create_task(client, token, project_public_id)

    create_response = client.post(
        f"/api/v1/comments/task/{task['public_id']}",
        json={"content": "First comment"},
        headers=auth_header(token),
    )

    assert create_response.status_code == 201
    assert create_response.json()["content"] == "First comment"
    assert create_response.json()["task_public_id"] == task["public_id"]

    list_response = client.get(
        f"/api/v1/comments/task/{task['public_id']}",
        headers=auth_header(token),
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    comment = create_response.json()

    update_response = client.put(
        f"/api/v1/comments/{comment['public_id']}",
        json={"content": "Updated comment"},
        headers=auth_header(token),
    )

    assert update_response.status_code == 200
    assert update_response.json()["content"] == "Updated comment"

    delete_response = client.delete(
        f"/api/v1/comments/{comment['public_id']}",
        headers=auth_header(token),
    )

    assert delete_response.status_code == 204

    restore_response = client.post(
        f"/api/v1/comments/{comment['public_id']}/restore",
        headers=auth_header(token),
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["public_id"] == comment["public_id"]
