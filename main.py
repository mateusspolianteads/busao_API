from fastapi import FastAPI
from database import Base, engine
from routes import (
    usuarios,
    clientes,
    eventos,
    pedidos,
    categorias,
    upload,
    importacao_route,
    login_route,
    export_route
)

from fastapi.middleware.cors import CORSMiddleware

from models.usuario import Usuario
from models.cliente import Cliente
from models.evento import Evento
from models.pedido import Pedido
from models.categoria import Categoria

app = FastAPI(
    title="Busão do Rolê API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "https://busaodorole.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria tabelas
Base.metadata.create_all(bind=engine)

# Rotas
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(eventos.router)
app.include_router(pedidos.router)
app.include_router(categorias.router)
app.include_router(upload.router)
app.include_router(importacao_route.router)
app.include_router(login_route.router)
app.include_router(export_route.router)

# Home
@app.get("/")
def home():
    return {
        "mensagem": "API Busão do Rolê funcionando"
    }

# Rodar API
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )