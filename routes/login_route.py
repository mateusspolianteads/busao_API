from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.login import LoginSchema
from services.login_service import login_usuario

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

@router.post("")
def login(dados: LoginSchema, db: Session = Depends(get_db)):
    return login_usuario(db, dados)