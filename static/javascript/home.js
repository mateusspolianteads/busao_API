const API_URL = "http://localhost:8000";

const token = localStorage.getItem("token");

let clientes = [];
let paginaAtualClientes = 1;
const clientesPorPagina = 10;
let totalClientesBanco = 0;

let pedidos = [];
let paginaAtualPedidos = 1;
const pedidosPorPagina = 10;
let totalPedidosBanco = 0;

let categorias = [];
let idEventoAtual = null;

let xhrImportacaoAtual = null;
let intervaloProgressoImportacao = null;

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();

  const savedTheme = localStorage.getItem("theme") || "dark";
  aplicarTema(savedTheme);

  const fileInputClientes = document.getElementById("file-input");
  if (fileInputClientes) {
    fileInputClientes.addEventListener("change", (e) =>
      importarPlanilha(e, "/pedidos/importar-planilha"),
    );
  }

  const fileInputPedidos = document.getElementById("file-input-pedidos");
  if (fileInputPedidos) {
    fileInputPedidos.style.display = "none";
  }

  const formEditarCliente = document.getElementById("form-editar-cliente");
  if (formEditarCliente) {
    formEditarCliente.addEventListener("submit", async (e) => {
      e.preventDefault();
      const id = document.getElementById("edit-cliente-id").value;
      const dados = {
        nome: document.getElementById("edit-nome").value,
        email: document.getElementById("edit-email").value,
        telefone: document.getElementById("edit-telefone").value,
      };

      const btnSalvar = formEditarCliente.querySelector(
        'button[type="submit"]',
      );
      const txtOriginal = btnSalvar ? btnSalvar.innerHTML : "";
      if (btnSalvar) {
        btnSalvar.disabled = true;
        btnSalvar.innerHTML = "<span class='spinner-btn'></span> Salvando...";
      }

      try {
        const response = await fetch(`${API_URL}/clientes/atualizar/${id}`, {
          method: "PUT",
          headers: getAuthHeaders(),
          body: JSON.stringify(dados),
        });

        if (!response.ok) throw new Error();
        alert("Cliente updated com sucesso!");
        fecharModalEditar();
        carregarClientes();
      } catch (error) {
        console.error("Erro:", error);
        alert("Erro ao atualizar cliente.");
      } finally {
        if (btnSalvar) {
          btnSalvar.disabled = false;
          btnSalvar.innerHTML = txtOriginal;
        }
      }
    });
  }

  const formEvento = document.getElementById("form-evento");
  if (formEvento) {
    formEvento.addEventListener("submit", async (e) => {
      e.preventDefault();
      const id = document.getElementById("evento-id").value;
      const data_input = document.getElementById("evento-data").value;

      const dadosEvento = {
        nome: document.getElementById("evento-nome").value,
        categoria_id: parseInt(
          document.getElementById("evento-categoria").value,
        ),
        data_evento: new Date(data_input).toISOString(),
        local: document.getElementById("evento-local").value,
        valor_passagem: parseFloat(
          document.getElementById("evento-valor").value,
        ),
        imagem: document.getElementById("evento-imagem-url").value || null,
      };

      const btnSalvar = formEvento.querySelector('button[type="submit"]');
      const txtOriginal = btnSalvar ? btnSalvar.innerHTML : "";
      if (btnSalvar) {
        btnSalvar.disabled = true;
        btnSalvar.innerHTML = "<span class='spinner-btn'></span> Salvando...";
      }

      try {
        const url = id
          ? `${API_URL}/eventos/atualizar/${id}`
          : `${API_URL}/eventos/cadastrar`;
        const method = id ? "PUT" : "POST";

        const response = await fetch(url, {
          method: method,
          headers: getAuthHeaders(),
          body: JSON.stringify(dadosEvento),
        });

        if (!response.ok) throw new Error();
        alert(id ? "Evento atualizado!" : "Evento cadastrado!");
        fecharModalEvento();
        carregarEventos();
      } catch (error) {
        console.error("Erro ao salvar evento:", error);
        alert("Erro ao salvar o evento.");
      } finally {
        if (btnSalvar) {
          btnSalvar.disabled = false;
          btnSalvar.innerHTML = txtOriginal;
        }
      }
    });
  }

  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  if (prevBtn)
    prevBtn.addEventListener("click", () => {
      if (paginaAtualClientes > 1) {
        paginaAtualClientes--;
        carregarClientes();
      }
    });

  if (nextBtn)
    nextBtn.addEventListener("click", () => {
      const totalPaginas = Math.ceil(totalClientesBanco / clientesPorPagina);

      if (paginaAtualClientes < totalPaginas) {
        paginaAtualClientes++;
        carregarClientes();
      }
    });

  const prevBtnPed = document.getElementById("prev-page-pedidos");
  const nextBtnPed = document.getElementById("next-page-pedidos");

  if (prevBtnPed)
    prevBtnPed.addEventListener("click", () => {
      if (paginaAtualPedidos > 1) {
        paginaAtualPedidos--;
        carregarPedidos();
      }
    });
  if (nextBtnPed)
    nextBtnPed.addEventListener("click", () => {
      const totalPaginas = Math.ceil(totalPedidosBanco / pedidosPorPagina);

      if (paginaAtualPedidos < totalPaginas) {
        paginaAtualPedidos++;
        carregarPedidos();
      }
    });

  const selectFiltroPedidos = document.getElementById("filtro-pedidos-evento");
  if (selectFiltroPedidos) {
    selectFiltroPedidos.addEventListener("change", (e) => {
      const idSelecionado = parseInt(e.target.value);
      if (idSelecionado) carregarPedidos(idSelecionado);
    });
  }

  const themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const novoTema = document.body.classList.contains("light-mode")
        ? "dark"
        : "light";
      localStorage.setItem("theme", novoTema);
      aplicarTema(novoTema);
    });
  }

  carregarEventos();
});

