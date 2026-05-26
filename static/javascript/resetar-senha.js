document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form")

    const senhaInput = document.getElementById("senha")
    const confirmarSenhaInput = document.getElementById("confirmar-senha")

    const button = document.querySelector(".btn-submit")

    form.addEventListener("submit", async (e) => {

        e.preventDefault()

        const senha = senhaInput.value.trim()
        const confirmarSenha = confirmarSenhaInput.value.trim()

        const token = new URLSearchParams(
            window.location.search
        ).get("token")

        if (!token) {

            mostrarMensagem(
                "Token inválido ou expirado",
                "erro"
            )

            return
        }

        if (!senha || !confirmarSenha) {

            mostrarMensagem(
                "Preencha todos os campos",
                "erro"
            )

            return
        }

        if (senha.length < 6) {

            mostrarMensagem(
                "A senha deve ter no mínimo 6 caracteres",
                "erro"
            )

            return
        }

        if (senha !== confirmarSenha) {

            mostrarMensagem(
                "As senhas não coincidem",
                "erro"
            )

            return
        }

        const textoOriginal = button.textContent

        button.disabled = true
        button.textContent = "Redefinindo..."

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/usuarios/resetar-senha",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        token,
                        nova_senha: senha
                    })
                }
            )

            const data = await response.json()

            if (response.ok) {

                mostrarMensagem(
                    "Senha redefinida com sucesso!",
                    "sucesso"
                )

                form.reset()

                setTimeout(() => {

                    window.location.href = "login.html"

                }, 2000)

            } else {

                mostrarMensagem(
                    data.detail || "Erro ao redefinir senha",
                    "erro"
                )

            }

        } catch (error) {

            console.error(error)

            mostrarMensagem(
                "Servidor offline ou erro de conexão",
                "erro"
            )

        } finally {

            button.disabled = false
            button.textContent = textoOriginal

        }

    })

})

function mostrarMensagem(texto, tipo) {

    const mensagemExistente = document.querySelector(".alert-message")

    if (mensagemExistente) {
        mensagemExistente.remove()
    }

    const div = document.createElement("div")

    div.classList.add("alert-message")
    div.classList.add(tipo)

    div.innerText = texto

    document
        .querySelector(".auth-container")
        .appendChild(div)

    setTimeout(() => {

        div.remove()

    }, 5000)

}