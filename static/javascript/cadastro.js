document.addEventListener("DOMContentLoaded", () => {
  const cadastroForm = document.querySelector(".login-form");
  const campoDoc = document.getElementById("doc");

  // Máscara CPF/CNPJ
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

  // Mostrar/ocultar senha
  document.addEventListener("click", (e) => {
    const toggleBtn = e.target.closest(".toggle-password-btn");

    if (toggleBtn) {
      const targetId = toggleBtn.getAttribute("data-target");
      const input = document.getElementById(targetId);

      if (input.type === "password") {
        input.type = "text";
        toggleBtn.innerHTML = '<i data-lucide="eye-off"></i>';
      } else {
        input.type = "password";
        toggleBtn.innerHTML = '<i data-lucide="eye"></i>';
      }

      lucide.createIcons();
    }
  });

  if (cadastroForm) {
    cadastroForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const senha = document.getElementById("senha").value;
      const confirmarSenha =
        document.getElementById("confirmar-senha").value;

      // Validação senha
      if (senha !== confirmarSenha) {
        alert("As senhas não coincidem.");
        return;
      }

      const dados = {
        nome: document.getElementById("nome").value,
        cpf_cnpj: document
          .getElementById("doc")
          .value.replace(/\D/g, ""),
        email: document.getElementById("email").value,
        senha: senha,
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
          }
        );

        const result = await response.json();

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