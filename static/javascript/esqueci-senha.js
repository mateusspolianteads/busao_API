document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form")
    const emailInput = document.getElementById("email")
    const button = document.querySelector(".btn-submit")

    form.addEventListener("submit", async (e) => {

        e.preventDefault()

        const email = emailInput.value.trim()

        if (!email) {

            mostrarMensagem(
                "Digite um email válido",
                "erro"
            )

            return
        }

        const textoOriginal = button.textContent

        button.disabled = true
        button.textContent = "Enviando..."

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/usuarios/esqueci-senha",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email })
                }
            )

            const data = await response.json()

            if (response.ok) {

                mostrarMensagem(
                    "Email de recuperação enviado com sucesso!",
                    "sucesso"
                )

                form.reset()

            } else {

                mostrarMensagem(
                    data.detail || "Erro ao enviar email",
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