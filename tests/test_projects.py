from tests.test_organizations import (
    auth_header,
    get_token,
    organization_payload,
)
from uuid import uuid4

def create_organization(client, token):

    response = client.post(
        "/api/v1/organizations",
        json=organization_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201

    return response.json()["public_id"]


def project_payload(
    name="Backend API",
    description="Project description",
):
    return {
        "name": name,
        "description": description,
    }


def test_create_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Backend API"


def test_list_projects(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/projects/organization/{organization_public_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    created = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    project_public_id = created.json()["public_id"]

    response = client.put(
        f"/api/v1/projects/{project_public_id}",
        json={
            "name": "Updated Project",
            "description": "Updated Description",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"


def test_delete_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    created = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    project_public_id = created.json()["public_id"]

    response = client.delete(
        f"/api/v1/projects/{project_public_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204


def test_create_project_invalid_organization(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/11111111-1111-1111-1111-111111111111",
        json=project_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_update_nonexistent_project(client):

    token = get_token(client)

    response = client.put(
        "/api/v1/projects/11111111-1111-1111-1111-111111111111",
        json={
            "name": "Test",
            "description": "Test",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_delete_nonexistent_project(client):

    token = get_token(client)

    response = client.delete(
        "/api/v1/projects/11111111-1111-1111-1111-111111111111",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_restore_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    ).json()

    project_public_id = project["public_id"]

    client.delete(
        f"/api/v1/projects/{project_public_id}",
        headers=auth_header(token),
    )

    response = client.post(
        f"/api/v1/projects/{project_public_id}/restore",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["public_id"] == project["public_id"]

def test_restore_active_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    )
    
    project = response.json()

    project_public_id = project["public_id"]

    response = client.post(
        f"/api/v1/projects/{project_public_id}/restore",
        headers=auth_header(token),
    )

    assert response.status_code == 400

def test_restore_missing_project(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/11111111-1111-1111-1111-111111111111/restore",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_archive_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    ).json()

    project_public_id = project["public_id"]

    response = client.post(
        f"/api/v1/projects/{project_public_id}/archive",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["is_archived"] is True

def test_archive_missing_project(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/11111111-1111-1111-1111-111111111111/archive",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_archive_project_twice(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    ).json()

    project_public_id = project["public_id"]

    client.post(
        f"/api/v1/projects/{project_public_id}/archive",
        headers=auth_header(token),
    )

    response = client.post(
        f"/api/v1/projects/{project_public_id}/archive",
        headers=auth_header(token),
    )

    assert response.status_code == 400

def test_unarchive_active_project(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    project = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    ).json()

    project_public_id = project["public_id"]
    
    response = client.post(
        f"/api/v1/projects/{project_public_id}/unarchive",
        headers=auth_header(token),
    )

    assert response.status_code == 400