async function importarPlanilha(
  event,
  endpoint,
  tituloModal = "Processando Planilha",
) {
  const arquivo = event.target.files[0];
  if (!arquivo) return;

  if (!idEventoAtual) {
    alert("Selecione um evento antes de importar!");
    event.target.value = "";
    return;
  }

  exibirModalProgresso(tituloModal);
  atualizarModalProgresso(0, "Iniciando leitura e upload do arquivo...");

  let porcentagemSimulada = 0;

  intervaloProgressoImportacao = setInterval(() => {
    if (porcentagemSimulada < 95) {
      porcentagemSimulada += 1;
      atualizarModalProgresso(
        porcentagemSimulada,
        `Processando dados no banco de dados... (${porcentagemSimulada}%)`,
      );
    }
  }, 1000);

  const xhr = new XMLHttpRequest();
  xhrImportacaoAtual = xhr;

  const formData = new FormData();
  formData.append("file", arquivo);
  formData.append("evento_id", idEventoAtual);

  xhr.open("POST", `${API_URL}${endpoint}`);

  xhr.onload = () => {
    clearInterval(intervaloProgressoImportacao);
    xhrImportacaoAtual = null;

    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        const resultado = JSON.parse(xhr.responseText);

        const txtPorcentagem = document.getElementById("porcentagem-progresso");
        const btnCancelar = document.getElementById("btn-cancelar-importacao");
        const spinner = document.getElementById("loading-spinner");
        const txtTitulo = document.getElementById("titulo-progresso");

        if (txtPorcentagem) txtPorcentagem.style.display = "none";
        if (btnCancelar) btnCancelar.style.display = "none";
        if (spinner) spinner.style.display = "none";
        if (txtTitulo) txtTitulo.style.display = "none";

        const statusProgresso = document.getElementById("status-progresso");
        if (statusProgresso) {
          statusProgresso.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 25px 0;">
              <i data-lucide="check-circle" style="width: 64px; height: 64px; color: #10b981;"></i>
              <span style="font-size: 1.4rem; font-weight: 700; color: #10b981;">Importação Concluída!</span>
              <span style="font-size: 0.95rem; opacity: 0.8; text-align: center; margin-top: 4px; color: #666;">
                ${resultado.total_clientes_novos} novos clientes e ${resultado.total_pedidos_criados} pedidos integrados.
              </span>
            </div>
          `;
          lucide.createIcons();
        }

        carregarClientes(idEventoAtual);
        carregarPedidos(idEventoAtual);

        setTimeout(() => {
          fecharModalProgresso();
        }, 2500);
      } catch (e) {
        console.error("Erro ao ler JSON de resposta:", e);
        fecharModalProgresso();
        alert("Erro ao interpretar resposta do servidor.");
      }
    } else {
      fecharModalProgresso();
      alert("Erro no servidor ao processar arquivo.");
    }
  };

  xhr.onerror = () => {
    clearInterval(intervaloProgressoImportacao);
    xhrImportacaoAtual = null;
    fecharModalProgresso();
    alert("Erro de rede ao enviar arquivo.");
  };

  xhr.send(formData);
  event.target.value = "";
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

function resetarBotaoCancelar() {
  const btnCancelar = document.getElementById("btn-cancelar-importacao");
  if (btnCancelar) {
    btnCancelar.textContent = "Cancelar Importação";
    btnCancelar.style.backgroundColor = "#ef4444";
    btnCancelar.onclick = cancelarImportacao;
  }
}

function exibirModalProgresso(titulo) {
  document.getElementById("titulo-progresso").textContent = titulo;
  document.getElementById("modal-progresso-importacao").style.display = "flex";
}

function atualizarModalProgresso(porcentagem, mensagem) {
  const text = document.getElementById("porcentagem-progresso");
  const status = document.getElementById("status-progresso");

  if (text) text.textContent = `${porcentagem}%`;
  if (status) status.textContent = mensagem;
}

function fecharModalProgresso() {
  document.getElementById("modal-progresso-importacao").style.display = "none";

  const text = document.getElementById("porcentagem-progresso");
  if (text) {
    text.textContent = "0%";
    text.style.display = "";
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

// --- FUNÇÕES DE RENDERIZAÇÃO DAS TABELAS ---

async function carregarClientes(eventoId = null) {
  if (eventoId !== null) {
    idEventoAtual = eventoId;
    paginaAtualClientes = 1;
  }

  const tabela = document.getElementById("tabela-clientes-body");
  if (tabela) {
    tabela.innerHTML =
      "<tr><td colspan='7' style='text-align:center; padding: 30px; opacity: 0.7;'><span class='spinner-inline'></span> Buscando participantes...</td></tr>";
  }

  try {
    const url = idEventoAtual
      ? `${API_URL}/clientes/evento/${idEventoAtual}?pagina=${paginaAtualClientes}&limite=10`
      : `${API_URL}/clientes/listar`;

    const response = await fetch(url,{
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok)
      throw new Error(`Erro na requisição: Status ${response.status}`);

    const textoResposta = await response.text();
    let dadosBrutos = textoResposta.trim() ? JSON.parse(textoResposta) : [];

    if (
      dadosBrutos &&
      typeof dadosBrutos === "object" &&
      !Array.isArray(dadosBrutos)
    ) {
      totalClientesBanco = dadosBrutos.total || 0;
      clientes = dadosBrutos.clientes || [];
    } else {
      clientes = Array.isArray(dadosBrutos) ? dadosBrutos : [];
      totalClientesBanco = clientes.length;
    }

    clientes.sort((a, b) => {
      const nomeA = a && a.nome ? String(a.nome) : "";
      const nomeB = b && b.nome ? String(b.nome) : "";
      return nomeA.localeCompare(nomeB, "pt-BR", { sensitivity: "base" });
    });

    mostrarPaginaClientes();
  } catch (error) {
    console.error("Erro no processamento de clientes:", error);
    if (tabela) {
      tabela.innerHTML = `<tr><td colspan='7' style='text-align:center; color: #ff4d4d; padding: 20px;'><strong>Erro ao processar dados do servidor.</strong></td></tr>`;
    }
  }
}

function mostrarPaginaClientes() {
  const tabela = document.getElementById("tabela-clientes-body");
  if (!tabela) return;
  tabela.innerHTML = "";

  if (clientes.length === 0) {
    tabela.innerHTML =
      "<tr><td colspan='7' style='text-align:center; opacity: 0.6; padding: 20px;'>Nenhum participante encontrado para este evento.</td></tr>";
    if (document.getElementById("current-page"))
      document.getElementById("current-page").textContent = 1;
    if (document.getElementById("total-pages"))
      document.getElementById("total-pages").textContent = 1;
    if (document.getElementById("prev-page"))
      document.getElementById("prev-page").disabled = true;
    if (document.getElementById("next-page"))
      document.getElementById("next-page").disabled = true;
    return;
  }

  clientes.forEach((cliente) => {
    const dataNasc = cliente.data_nascimento
      ? new Date(cliente.data_nascimento).toLocaleDateString("pt-BR", {
          timeZone: "UTC",
        })
      : "---";
    const clienteJson = JSON.stringify(cliente).replace(/"/g, "&quot;");

    tabela.innerHTML += `
        <tr>
          <td><strong>${cliente.nome}</strong></td>
          <td>${cliente.cpf || "---"}</td>
          <td>${dataNasc}</td>
          <td>${cliente.email}</td>
          <td>${cliente.telefone || "---"}</td>
          <td><span class="status paid">Ativo</span></td>
          <td style="text-align: center;">
            <button class="btn-edit-table" onclick="abrirModalEditar(${clienteJson})">
              <i data-lucide="pencil" style="width: 16px;"></i>
            </button>
          </td>
        </tr>
      `;
  });

  const totalGeralDoBanco = totalClientesBanco || clientes.length;
  const totalPaginas = Math.ceil(totalGeralDoBanco / clientesPorPagina) || 1;

  if (document.getElementById("current-page"))
    document.getElementById("current-page").textContent = paginaAtualClientes;
  if (document.getElementById("total-pages"))
    document.getElementById("total-pages").textContent = totalPaginas;
  if (document.getElementById("prev-page"))
    document.getElementById("prev-page").disabled = paginaAtualClientes === 1;
  if (document.getElementById("next-page"))
    document.getElementById("next-page").disabled =
      paginaAtualClientes === totalPaginas;

  lucide.createIcons();
}

function proximaPaginaClientes() {
  const totalPaginas = Math.ceil(totalClientesBanco / clientesPorPagina) || 1;
  if (paginaAtualClientes < totalPaginas) {
    paginaAtualClientes++;
    carregarClientes();
  }
}

function paginaAnteriorClientes() {
  if (paginaAtualClientes > 1) {
    paginaAtualClientes--;
    carregarClientes();
  }
}

async function verClientesDoEvento(idEvento, nomeEvento, botao) {
  const titulo = document.getElementById("titulo-clientes-evento");
  const subtitulo = document.getElementById("subtitulo-clientes-evento");

  if (titulo) titulo.innerText = `Clientes: ${nomeEvento}`;
  if (subtitulo)
    subtitulo.innerText = `Gerenciando participantes do evento #${idEvento}`;

  let txtOriginal = "";
  if (botao) {
    botao.disabled = true;
    txtOriginal = botao.innerHTML;
    botao.innerHTML = "<span class='spinner-btn'></span> Buscando...";
  }

  try {
    await carregarClientes(idEvento);
    trocarPagina("clientes");
  } catch (error) {
    console.error("Erro na transição de página dos participantes:", error);
  } finally {
    if (botao) {
      botao.disabled = false;
      botao.innerHTML = txtOriginal;
      lucide.createIcons();
    }
  }
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

async function carregarCategorias() {
  try {
    const response = await fetch(`${API_URL}/categorias/listar`,{
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error();
    categorias = await response.json();

    const selectCategoria = document.getElementById("evento-categoria");
    if (!selectCategoria) return;

    selectCategoria.innerHTML = `<option value="" disabled selected hidden>Selecione uma categoria</option>`;
    categorias.forEach((cat) => {
      selectCategoria.innerHTML += `<option value="${cat.id}">${cat.nome}</option>`;
    });
  } catch (error) {
    console.error("Erro ao sincronizar categorias com o backend:", error);
  }
}

async function carregarEventos() {
  const gridContainer = document.getElementById("tabela-eventos-body");
  if (gridContainer) {
    gridContainer.innerHTML =
      "<div style='grid-column: 1/-1; text-align: center; padding: 50px; opacity: 0.7;'><span class='spinner-inline'></span> Carregando eventos ativos...</div>";
  }

  try {
    if (categorias.length === 0) await carregarCategorias();

    const response = await fetch(`${API_URL}/eventos/listar`,{
      headers: getAuthHeaders(),
    });
    if (!response.ok) return;
    const eventos = await response.json();

    if (!gridContainer) return;
    gridContainer.innerHTML = "";

    if (eventos.length === 0) {
      gridContainer.innerHTML =
        "<div style='grid-column: 1/-1; text-align: center; padding: 50px; opacity: 0.5;'>Nenhum evento localizado.</div>";
      return;
    }

    eventos.forEach((evento) => {
      const dataFormatada =
        new Date(evento.data_evento).toLocaleDateString("pt-BR") +
        " " +
        new Date(evento.data_evento).toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        });
      const tagImagem = evento.imagem
        ? `<img src="${evento.imagem}" alt="${evento.nome}">`
        : "";
      const classeNoImage = evento.imagem ? "" : "no-image";
      const objCategoria = categorias.find((c) => c.id === evento.categoria_id);
      const nomeCategoria = objCategoria
        ? objCategoria.nome
        : `ID: ${evento.categoria_id}`;

      gridContainer.innerHTML += `
        <div class="event-card">
          <div class="event-card-banner ${classeNoImage}">
            ${tagImagem}
            <span class="event-card-category">${nomeCategoria}</span>
            <div class="event-card-actions">
              <button class="btn-edit-table" onclick="prepararEdicaoEvento(${evento.id})" title="Editar"><i data-lucide="pencil" style="width: 16px;"></i></button>
              <button class="btn-edit-table btn-delete-table" onclick="deletarEvento(${evento.id})" title="Excluir"><i data-lucide="trash-2" style="width: 16px;"></i></button>
            </div>
          </div>
          <div class="event-card-body">
            <h3 class="event-card-title">${evento.nome}</h3>
            <div class="event-card-info-item"><i data-lucide="calendar"></i><span>${dataFormatada}</span></div>
            <div class="event-card-info-item"><i data-lucide="map-pin"></i><span>${evento.local}</span></div>
            <div class="event-card-footer" style="display: flex; flex-direction: column; gap: 12px; align-items: stretch;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <div class="event-card-price-label">Passagem</div>
                  <div class="event-card-price-value">R$ ${evento.valor_passagem.toFixed(2).replace(".", ",")}</div>
                </div>
              </div>
              <button class="btn-import" onclick="verClientesDoEvento(${evento.id}, '${evento.nome.replace(/'/g, "\\'")}', this)" style="width: 100%; justify-content: center; margin: 0; padding: 10px;">
                <i data-lucide="users" style="width: 16px; height: 16px;"></i>Ver Participantes
              </button>
            </div>
          </div>
        </div>
      `;
    });
    lucide.createIcons();
  } catch (error) {
    console.error("Erro ao carregar eventos:", error);
  }

  await popularFiltroEventosPedidos(idEventoAtual ?? "");
}

async function fazerUploadImagem(input) {
  const file = input.files[0];
  if (!file) return;

  const formEvento = document.getElementById("form-evento");
  const btnSalvar = formEvento
    ? formEvento.querySelector('button[type="submit"]')
    : null;
  const statusLabel = document.getElementById("upload-status");

  if (statusLabel) {
    statusLabel.style.color = "var(--text-dim)";
    statusLabel.innerText = "Enviando para o Supabase...";
  }
  if (btnSalvar) {
    btnSalvar.disabled = true;
    btnSalvar.style.opacity = "0.5";
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_URL}/upload/`, {
      method: "POST",
      body: formData,
      headers: {Authorization: `Bearer ${localStorage.getItem("token")}`,},
    });
    const resultado = await response.json();

    if (resultado.url) {
      document.getElementById("evento-imagem-url").value = resultado.url;
      if (statusLabel) {
        statusLabel.style.color = "#00ff88";
        statusLabel.innerText = "Upload concluído!";
      }
    } else {
      if (statusLabel) {
        statusLabel.style.color = "#ff4d4d";
        statusLabel.innerText = "Falha no envio.";
      }
    }
  } catch (error) {
    console.error("Erro no upload:", error);
    if (statusLabel) {
      statusLabel.style.color = "#ff4d4d";
      statusLabel.innerText = "Erro ao carregar arquivo.";
    }
  } finally {
    if (btnSalvar) {
      btnSalvar.disabled = false;
      btnSalvar.style.opacity = "1";
    }
  }
}

async function prepararEdicaoEvento(id) {
  try {
    await carregarCategorias();
    const response = await fetch(`${API_URL}/eventos/consultar/${id}`,{
      headers: getAuthHeaders(),
    });
    if (!response.ok) return;
    const evento = await response.json();

    document.getElementById("modal-evento-titulo").innerText = "Editar Evento";
    document.getElementById("evento-id").value = evento.id;
    document.getElementById("evento-nome").value = evento.nome;
    document.getElementById("evento-categoria").value = evento.categoria_id;
    if (evento.data_evento)
      document.getElementById("evento-data").value =
        evento.data_evento.substring(0, 16);
    document.getElementById("evento-local").value = evento.local;
    document.getElementById("evento-valor").value = evento.valor_passagem;
    document.getElementById("evento-imagem-url").value = evento.imagem || "";

    const formEvento = document.getElementById("form-evento");
    const btnSalvar = formEvento
      ? formEvento.querySelector('button[type="submit"]')
      : null;
    if (btnSalvar) {
      btnSalvar.disabled = false;
      btnSalvar.style.opacity = "1";
    }
    document.getElementById("modal-evento").style.display = "flex";
  } catch (error) {
    console.error(error);
  }
}

async function deletarEvento(id) {
  if (!confirm("Remover este evento de forma permanente?")) return;
  try {
    const response = await fetch(`${API_URL}/eventos/deletar/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (response.ok) carregarEventos();
  } catch (error) {
    console.error(error);
  }
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

async function popularFiltroEventosPedidos(idSelecionado) {
  const selectFiltro = document.getElementById("filtro-pedidos-evento");
  if (!selectFiltro) return;

  try {
    const response = await fetch(`${API_URL}/eventos/listar`,{
      headers: getAuthHeaders(),
    });
    if (!response.ok) return;
    const eventos = await response.json();

    selectFiltro.innerHTML = "";
    if (eventos.length === 0) {
      selectFiltro.innerHTML = `<option value="">Nenhum evento cadastrado</option>`;
      return;
    }

    eventos.forEach((ev) => {
      selectFiltro.innerHTML += `<option value="${ev.id}">${ev.nome}</option>`;
    });
    selectFiltro.value = idSelecionado;
  } catch (error) {
    console.error("Erro ao popular filtro de eventos em pedidos:", error);
  }
}

async function carregarPedidos(eventoId = null) {
  if (eventoId !== null && eventoId !== idEventoAtual) {
    idEventoAtual = eventoId;
    paginaAtualPedidos = 1;
  }

  exibirMensagemTabelaPedidos(
    "<span class='spinner-inline'></span> Buscando pedidos atualizados...",
  );

  if (!idEventoAtual) {
    try {
      const resEventos = await fetch(`${API_URL}/eventos/listar`,{
        headers: getAuthHeaders(),
      })
      if (resEventos.ok) {
        const eventos = await resEventos.json();
        if (eventos.length > 0) {
          idEventoAtual = eventos[0].id;
        } else {
          exibirMensagemTabelaPedidos(
            "Nenhum evento cadastrado para carregar pedidos.",
          );
          return;
        }
      }
    } catch (error) {
      console.error("Erro ao buscar evento inicial para pedidos:", error);
      exibirMensagemTabelaPedidos("Erro ao inicializar filtro de eventos.");
      return;
    }
  }

  await popularFiltroEventosPedidos(idEventoAtual);

  try {
    const response = await fetch(
      `${API_URL}/pedidos/evento/${idEventoAtual}?pagina=${paginaAtualPedidos}&limite=${pedidosPorPagina}`,{
        headers: getAuthHeaders(),
      }
    );

    if (response.status === 404) {
      pedidos = [];
      paginaAtualPedidos = 1;
      mostrarPaginaPedidos();
      return;
    }

    if (!response.ok) throw new Error();
    const dados = await response.json();

    pedidos = dados.pedidos || [];
    totalPedidosBanco = dados.total || 0;
    mostrarPaginaPedidos();
  } catch (error) {
    console.error("Erro ao buscar pedidos no servidor:", error);
    exibirMensagemTabelaPedidos(
      "Erro crítico ao se comunicar com o servidor.",
      "#ff4d4d",
    );
  }
}

function exibirMensagemTabelaPedidos(mensagem, cor = "var(--text-dim)") {
  const table = document.getElementById("tabela-pedidos-body");
  if (table) {
    table.innerHTML = `<tr><td colspan='12' style='text-align:center; padding: 30px; color: ${cor};'>${mensagem}</td></tr>`;
  }
}

function mostrarPaginaPedidos() {
  const table = document.getElementById("tabela-pedidos-body");
  if (!table) return;
  table.innerHTML = "";

  if (pedidos.length === 0) {
    table.innerHTML =
      "<tr><td colspan='12' style='text-align:center; opacity: 0.6; padding: 20px;'>Nenhum pedido encontrado para este evento.</td></tr>";
    if (document.getElementById("current-page-pedidos"))
      document.getElementById("current-page-pedidos").textContent = 1;
    if (document.getElementById("total-pages-pedidos"))
      document.getElementById("total-pages-pedidos").textContent = 1;
    if (document.getElementById("prev-page-pedidos"))
      document.getElementById("prev-page-pedidos").disabled = true;
    if (document.getElementById("next-page-pedidos"))
      document.getElementById("next-page-pedidos").disabled = true;
    return;
  }

  const totalPaginas = Math.ceil(totalPedidosBanco / pedidosPorPagina) || 1;
  if (paginaAtualPedidos > totalPaginas) paginaAtualPedidos = totalPaginas;
  if (paginaAtualPedidos < 1) paginaAtualPedidos = 1;

  pedidos.forEach((pedido) => {
    const dataVenda = pedido.data_venda
      ? new Date(pedido.data_venda).toLocaleDateString("pt-BR")
      : "---";
    const valorLote = pedido.valor_lote
      ? parseFloat(pedido.valor_lote).toLocaleString("pt-BR", {
          style: "currency",
          currency: "BRL",
        })
      : "R$ 0,00";
    const transferido = pedido.transferido ? "Sim" : "Não";
    const aprovado = pedido.aprovado ? "Sim" : "Não";

    table.innerHTML += `
        <tr>
          <td>#${pedido.id}</td>
          <td><strong>${pedido.cliente_nome || "---"}</strong></td>
          <td>${pedido.evento_nome || "---"}</td>
          <td>${dataVenda}</td>
          <td>${pedido.status_pedido || "---"}</td>
          <td>${pedido.status_ingresso || "---"}</td>
          <td>${pedido.lote || "---"}</td>
          <td>${valorLote}</td>
          <td>${pedido.canal_venda || "---"}</td>
          <td>${pedido.metodo_pagamento || "---"}</td>
          <td>${transferido}</td>
          <td>${aprovado}</td>
        </tr>
      `;
  });

  const spanAtual = document.getElementById("current-page-pedidos");
  const spanTotal = document.getElementById("total-pages-pedidos");

  if (spanAtual) spanAtual.textContent = paginaAtualPedidos;
  if (spanTotal) spanTotal.textContent = totalPaginas;

  const prevBtnPed = document.getElementById("prev-page-pedidos");
  const nextBtnPed = document.getElementById("next-page-pedidos");

  if (prevBtnPed) prevBtnPed.disabled = paginaAtualPedidos === 1;
  if (nextBtnPed) nextBtnPed.disabled = paginaAtualPedidos >= totalPaginas;

  lucide.createIcons();
}

function trocarPagina(id) {
  document
    .querySelectorAll(".tab-content")
    .forEach((c) => c.classList.remove("active"));
  document
    .querySelectorAll(".nav-link")
    .forEach((l) => l.classList.remove("active"));

  const tab = document.getElementById("content-" + id);
  const linkId = id === "clientes" ? "link-eventos" : "link-" + id;
  const link = document.getElementById(linkId);

  if (tab) tab.classList.add("active");
  if (link) link.classList.add("active");

  if (id === "eventos") {
    idEventoAtual = null;
    carregarEventos();
  }
  if (id === "pedidos"){
    if (!idEventoAtual){
      exibirMensagemTabelaPedidos("Selecione um evento para ver os pedidos.")
      return
    }

  } carregarPedidos(idEventoAtual);
}

function aplicarTema(theme) {
  const body = document.body;
  const logo = document.getElementById("main-logo");
  const icon = document.getElementById("theme-icon");

  if (theme === "light") {
    body.classList.add("light-mode");
    if (logo) logo.src = "../static/img/logo_preta.png";
    if (icon) icon.setAttribute("data-lucide", "sun");
  } else {
    body.classList.remove("light-mode");
    if (logo) logo.src = "../static/img/logo_branca.png";
    if (icon) icon.setAttribute("data-lucide", "moon");
  }

  lucide.createIcons();
}

function abrirModalLogout() {
  const modal = document.getElementById('modal-logout');
  if (modal) {
    modal.style.display = 'flex';
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }
}

function fecharModalLogout() {
  const modal = document.getElementById('modal-logout');
  if (modal) {
    modal.style.display = 'none';
  }
}

function confirmarLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_data");
  sessionStorage.clear();

  window.location.href = "login.html";
}

function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}