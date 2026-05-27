from fastapi import APIRouter, UploadFile, File, Depends
from supabase_client import supabase
from uuid import uuid4
from utils.auth import verify_token


router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
    dependencies=[Depends(verify_token)]
)

@router.post("/")
async def upload(file: UploadFile = File(...)):
    try:
        nome_arquivo = f"{uuid4()}-{file.filename}"

        conteudo = await file.read()

        supabase.storage.from_("uploads").upload(nome_arquivo, conteudo)

        url = supabase.storage.from_("uploads").get_public_url(nome_arquivo)

        return {"url": url}
    except Exception as e:
        return {"error": str(e)}