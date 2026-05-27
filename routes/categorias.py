from fastapi import APIRouter, Depends
from database import SessionLocal
from schemas.categoria import CategoriaCreate, CategoriaUpdate
from services.categoria_service import (
    criar_categoria,
    listar_categorias,
    consultar_categoria,
    atualizar_categoria,
    deletar_categoria
)
from utils.auth import verify_token

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
    dependencies=[Depends(verify_token)]
)

@router.post("/cadastrar")
def cadastrar(categoria: CategoriaCreate):
    db = SessionLocal()

    try:
        nova_categoria = criar_categoria(db, categoria)

        return {
            "mensagem": "Categoria criada com sucesso",
            "categoria": {
                "id": nova_categoria.id,
                "nome": nova_categoria.nome
            }
        }

    finally:
        db.close()


@router.get("/listar")
def listar():
    db = SessionLocal()

    try:
        categorias = listar_categorias(db)

        return categorias

    finally:
        db.close()


@router.get("/consultar/{id}")
def consultar(id: int):
    db = SessionLocal()

    try:
        categoria = consultar_categoria(db, id)

        return {
            "id": categoria.id,
            "nome": categoria.nome
        }

    finally:
        db.close()


@router.put("/atualizar/{id}")
def atualizar(id: int, dados: CategoriaUpdate):
    db = SessionLocal()

    try:
        categoria_atualizada = atualizar_categoria(
            db,
            id,
            dados
        )

        return {
            "mensagem": "Categoria atualizada com sucesso",
            "categoria": {
                "id": categoria_atualizada.id,
                "nome": categoria_atualizada.nome
            }
        }

    finally:
        db.close()


@router.delete("/deletar/{id}")
def deletar(id: int):
    db = SessionLocal()

    try:
        deletar_categoria(db, id)

        return {
            "mensagem": "Categoria deletada com sucesso"
        }

    finally:
        db.close()