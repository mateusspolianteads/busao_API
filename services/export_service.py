import os
import re
import tempfile
import unicodedata
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase_client import supabase as supabase_client

def _fazer_login(pagina, cpf, senha):
    for tentativa in range(1, 3):
        # 20 segundos na primeira tentativa, 60 na segunda
        timeout_val = 20000 if tentativa == 1 else 60000

        try:
            print(f"[INFO] Iniciando tentativa de login {tentativa} (timeout: {timeout_val}ms)...", flush=True)

            pagina.goto(
                "https://cheers.com.br/", 
                wait_until="domcontentloaded", 
                timeout=timeout_val
            )

            # Aguarda o botão principal de login
            pagina.wait_for_selector("#login-btn", timeout=timeout_val)
            pagina.locator("#login-btn").click()

            # Preenche o CPF
            pagina.wait_for_selector("#email-input", timeout=timeout_val)
            pagina.locator("#email-input").fill(cpf)
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            # Tenta clicar em entrar com senha, se o site pedir
            try:
                pagina.get_by_text("Prefiro entrar com senha").click(timeout=5000)
            except:
                pass

            # Preenche a senha
            pagina.get_by_test_id("password").wait_for(timeout=timeout_val)
            pagina.locator("[data-testid='password']").fill(senha)
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            # Verifica se o login foi concluído com sucesso
            pagina.get_by_test_id("entityManager").wait_for(timeout=timeout_val)
            print(f"[OK] Login realizado com sucesso na tentativa {tentativa}.", flush=True)
            return

        except Exception as e:
            print(f"[WARN] Falha na tentativa {tentativa}. Erro: {e}", flush=True)
            print(f"[DEBUG] URL atual durante a falha: {pagina.url}", flush=True)
            if tentativa == 1:
                try:
                    # Limpa os cookies antes da próxima tentativa para garantir um estado limpo
                    pagina.context.clear_cookies()
                except:
                    pass

    raise Exception("Login falhou após 2 tentativas completas.")

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

    print(f"[INFO] Iniciando processo para o evento: {evento}", flush=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--disable-setuid-sandbox",
                    "--disable-software-rasterizer",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                accept_downloads=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                extra_http_headers={
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.google.com/",
                }
            )
            
            page = context.new_page()
            page.set_default_timeout(60000)

            _fazer_login(page, cpf, senha)

            print("[INFO] Navegando até a página do evento...", flush=True)
            page.get_by_test_id("entityManager").click()
            page.get_by_role("menuitem", name="Meus Eventos Minhas Páginas Á").click()

            page.locator("p.side-event-title").first.wait_for(timeout=60000)
            page.locator("p.side-event-title").first.click()

            elemento_evento = page.locator("a.event-list-link", has_text=evento)
            elemento_evento.first.wait_for(timeout=60000)

            if elemento_evento.count() == 0:
                print(f"[ERROR] Evento '{evento}' não encontrado.", flush=True)
                raise ValueError(f"Evento '{evento}' não encontrado")

            elemento_evento.click()
            print(f"[OK] Evento '{evento}' selecionado.", flush=True)

            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            print("[INFO] Solicitando exportação...", flush=True)
            page.locator("button", has_text="Exportar").click()
            page.locator("#advance-btn-small-step-alert").wait_for(timeout=60000)

            with page.expect_download(timeout=120000) as download_info:
                page.locator("#advance-btn-small-step-alert").click()
                print("[INFO] Download iniciado...", flush=True)

            download = download_info.value
            download.save_as(caminho_temporario)
            print(f"[OK] Arquivo salvo temporariamente: {caminho_temporario}", flush=True)

            caminho_storage = f"exports_cheers/{nome_arquivo}"
            print(f"[INFO] Iniciando upload para Supabase: {caminho_storage}", flush=True)

            with open(caminho_temporario, "rb") as f:
                supabase_client.storage.from_("uploads").upload(
                    path=caminho_storage,
                    file=f,
                    file_options={
                        "content-type": "application/vnd.ms-excel",
                        "upsert": "true",
                    },
                )

            print("[OK] Upload finalizado com sucesso.", flush=True)
            return caminho_storage

    except Exception as e:
        print(f"[ERROR] Erro crítico no processo: {e}", flush=True)
        raise e
    finally:
        try:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
                print("[INFO] Arquivo temporário removido.", flush=True)
        except:
            pass