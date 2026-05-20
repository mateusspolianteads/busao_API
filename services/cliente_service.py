from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.cliente import Cliente
from models.pedido import Pedido

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

def listar_clientes_por_evento(db: Session, evento_id: int):
    # Retorna os clientes associados ao evento através do Pedido (pivô)
    # Se não houver nenhum, retorna [] com status 200 de forma limpa
    return (
        db.query(Cliente)
        .join(Pedido, Cliente.id == Pedido.cliente_id)
        .filter(Pedido.evento_id == evento_id)
        .distinct()
        .all()
    )