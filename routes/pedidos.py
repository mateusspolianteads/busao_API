from fastapi import APIRouter, UploadFile, File
from database import SessionLocal
import pandas as pd
from io import BytesIO
from models.cliente import Cliente
from models.evento import Evento

from models.pedido import Pedido

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/listar")
def listar():
    db = SessionLocal()
    try:
        # A query retorna tuplas, onde cada item corresponde aos campos selecionados
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
            .all()
        )

        # CONVERSÃO PARA LISTA DE DICIONÁRIOS
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


""" @router.post("/importar-planilha")
async def importar_planilha(file: UploadFile = File(...)):
    db = SessionLocal()

    try:
        conteudo = await file.read()

        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(conteudo))

        elif file.filename.endswith(".xls"):
            df = pd.read_excel(BytesIO(conteudo))

        else:
            return {"erro": "Formato inválido"}

        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        pedidos_importados = []

        for _, row in df.iterrows():

            pedido = Pedido(
                cliente_id=int(row["cliente_id"]),
                evento_id=int(row["evento_id"]),
                data_venda=row.get("data_venda"),
                status_pedido=str(row.get("status_pedido", "")),
                status_ingresso=str(row.get("status_ingresso", "")),
                lote=row.get("lote"),
                valor_lote=row.get("valor_lote"),
                canal_venda=row.get("canal_venda"),
                metodo_pagamento=row.get("metodo_pagamento"),
                transferido=bool(row.get("transferido", False)),
                aprovado=bool(row.get("aprovado", False))
            )

            db.add(pedido)

            pedidos_importados.append({
                "cliente_id": pedido.cliente_id,
                "evento_id": pedido.evento_id
            })

        db.commit()

        return {
            "mensagem": "Importação de pedidos finalizada",
            "total_importados": len(pedidos_importados),
            "pedidos_importados": pedidos_importados
        }

    finally:
        db.close() """
