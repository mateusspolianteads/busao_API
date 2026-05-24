from brevo import Brevo
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("BREVO_API_KEY")
email_remetente = os.getenv("BREVO_EMAIL")
nome_remetente = os.getenv("BREVO_NOME")

client = Brevo(api_key=api_key)


def enviar_email(destinatario, nome, assunto, html):

    try:

        response = client.transactional_emails.send_transac_email(
            subject=assunto,

            html_content=html,

            sender=SendTransacEmailRequestSender(
                name=nome_remetente,
                email=email_remetente,
            ),

            to=[
                SendTransacEmailRequestToItem(
                    email=destinatario,
                    name=nome,
                )
            ],
        )

        print("EMAIL ENVIADO:", response.message_id)

        return True

    except Exception as e:

        print("ERRO AO ENVIAR EMAIL:", e)

        return False