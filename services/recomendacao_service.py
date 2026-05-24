from sqlalchemy import func
from models.pedido import Pedido
from models.evento import Evento
from models.cliente import Cliente


def buscar_clientes_por_categoria(db, categoria_id):
    
    resultado = (
        db.query(Cliente)
        .join(Pedido, Pedido.cliente_id == Cliente.id)
        .join(Evento, Evento.id == Pedido.evento_id)
        .filter(Evento.categoria_id == categoria_id)
        .group_by(Cliente.id)
        .order_by(func.count(Pedido.id).desc())
        .all()
    )

    return resultado