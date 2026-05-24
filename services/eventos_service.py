from fastapi import HTTPException
from models.evento import Evento
from services.crm_service import processar_novo_evento


def criar_evento(db, dados):

    novo_evento = Evento(
        nome=dados.nome,
        categoria_id=dados.categoria_id,
        data_evento=dados.data_evento,
        local=dados.local,
        valor_passagem=dados.valor_passagem,
        imagem=dados.imagem
    )

    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    processar_novo_evento(db, novo_evento)

    return novo_evento


def listar_eventos(db):
    return db.query(Evento).all()


def buscar_evento_por_id(db, evento_id):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()

    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    return evento


def atualizar_evento(db, evento_id, dados):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()

    if not evento:
        return None

    if dados.nome is not None:
        evento.nome = dados.nome

    if dados.categoria_id is not None:
        evento.categoria_id = dados.categoria_id

    if dados.data_evento is not None:
        evento.data_evento = dados.data_evento

    if dados.local is not None:
        evento.local = dados.local

    if dados.valor_passagem is not None:
        evento.valor_passagem = dados.valor_passagem

    if dados.imagem is not None:
        evento.imagem = dados.imagem

    db.commit()
    db.refresh(evento)

    return evento


def deletar_evento(db, evento_id):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()

    if not evento:
        return False

    db.delete(evento)
    db.commit()

    return True