from fastapi import HTTPException
from models.usuario import Usuario
from utils.security import (
    verificar_senha,
    criar_token,
    criar_refresh_token
)

def login_usuario(db, dados):

    user = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos"
        )

    if not verificar_senha(dados.senha, user.senha):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos"
        )

    access_token = criar_token({"sub": user.email})
    refresh_token = criar_refresh_token({"sub": user.email})

    return {
        "status": "ok",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "usuario": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email
        }
    }