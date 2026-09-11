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


def create_user(client, email, name):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": name,
        },
    )
    assert response.status_code == 201
    return response.json()


def login(client, email):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def member_comment_context(client, email="comment-member@example.com"):
    owner_token = get_token(client)
    organization_public_id = create_organization(client, owner_token)
    project_public_id = create_project(
        client,
        owner_token,
        organization_public_id,
    )
    task = create_task(client, owner_token, project_public_id)
    member = create_user(client, email, "Comment Member")

    response = client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={"user_id": member["public_id"], "role": "employee"},
        headers=auth_header(owner_token),
    )
    assert response.status_code == 201

    member_token = login(client, email)
    comment_response = client.post(
        f"/api/v1/comments/task/{task['public_id']}",
        json={"content": "Member comment"},
        headers=auth_header(member_token),
    )
    assert comment_response.status_code == 201

    return {
        "owner_token": owner_token,
        "organization_public_id": organization_public_id,
        "member_token": member_token,
        "comment": comment_response.json(),
    }


def leave_organization(client, context):
    response = client.delete(
        f"/api/v1/organizations/{context['organization_public_id']}/leave",
        headers=auth_header(context["member_token"]),
    )
    assert response.status_code == 204


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


def test_former_comment_author_cannot_update_comment(client):
    context = member_comment_context(client, "former-update@example.com")
    leave_organization(client, context)

    response = client.put(
        f"/api/v1/comments/{context['comment']['public_id']}",
        json={"content": "Unauthorized update"},
        headers=auth_header(context["member_token"]),
    )

    assert response.status_code == 403


def test_former_comment_author_cannot_delete_comment(client):
    context = member_comment_context(client, "former-delete@example.com")
    leave_organization(client, context)

    response = client.delete(
        f"/api/v1/comments/{context['comment']['public_id']}",
        headers=auth_header(context["member_token"]),
    )

    assert response.status_code == 403


def test_former_comment_author_cannot_restore_comment(client):
    context = member_comment_context(client, "former-restore@example.com")

    delete_response = client.delete(
        f"/api/v1/comments/{context['comment']['public_id']}",
        headers=auth_header(context["member_token"]),
    )
    assert delete_response.status_code == 204
    leave_organization(client, context)

    response = client.post(
        f"/api/v1/comments/{context['comment']['public_id']}/restore",
        headers=auth_header(context["member_token"]),
    )

    assert response.status_code == 403


def test_organization_admin_can_mutate_another_members_comment(client):
    owner_token = get_token(client)
    organization_public_id = create_organization(client, owner_token)
    project_public_id = create_project(
        client,
        owner_token,
        organization_public_id,
    )
    task = create_task(client, owner_token, project_public_id)
    admin = create_user(client, "comment-admin@example.com", "Comment Admin")

    response = client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={"user_id": admin["public_id"], "role": "admin"},
        headers=auth_header(owner_token),
    )
    assert response.status_code == 201

    comment_response = client.post(
        f"/api/v1/comments/task/{task['public_id']}",
        json={"content": "Owner comment"},
        headers=auth_header(owner_token),
    )
    assert comment_response.status_code == 201
    comment_public_id = comment_response.json()["public_id"]
    admin_token = login(client, "comment-admin@example.com")

    update_response = client.put(
        f"/api/v1/comments/{comment_public_id}",
        json={"content": "Admin update"},
        headers=auth_header(admin_token),
    )
    assert update_response.status_code == 200

    delete_response = client.delete(
        f"/api/v1/comments/{comment_public_id}",
        headers=auth_header(admin_token),
    )
    assert delete_response.status_code == 204

    restore_response = client.post(
        f"/api/v1/comments/{comment_public_id}/restore",
        headers=auth_header(admin_token),
    )
    assert restore_response.status_code == 200
