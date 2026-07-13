from app.core.security import hash_password
from app.models.user import User


def create_user(client, email, name):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": name,
        },
    )


def get_token(client):
    create_user(
        client,
        "owner@example.com",
        "Owner",
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


def create_organization(client, token):
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Cybrez",
            "slug": "cybrez",
            "description": "Testing",
            "logo_url": None,
        },
        headers=auth_header(token),
    )

    return response.json()["id"]


def test_add_member(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    response = client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={
            "user_id": 2,
            "role": "member",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == 2


def test_add_duplicate_member(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={
            "user_id": 2,
            "role": "member",
        },
        headers=auth_header(token),
    )

    response = client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={
            "user_id": 2,
            "role": "member",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_list_members(client):

    token = get_token(client)

    organization_id = create_organization(
        client,
        token,
    )

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={
            "user_id": 2,
            "role": "member",
        },
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/organizations/{organization_id}/members",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_members_invalid_organization(client):

    token = get_token(client)

    response = client.get(
        "/api/v1/organizations/999/members",
        headers=auth_header(token),
    )

    assert response.status_code == 404