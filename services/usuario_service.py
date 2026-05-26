from fastapi import HTTPException
from models.usuario import Usuario
from validate_docbr import CPF, CNPJ
from utils.security import hash_senha

cpf_validator = CPF()
cnpj_validator = CNPJ()


def criar_usuario(db, dados):

    email_existente = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if email_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    cpf_cnpj = str(dados.cpf_cnpj).strip()

    if not cpf_cnpj.isdigit():
        raise HTTPException(
            status_code=400, detail="Preencha CPF/CNPJ apenas com números"
        )

    is_cpf_valido = cpf_validator.validate(cpf_cnpj)
    is_cnpj_valido = cnpj_validator.validate(cpf_cnpj)

    if not (is_cpf_valido or is_cnpj_valido):
        raise HTTPException(status_code=400, detail="CPF/CNPJ inválido")

    cpf_existente = db.query(Usuario).filter(Usuario.cpf_cnpj == cpf_cnpj).first()

    if cpf_existente:
        raise HTTPException(status_code=400, detail="CPF/CNPJ já cadastrado")

    novo_usuario = Usuario(
        nome=dados.nome,
        cpf_cnpj=cpf_cnpj,
        email=dados.email,
        senha=hash_senha(dados.senha),
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


def consultar_usuario(db, usuario_id):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario


def redefinir_senha(db, email, nova_senha):

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.senha = hash_senha(nova_senha)

    db.commit()

    return True
