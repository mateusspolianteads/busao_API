from fastapi import APIRouter, HTTPException, status
from database import SessionLocal
from models.cliente import Cliente
from models.evento import Evento
from models.pedido import Pedido

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.get("/evento/{evento_id}")
def listar_por_evento(evento_id: int, skip: int = 0, limit: int = 10):
    db = SessionLocal()
    try:
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
            .limit(limit) 
            .all()
        )

        # RETIRADO O ERRO 404 AQUI. 
        # Se não tiver dados (ex: página 2 vazia), ele simplesmente desce e retorna a lista vazia [].

        # Retorna os dados mapeados no formato que o frontend consome
        lista_pedidos = []
        for p in resultados:
            lista_pedidos.append(
                {
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
                }
            )

        return lista_pedidos

    finally:
        db.close()
