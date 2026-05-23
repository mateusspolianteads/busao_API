from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PedidoBase(BaseModel):

    cliente_id: int
    evento_id: int
    data_venda: datetime
    status_pedido: str
    status_ingresso: str
    lote: str
    valor_lote: float
    canal_venda: str
    metodo_pagamento: str
    transferido: Optional[str] = None
    aprovado: str


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(PedidoBase):
    pass


class PedidoResponse(PedidoBase):
    id: int

    class Config:
        from_attributes = True