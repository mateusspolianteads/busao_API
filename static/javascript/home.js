const API_URL = "http://localhost:8000";

let clientes = [];
let paginaAtualClientes = 1;
const clientesPorPagina = 10;

let pedidos = [];
let paginaAtualPedidos = 1;
const pedidosPorPagina = 10;

let categorias = [];
let idEventoAtual = null;

// --- VARIÁVEIS GLOBAIS PARA CONTROLE DE CANCELAMENTO ---
let xhrImportacaoAtual = null;
let intervaloProgressoImportacao = null;

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();

  const savedTheme = localStorage.getItem("theme") || "dark";
  aplicarTema(savedTheme);

  const fileInputClientes = document.getElementById("file-input");
  if (fileInputClientes) {
    fileInputClientes.addEventListener(
      "change",
      (e) => importarPlanilha(e, "/clientes/importar-planilha"),
    );
  }

  const fileInputPedidos = document.getElementById("file-input-pedidos");
  if (fileInputPedidos) {
    fileInputPedidos.addEventListener("change", (e) =>
      importarPlanilha(e, "/pedidos/importar-planilha"),
    );
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

      try {
        const response = await fetch(`${API_URL}/clientes/atualizar/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dados),
        });

        if (!response.ok) throw new Error();
        alert("Cliente atualizado com sucesso!");
        fecharModalEditar();
        carregarClientes();
      } catch (error) {
        console.error("Erro:", error);
        alert("Erro ao atualizar cliente.");
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

      try {
        const url = id
          ? `${API_URL}/eventos/atualizar/${id}`
          : `${API_URL}/eventos/cadastrar`;
        const method = id ? "PUT" : "POST";

        const response = await fetch(url, {
          method: method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dadosEvento),
        });

        if (!response.ok) throw new Error();
        alert(id ? "Evento atualizado!" : "Evento cadastrado!");
        fecharModalEvento();
        carregarEventos();
      } catch (error) {
        console.error("Erro ao salvar evento:", error);
        alert("Erro ao salvar o evento.");
      }
    });
  }

  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  if (prevBtn)
    prevBtn.addEventListener("click", () => {
      if (paginaAtualClientes > 1) {
        paginaAtualClientes--;
        mostrarPaginaClientes();
      }
    });
  if (nextBtn)
    nextBtn.addEventListener("click", () => {
      if (
        paginaAtualClientes < Math.ceil(clientes.length / clientesPorPagina)
      ) {
        paginaAtualClientes++;
        mostrarPaginaClientes();
      }
    });

  const prevBtnPed = document.getElementById("prev-page-pedidos");
  const nextBtnPed = document.getElementById("next-page-pedidos");
  if (prevBtnPed)
    prevBtnPed.addEventListener("click", () => {
      if (paginaAtualPedidos > 1) {
        paginaAtualPedidos--;
        mostrarPaginaPedidos();
      }
    });
  if (nextBtnPed)
    nextBtnPed.addEventListener("click", () => {
      if (paginaAtualPedidos < Math.ceil(pedidos.length / pedidosPorPagina)) {
        paginaAtualPedidos++;
        mostrarPaginaPedidos();
      }
    });

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
  if (!arquivo) {
    console.warn("[Importação] Nenhum arquivo foi selecionado.");
    return;
  }

  if (!idEventoAtual) {
    console.error(
      "[Importação] Erro: Tentativa de importação sem idEventoAtual definido.",
    );
    alert("Selecione um evento antes de importar!");
    event.target.value = "";
    return;
  }

  console.log(
    `[Importação] Iniciando processo. Arquivo: ${arquivo.name}, Tamanho: ${arquivo.size} bytes, Evento ID: ${idEventoAtual}`,
  );

  exibirModalProgresso(tituloModal);
  atualizarModalProgresso(0, "Iniciando upload...");

  let porcentagemSimulada = 0;
  console.log(
    "[Importação] Iniciando temporizador de progresso visual (1% por segundo).",
  );

  intervaloProgressoImportacao = setInterval(() => {
    if (porcentagemSimulada < 95) {
      porcentagemSimulada += 1;
      atualizarModalProgresso(
        porcentagemSimulada,
        `Processando planilha... ${porcentagemSimulada}%`,
      );
      console.log(`[Importação - Progresso Ativo] ${porcentagemSimulada}%`);
    }
  }, 1000);

  const xhr = new XMLHttpRequest();
  xhrImportacaoAtual = xhr; // Guarda a instância ativa para permitir o .abort()

  const formData = new FormData();
  formData.append("file", arquivo);
  formData.append("evento_id", idEventoAtual);

  const urlFinal = `${API_URL}${endpoint}`;
  console.log(`[Importação] Enviando requisição POST para: ${urlFinal}`);

  xhr.open("POST", urlFinal);

  xhr.onload = () => {
    clearInterval(intervaloProgressoImportacao);
    xhrImportacaoAtual = null;
    console.log(`[Importação] Servidor respondeu com Status: ${xhr.status}`);

    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        const resultado = JSON.parse(xhr.responseText);
        console.log(
          "[Importação] Resposta do servidor decodificada com sucesso:",
          resultado,
        );

        console.log(
          "[Importação] Forçando progresso visual para 100% (Concluído).",
        );
        atualizarModalProgresso(100, "Processamento concluído!");

        setTimeout(() => {
          fecharModalProgresso();

          alert(
            `Sucesso! ${resultado.total_clientes_novos} novos clientes e ${resultado.total_pedidos_criados} pedidos.`,
          );

          console.log(
            "[Importação] Atualizando tabelas de clientes e pedidos na interface...",
          );
          carregarClientes(idEventoAtual);
          carregarPedidos();
        }, 500);
      } catch (e) {
        console.error("[Importação] Erro ao tentar ler o JSON de resposta:", e);
        fecharModalProgresso();
        alert("Erro ao interpretar resposta do servidor.");
      }
    } else {
      console.error(
        `[Importação] O servidor retornou um erro estrutural. Status: ${xhr.status}, Resposta: ${xhr.responseText}`,
      );
      fecharModalProgresso();
      alert("Erro no servidor ao processar arquivo.");
    }
  };

  xhr.onerror = () => {
    clearInterval(intervaloProgressoImportacao);
    xhrImportacaoAtual = null;
    console.error(
      "[Importação] Falha crítica de rede (XHR onerror disparado).",
    );
    fecharModalProgresso();
    alert("Erro de rede ao enviar arquivo.");
  };

  xhr.onabort = () => {
    console.log("[Importação] Requisição cancelada com sucesso no cliente.");
  };

  xhr.send(formData);
  event.target.value = "";
}

// --- FUNÇÃO PARA CANCELAR A IMPORTAÇÃO ---
function cancelarImportacao() {
  if (xhrImportacaoAtual) {
    console.log("[Importação] Cancelamento solicitado pelo usuário. Abortando XHR...");
    xhrImportacaoAtual.abort(); // Interrompe a conexão HTTP na hora
    xhrImportacaoAtual = null;
  }

  if (intervaloProgressoImportacao) {
    clearInterval(intervaloProgressoImportacao);
    intervaloProgressoImportacao = null;
  }

  fecharModalProgresso();

  // Limpa o valor dos inputs de ficheiro para permitir selecionar o mesmo arquivo novamente
  const fClientes = document.getElementById("file-input");
  const fPedidos = document.getElementById("file-input-pedidos");
  if (fClientes) fClientes.value = "";
  if (fPedidos) fPedidos.value = "";

  alert("Importação cancelada. Nenhuma alteração foi salva no banco.");
}

function exibirModalProgresso(titulo) {
  document.getElementById("titulo-progresso").textContent = titulo;
  document.getElementById("modal-progresso-importacao").style.display = "flex";
}

function atualizarModalProgresso(porcentagem, mensagem) {
  const text = document.getElementById("porcentagem-progresso");
  const status = document.getElementById("status-progresso");

  if (text) text.textContent = `${porcentagem}%`;
  if (status) status.textContent = mensagem; // Corrigido aqui de 'mensaje' para 'mensagem'
}

function fecharModalProgresso() {
  document.getElementById("modal-progresso-importacao").style.display = "none";

  const text = document.getElementById("porcentagem-progresso");
  if (text) text.textContent = "0%";
}

async function carregarClientes(eventoId = null) {
  if (eventoId !== null) {
    idEventoAtual = eventoId;
  }

  try {
    const url = idEventoAtual
      ? `${API_URL}/clientes/evento/${idEventoAtual}`
      : `${API_URL}/clientes/listar`;

    const response = await fetch(url);

    if (!response.ok) throw new Error();

    clientes = await response.json();

    clientes.sort((a, b) =>
      a.nome.localeCompare(b.nome, "pt-BR", { sensitivity: "base" }),
    );
    paginaAtualClientes = 1;
    mostrarPaginaClientes();
  } catch (error) {
    console.error("Erro ao carregar clientes:", error);
    const tabela = document.getElementById("tabela-clientes-body");
    if (tabela)
      tabela.innerHTML =
        "<tr><td colspan='7' style='text-align:center; color: #ff4d4d;'>Erro crítico ao se comunicar com o servidor.</td></tr>";
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

  const inicio = (paginaAtualClientes - 1) * clientesPorPagina;
  const fim = inicio + clientesPorPagina;
  const clientesPagina = clientes.slice(inicio, fim);

  clientesPagina.forEach((cliente) => {
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

  const totalPaginas = Math.ceil(clientes.length / clientesPorPagina) || 1;
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

async function verClientesDoEvento(idEvento, nomeEvento) {
  const titulo = document.getElementById("titulo-clientes-evento");
  const subtitulo = document.getElementById("subtitulo-clientes-evento");

  if (titulo) titulo.innerText = `Clientes: ${nomeEvento}`;
  if (subtitulo)
    subtitulo.innerText = `Gerenciando participantes do evento #${idEvento}`;

  await carregarClientes(idEvento);
  trocarPagina("clientes");
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
    const response = await fetch(`${API_URL}/categorias/listar`);
    if (!response.ok) throw new Error();
    categorias = await response.json();

    const selectCategoria = document.getElementById("evento-categoria");
    if (!selectCategoria) return;

    selectCategoria.innerHTML = `
      <option value="" disabled selected hidden>
        Selecione uma categoria
      </option>
    `;

    categorias.forEach((cat) => {
      selectCategoria.innerHTML += `<option value="${cat.id}">${cat.nome}</option>`;
    });
  } catch (error) {
    console.error("Erro ao sincronizar categorias com o backend:", error);
  }
}

async function carregarEventos() {
  try {
    if (categorias.length === 0) {
      await carregarCategorias();
    }

    const response = await fetch(`${API_URL}/eventos/listar`);
    if (!response.ok) return;
    const eventos = await response.json();
    const gridContainer = document.getElementById("tabela-eventos-body");
    if (!gridContainer) return;
    gridContainer.innerHTML = "";

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
              <button class="btn-edit-table" onclick="prepararEdicaoEvento(${evento.id})" title="Editar">
                <i data-lucide="pencil" style="width: 16px;"></i>
              </button>
              <button class="btn-edit-table btn-delete-table" onclick="deletarEvento(${evento.id})" title="Excluir">
                <i data-lucide="trash-2" style="width: 16px;"></i>
              </button>
            </div>
          </div>
          <div class="event-card-body">
            <h3 class="event-card-title">${evento.nome}</h3>
            <div class="event-card-info-item">
              <i data-lucide="calendar"></i>
              <span>${dataFormatada}</span>
            </div>
            <div class="event-card-info-item">
              <i data-lucide="map-pin"></i>
              <span>${evento.local}</span>
            </div>
            <div class="event-card-footer" style="display: flex; flex-direction: column; gap: 12px; align-items: stretch;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <div class="event-card-price-label">Passagem</div>
                  <div class="event-card-price-value">R$ ${evento.valor_passagem.toFixed(2).replace(".", ",")}</div>
                </div>
              </div>
              
              <button class="btn-import" onclick="verClientesDoEvento(${evento.id}, '${evento.nome.replace(/'/g, "\\'")}')" style="width: 100%; justify-content: center; margin: 0; padding: 10px;">
                <i data-lucide="users" style="width: 16px; height: 16px;"></i>
                Ver Participantes
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

    const response = await fetch(`${API_URL}/eventos/consultar/${id}`);
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

async function carregarPedidos() {
  try {
    const response = await fetch(`${API_URL}/pedidos/listar`);
    if (!response.ok) throw new Error();
    pedidos = await response.json();
    paginaAtualPedidos = 1;
    mostrarPaginaPedidos();
  } catch (error) {
    console.error(error);
  }
}

function mostrarPaginaPedidos() {
  const tabela = document.getElementById("tabela-pedidos-body");
  if (!tabela) return;
  tabela.innerHTML = "";

  const totalPaginas = Math.ceil(pedidos.length / pedidosPorPagina) || 1;

  if (paginaAtualPedidos > totalPaginas) paginaAtualPedidos = totalPaginas;
  if (paginaAtualPedidos < 1) paginaAtualPedidos = 1;

  const inicio = (paginaAtualPedidos - 1) * pedidosPorPagina;
  const fim = inicio + pedidosPorPagina;
  const pedidosPagina = pedidos.slice(inicio, fim);

  pedidosPagina.forEach((pedido) => {
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

    tabela.innerHTML += `
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
  if (id === "pedidos") carregarPedidos();
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