import os
import re
import tempfile
import unicodedata
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase_client import supabase as supabase_client

_lock = threading.Lock()

_playwright = None
_browser = None


def _get_browser():
    global _playwright, _browser

    if _browser:
        return _browser

    _playwright = sync_playwright().start()

    _browser = _playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-zygote",
            "--single-process"
        ]
    )

    return _browser


def _bloquear_recursos(contexto):
    def handler(route):
        if route.request.resource_type in ["image", "media", "font"]:
            route.abort()
        else:
            route.continue_()

    contexto.route("**/*", handler)


def _limpar_nome_arquivo(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "", texto)


def exportar_ingressos(cpf: str, senha: str, evento: str) -> str:
    nome_limpo = _limpar_nome_arquivo(evento)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_limpo}_{timestamp}.xls"

    caminho_temporario = os.path.join(tempfile.gettempdir(), nome_arquivo)

    with _lock:
        browser = _get_browser()
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            accept_downloads=True
        )

        try:
            _bloquear_recursos(context)
            page = context.new_page()

            page.set_default_timeout(60000)
            page.set_default_navigation_timeout(60000)

            _fazer_login(page, cpf, senha)

            page.get_by_test_id("entityManager").click()
            page.get_by_role("menuitem", name="Meus Eventos Minhas Páginas Á").click()

            page.locator("p.side-event-title").first.click()

            elemento_evento = page.locator("a.event-list-link", has_text=evento)

            if elemento_evento.count() == 0:
                raise ValueError(f"Evento '{evento}' não encontrado")

            elemento_evento.first.click()

            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            page.locator("button", has_text="Exportar").click()
            page.locator("#advance-btn-small-step-alert").wait_for(state="visible")

            with page.expect_download(timeout=60000) as download_info:
                page.locator("#advance-btn-small-step-alert").click()

            download = download_info.value
            download.save_as(caminho_temporario)

            supabase = supabase_client
            caminho_storage = f"exports_cheers/{nome_arquivo}"

            with open(caminho_temporario, "rb") as f:
                supabase.storage.from_("uploads").upload(
                    path=caminho_storage,
                    file=f,
                    file_options={
                        "content-type": "application/vnd.ms-excel",
                        "upsert": "true"
                    },
                )

            return caminho_storage

        finally:
            try:
                context.close()
            except:
                pass

            try:
                if os.path.exists(caminho_temporario):
                    os.remove(caminho_temporario)
            except:
                pass