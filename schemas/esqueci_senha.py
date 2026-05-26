from pydantic import BaseModel


class EsqueciSenhaSchema(BaseModel):
    email: str