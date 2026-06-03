from fastapi import FastAPI
from database import Base, engine
from datetime import datetime

# Importação das rotas (agrupadas)
from routes import (
    usuarios,
    clientes,
    eventos,
    pedidos,
    categorias,
    upload,
    importacao_route,
    login_route,
    export_route,
)


from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request

from models.usuario import Usuario
from models.cliente import Cliente
from models.evento import Evento
from models.pedido import Pedido
from models.categoria import Categoria

app = FastAPI(title="Busão do Rolê API", version="1.0.0")

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

# GZip middleware para reduzir payloads de resposta
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Cria tabelas
Base.metadata.create_all(bind=engine)

print("Tabelas verificadas:", datetime.now())

# Serve arquivos estáticos com cache-control
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.middleware("http")
async def add_cache_control(request: Request, call_next):
    response = await call_next(request)
    try:
        if request.url.path.startswith("/static/"):
            # cache por 7 dias
            response.headers["Cache-Control"] = "public, max-age=604800, immutable"
    except Exception:
        pass
    return response

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
    return {"mensagem": "API Busão do Rolê funcionando"}


# Rodar API
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
