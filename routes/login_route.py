from fastapi import APIRouter
from database import SessionLocal
from schemas.login import LoginSchema
from services.login_service import login_usuario

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

@router.post("")
def login(dados: LoginSchema):

    db = SessionLocal()

    try:
        return login_usuario(db, dados)

    finally:
        db.close()