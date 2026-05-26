from fastapi import FastAPI
from database import Base, engine
from routes import usuarios, clientes, eventos, pedidos, categorias, upload, importacao_route
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:64444",
        "http://127.0.0.1:64444"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(eventos.router)
app.include_router(pedidos.router)
app.include_router(categorias.router)
app.include_router(upload.router)
app.include_router(importacao_route.router)

@app.get("/")
def home():
    return {"mensagem": "API Busão do Rolê funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )