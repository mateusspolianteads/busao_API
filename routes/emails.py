from fastapi import APIRouter
from services.email_service import enviar_email

router = APIRouter()

@router.get("/teste-email")
def teste_email():

    enviado = enviar_email(
        destinatario="SEUEMAIL@gmail.com",
        nome="Gabriel",
        assunto="Teste CRM",
        html="""
        <h1>Email funcionando 🚀</h1>
        """
    )

    return {
        "enviado": enviado
    }