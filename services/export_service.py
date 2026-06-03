import os
import re
import tempfile
import unicodedata
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase_client import supabase as supabase_client


def _bloquear_recursos(contexto):
    def handler(route):
        if route.request.resource_type in ["image", "media", "font"]:
            route.abort()
        else:
            route.continue_()

    contexto.route("**/*", handler)


def _fazer_login(pagina, cpf, senha):
    for tentativa in range(3):
        try:
            print(f"[INFO] Tentativa login {tentativa + 1}")

            pagina.goto("https://cheers.com.br/", wait_until="domcontentloaded", timeout=60000)

            pagina.locator("#login-btn").wait_for(state="visible", timeout=30000)
            pagina.locator("#login-btn").click()

            pagina.locator("#email-input").wait_for(state="visible", timeout=15000)
            pagina.locator("#email-input").fill(cpf)

            pagina.locator("form").get_by_role("button", name="Entrar").click()
            pagina.locator("form").get_by_role("button", name="Prefiro entrar com senha").click()

            pagina.get_by_test_id("password").fill(senha)

            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.get_by_test_id("entityManager").wait_for(state="visible", timeout=30000)

            print("[OK] Login realizado")
            return

        except Exception as e:
            print(f"[WARN] Falha login: {e}")

            try:
                pagina.goto("https://cheers.com.br/", wait_until="domcontentloaded", timeout=30000)
            except:
                pass

    raise Exception("Login falhou após 3 tentativas")


def _limpar_nome_arquivo(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    texto = re.sub(r"[^a-zA-Z0-9_\-\.]", "", texto)
    return texto


def exportar_ingressos(cpf: str, senha: str, evento: str) -> str:
    nome_limpo = _limpar_nome_arquivo(evento)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_limpo}_{timestamp}.xls"

    caminho_temporario = os.path.join(tempfile.gettempdir(), nome_arquivo)

    browser = None
    context = None
    page = None

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--single-process"
                ]
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                accept_downloads=True
            )

            _bloquear_recursos(context)

            page = context.new_page()
            page.set_default_timeout(15000)

            _fazer_login(page, cpf, senha)

            page.get_by_test_id("entityManager").click()
            page.get_by_role("menuitem", name="Meus Eventos Minhas Páginas Á").click()

            page.locator("p.side-event-title").first.wait_for(state="visible")
            page.locator("p.side-event-title").first.click()

            elemento_evento = page.locator("a.event-list-link", has_text=evento)

            try:
                elemento_evento.first.wait_for(state="attached", timeout=5000)
            except:
                pass

            if elemento_evento.count() == 0:
                raise ValueError(f"Evento '{evento}' não encontrado")

            elemento_evento.click()
            print(f"[OK] Evento selecionado: {evento}")

            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            page.locator("button", has_text="Exportar").click()
            page.locator("#advance-btn-small-step-alert").wait_for(state="visible")

            with page.expect_download(timeout=60000) as download_info:
                page.locator("#advance-btn-small-step-alert").click()

            download = download_info.value
            download.save_as(caminho_temporario)

            print(f"[OK] Arquivo salvo local: {caminho_temporario}")

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

            print(f"[OK] Upload Supabase: {caminho_storage}")

            return caminho_storage

    except Exception as error:
        print(f"[ERROR] Falha na automação: {error}")
        raise error

    finally:
        try:
            if page:
                page.close()
        except:
            pass

        try:
            if context:
                context.close()
        except:
            pass

        try:
            if browser:
                browser.close()
        except:
            pass

        try:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
        except:
            pass