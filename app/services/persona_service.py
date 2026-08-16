from uuid import UUID

from sqlalchemy.orm import Session

from app.models.persona import Persona
from app.repositories.persona_repository import PersonaRepository
from app.schemas.persona import PersonaCreate, PersonaUpdate


class PersonaService:

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        data: PersonaCreate,
    ) -> Persona:
        existing_type = (
            PersonaRepository.get_user_persona_by_type(
                db,
                user_id,
                data.type.value,
            )
        )

        if existing_type:
            raise ValueError(
                f"You already have a {data.type.value} persona"
            )

        existing_slug = (
            PersonaRepository.get_by_slug(
                db,
                data.slug,
            )
        )

        if existing_slug:
            raise ValueError(
                "That persona slug is already in use"
            )

        persona = Persona(
            user_id=user_id,
            type=data.type.value,
            display_name=data.display_name,
            slug=data.slug,
            bio=data.bio,
            is_public=data.is_public,
            is_directory_visible=data.is_directory_visible,
        )

        return PersonaRepository.create(
            db,
            persona,
        )

    @staticmethod
    def get_user_personas(
        db: Session,
        user_id: int,
    ) -> list[Persona]:
        return PersonaRepository.get_user_personas(
            db,
            user_id,
        )

    @staticmethod
    def get_public_persona(
        db: Session,
        public_id: UUID,
    ) -> Persona | None:
        return PersonaRepository.get_public_by_public_id(
            db,
            public_id,
        )

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        public_id: UUID,
        data: PersonaUpdate,
    ) -> Persona:
        persona = (
            PersonaRepository.get_user_persona_by_public_id(
                db,
                user_id,
                public_id,
            )
        )

        if persona is None:
            raise ValueError("Persona not found")

        if data.type is not None:
            existing_type = (
                PersonaRepository.get_user_persona_by_type(
                    db,
                    user_id,
                    data.type.value,
                )
            )

            if (
                existing_type
                and existing_type.id != persona.id
            ):
                raise ValueError(
                    f"You already have a {data.type.value} persona"
                )

            persona.type = data.type.value

        if data.slug is not None:
            existing_slug = (
                PersonaRepository.get_by_slug(
                    db,
                    data.slug,
                )
            )

            if (
                existing_slug
                and existing_slug.id != persona.id
            ):
                raise ValueError(
                    "That persona slug is already in use"
                )

            persona.slug = data.slug

        if data.display_name is not None:
            persona.display_name = data.display_name

        if data.bio is not None:
            persona.bio = data.bio

        if data.is_public is not None:
            persona.is_public = data.is_public

        if data.is_directory_visible is not None:
            persona.is_directory_visible = (
                data.is_directory_visible
            )

        return PersonaRepository.update(
            db,
            persona,
        )

    @staticmethod
    def delete(
        db: Session,
        user_id: int,
        public_id: UUID,
    ) -> Persona:
        persona = (
            PersonaRepository.get_user_persona_by_public_id(
                db,
                user_id,
                public_id,
            )
        )

        if persona is None:
            raise ValueError("Persona not found")

        return PersonaRepository.delete(
            db,
            persona,
            user_id,
        )