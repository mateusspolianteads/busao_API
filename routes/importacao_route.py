from fastapi import APIRouter, Depends, File, Form, UploadFile, Request
from sqlalchemy.orm import Session
from database import get_db 
from services.importacao_service import processar_planilha_clientes_e_pedidos

router = APIRouter(prefix="/pedidos", tags=["Importação"]) 

@router.post("/importar-planilha", status_code=201)
async def importar_clientes_e_pedidos_planilha(
    request: Request,
    evento_id: int = Form(...),
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    conteudo_arquivo = await file.read()
    nome_arquivo = file.filename

    resultado = await processar_planilha_clientes_e_pedidos(
        request=request,
        db=db,
        evento_id=evento_id,
        conteudo_arquivo=conteudo_arquivo,
        nome_arquivo=nome_arquivo
    )
    
    return resultado