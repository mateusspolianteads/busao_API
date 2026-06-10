def template_novo_evento(cliente, evento):
    return f"""
    <div style="
        background:#0f172a;
        padding:40px;
        font-family:Arial,sans-serif;
        color:white;
    ">

        <h1 style="color:#22c55e;">
            🎉 Novo evento para você
        </h1>

        <h2>{evento.nome}</h2>

        <p>
            Olá <b>{cliente.nome}</b>
        </p>

        <p>
            Detectamos que você curte eventos dessa categoria 👀
        </p>

        <img
            src="{evento.imagem}"
            alt="{evento.nome}"
            style="
                width:100%;
                border-radius:16px;
                margin-top:20px;
            "
        >

        <p style="margin-top:30px;">
            🚍 Transporte ida e volta disponível
        </p>

    </div>
    """