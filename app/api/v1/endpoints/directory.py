from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.persona_repository import PersonaRepository
from app.schemas.persona import PersonaResponse


router = APIRouter(
    prefix="/directory",
    tags=["Directory"],
)


@router.get(
    "",
    response_model=list[PersonaResponse],
)
def get_directory(
    db: Session = Depends(get_db),
):
    return PersonaRepository.get_public_directory_personas(
        db,
    )