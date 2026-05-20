from fastapi import APIRouter
from database import SessionLocal
from schemas.evento import EventoCreate, EventoUpdate
from models.evento import Evento
from services.eventos_service import (
    criar_evento,
    listar_eventos,
    buscar_evento_por_id,
    atualizar_evento,
    deletar_evento
)

router = APIRouter(
    prefix="/eventos",
    tags=["Eventos"]
)


@router.post("/cadastrar")
def cadastrar(evento: EventoCreate):
    db = SessionLocal()
    try:
        novo = criar_evento(db, evento)
        return novo
    finally:
        db.close()


@router.get("/listar")
def listar():
    db = SessionLocal()
    try:
        return listar_eventos(db)
    finally:
        db.close()


@router.get("/consultar/{id}")
def consultar(id: int):
    db = SessionLocal()
    try:
        return buscar_evento_por_id(db, id)
    finally:
        db.close()


@router.put("/atualizar/{id}")
def atualizar(id: int, dados: EventoUpdate):
    db = SessionLocal()
    try:
        return atualizar_evento(db, id, dados)
    finally:
        db.close()


@router.delete("/deletar/{id}")
def deletar(id: int):
    db = SessionLocal()
    try:
        deletar_evento(db, id)
        return {"mensagem": "Evento deletado com sucesso"}
    finally:
        db.close()