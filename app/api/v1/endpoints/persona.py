from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.persona import (
    PersonaCreate,
    PersonaResponse,
    PersonaUpdate,
    PublicPersonaResponse,
)
from app.services.persona_service import PersonaService


router = APIRouter(
    prefix="/personas",
    tags=["Personas"],
)


@router.post(
    "",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_persona(
    data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PersonaService.create(
            db,
            current_user.id,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=list[PersonaResponse],
)
def get_my_personas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PersonaService.get_user_personas(
        db,
        current_user.id,
    )


@router.get(
    "/{public_id}",
    response_model=PublicPersonaResponse,
)
def get_persona(
    public_id: UUID,
    db: Session = Depends(get_db),
):
    persona = PersonaService.get_public_persona(
        db,
        public_id,
    )

    if persona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found",
        )

    return persona

@router.patch(
    "/{public_id}",
    response_model=PersonaResponse,
)
def update_persona(
    public_id: UUID,
    data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PersonaService.update(
            db,
            current_user.id,
            public_id,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{public_id}",
    response_model=PersonaResponse,
)
def delete_persona(
    public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PersonaService.delete(
            db,
            current_user.id,
            public_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )