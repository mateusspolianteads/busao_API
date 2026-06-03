from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.evento import EventoCreate, EventoUpdate
from models.evento import Evento
from services.eventos_service import (
    criar_evento,
    listar_eventos,
    buscar_evento_por_id,
    atualizar_evento,
    deletar_evento
)
from utils.auth import verify_token

router = APIRouter(
    prefix="/eventos",
    tags=["Eventos"],
    dependencies=[Depends(verify_token)]
)


@router.post("/cadastrar")
def cadastrar(evento: EventoCreate, db: Session = Depends(get_db)):
    novo = criar_evento(db, evento)
    return novo


@router.get("/listar")
def listar(db: Session = Depends(get_db)):
    return listar_eventos(db)


@router.get("/consultar/{id}")
def consultar(id: int, db: Session = Depends(get_db)):
    return buscar_evento_por_id(db, id)


@router.put("/atualizar/{id}")
def atualizar(id: int, dados: EventoUpdate, db: Session = Depends(get_db)):
    return atualizar_evento(db, id, dados)


@router.delete("/deletar/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    deletar_evento(db, id)
    return {"mensagem": "Evento deletado com sucesso"}