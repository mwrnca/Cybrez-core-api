def create_user(client, email, name):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": name,
        },
    )

    return response.json()


def login(client, email):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )

    return response.json()["access_token"]


def get_token_and_owner(client):
    owner = create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(client, "owner@example.com")

    return token, owner["public_id"]


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

    return response.json()["public_id"]


def test_add_member(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    member = create_user(
        client,
        "member@example.com",
        "Member",
    )

    response = client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={
            "user_id": member["public_id"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == member["public_id"]


def test_add_duplicate_member(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    member = create_user(
        client,
        "member@example.com",
        "Member",
    )

    client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={
            "user_id": member["public_id"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    response = client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={
            "user_id": member["public_id"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_list_members(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    member = create_user(
        client,
        "member@example.com",
        "Member",
    )

    client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={
            "user_id": member["public_id"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/organizations/{organization_public_id}/members",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_members_invalid_organization(client):

    token, owner_public_id = get_token_and_owner(client)

    response = client.get(
        "/api/v1/organizations/11111111-1111-1111-1111-111111111111/members",
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_remove_member(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    member = create_user(
        client,
        "member@example.com",
        "Member",
    )

    client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={
            "user_id": member["public_id"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    response = client.delete(
        f"/api/v1/organizations/{organization_public_id}/members/{member['public_id']}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/organizations/{organization_public_id}/members",
        headers=auth_header(token),
    )

    assert len(response.json()) == 1
    assert response.json()[0]["role"] == "owner"


def test_cannot_remove_owner(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.delete(
        f"/api/v1/organizations/{organization_public_id}/members/{owner_public_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_leave_organization(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    member = create_user(
        client,
        "member@example.com",
        "Member",
    )

    client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={
            "user_id": member["public_id"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    member_token = login(client, "member@example.com")

    response = client.delete(
        f"/api/v1/organizations/{organization_public_id}/leave",
        headers=auth_header(member_token),
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/organizations/{organization_public_id}/members",
        headers=auth_header(token),
    )

    assert len(response.json()) == 1
    assert response.json()[0]["role"] == "owner"


def test_owner_cannot_leave_organization(client):

    token, owner_public_id = get_token_and_owner(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.delete(
        f"/api/v1/organizations/{organization_public_id}/leave",
        headers=auth_header(token),
    )

    assert response.status_code == 400