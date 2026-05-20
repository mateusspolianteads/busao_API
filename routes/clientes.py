from fastapi import APIRouter, HTTPException, status
from database import SessionLocal

from schemas.cliente import ClienteUpdate
from services.cliente_service import (
    listar_clientes,
    atualizar_cliente,
    listar_clientes_por_evento,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/listar")
def listar():
    db = SessionLocal()
    try:
        return listar_clientes(db)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro ao listar clientes: {str(e)}"
        )
    finally:
        db.close()


@router.put("/atualizar/{id}")
def atualizar(id: int, cliente: ClienteUpdate):
    db = SessionLocal()
    try:
        cliente_atualizado = atualizar_cliente(db, id, cliente)
        return {
            "mensagem": "Cliente atualizado com sucesso",
            "cliente": cliente_atualizado,
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )
    finally:
        db.close()


@router.get("/evento/{evento_id}")
def listar_por_evento(
    evento_id: int,
    pagina: int = 1,
    limite: int = 10,
    search: str = "",
):
    db = SessionLocal()

    try:
        clientes, total = listar_clientes_por_evento(
            db, evento_id, pagina, limite, search
        )

        return {
            "clientes": clientes,
            "total": total
        }

    finally:
        db.close()
