from services.recomendacao_service import buscar_clientes_por_categoria
from services.email_service import enviar_email
from crm.email_evento import template_novo_evento


def processar_novo_evento(db, evento):

    clientes = buscar_clientes_por_categoria(
        db,
        evento.categoria_id
    )

    print(f"EVENTO NOVO: {evento.nome}")
    print(f"CLIENTES ENCONTRADOS: {len(clientes)}")

    for cliente in clientes:

        if not cliente.email:
            continue
        
        html = template_novo_evento(cliente, evento)

        enviar_email(
            destinatario=cliente.email,
            nome=cliente.nome,
            assunto=f"Novo evento: {evento.nome}",
            html=html
        )
        print(f"ENVIANDO EMAIL PARA: {cliente.email}")