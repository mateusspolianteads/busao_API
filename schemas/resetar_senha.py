from pydantic import BaseModel


class ResetarSenhaSchema(BaseModel):
    token: str
    nova_senha: str