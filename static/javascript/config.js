window.API_URL = (window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1"))
  ? "http://127.0.0.1:8000"
  : "https://busao-api.onrender.com";

window.SUPABASE_URL = "https://okazcozfvmvbkagxdwon.supabase.co";

const token = localStorage.getItem("token");

let clientes = [];
let paginaAtualClientes = 1;
const clientesPorPagina = 10;
let totalClientesBanco = 0;
const clientesCache = {};
const clientesCacheTTL = 5000;

let pedidos = [];
let paginaAtualPedidos = 1;
const pedidosPorPagina = 10;
let totalPedidosBanco = 0;

let categorias = [];
let idEventoAtual = null;
let xhrImportacaoAtual = null;
let intervaloProgressoImportacao = null;
let exportacaoEmProgresso = false;

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
