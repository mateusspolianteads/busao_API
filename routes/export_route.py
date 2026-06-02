import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.export_service import exportar_ingressos
from fastapi.responses import StreamingResponse
from supabase import create_client
import io

router = APIRouter(prefix="/pedidos", tags=["Exportação"])

class ExportarIngressosRequest(BaseModel):
    evento: str = Field(..., example="Pré carnaval BBO")

class BaixarArquivoExportadoRequest(BaseModel):
    nome_arquivo: str = Field(..., example="Pre_carnaval_BBO.xls")

@router.post("/exportar-planilha")
def exportar_ingressos_endpoint(payload: ExportarIngressosRequest):
    try:
        cpf = os.getenv("CHEERS_CPF")
        senha = os.getenv("CHEERS_SENHA")

        if not cpf or not senha:
            raise HTTPException(status_code=500, detail="Credenciais CHEERS_CPF ou CHEERS_SENHA não configuradas no ambiente.")

        caminho_storage = exportar_ingressos(
            cpf=cpf,
            senha=senha,
            evento=payload.evento
        )
        
        nome_arquivo = caminho_storage.split("/")[-1]
        
        return {
            "status": "sucesso",
            "caminho_storage": caminho_storage,
            "nome_arquivo": nome_arquivo,
            "mensagem": f"Arquivo '{nome_arquivo}' exportado e salvo no Supabase com sucesso."
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar requisição: {str(e)}")

@router.post("/baixar-arquivo-exportado")
def baixar_arquivo_exportado(payload: BaixarArquivoExportadoRequest):
    """Baixa arquivo exportado do Supabase Storage e retorna para o cliente."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise HTTPException(status_code=500, detail="Configurações do Supabase ausentes no ambiente.")
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Caminho do arquivo no Supabase
        caminho = f"exports_cheers/{payload.nome_arquivo}"
        
        print(f"[INFO] Baixando arquivo do Supabase: {caminho}")
        
        # Faz download do arquivo
        response = supabase.storage.from_("uploads").download(caminho)
        
        if not response:
            raise HTTPException(status_code=404, detail=f"Arquivo '{payload.nome_arquivo}' não encontrado no Supabase.")
        
        print(f"[OK] Arquivo baixado do Supabase com sucesso")
        
        # Retorna como streaming para economizar memória
        return StreamingResponse(
            io.BytesIO(response),
            media_type="application/vnd.ms-excel",
            headers={"Content-Disposition": f"attachment; filename={payload.nome_arquivo}"}
        )
        
    except Exception as e:
        print(f"[ERROR] Erro ao baixar arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao baixar arquivo: {str(e)}")