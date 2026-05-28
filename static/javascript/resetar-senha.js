document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const senhaInput = document.getElementById("senha");
    const confirmarSenhaInput = document.getElementById("confirmar-senha");
    const button = document.querySelector(".btn-submit");

    if(form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const senha = senhaInput.value.trim();
            const confirmarSenha = confirmarSenhaInput.value.trim();
            const token = new URLSearchParams(window.location.search).get("token");

            if (!token) {
                mostrarMensagem("Token inválido ou expirado", "erro");
                return;
            }

            if (!senha || !confirmarSenha) {
                mostrarMensagem("Preencha todos os campos", "erro");
                return;
            }

            if (senha.length < 6) {
                mostrarMensagem("A senha deve ter no mínimo 6 caracteres", "erro");
                return;
            }

            if (senha !== confirmarSenha) {
                mostrarMensagem("As senhas não coincidem", "erro");
                return;
            }

            const textoOriginal = button.textContent;
            button.disabled = true;
            button.textContent = "Redefinindo...";

            try {
                const response = await fetch(`${API_URL}/usuarios/resetar-senha`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        token,
                        nova_senha: senha
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // AQUI ESTÁ A MÁGICA: Substitui o conteúdo do formulário pela mensagem de sucesso!
                    const container = document.querySelector(".auth-container");
                    
                    container.innerHTML = `
                        <div style="text-align: center; padding: 20px 0;">
                            <i data-lucide="check-circle" style="color: #2ecc71; width: 64px; height: 64px; margin-bottom: 24px; display: inline-block;"></i>
                            <h1 style="font-size: 24px; font-weight: 800; margin-bottom: 12px; color: #ffffff; letter-spacing: -0.5px;">Senha redefinida com sucesso</h1>
                            <p style="color: var(--text-dim); font-size: 15px; line-height: 1.5;">Você já pode fechar esta página e fazer login novamente no aplicativo.</p>
                        </div>
                    `;
                    
                    // Renderiza o novo ícone de "check" que colocamos no HTML acima
                    lucide.createIcons();
                    
                } else {
                    mostrarMensagem(data.detail || "Erro ao redefinir senha", "erro");
                    button.disabled = false;
                    button.textContent = textoOriginal;
                }

            } catch (error) {
                console.error(error);
                mostrarMensagem("Servidor offline ou erro de conexão", "erro");
                button.disabled = false;
                button.textContent = textoOriginal;
            }
        });
    }
});

function mostrarMensagem(texto, tipo) {
    const mensagemExistente = document.querySelector(".alert-message");

    if (mensagemExistente) {
        mensagemExistente.remove();
    }

    const div = document.createElement("div");
    div.classList.add("alert-message");
    div.classList.add(tipo);
    div.innerText = texto;

    document.querySelector(".auth-container").appendChild(div);

    setTimeout(() => {
        if(document.body.contains(div)) {
            div.remove();
        }
    }, 5000);
}