from tests.test_organizations import auth_header, get_token
from app.services.notification_service import NotificationService


def test_notification_flow(client, db):
    token = get_token(client)

    create_response = client.get(
        "/api/v1/notifications/",
        headers=auth_header(token),
    )

    assert create_response.status_code == 200
    assert create_response.json() == []

    user = db.query(type(db)).first() if False else None
