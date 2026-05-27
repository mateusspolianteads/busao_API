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
  if (id === "pedidos") {
    if (!idEventoAtual) {
      exibirMensagemTabelaPedidos("Selecione um evento para ver os pedidos.");
      return;
    }
  }
  carregarPedidos(idEventoAtual);
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
