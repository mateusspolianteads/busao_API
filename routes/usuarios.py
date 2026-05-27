from fastapi import APIRouter, HTTPException 
from database import SessionLocal
from schemas.usuario import UsuarioCreate
from services.usuario_service import criar_usuario, consultar_usuario
from services.email_service import enviar_email
from pydantic import BaseModel
from models.usuario import Usuario
from utils.security import criar_token_reset_senha, validar_token_reset_senha,renovar_access_token
from crm.email_reset_senha import template_reset_senha
from schemas.esqueci_senha import EsqueciSenhaSchema
from schemas.resetar_senha import ResetarSenhaSchema
from services.usuario_service import redefinir_senha

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

class LoginSchema(BaseModel):
    usuario: str
    senha: str


@router.post("/cadastrar")
def cadastrar(usuario: UsuarioCreate):
    db = SessionLocal()
    try:  
        novo_usuario = criar_usuario(db, usuario)

        return {
            "mensagem": "Usuário cadastrado com sucesso",
            "usuario": {
                "id": novo_usuario.id,
                "nome": novo_usuario.nome,
                "email": novo_usuario.email
            }
        }
    finally:
        db.close() 

@router.get("/consultar/{id}")
def consultar_por_id(id: int):
    db = SessionLocal()
    try:  
        usuario = consultar_usuario(db, id)

        if not usuario: 
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return usuario
    finally:
        db.close()

@router.post("/esqueci-senha")
def esqueci_senha(dados: EsqueciSenhaSchema):

    db = SessionLocal()

    try:

        user = db.query(Usuario).filter(
            Usuario.email == dados.email
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Email não encontrado"
            )

        token = criar_token_reset_senha(user.email)

        link = f"http://localhost:5500/templates/resetar-senha.html?token={token}"

        html = template_reset_senha(
            user.nome,
            link
        )

        enviar_email(
            destinatario=user.email,
            nome=user.nome,
            assunto="Redefinição de senha",
            html=html
        )

        return {
            "mensagem": "Email enviado com sucesso"
        }

    finally:
        db.close()

@router.post("/resetar-senha")
def resetar_senha(dados: ResetarSenhaSchema):

    db = SessionLocal()

    try:

        email = validar_token_reset_senha(
            dados.token
        )

        redefinir_senha(
            db,
            email,
            dados.nova_senha
        )

        return {
            "mensagem": "Senha redefinida com sucesso"
        }

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Token inválido ou expirado"
        )

    finally:

        db.close()

@router.post("/refresh")
def refresh_token(dados: dict):

    refresh_token = dados.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Refresh token obrigatório"
        )

    try:
        novo_access_token = renovar_access_token(refresh_token)

        return {
            "access_token": novo_access_token
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido"
        )