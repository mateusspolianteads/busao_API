from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import verify_token
from services.pedido_service import (
    deletar_pedidos_do_evento,
    listar_pedido_por_evento,
    obter_dados_dashboard,
)

router = APIRouter(
    prefix="/pedidos", tags=["Pedidos"], dependencies=[Depends(verify_token)]
)


@router.get("/evento/{evento_id}")
def listar_por_evento(
    evento_id: int,
    pagina: int = 1,
    limite: int = 10,
    db: Session = Depends(get_db),
):
    return listar_pedido_por_evento(
        db=db, evento_id=evento_id, pagina=pagina, limite=limite
    )


@router.get("/dashboard")
def dashboard(
    canal_venda: str = None,
    periodo: str = None,
    db: Session = Depends(get_db),
):
    return obter_dados_dashboard(db=db, canal_venda=canal_venda, periodo=periodo)


@router.delete("/evento/{evento_id}")
def deletar_pedidos_evento(
    evento_id: int,
    db: Session = Depends(get_db),
):
    return deletar_pedidos_do_evento(db, evento_id)
