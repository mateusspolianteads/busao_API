document.addEventListener("DOMContentLoaded", () => {
  if (!token) {
    window.location.href = "login.html";
    return;
  }

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
        const response = await fetch(`${window.API_URL}/clientes/atualizar/${id}`, {
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
          ? `${window.API_URL}/eventos/atualizar/${id}`
          : `${window.API_URL}/eventos/cadastrar`;
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

  const selectCanalVenda = document.getElementById(
    "select-canal-venda-dashboard",
  );
  const selectPeriodo = document.getElementById("select-periodo-dashboard");

  if (selectCanalVenda)
    selectCanalVenda.addEventListener("change", () => {
      carregarDashboard(selectCanalVenda.value, selectPeriodo?.value || "");
    });

  if (selectPeriodo)
    selectPeriodo.addEventListener("change", () => {
      carregarDashboard(selectCanalVenda?.value || "", selectPeriodo.value);
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
  carregarDashboard();
});
