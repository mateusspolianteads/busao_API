import os
import re
import tempfile
import unicodedata
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase_client import supabase as supabase_client


def _bloquear_recursos(contexto):
    def handler(route):
        if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
            route.abort()
        else:
            route.continue_()

    contexto.route("**/*", handler)


def _fazer_login(pagina, cpf, senha):
    for tentativa in range(1, 3):
        try:
            print(f"[INFO] Tentativa login {tentativa}")

            pagina.goto(
                "https://cheers.com.br/",
                wait_until="domcontentloaded",
                timeout=5000 if tentativa == 1 else 60000,
            )

            pagina.wait_for_timeout(1000 if tentativa == 1 else 2000)

            pagina.wait_for_selector(
                "#login-btn", timeout=30000 if tentativa == 1 else 60000
            )
            pagina.locator("#login-btn").click()

            pagina.wait_for_selector(
                "#email-input", timeout=30000 if tentativa == 1 else 60000
            )
            pagina.locator("#email-input").fill(cpf)

            pagina.locator("form").get_by_role("button", name="Entrar").click()

            try:
                pagina.get_by_text("Prefiro entrar com senha").click(
                    timeout=5000 if tentativa == 1 else 15000
                )
            except:
                raise Exception("Botão senha não apareceu")

            pagina.get_by_test_id("password").wait_for(timeout=60000)
            pagina.get_by_test_id("password").fill(senha)

            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.get_by_test_id("entityManager").wait_for(timeout=60000)

            print("[OK] Login realizado")
            return

        except Exception as e:
            print(f"[WARN] Falha login tentativa {tentativa}: {e}")

            try:
                pagina.goto(
                    "https://cheers.com.br/",
                    wait_until="domcontentloaded",
                    timeout=20000,
                )
            except:
                pass

    raise Exception("Login falhou após 2 tentativas")


def _limpar_nome_arquivo(texto: str) -> str:
    texto = (
        unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    )
    texto = texto.replace(" ", "_")
    texto = re.sub(r"[^a-zA-Z0-9_\-\.]", "", texto)
    return texto


def exportar_ingressos(cpf: str, senha: str, evento: str) -> str:
    nome_limpo = _limpar_nome_arquivo(evento)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_limpo}_{timestamp}.xls"

    caminho_temporario = os.path.join(tempfile.gettempdir(), nome_arquivo)

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                ],
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 720}, accept_downloads=True
            )

            _bloquear_recursos(context)

            page = context.new_page()
            page.set_default_timeout(60000)

            _fazer_login(page, cpf, senha)

            page.get_by_test_id("entityManager").click()
            page.get_by_role("menuitem", name="Meus Eventos Minhas Páginas Á").click()

            page.locator("p.side-event-title").first.wait_for(timeout=60000)
            page.locator("p.side-event-title").first.click()

            elemento_evento = page.locator("a.event-list-link", has_text=evento)

            elemento_evento.first.wait_for(timeout=60000)

            if elemento_evento.count() == 0:
                raise ValueError(f"Evento '{evento}' não encontrado")

            elemento_evento.click()
            print(f"[OK] Evento selecionado: {evento}")

            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            page.locator("button", has_text="Exportar").click()
            page.locator("#advance-btn-small-step-alert").wait_for(timeout=60000)

            with page.expect_download(timeout=120000) as download_info:
                page.locator("#advance-btn-small-step-alert").click()

            download = download_info.value
            download.save_as(caminho_temporario)

            print(f"[OK] Arquivo salvo local: {caminho_temporario}")

            caminho_storage = f"exports_cheers/{nome_arquivo}"

            with open(caminho_temporario, "rb") as f:
                supabase_client.storage.from_("uploads").upload(
                    path=caminho_storage,
                    file=f,
                    file_options={
                        "content-type": "application/vnd.ms-excel",
                        "upsert": "true",
                    },
                )

            print(f"[OK] Upload Supabase: {caminho_storage}")

            return caminho_storage

    finally:
        try:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
        except:
            pass
