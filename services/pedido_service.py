from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.pedido import Pedido
from models.evento import Evento
from models.cliente import Cliente
from utils.cache import cached


def criar_pedido(db: Session, dados):
    pedido_existente = db.query(Pedido).filter(Pedido.id == dados.id).first()
    if pedido_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um Pedido com esse ID",
        )

    novo_pedido = Pedido(
        id=dados.id,
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
        aprovado=dados.aprovado,
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


def listar_pedido_por_evento(
    db: Session, evento_id: int, pagina: int = 1, limite: int = 10
) -> dict:
    skip = (pagina - 1) * limite

    @cached(ttl=5)
    def _fetch(evento_id, pagina, limite):
        total = db.query(Pedido).filter(Pedido.evento_id == evento_id).count()

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
        return total, resultados

    total, resultados = _fetch(evento_id, pagina, limite)

    lista_pedidos = [
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
        for p in resultados
    ]

    return {
        "pedidos": lista_pedidos,
        "total": total,
        "pagina": pagina,
        "limite": limite,
    }


def obter_dados_dashboard(
    db: Session, canal_venda: str = None, periodo: str = None
) -> dict:
    if db.bind.dialect.name == "postgresql":
        periodo_expr = func.to_char(Pedido.data_venda, "YYYY-MM")
    else:
        periodo_expr = func.strftime("%Y-%m", Pedido.data_venda)

    @cached(ttl=10)
    def _fetch_dashboard(canal_venda, periodo):
        vendedor_query = (
            db.query(Pedido.canal_venda)
            .distinct()
            .filter(Pedido.canal_venda != None)
            .order_by(Pedido.canal_venda)
        )
        vendedores = [v[0] for v in vendedor_query.all() if v[0]]

        periodo_query = db.query(periodo_expr).distinct().order_by(periodo_expr.desc())
        periodos = [p[0] for p in periodo_query.all() if p[0]]

        base_query = db.query(Pedido).join(Evento)

        if canal_venda:
            base_query = base_query.filter(Pedido.canal_venda == canal_venda)
        if periodo:
            base_query = base_query.filter(periodo_expr == periodo)

        totals = base_query.with_entities(
            func.coalesce(func.sum(Pedido.valor_lote), 0.0),
            func.count(Pedido.id),
            func.count(func.distinct(Pedido.evento_id)),
        ).first()

        total_vendas = float(totals[0] or 0)
        ingressos_vendidos = int(totals[1] or 0)
        eventos_com_venda = int(totals[2] or 0)

        eventos_query = db.query(
            Evento.id.label("evento_id"),
            Evento.nome.label("nome"),
            func.count(Pedido.id).label("total_pedidos"),
            func.coalesce(func.sum(Pedido.valor_lote), 0.0).label("total_vendas"),
            func.max(Pedido.canal_venda).label("canal_venda"),
            func.max(periodo_expr).label("periodo"),
        ).join(Pedido, Pedido.evento_id == Evento.id)

        if canal_venda:
            eventos_query = eventos_query.filter(Pedido.canal_venda == canal_venda)
        if periodo:
            eventos_query = eventos_query.filter(periodo_expr == periodo)

        eventos_result = (
            eventos_query.group_by(Evento.id)
            .order_by(func.sum(Pedido.valor_lote).desc())
            .all()
        )

        return {
            "vendedores": vendedores,
            "periodos": periodos,
            "total_vendas": total_vendas,
            "ingressos_vendidos": ingressos_vendidos,
            "eventos_com_venda": eventos_com_venda,
            "eventos_result": eventos_result,
        }

    dashboard_data = _fetch_dashboard(canal_venda, periodo)

    vendedores = dashboard_data["vendedores"]
    periodos = dashboard_data["periodos"]
    total_vendas = dashboard_data["total_vendas"]
    ingressos_vendidos = dashboard_data["ingressos_vendidos"]
    eventos_com_venda = dashboard_data["eventos_com_venda"]
    eventos_result = dashboard_data["eventos_result"]

    eventos = [
        {
            "evento_id": e.evento_id,
            "nome": e.nome,
            "evento_nome": e.nome,
            "total_pedidos": int(e.total_pedidos or 0),
            "total_vendas": float(e.total_vendas or 0),
            "canal_venda": e.canal_venda,
            "periodo": e.periodo,
        }
        for e in eventos_result
    ]

    return {
        "filtros": {
            "vendedores": vendedores,
            "periodos": periodos,
        },
        "totals": {
            "total_vendas": total_vendas,
            "ingressos_vendidos": ingressos_vendidos,
            "eventos_com_venda": eventos_com_venda,
        },
        "eventos": eventos,
    }


def deletar_pedido(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    cliente_id = pedido.cliente_id

    db.delete(pedido)
    db.commit()

    # verifica se o cliente ainda tem pedidos
    pedidos_restantes = (
        db.query(Pedido)
        .filter(Pedido.cliente_id == cliente_id)
        .count()
    )

    if pedidos_restantes == 0:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if cliente:
            db.delete(cliente)
            db.commit()

    return {"mensagem": "Pedido deletado com sucesso"}
