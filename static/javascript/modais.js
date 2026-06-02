function atualizarModalProgresso(porcentagem, mensagem) {
  const text = document.getElementById("porcentagem-progresso");
  const status = document.getElementById("status-progresso");

  if (text) text.textContent = `${porcentagem}%`;
  if (status) status.textContent = mensagem;
}

function exibirModalProgresso(titulo) {
  document.getElementById("titulo-progresso").textContent = titulo;
  document.getElementById("modal-progresso-importacao").style.display = "flex";
}

function fecharModalProgresso() {
  document.getElementById("modal-progresso-importacao").style.display = "none";

  // CORREÇÃO: Garante que o texto de porcentagem volte a ficar visível na próxima importação
  const txtPorcentagem = document.getElementById("porcentagem-progresso");
  if (txtPorcentagem) {
    txtPorcentagem.style.display = "";
  }

  const btnCancelar = document.getElementById("btn-cancelar-importacao");
  if (btnCancelar) {
    btnCancelar.style.display = "";
    resetarBotaoCancelar();
  }

  const spinner = document.getElementById("loading-spinner");
  if (spinner) {
    spinner.style.display = "";
  }

  const txtTitulo = document.getElementById("titulo-progresso");
  if (txtTitulo) {
    txtTitulo.style.display = "";
  }

  const status = document.getElementById("status-progresso");
  if (status) {
    status.innerHTML = "Lendo os dados do arquivo, por favor aguarde...";
  }
}

function resetarBotaoCancelar() {
  const btnCancelar = document.getElementById("btn-cancelar-importacao");
  if (btnCancelar) {
    btnCancelar.textContent = "Cancelar Importação";
    btnCancelar.style.backgroundColor = "#ef4444";
    btnCancelar.onclick = cancelarImportacao;
  }
}

function cancelarImportacao() {
  if (xhrImportacaoAtual) {
    xhrImportacaoAtual.abort();
    xhrImportacaoAtual = null;
  }
  if (intervaloProgressoImportacao) {
    clearInterval(intervaloProgressoImportacao);
    intervaloProgressoImportacao = null;
  }
  fecharModalProgresso();

  const fClientes = document.getElementById("file-input");
  if (fClientes) fClientes.value = "";

  alert("Importação cancelada. Nenhuma alteração foi salva no banco.");
}

function abrirModalEditar(cliente) {
  document.getElementById("edit-cliente-id").value = cliente.id;
  document.getElementById("edit-nome").value = cliente.nome;
  document.getElementById("edit-email").value = cliente.email;
  document.getElementById("edit-telefone").value = cliente.telefone || "";
  document.getElementById("modal-editar-cliente").style.display = "flex";
}

function fecharModalEditar() {
  document.getElementById("modal-editar-cliente").style.display = "none";
}

async function abrirModalEvento() {
  const form = document.getElementById("form-evento");
  if (form) form.reset();

  document.getElementById("evento-id").value = "";
  document.getElementById("evento-imagem-url").value = "";
  if (document.getElementById("upload-status"))
    document.getElementById("upload-status").innerText = "";

  const btnSalvar = form ? form.querySelector('button[type="submit"]') : null;
  if (btnSalvar) {
    btnSalvar.disabled = false;
    btnSalvar.style.opacity = "1";
  }

  await carregarCategorias();
  document.getElementById("modal-evento-titulo").innerText = "Cadastrar Evento";
  document.getElementById("modal-evento").style.display = "flex";
}

function fecharModalEvento() {
  document.getElementById("modal-evento").style.display = "none";
}

function abrirModalLogout() {
  const modal = document.getElementById("modal-logout");
  if (modal) {
    modal.style.display = "flex";
    if (typeof lucide !== "undefined") {
      lucide.createIcons();
    }
  }
}

function fecharModalLogout() {
  const modal = document.getElementById("modal-logout");
  if (modal) {
    modal.style.display = "none";
  }
}

function confirmarLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_data");
  sessionStorage.clear();

  window.location.href = "login.html";
}