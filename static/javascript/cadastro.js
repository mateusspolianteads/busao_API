document.addEventListener('DOMContentLoaded', () => {
    const cadastroForm = document.querySelector('.login-form');

    // Lógica para mostrar/ocultar senha (Olhinho)
    document.addEventListener('click', (e) => {
        const toggleBtn = e.target.closest('.toggle-password-btn');
        if (toggleBtn) {
            const targetId = toggleBtn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            if (input.type === 'password') {
                input.type = 'text';
                toggleBtn.innerHTML = '<i data-lucide="eye-off"></i>';
            } else {
                input.type = 'password';
                toggleBtn.innerHTML = '<i data-lucide="eye"></i>';
            }
            // Recarrega os ícones do Lucide para o novo ícone aparecer
            lucide.createIcons();
        }
    });

    if (cadastroForm) {
        cadastroForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const senha = document.getElementById("senha").value;
            const confirmarSenha = document.getElementById("confirmar-senha").value;

            // Validação de senha
            if (senha !== confirmarSenha) {
                alert("As senhas não coincidem. Verifique e tente novamente.");
                return; // Impede que o formulário seja enviado
            }

            const dados = {
                nome: document.getElementById("nome").value,
                cpf_cnpj: document.getElementById("doc").value,
                email: document.getElementById("email").value,
                senha: senha
            };

            try {
                const response = await fetch("http://127.0.0.1:8000/usuarios/cadastrar", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(dados)
                });

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