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

            # Abre a página inicial de forma mais leve
            pagina.goto(
                "https://cheers.com.br/",
                wait_until="commit",  # Não espera carregar trackers pesados para interagir
                timeout=45000,
            )

            # Evita o uso de pagina.content() [Consome muita memória RAM]
            # Procura diretamente por elementos típicos de desafio do Cloudflare
            cloudflare_box = pagina.locator("#cloudflare-challenge, iframe[src*='challenges.cloudflare.com']").first
            if cloudflare_box.count() > 0:
                print("[WARN] Cloudflare/Turnstile detectado! Aguardando estabilização...", flush=True)
                pagina.wait_for_load_state("networkidle", timeout=10000)
            else:
                pagina.wait_for_timeout(2000)

            # 1. Clica no botão de Entrar
            login_btn = pagina.locator("#login-btn-mobile, #login-btn").first
            login_btn.wait_for(state="visible", timeout=20000)
            
            # Movimento simulado sutil
            login_btn.hover()
            login_btn.click()

            # 2. Preenche o campo de e-mail/CPF
            email = pagina.locator("#email-input, input[placeholder*='CPF']").first
            email.wait_for(state="visible", timeout=20000)
            email.fill(cpf)

            # Avança o primeiro formulário
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            # Espera a transição de estado sem travar o processo
            pagina.wait_for_load_state("domcontentloaded")

            # 3. Força o clique em "Prefiro entrar com senha"
            print("[INFO] Alternando para fluxo de senha...", flush=True)
            botao_senha = pagina.get_by_role("button", name="Prefiro entrar com senha").first
            if botao_senha.count() == 0:
                botao_senha = pagina.get_by_text("Prefiro entrar com senha").first

            botao_senha.wait_for(state="visible", timeout=15000)
            botao_senha.click()

            # 4. Preenchimento do campo de senha
            senha_input = pagina.get_by_test_id("password").first
            senha_input.wait_for(state="visible", timeout=15000)
            senha_input.fill(senha)

            # Confirma o login definitivo
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            # Valida o login esperando o painel interno
            manager = pagina.locator("[data-testid='entityManager']").first
            manager.wait_for(state="visible", timeout=45000)

            print(f"[OK] Login realizado na tentativa {tentativa}", flush=True)
            return

        except Exception as e:
            print(f"[WARN] Falha tentativa {tentativa}: {e}", flush=True)

            # Geração de logs de debug otimizada para menor consumo de memória
            try:
                timestamp_erro = datetime.now().strftime("%Y%m%d_%H%M%S")
                caminho_print = os.path.join(tempfile.gettempdir(), f"debug_print_{timestamp_erro}.png")
                pagina.screenshot(path=caminho_print, type="jpeg", quality=60) # JPEG consome menos RAM/espaço que PNG
                
                with open(caminho_print, "rb") as f:
                    supabase_client.storage.from_("uploads").upload(
                        path=f"debug/print_{timestamp_erro}.jpeg",
                        file=f,
                        file_options={"content-type": "image/jpeg", "upsert": "true"}
                    )
                if os.path.exists(caminho_print): 
                    os.remove(caminho_print)
            except Exception as erro_debug:
                print(f"[ERROR] Não foi possível extrair mídia de debug: {erro_debug}", flush=True)

            # Limpeza agressiva de estado do navegador em caso de erro
            try:
                pagina.context.clear_cookies()
                pagina.context.clear_permissions()
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

    # Inicialização de variáveis para garantir fechamento correto no 'finally'
    browser = None
    context = None
    
    try:
        with sync_playwright() as p:
            # 1. Argumentos focados em performance extrema (baixa RAM) e evasão silenciosa
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox",
                    "--no-zygote",                  # Evita processos clones órfãos consumindo RAM
                    "--single-process",             # Junta os processos do Chrome em uma única thread (economia drástica de memória em VPS)
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                    "--ignore-certificate-errors"
                ],
            )

            # 2. Contexto limpo sem injeções manuais de JS detectáveis
            context = browser.new_context(
                viewport={"width": 1280, "height": 720}, # Resolução reduzida levemente para poupar memória gráfica simulada
                accept_downloads=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )

            page = context.new_page()
            page.set_default_timeout(45000) # Reduzido de 60s para evitar que processos travados fiquem prendendo a RAM do servidor

            # Executa o fluxo de login
            _fazer_login(page, cpf, senha)

            # Navegação interna do painel
            try:
                page.get_by_test_id("entityManager").click()
                page.get_by_text("Meus Eventos").first.click()
            except:
                page.get_by_role("menuitem", name=re.compile("Meus Eventos", re.IGNORECASE)).click()

            page.locator("p.side-event-title").first.wait_for(state="visible", timeout=30000)
            page.locator("p.side-event-title").first.click()

            evento_locator = page.locator("a.event-list-link", has_text=evento).first
            if evento_locator.count() == 0:
                raise Exception(f"Evento '{evento}' não encontrado na listagem")

            evento_locator.click()
            print(f"[OK] Evento selecionado: {evento}", flush=True)

            # Abas internas do evento
            page.locator("span", has_text="Ingressos").first.click()
            page.get_by_role("link", name="Gerenciar Ingressos").click()

            # Dispara exportação
            page.locator("button", has_text="Exportar").first.click()
            
            botao_download = page.locator("#advance-btn-small-step-alert, button:has-text('Download')").first
            botao_download.wait_for(state="visible", timeout=45000)

            # Coleta do arquivo
            with page.expect_download(timeout=60000) as download_info:
                botao_download.click()

            download = download_info.value
            download.save_as(caminho_temporario)
            print(f"[OK] Download salvo localmente em: {caminho_temporario}", flush=True)

            caminho_storage = f"exports_cheers/{nome_arquivo}"

            # Upload para o Supabase
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
        # Coleta de lixo e encerramento manual e seguro de processos para evitar vazamentos de memória na VPS
        if context:
            try: context.close()
            except: pass
        if browser:
            try: browser.close()
            except: pass
        try:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
        except:
            pass