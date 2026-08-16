from uuid import UUID

from sqlalchemy.orm import Session

from app.core.soft_delete import soft_delete
from app.models.persona import Persona

class PersonaRepository:

    @staticmethod
    def create(
        db: Session,
        persona: Persona,
    ) -> Persona:
        db.add(persona)
        db.commit()
        db.refresh(persona)

        return persona

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id: UUID,
    ) -> Persona | None:
        return (
            db.query(Persona)
            .filter(
                Persona.public_id == public_id,
                Persona.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_user_persona_by_public_id(
        db: Session,
        user_id: int,
        public_id: UUID,
    ) -> Persona | None:
        return (
            db.query(Persona)
            .filter(
                Persona.public_id == public_id,
                Persona.user_id == user_id,
                Persona.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_by_slug(
        db: Session,
        slug: str,
    ) -> Persona | None:
        return (
            db.query(Persona)
            .filter(
                Persona.slug == slug,
                Persona.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_user_persona_by_type(
        db: Session,
        user_id: int,
        persona_type: str,
    ) -> Persona | None:
        return (
            db.query(Persona)
            .filter(
                Persona.user_id == user_id,
                Persona.type == persona_type,
                Persona.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_user_personas(
        db: Session,
        user_id: int,
    ) -> list[Persona]:
        return (
            db.query(Persona)
            .filter(
                Persona.user_id == user_id,
                Persona.deleted_at.is_(None),
            )
            .all()
        )

    @staticmethod
    def get_public_directory_personas(
        db: Session,
    ) -> list[Persona]:
        return (
            db.query(Persona)
            .filter(
                Persona.is_public.is_(True),
                Persona.is_directory_visible.is_(True),
                Persona.deleted_at.is_(None),
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        persona: Persona,
    ) -> Persona:
        db.commit()
        db.refresh(persona)

        return persona

    @staticmethod
    def delete(
        db: Session,
        persona: Persona,
        deleted_by: int | None = None,
    ) -> Persona:
        soft_delete(
            persona,
            deleted_by,
        )

        db.commit()
        db.refresh(persona)

        return persona

    @staticmethod
    def get_public_by_public_id(
        db: Session,
        public_id: UUID,
    ) -> Persona | None:
        return (
            db.query(Persona)
            .filter(
                Persona.public_id == public_id,
                Persona.is_public.is_(True),
                Persona.deleted_at.is_(None),
            )
            .first()
        )

    