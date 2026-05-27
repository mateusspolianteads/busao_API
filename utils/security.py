from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
EXPIRATION_MINUTES = int(os.getenv("EXPIRATION_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str):
    senha_limpa = hashlib.sha256(senha.encode()).hexdigest()
    return pwd_context.hash(senha_limpa)


def verificar_senha(senha_plana, senha_hash):
    senha_limpa = hashlib.sha256(senha_plana.encode()).hexdigest()
    return pwd_context.verify(senha_limpa, senha_hash)


def criar_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def criar_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def criar_token_reset_senha(email: str):

    expire = datetime.utcnow() + timedelta(minutes=30)

    dados = {
        "sub": email,
        "type": "reset_senha",
        "exp": expire
    }

    return jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def validar_token_reset_senha(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "reset_senha":
            return None

        email = payload.get("sub")

        return email

    except JWTError:
        return None
    
def renovar_access_token(refresh_token: str):

    try:

        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise Exception("Token inválido")

        novo_payload = {
            "sub": payload.get("sub")
        }

        novo_access_token = criar_token(
            novo_payload
        )

        return novo_access_token

    except JWTError:
        raise Exception("Refresh token inválido")