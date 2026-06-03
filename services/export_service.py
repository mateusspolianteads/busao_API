import os
import re
import tempfile
import unicodedata
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase_client import supabase as supabase_client


def _fazer_login(pagina, cpf, senha):
    for tentativa in range(1, 3):
        try:
            print(f"[INFO] Tentativa login {tentativa}", flush=True)

            pagina.goto(
                "https://cheers.com.br/",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            pagina.wait_for_timeout(2500)

            login_btn = pagina.locator("#login-btn")
            login_btn.wait_for(timeout=30000)
            login_btn.click()

            email = pagina.locator("#email-input")
            email.wait_for(timeout=30000)
            email.fill(cpf)

            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.wait_for_timeout(2000)

            # fluxo opcional (não quebra login)
            try:
                botao_senha = pagina.get_by_text("Prefiro entrar com senha")
                if botao_senha.count() > 0:
                    botao_senha.first.click(timeout=5000)
            except:
                pass

            # espera segura do campo senha (sem count())
            senha_input = pagina.locator("[data-testid='password'], input[type='password']").first

            try:
                senha_input.wait_for(timeout=30000)
            except:
                raise Exception("Campo de senha não apareceu no Render")

            senha_input.fill(senha)

            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.wait_for_timeout(3000)

            manager = pagina.locator("[data-testid='entityManager']")
            manager.wait_for(timeout=60000)

            print(f"[OK] Login realizado na tentativa {tentativa}", flush=True)
            return

        except Exception as e:
            print(f"[WARN] Falha tentativa {tentativa}: {e}", flush=True)

            # --- SISTEMA DE EXTRAÇÃO DE TAGS E SCREENSHOT PARA DEBUG ---
            try:
                timestamp_erro = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 1. Captura as tags HTML (DOM) completas da página
                html_puro = pagina.content()
                caminho_html = os.path.join(tempfile.gettempdir(), f"debug_tags_{timestamp_erro}.html")
                with open(caminho_html, "w", encoding="utf-8") as f:
                    f.write(html_puro)
                
                # 2. Tira um print visual do erro
                caminho_print = os.path.join(tempfile.gettempdir(), f"debug_print_{timestamp_erro}.png")
                pagina.screenshot(path=caminho_print)
                
                # 3. Faz o upload do arquivo HTML para o Supabase
                with open(caminho_html, "rb") as f:
                    supabase_client.storage.from_("uploads").upload(
                        path=f"debug/tags_{timestamp_erro}.html",
                        file=f,
                        file_options={"content-type": "text/html", "upsert": "true"}
                    )
                
                # 4. Faz o upload do Print para o Supabase
                with open(caminho_print, "rb") as f:
                    supabase_client.storage.from_("uploads").upload(
                        path=f"debug/print_{timestamp_erro}.png",
                        file=f,
                        file_options={"content-type": "image/png", "upsert": "true"}
                    )
                
                print(f"[DEBUG] Tags HTML salvas no Supabase em: debug/tags_{timestamp_erro}.html", flush=True)
                print(f"[DEBUG] Print da tela salvo no Supabase em: debug/print_{timestamp_erro}.png", flush=True)
                
                # Limpa os arquivos de debug locais
                if os.path.exists(caminho_html): os.remove(caminho_html)
                if os.path.exists(caminho_print): os.remove(caminho_print)
            except Exception as erro_debug:
                print(f"[ERROR] Não foi possível extrair o HTML de debug: {erro_debug}", flush=True)
            # -----------------------------------------------------------

            try:
                pagina.context.clear_cookies()
                pagina.wait_for_timeout(1500)
            except:
                pass

    raise Exception("Login falhou após 2 tentativas")


def _limpar_nome_arquivo(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "", texto)


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
                viewport={"width": 1366, "height": 768},
                accept_downloads=True,
            )

            page = context.new_page()
            page.set_default_timeout(60000)

            _fazer_login(page, cpf, senha)

            page.get_by_test_id("entityManager").click()
            page.get_by_role("menuitem", name="Meus Eventos Minhas Páginas Á").click()

            page.locator("p.side-event-title").first.wait_for(timeout=60000)
            page.locator("p.side-event-title").first.click()

            evento_locator = page.locator("a.event-list-link", has_text=evento)

            if evento_locator.count() == 0:
                raise Exception(f"Evento '{evento}' não encontrado")

            evento_locator.first.click()

            print(f"[OK] Evento selecionado: {evento}", flush=True)

            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            page.locator("button", has_text="Exportar").click()
            page.locator("#advance-btn-small-step-alert").wait_for(timeout=60000)

            with page.expect_download(timeout=120000) as download_info:
                page.locator("#advance-btn-small-step-alert").click()

            download = download_info.value
            download.save_as(caminho_temporario)

            print(f"[OK] Download salvo: {caminho_temporario}", flush=True)

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

            print(f"[OK] Upload concluído: {caminho_storage}", flush=True)

            return caminho_storage

    finally:
        try:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
        except:
            pass