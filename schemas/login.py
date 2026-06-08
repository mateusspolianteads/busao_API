from pydantic import BaseModel, EmailStr, Field

class LoginSchema(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    senha: str = Field(..., example="mudar123")