from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.pedido import Pedido

def criar_pedido(db: Session, dados):
    pedido_existente = db.query(Pedido).filter(Pedido.id == dados.id).first()
    if pedido_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Já existe um Pedido com esse ID"
        )
    
    novo_pedido = Pedido(
        id=dados.id,  # Mantém o ID enviado pelo front/API
        cliente_id=dados.cliente_id,
        evento_id=dados.evento_id,
        data_venda=dados.data_venda,
        status_pedido=dados.status_pedido,
        status_ingresso=dados.status_ingresso,
        lote=dados.lote,
        valor_lote=dados.valor_lote,
        canal_venda=dados.canal_venda,
        metodo_pagamento=dados.metodo_pagamento,
        transferido=dados.transferido,
        aprovado=dados.aprovado
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido

def consultar_pedido(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
        )
    return pedido