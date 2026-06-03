async function importarPlanilha(event, endpoint, tituloModal = "Processando Planilha") {
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
  // Usa a sua variável global já existente
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
  // Alimenta a sua variável global já existente
  xhrImportacaoAtual = xhr;

  const formData = new FormData();
  formData.append("file", arquivo);
  formData.append("evento_id", idEventoAtual);

  xhr.open("POST", `${window.API_URL}${endpoint}`);
  const authHeaders = getAuthHeaders();
  if (authHeaders.Authorization) {
    xhr.setRequestHeader("Authorization", authHeaders.Authorization);
  }

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

async function carregarClientes(eventoId = null) {
  if (eventoId !== null) {
    idEventoAtual = eventoId;
    paginaAtualClientes = 1;
  }

  const tabela = document.getElementById("tabela-clientes-body");
    /* if (tabela) {
      tabela.innerHTML =
        "<tr><td colspan='7' style='text-align:center; padding: 30px; opacity: 0.7;'><span class='spinner-inline'></span> Buscando participantes...</td></tr>";
    } */

  if (idEventoAtual && clientesCache[idEventoAtual]) {
    const paginaCache = clientesCache[idEventoAtual][paginaAtualClientes];
    if (paginaCache && paginaCache.expires > Date.now()) {
      clientes = paginaCache.clientes;
      totalClientesBanco = paginaCache.total;
      mostrarPaginaClientes();
      return;
    }
  }

  try {
    const url = idEventoAtual
      ? `${window.API_URL}/clientes/evento/${idEventoAtual}?pagina=${paginaAtualClientes}&limite=10`
      : `${window.API_URL}/clientes/listar`;

    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });
    if (!response.ok)
      throw new Error(`Erro na requisição: Status ${response.status}`);

    const textoResposta = await response.text();
    let dadosBrutos = textoResposta.trim() ? JSON.parse(textoResposta) : [];

    if (dadosBrutos && typeof dadosBrutos === "object" && !Array.isArray(dadosBrutos)) {
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

    if (idEventoAtual) {
      clientesCache[idEventoAtual] = clientesCache[idEventoAtual] || {};
      clientesCache[idEventoAtual][paginaAtualClientes] = {
        clientes,
        total: totalClientesBanco,
        expires: Date.now() + clientesCacheTTL,
      };
    }

    mostrarPaginaClientes();
  } catch (error) {
    console.error("Erro no processamento de clientes:", error);
    if (tabela) {
      tabela.innerHTML = `<tr><td colspan='7' style='text-align:center; color: #ff4d4d; padding: 20px;'><strong>Erro ao processar dados do servidor.</strong></td></tr>`;
    }
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

async function carregarCategorias() {
  console.log("[CATEGORIAS] Carregando categorias...");
  try {
    const response = await fetch(`${window.API_URL}/categorias/listar`, {
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
  console.log("[EVENTOS] Carregando eventos...");
  const gridContainer = document.getElementById("tabela-eventos-body");
  if (gridContainer) {
    gridContainer.innerHTML =
      "<div style='grid-column: 1/-1; text-align: center; padding: 50px; opacity: 0.7;'><span class='spinner-inline'></span> Carregando eventos ativos...</div>";
  }

  try {
    if (categorias.length === 0) await carregarCategorias();

    const response = await fetch(`${window.API_URL}/eventos/listar`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) return;
    
    // cacheEventos assume-se global ou vinda do escopo correto do sistema
    const listaEventos = await response.json(); 
    window.cacheEventos = listaEventos; 

    if (!gridContainer) return;
    gridContainer.innerHTML = "";

    if (listaEventos.length === 0) {
      gridContainer.innerHTML =
        "<div style='grid-column: 1/-1; text-align: center; padding: 50px; opacity: 0.5;'>Nenhum evento localizado.</div>";
      return;
    }

    listaEventos.forEach((evento) => {
      const dataFormatada =
        new Date(evento.data_evento).toLocaleDateString("pt-BR") +
        " " +
        new Date(evento.data_evento).toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        });
      const tagImagem = evento.imagem ? `<img src="${evento.imagem}" alt="${evento.nome}" loading="lazy" decoding="async">` : "";
      const classeNoImage = evento.imagem ? "" : "no-image";
      const objCategoria = categorias.find((c) => c.id === evento.categoria_id);
      const nomeCategoria = objCategoria ? objCategoria.nome : `ID: ${evento.categoria_id}`;

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

  popularFiltroEventosPedidos(idEventoAtual ?? "");
}

async function fazerUploadImagem(input) {
  const file = input.files[0];
  if (!file) return;

  const formEvento = document.getElementById("form-evento");
  const btnSalvar = formEvento ? formEvento.querySelector('button[type="submit"]') : null;
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
    const response = await fetch(`${window.API_URL}/upload/`, {
      method: "POST",
      body: formData,
      headers: {Authorization: getAuthHeaders().Authorization}
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
    const response = await fetch(`${window.API_URL}/eventos/consultar/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) return;
    const evento = await response.json();

    document.getElementById("modal-evento-titulo").innerText = "Editar Evento";
    document.getElementById("evento-id").value = evento.id;
    document.getElementById("evento-nome").value = evento.nome;
    document.getElementById("evento-categoria").value = evento.categoria_id;
    if (evento.data_evento)
      document.getElementById("evento-data").value = evento.data_evento.substring(0, 16);
    document.getElementById("evento-local").value = evento.local;
    document.getElementById("evento-valor").value = evento.valor_passagem;
    document.getElementById("evento-imagem-url").value = evento.imagem || "";

    const formEvento = document.getElementById("form-evento");
    const btnSalvar = formEvento ? formEvento.querySelector('button[type="submit"]') : null;
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
    const response = await fetch(`${window.API_URL}/eventos/deletar/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (response.ok) carregarEventos();
  } catch (error) {
    console.error(error);
  }
}

function popularFiltroEventosPedidos(idSelecionado) {
  const selectFiltro = document.getElementById("filtro-pedidos-evento");
  if (!selectFiltro) return;

  selectFiltro.innerHTML = "";
  const listaEventos = window.cacheEventos || [];
  if (listaEventos.length === 0) {
    selectFiltro.innerHTML = `<option value="">Nenhum evento cadastrado</option>`;
    return;
  }

  listaEventos.forEach((ev) => {
    selectFiltro.innerHTML += `<option value="${ev.id}">${ev.nome}</option>`;
  });
  selectFiltro.value = idSelecionado;
}

async function carregarPedidos(eventoId = null) {
  if (eventoId !== null && eventoId !== idEventoAtual) {
    idEventoAtual = eventoId;
    paginaAtualPedidos = 1;
  }

/*   exibirMensagemTabelaPedidos("<span class='spinner-inline'></span> Buscando pedidos atualizados...");
 */
  const listaEventos = window.cacheEventos || [];
  if (!idEventoAtual) {
    if (listaEventos.length > 0) {
      idEventoAtual = listaEventos[0].id;
    } else {
      try {
        const resEventos = await fetch(`${window.API_URL}/eventos/listar`, { headers: getAuthHeaders() });
        if (resEventos.ok) {
          window.cacheEventos = await resEventos.json();
          if (window.cacheEventos.length > 0) idEventoAtual = window.cacheEventos[0].id;
        }
      } catch (error) {
        console.error("Erro ao buscar evento inicial:", error);
      }
    }
  }

  if (!idEventoAtual) {
    exibirMensagemTabelaPedidos("Nenhum evento cadastrado para carregar pedidos.");
    return;
  }

  popularFiltroEventosPedidos(idEventoAtual);

  try {
    const response = await fetch(
      `${window.API_URL}/pedidos/evento/${idEventoAtual}?pagina=${paginaAtualPedidos}&limite=${pedidosPorPagina}`,
      { headers: getAuthHeaders() },
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
    exibirMensagemTabelaPedidos("Erro crítico ao se comunicar com o servidor.", "#ff4d4d");
  }
}

async function carregarDashboard(canal_venda = "", periodo = "") {
  console.log("[DASHBOARD] Carregando dashboard...");
  try {
    const query = new URLSearchParams();
    if (canal_venda) query.append("canal_venda", canal_venda);
    if (periodo) query.append("periodo", periodo);

    const url = `${window.API_URL}/pedidos/dashboard?${query.toString()}`;
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error(`Status ${response.status}`);

    const dados = await response.json();
    vendedoresDashboard = dados.filtros.vendedores || [];
    periodosDashboard = dados.filtros.periodos || [];
    eventosDashboard = dados.eventos || [];
    dashboardFiltroCanal = canal_venda || "";
    dashboardFiltroPeriodo = periodo || "";
    dashboardPaginaAtual = 1;
    dashboardTotalPaginas = Math.ceil(eventosDashboard.length / dashboardPorPagina) || 1;

    atualizarDashboardMetrics(dados.totals || {});
    popularFiltrosDashboard(canal_venda, periodo);
    renderizarDashboardEventos(eventosDashboard);
  } catch (error) {
    console.error("Erro ao carregar dashboard:", error);
    atualizarDashboardMetrics({ total_vendas: 0, ingressos_vendidos: 0, eventos_com_venda: 0 });
    renderizarDashboardEventos([]);
  }
}

async function atualizarCheers() {
  if (!idEventoAtual) {
    alert("Selecione um evento antes de atualizar!");
    return;
  }

  console.log("[EXPORTACAO] Iniciando exportação...");
  exportacaoEmProgresso = true;

  const listaEventos = window.cacheEventos || [];
  const eventoAtual = listaEventos.find((e) => e.id === idEventoAtual);
  
  if (!eventoAtual) {
    alert("Evento não encontrado localmente! Atualize a lista.");
    exportacaoEmProgresso = false;
    return;
  }

  // Escopo local puro: não precisa mais de variáveis globais de controle de cancelamento
  const nomeEventoExportacao = eventoAtual.nome;
  
  exibirModalProgressoExportacao("Sincronizando com Cheers");
  atualizarModalProgressoExportacao(10, "Iniciando sincronização com Cheers...");

  let porcentagemSimulada = 10;
  const intervaloProgressoExportacao = setInterval(() => {
    if (porcentagemSimulada < 90) {
      porcentagemSimulada += 5;
      atualizarModalProgressoExportacao(
        porcentagemSimulada,
        `Exportando dados do evento: ${nomeEventoExportacao}... (${porcentagemSimulada}%)`,
      );
    }
  }, 800);

  try {
    const response = await fetch(`${window.API_URL}/pedidos/exportar-planilha`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ evento: nomeEventoExportacao })
    });

    clearInterval(intervaloProgressoExportacao);

    if (response.ok) {
      const resultado = await response.json();
      const nomeArquivoExportado = resultado.nome_arquivo;
      
      atualizarModalProgressoExportacao(100, "Processamento completo!");

      setTimeout(() => {
        exibirResultadoExportacao(nomeArquivoExportado);
      }, 500);
    } else {
      exportacaoEmProgresso = false;
      try {
        const erro = await response.json();
        alert(erro.detail || "Erro ao exportar dados do Cheers. Verifique se o nome do evento existe no Cheers.");
      } catch (e) {
        alert("Erro ao exportar dados do Cheers.");
      }
      fecharModalProgressoExportacao();
    }
  } catch (error) {
    clearInterval(intervaloProgressoExportacao);
    exportacaoEmProgresso = false;
    console.error("[EXPORTACAO] Erro ao preparar exportação:", error);
    alert("Erro ao preparar a sincronização com Cheers.");
    fecharModalProgressoExportacao();
  }
}

function exibirModalProgressoExportacao(titulo) {
  document.getElementById("titulo-progresso-export").textContent = titulo;
  document.getElementById("modal-progresso-exportacao").style.display = "flex";
}

function atualizarModalProgressoExportacao(porcentagem, mensagem) {
  const status = document.getElementById("status-progresso-export");
  if (status) status.textContent = mensagem;
}

function fecharModalProgressoExportacao() {
  document.getElementById("modal-progresso-exportacao").style.display = "none";

  const spinner = document.getElementById("loading-spinner-export");
  if (spinner) spinner.style.display = "";

  const txtTitulo = document.getElementById("titulo-progresso-export");
  if (txtTitulo) txtTitulo.style.display = "";

  const status = document.getElementById("status-progresso-export");
  if (status) status.innerHTML = "Sincronizando com Cheers, por favor aguarde...";

  const btnCancelar = document.getElementById("btn-cancelar-exportacao");
  if (btnCancelar) btnCancelar.style.display = "";
}

function exibirResultadoExportacao(nomeArquivo) {
  const loadingSpinner = document.getElementById("loading-spinner-export");
  const btnCancelar = document.getElementById("btn-cancelar-exportacao");
  const txtTitulo = document.getElementById("titulo-progresso-export");
  const statusProgresso = document.getElementById("status-progresso-export");

  if (loadingSpinner) loadingSpinner.style.display = "none";
  if (btnCancelar) btnCancelar.style.display = "none";
  if (txtTitulo) txtTitulo.style.display = "none";

  if (statusProgresso) {
    statusProgresso.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 25px 0;">
        <i data-lucide="check-circle" style="width: 64px; height: 64px; color: #10b981;"></i>
        <span style="font-size: 1.2rem; font-weight: 700; color: #10b981;">Exportação Concluída!</span>
        
        <div style="width: 100%; text-align: left; background: #f3f4f6; padding: 12px; border-radius: 6px; margin: 10px 0;">
          <span style="font-size: 0.85rem; color: #666; display: block; margin-bottom: 4px;">📄 Arquivo Exportado:</span>
          <span style="font-size: 0.95rem; font-weight: 600; color: #333; word-break: break-all;">${nomeArquivo}</span>
        </div>

        <button id="btn-importar-exportado" onclick="importarArquivoExportado('${nomeArquivo}')" style="
          margin-top: 15px;
          padding: 11px 20px;
          background-color: #10b981;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          width: 100%;
          font-family: inherit;
          transition: background 0.2s, transform 0.1s;
        " onmouseover="this.style.backgroundColor='#059669'" onmouseout="this.style.backgroundColor='#10b981'" onmousedown="this.style.transform='scale(0.98)'" onmouseup="this.style.transform='scale(1)'">
          Importar Arquivo
        </button>
      </div>
    `;
    lucide.createIcons();
  }
}

async function importarArquivoExportado(nomeArquivo) {
  console.log("[IMPORTACAO] Iniciando importação de arquivo exportado...");
  fecharModalProgressoExportacao();
  exportacaoEmProgresso = false;

  exibirModalProgresso("Importando Dados Exportados");
  atualizarModalProgresso(0, "Iniciando leitura do arquivo exportado...");

  let porcentagemSimulada = 0;
  const intervalo = setInterval(() => {
    if (porcentagemSimulada < 95) {
      porcentagemSimulada += 2;
      atualizarModalProgresso(
        porcentagemSimulada,
        `Processando dados no banco de dados... (${porcentagemSimulada}%)`,
      );
    }
  }, 500);

  try {
    const resArquivo = await fetch(`${window.API_URL}/pedidos/baixar-arquivo-exportado`, {
      method: "POST",
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ nome_arquivo: nomeArquivo }),
    });

    if (!resArquivo.ok) {
      const erroTexto = await resArquivo.text();
      throw new Error(`Erro ${resArquivo.status} ao baixar arquivo: ${erroTexto}`);
    }

    const blobArquivo = await resArquivo.blob();

    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    const file = new File([blobArquivo], nomeArquivo, { type: "application/vnd.ms-excel" });
    formData.append("file", file);
    formData.append("evento_id", idEventoAtual);

    xhr.open("POST", `${window.API_URL}/pedidos/importar-planilha`);
    const authHeaders = getAuthHeaders();
    if (authHeaders.Authorization) {
      xhr.setRequestHeader("Authorization", authHeaders.Authorization);
    }

    xhr.onload = () => {
      clearInterval(intervalo);

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
        alert("Erro no servidor ao importar arquivo.");
      }
    };

    xhr.onerror = () => {
      clearInterval(intervalo);
      fecharModalProgresso();
      alert("Erro de rede ao importar arquivo.");
    };

    xhr.send(formData);
  } catch (error) {
    clearInterval(intervalo);
    fecharModalProgresso();
    console.error("Erro ao baixar arquivo:", error);
    alert("Erro ao baixar arquivo. Verifique se o arquivo existe.");
  }
}