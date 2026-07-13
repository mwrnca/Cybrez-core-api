from app.core.security import hash_password
from app.models.user import User


def get_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "password": "password123",
            "full_name": "Owner",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "owner@example.com",
            "password": "password123",
        },
    )

    return response.json()["access_token"]


def auth_header(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def organization_payload(
    name="Cybrez",
    slug="cybrez",
    description="Testing organization",
):
    return {
        "name": name,
        "slug": slug,
        "description": description,
        "logo_url": None,
    }


def test_create_organization(client):

    token = get_token(client)

    response = client.post(
        "/api/v1/organizations",
        json=organization_payload(),
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Cybrez"
    assert response.json()["slug"] == "cybrez"


def test_list_organizations(client):

    token = get_token(client)

    client.post(
        "/api/v1/organizations",
        json=organization_payload(),
        headers=auth_header(token),
    )

    response = client.get(
        "/api/v1/organizations/",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_organization(client):

    token = get_token(client)

    created = client.post(
        "/api/v1/organizations",
        json=organization_payload(),
        headers=auth_header(token),
    )

    organization_id = created.json()["id"]

    response = client.get(
        f"/api/v1/organizations/{organization_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == organization_id


def test_update_organization(client):

    token = get_token(client)

    created = client.post(
        "/api/v1/organizations",
        json=organization_payload(),
        headers=auth_header(token),
    )

    organization_id = created.json()["id"]

    response = client.put(
        f"/api/v1/organizations/{organization_id}",
        json=organization_payload(
            name="New Name",
            slug="new-name",
            description="Updated",
        ),
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["slug"] == "new-name"


def test_delete_organization(client):

    token = get_token(client)

    created = client.post(
        "/api/v1/organizations",
        json=organization_payload(
            name="Delete Me",
            slug="delete-me",
            description="Delete",
        ),
        headers=auth_header(token),
    )

    organization_id = created.json()["id"]

    response = client.delete(
        f"/api/v1/organizations/{organization_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/organizations/{organization_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_get_nonexistent_organization(client):

    token = get_token(client)

    response = client.get(
        "/api/v1/organizations/9999",
        headers=auth_header(token),
    )

    assert response.status_code == 404