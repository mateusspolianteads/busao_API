document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.querySelector(".login-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const dados = {
        email: document.getElementById("email").value,
        senha: document.getElementById("senha").value,
      };

      try {
        const response = await fetch(`${window.API_URL}/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(dados),
        });

        const resultado = await response.json();

        if (response.ok) {
          console.log("LOGIN RESPONSE:", resultado);

          const token =
            resultado.access_token ||
            resultado.token ||
            resultado.access ||
            resultado.data?.access_token;

          const refresh =
            resultado.refresh_token ||
            resultado.refresh ||
            resultado.data?.refresh_token;

          if (!token) {
            alert("Erro: backend não retornou token");
            return;
          }

          localStorage.setItem("token", token);

          if (refresh) {
            localStorage.setItem("refresh_token", refresh);
          }

          alert("Login realizado com sucesso!");
          window.location.href = "home.html";
        } else {
          if (Array.isArray(resultado.detail)) {
            let mensagem = resultado.detail[0].msg;

            if (mensagem.includes("valid email address")) {
              mensagem = "Email inválido.";
            }

            alert("Atenção: " + mensagem);
          } else {
            alert(
              "Atenção: " + (resultado.detail || "Erro ao processar dados"),
            );
          }
        }
      } catch (error) {
        console.error("Erro na requisição:", error);
        alert("Servidor Offline. Verifique se o Python está rodando.");
      }
    });
  }
});
