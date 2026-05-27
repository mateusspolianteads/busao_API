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

let vendedoresDashboard = [];
let periodosDashboard = [];
let eventosDashboard = [];
let dashboardPaginaAtual = 1;
const dashboardPorPagina = 10;
let dashboardTotalPaginas = 1;
let dashboardFiltroCanal = "";
let dashboardFiltroPeriodo = "";

function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}
