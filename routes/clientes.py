from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import verify_token

from schemas.cliente import ClienteUpdate
from services.cliente_service import (
    deletar_cliente_por_id,
    deletar_clientes,
    listar_clientes,
    atualizar_cliente,
    listar_clientes_por_evento,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"], dependencies=[Depends(verify_token)])


@router.get("/listar")
def listar(db: Session = Depends(get_db)):
    try:
        return listar_clientes(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar clientes: {str(e)}",
        )


@router.put("/atualizar/{id}")
def atualizar(id: int, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    try:
        cliente_atualizado = atualizar_cliente(db, id, cliente)
        return {"mensagem": "Cliente atualizado com sucesso", "cliente": cliente_atualizado}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cliente: {str(e)}",
        )


@router.get("/evento/{evento_id}")
def listar_por_evento(
    evento_id: int,
    pagina: int = 1,
    limite: int = 10,
    search: str = "",
    db: Session = Depends(get_db),
):
    clientes, total = listar_clientes_por_evento(db, evento_id, pagina, limite, search)
    return {"clientes": clientes, "total": total}

@router.delete("/deletar/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    try:
        return deletar_cliente_por_id(db, id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar cliente: {str(e)}",
        )
    
@router.delete("/deletar")
def deletar_todos_clientes(db: Session = Depends(get_db)):
    return deletar_clientes(db)