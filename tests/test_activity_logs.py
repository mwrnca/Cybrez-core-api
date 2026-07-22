from tests.test_organizations import (
    auth_header,
    get_token,
    create_organization,
)
from uuid import UUID

def test_list_activity_logs(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_activity_logs_invalid_org(client):

    token = get_token(client)

    response = client.get(
        "/api/v1/activity-logs/11111111-1111-1111-1111-111111111111",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_activity_logs_requires_login(client):

    response = client.get(
        "/api/v1/activity-logs/11111111-1111-1111-1111-111111111111",
    )

    assert response.status_code == 401

def test_activity_log_created(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )

    logs = response.json()

    assert len(logs) >= 2

def test_activity_logs_sorted(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "First",
            "description": "One",
        },
        headers=auth_header(token),
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Second",
            "description": "Two",
        },
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )

    logs = response.json()

    assert logs[0]["created_at"] >= logs[1]["created_at"]