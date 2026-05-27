from fastapi import APIRouter, Depends
from database import SessionLocal
from utils.auth import verify_token
from services.pedido_service import listar_pedido_por_evento, obter_dados_dashboard

router = APIRouter(
    prefix="/pedidos", 
    tags=["Pedidos"], 
    dependencies=[Depends(verify_token)]
)


@router.get("/evento/{evento_id}")
def listar_por_evento(
    evento_id: int,
    pagina: int = 1,
    limite: int = 10
):
    db = SessionLocal()
    try:
        return listar_pedido_por_evento(
            db=db, 
            evento_id=evento_id, 
            pagina=pagina, 
            limite=limite
        )
    finally:
        db.close()


@router.get("/dashboard")
def dashboard(
    canal_venda: str = None,
    periodo: str = None
):
    db = SessionLocal()
    try:
        return obter_dados_dashboard(
            db=db, 
            canal_venda=canal_venda, 
            periodo=periodo
        )
    finally:
        db.close()