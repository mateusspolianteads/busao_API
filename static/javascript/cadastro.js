document.addEventListener("DOMContentLoaded", () => {
  const cadastroForm = document.querySelector(".login-form");

  const campoDoc = document.getElementById("doc");

  campoDoc.addEventListener("input", (e) => {
    let valor = e.target.value.replace(/\D/g, "");

    if (valor.length <= 11) {
      // CPF
      valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
      valor = valor.replace(/(\d{3})(\d)/, "$1.$2");
      valor = valor.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    } else {
      // CNPJ
      valor = valor.replace(/^(\d{2})(\d)/, "$1.$2");
      valor = valor.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
      valor = valor.replace(/\.(\d{3})(\d)/, ".$1/$2");
      valor = valor.replace(/(\d{4})(\d)/, "$1-$2");
    }

    e.target.value = valor;
  });

  if (cadastroForm) {
    cadastroForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const dados = {
        nome: document.getElementById("nome").value,
        cpf_cnpj: document
          .getElementById("doc")
          .value.replace(/\D/g, ""),
        email: document.getElementById("email").value,
        senha: document.getElementById("senha").value,
      };

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/usuarios/cadastrar",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(dados),
          },
        );

        const result = await response.json();
        console.log(result);

        if (response.ok) {
          alert("Usuário cadastrado com sucesso!");
          window.location.href = "login.html";
        } else {
          alert(result.detail || "Erro ao cadastrar");
        }
      } catch (error) {
        console.error(error);
        alert("Erro de conexão com a API");
      }
    });
  }
});