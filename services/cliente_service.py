from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.cliente import Cliente
from models.pedido import Pedido
from utils.cache import cached

def criar_cliente(db: Session, dados):
    cpf_existente = db.query(Cliente).filter(Cliente.cpf == dados.cpf).first()
    if cpf_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já cadastrado"
        )

    novo_cliente = Cliente(
        nome=dados.nome,
        data_nascimento=dados.data_nascimento,
        cpf=dados.cpf,
        email=dados.email,
        telefone=dados.telefone,
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente

def consultar_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    return cliente

def listar_clientes(db: Session):
    return db.query(Cliente).all()

def buscar_clientes_por_nome(db: Session, cliente_nome: str):
    clientes = db.query(Cliente).filter(Cliente.nome.ilike(f"%{cliente_nome}%")).all()
    if not clientes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum cliente encontrado com este nome",
        )
    return clientes

def atualizar_cliente(db: Session, cliente_id: int, dados):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    if dados.nome is not None:
        cliente.nome = dados.nome
    if dados.email is not None:
        cliente.email = dados.email
    if dados.telefone is not None:
        cliente.telefone = dados.telefone

    db.commit()
    db.refresh(cliente)
    return cliente

def listar_clientes_por_evento(db, evento_id, pagina, limite, search):
    # Cache page results for short TTL to make pagination fast for repeated requests
    @cached(ttl=5)
    def _fetch(evento_id, pagina, limite, search):
        cliente_ids_subquery = (
            db.query(Pedido.cliente_id)
            .filter(Pedido.evento_id == evento_id)
            .distinct()
            .subquery()
        )

        query = (
            db.query(Cliente)
            .join(cliente_ids_subquery, Cliente.id == cliente_ids_subquery.c.cliente_id)
        )

        if search:
            query = query.filter(Cliente.nome.ilike(f"{search}%"))

        total = query.count()

        clientes = (
            query.order_by(Cliente.nome)
            .offset((pagina - 1) * limite)
            .limit(limite)
            .all()
        )

        return clientes, total

    return _fetch(evento_id, pagina, limite, search)

def deletar_cliente_por_id(db, cliente_id):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    db.query(Pedido).filter(Pedido.cliente_id == cliente_id).delete()
    db.delete(cliente)
    db.commit()
    return {"detail": "Cliente deletado com sucesso"}

def deletar_clientes(db):
    db.query(Pedido).delete()
    db.query(Cliente).delete()
    db.commit()

    return {"detail": "Todos os clientes foram deletados com sucesso"}