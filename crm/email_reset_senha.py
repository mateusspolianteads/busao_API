def template_reset_senha(nome, link):

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">

    <head>
        <meta charset="UTF-8">
    </head>

    <body style="
        margin:0;
        padding:0;
        background:#f4f4f4;
        font-family:Arial, sans-serif;
    ">

        <table width="100%" cellspacing="0" cellpadding="0" style="padding:40px 0;">

            <tr>
                <td align="center">

                    <table width="600" cellspacing="0" cellpadding="0"
                        style="
                            background:#ffffff;
                            border-radius:16px;
                            overflow:hidden;
                            box-shadow:0 4px 20px rgba(0,0,0,0.08);
                        ">

                        <!-- HEADER -->
                        <tr>
                            <td
                                style="
                                    background:#ff6b00;
                                    padding:30px;
                                    text-align:center;
                                ">

                                <h1 style="
                                    color:white;
                                    margin:0;
                                    font-size:32px;
                                ">
                                    Busão do Rolê
                                </h1>

                            </td>
                        </tr>

                        <!-- CONTEUDO -->
                        <tr>
                            <td style="padding:40px;">

                                <h2 style="
                                    margin-top:0;
                                    color:#222;
                                ">
                                    Redefinição de senha
                                </h2>

                                <p style="
                                    color:#555;
                                    font-size:16px;
                                    line-height:1.6;
                                ">
                                    Olá <strong>{nome}</strong>,
                                </p>

                                <p style="
                                    color:#555;
                                    font-size:16px;
                                    line-height:1.6;
                                ">
                                    Recebemos uma solicitação para redefinir sua senha.
                                </p>

                                <p style="
                                    color:#555;
                                    font-size:16px;
                                    line-height:1.6;
                                ">
                                    Clique no botão abaixo para criar uma nova senha:
                                </p>

                                <!-- BOTAO -->
                                <div style="
                                    text-align:center;
                                    margin:40px 0;
                                ">

                                    <a href="{link}"
                                        style="
                                            background:#ff6b00;
                                            color:white;
                                            text-decoration:none;
                                            padding:16px 32px;
                                            border-radius:10px;
                                            display:inline-block;
                                            font-weight:bold;
                                            font-size:16px;
                                        ">

                                        Redefinir Senha

                                    </a>

                                </div>

                                <p style="
                                    color:#888;
                                    font-size:14px;
                                    line-height:1.6;
                                ">
                                    Esse link expira em 30 minutos.
                                </p>

                                <p style="
                                    color:#888;
                                    font-size:14px;
                                    line-height:1.6;
                                ">
                                    Se você não solicitou a redefinição de senha,
                                    ignore este email.
                                </p>

                            </td>
                        </tr>

                        <!-- FOOTER -->
                        <tr>
                            <td
                                style="
                                    background:#fafafa;
                                    padding:25px;
                                    text-align:center;
                                    border-top:1px solid #eee;
                                ">

                                <p style="
                                    margin:0;
                                    color:#999;
                                    font-size:13px;
                                ">
                                    © 2026 Busão do Rolê — Todos os direitos reservados
                                </p>

                            </td>
                        </tr>

                    </table>

                </td>
            </tr>

        </table>

    </body>

    </html>
    """