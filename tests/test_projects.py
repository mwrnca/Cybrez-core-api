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

    organization_id = create_organization(
        client,
        token,
    )

    response = client.post(
        f"/api/v1/projects/{organization_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Backend API"


def test_list_projects(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    client.post(
        f"/api/v1/projects/{organization_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/projects/organization/{organization_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_project(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    created = client.post(
        f"/api/v1/projects/{organization_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    project_id = created.json()["id"]

    response = client.put(
        f"/api/v1/projects/{project_id}",
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

    organization_id = create_organization(
        client,
        token,
    )

    created = client.post(
        f"/api/v1/projects/{organization_id}",
        json=project_payload(),
        headers=auth_header(token),
    )

    project_id = created.json()["id"]

    response = client.delete(
        f"/api/v1/projects/{project_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204


def test_create_project_invalid_organization(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/projects/9999",
        json=project_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_update_nonexistent_project(client):

    token = get_token(client)

    response = client.put(
        "/api/v1/projects/9999",
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
        "/api/v1/projects/9999",
        headers=auth_header(token),
    )

    assert response.status_code == 404