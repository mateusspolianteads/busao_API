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
def listar_por_evento(evento_id: int):
    db = SessionLocal()
    try:
        # Agora retorna a lista diretamente (mesmo se for vazia []), sem estourar 404 falso
        return listar_clientes_por_evento(db, evento_id)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro ao listar clientes do evento: {str(e)}"
        )
    finally:
        db.close()