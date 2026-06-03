from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
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
def cadastrar(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    nova_categoria = criar_categoria(db, categoria)
    return {
        "mensagem": "Categoria criada com sucesso",
        "categoria": {"id": nova_categoria.id, "nome": nova_categoria.nome},
    }


@router.get("/listar")
def listar(db: Session = Depends(get_db)):
    return listar_categorias(db)


@router.get("/consultar/{id}")
def consultar(id: int, db: Session = Depends(get_db)):
    categoria = consultar_categoria(db, id)
    return {"id": categoria.id, "nome": categoria.nome}


@router.put("/atualizar/{id}")
def atualizar(id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria_atualizada = atualizar_categoria(db, id, dados)
    return {
        "mensagem": "Categoria atualizada com sucesso",
        "categoria": {"id": categoria_atualizada.id, "nome": categoria_atualizada.nome},
    }


@router.delete("/deletar/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    deletar_categoria(db, id)
    return {"mensagem": "Categoria deletada com sucesso"}