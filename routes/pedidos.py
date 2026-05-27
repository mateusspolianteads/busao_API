from fastapi import APIRouter, HTTPException, status, Depends
from database import SessionLocal
from models.cliente import Cliente
from models.evento import Evento
from models.pedido import Pedido
from utils.auth import verify_token

router = APIRouter(prefix="/pedidos", tags=["Pedidos"], dependencies=[Depends(verify_token)])

@router.get("/evento/{evento_id}")
def listar_por_evento(
    evento_id: int,
    pagina: int = 1,
    limite: int = 10
):
    db = SessionLocal()

    try:
        skip = (pagina - 1) * limite

        total = (
            db.query(Pedido)
            .filter(Pedido.evento_id == evento_id)
            .count()
        )

        resultados = (
            db.query(
                Pedido.id,
                Pedido.data_venda,
                Pedido.status_pedido,
                Pedido.status_ingresso,
                Pedido.lote,
                Pedido.valor_lote,
                Pedido.canal_venda,
                Pedido.metodo_pagamento,
                Pedido.transferido,
                Pedido.aprovado,
                Cliente.nome.label("cliente_nome"),
                Evento.nome.label("evento_nome"),
            )
            .join(Cliente, Pedido.cliente_id == Cliente.id)
            .join(Evento, Pedido.evento_id == Evento.id)
            .filter(Pedido.evento_id == evento_id)
            .offset(skip)
            .limit(limite)
            .all()
        )

        lista_pedidos = []

        for p in resultados:
            lista_pedidos.append({
                "id": p.id,
                "data_venda": p.data_venda.isoformat() if p.data_venda else None,
                "status_pedido": p.status_pedido,
                "status_ingresso": p.status_ingresso,
                "lote": p.lote,
                "valor_lote": float(p.valor_lote) if p.valor_lote else 0.0,
                "canal_venda": p.canal_venda,
                "metodo_pagamento": p.metodo_pagamento,
                "transferido": p.transferido,
                "aprovado": p.aprovado,
                "cliente_nome": p.cliente_nome,
                "evento_nome": p.evento_nome,
            })

        return {
            "pedidos": lista_pedidos,
            "total": total,
            "pagina": pagina,
            "limite": limite
        }

    finally:
        db.close()
