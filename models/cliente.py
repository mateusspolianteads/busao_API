from sqlalchemy import Column, Date, Integer, String, ForeignKey
from database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=True)
    cpf = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)