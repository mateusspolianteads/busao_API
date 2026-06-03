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

            # Abre a página inicial
            pagina.goto(
                "https://cheers.com.br/",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            pagina.wait_for_timeout(2500)

            # 1. Clica no botão de Entrar (Mobile/Responsivo conforme o HTML que você mandou)
            # Usamos o ID específico e deixamos o ID antigo como fallback caso mude o tamanho da tela
            login_btn = pagina.locator("#login-btn-mobile, #login-btn").first
            login_btn.wait_for(timeout=30000)
            login_btn.click()

            # 2. Preenche o campo de e-mail/CPF
            email = pagina.locator("#email-input, input[placeholder*='CPF']").first
            email.wait_for(timeout=30000)
            email.fill(cpf)

            # Avança o primeiro formulário
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.wait_for_timeout(2000)

            # 3. Força o clique em "Prefiro entrar com senha" usando a estrutura do botão real
            print("[INFO] Alternando para fluxo de senha...", flush=True)
            botao_senha = pagina.get_by_role("button", name="Prefiro entrar com senha").first
            
            # Caso o get_by_role falhe por conta da div interna, usamos o seletor por texto plano como plano B
            if botao_senha.count() == 0:
                botao_senha = pagina.get_by_text("Prefiro entrar com senha").first

            botao_senha.wait_for(timeout=20000)
            botao_senha.click()

            # 4. Espera segura e preenchimento do campo de senha usando o data-testid exato do HTML
            senha_input = pagina.get_by_test_id("password").first
            
            try:
                senha_input.wait_for(timeout=30000)
            except:
                raise Exception("Campo de senha (data-testid='password') não apareceu no Render")

            senha_input.fill(senha)

            # Confirma o login definitivo
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.wait_for_timeout(3000)

            # Valida se o login deu certo esperando o elemento do painel
            manager = pagina.locator("[data-testid='entityManager']").first
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

            # Criando o contexto simulando um ambiente real com User-Agent ativo
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                accept_downloads=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            page = context.new_page()
            page.set_default_timeout(60000)

            # Realiza o fluxo de login atualizado
            _fazer_login(page, cpf, senha)

            # Acessa o menu lateral de eventos de forma resiliente
            try:
                page.get_by_test_id("entityManager").click()
                page.get_by_text("Meus Eventos").first.click()
            except:
                # Fallback genérico caso o menu estrutural mude de nome
                page.get_by_role("menuitem", name=re.compile("Meus Eventos", re.IGNORECASE)).click()

            page.locator("p.side-event-title").first.wait_for(timeout=60000)
            page.locator("p.side-event-title").first.click()

            evento_locator = page.locator("a.event-list-link", has_text=evento).first

            if evento_locator.count() == 0:
                raise Exception(f"Evento '{evento}' não encontrado na listagem")

            evento_locator.click()
            print(f"[OK] Evento selecionado: {evento}", flush=True)

            # Navegação interna do painel do evento
            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            # Dispara a exportação da planilha
            page.locator("button", has_text="Exportar").first.click()
            
            # Aguarda o botão final de download (aceita o ID antigo ou o texto "Download" do modal)
            botao_download = page.locator("#advance-btn-small-step-alert, button:has-text('Download')").first
            botao_download.wait_for(timeout=60000)

            # Captura e salva o fluxo de download do arquivo .xls
            with page.expect_download(timeout=120000) as download_info:
                botao_download.click()

            download = download_info.value
            download.save_as(caminho_temporario)

            print(f"[OK] Download salvo localmente em: {caminho_temporario}", flush=True)

            caminho_storage = f"exports_cheers/{nome_arquivo}"

            # Faz o upload do arquivo final consolidado para o Supabase
            with open(caminho_temporario, "rb") as f:
                supabase_client.storage.from_("uploads").upload(
                    path=caminho_storage,
                    file=f,
                    file_options={
                        "content-type": "application/vnd.ms-excel",
                        "upsert": "true",
                    },
                )

            print(f"[OK] Upload concluído para o Supabase: {caminho_storage}", flush=True)
            return caminho_storage

    finally:
        try:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
        except:
            pass