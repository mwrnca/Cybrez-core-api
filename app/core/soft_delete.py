from datetime import datetime, timezone


def soft_delete(instance, user_id: int | None = None):
    instance.deleted_at = datetime.now(timezone.utc)
    instance.deleted_by = user_id