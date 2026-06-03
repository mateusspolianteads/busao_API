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

            # Aguarda um tempo humano para carregamento de scripts assíncronos
            pagina.wait_for_timeout(4000)

            # Detecção de barreira do Cloudflare (Desafio de Verificação)
            conteudo_pagina = pagina.content().lower()
            if "cloudflare" in conteudo_pagina or "just a moment" in conteudo_pagina:
                print("[WARN] Cloudflare detectado na página! Aguardando bypass automático...", flush=True)
                pagina.wait_for_timeout(6000)

            # 1. Clica no botão de Entrar (Mobile/Responsivo conforme o HTML real)
            login_btn = pagina.locator("#login-btn-mobile, #login-btn").first
            login_btn.wait_for(timeout=30000)
            
            # Movimento simulado antes de clicar para quebrar heurísticas de bot
            login_btn.hover()
            pagina.wait_for_timeout(300)
            login_btn.click()

            # 2. Preenche o campo de e-mail/CPF
            email = pagina.locator("#email-input, input[placeholder*='CPF']").first
            email.wait_for(timeout=30000)
            email.focus()
            email.fill(cpf)

            # Avança o primeiro formulário
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.wait_for_timeout(3000)

            # 3. Força o clique em "Prefiro entrar com senha" usando a estrutura do botão real
            print("[INFO] Alternando para fluxo de senha...", flush=True)
            botao_senha = pagina.get_by_role("button", name="Prefiro entrar com senha").first
            
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

            senha_input.focus()
            senha_input.fill(senha)

            # Confirma o login definitivo
            pagina.locator("form").get_by_role("button", name="Entrar").click()

            pagina.wait_for_timeout(4000)

            # Valida se o login deu certo esperando o elemento do painel interno
            manager = pagina.locator("[data-testid='entityManager']").first
            manager.wait_for(timeout=60000)

            print(f"[OK] Login realizado na tentativa {tentativa}", flush=True)
            return

        except Exception as e:
            print(f"[WARN] Falha tentativa {tentativa}: {e}", flush=True)

            # --- SISTEMA DE EXTRAÇÃO DE TAGS E SCREENSHOT PARA DEBUG ---
            try:
                timestamp_erro = datetime.now().strftime("%Y%m%d_%H%M%S")
                html_puro = pagina.content()
                caminho_html = os.path.join(tempfile.gettempdir(), f"debug_tags_{timestamp_erro}.html")
                with open(caminho_html, "w", encoding="utf-8") as f:
                    f.write(html_puro)
                
                caminho_print = os.path.join(tempfile.gettempdir(), f"debug_print_{timestamp_erro}.png")
                pagina.screenshot(path=caminho_print)
                
                with open(caminho_html, "rb") as f:
                    supabase_client.storage.from_("uploads").upload(
                        path=f"debug/tags_{timestamp_erro}.html",
                        file=f,
                        file_options={"content-type": "text/html", "upsert": "true"}
                    )
                
                with open(caminho_print, "rb") as f:
                    supabase_client.storage.from_("uploads").upload(
                        path=f"debug/print_{timestamp_erro}.png",
                        file=f,
                        file_options={"content-type": "image/png", "upsert": "true"}
                    )
                
                print(f"[DEBUG] Tags HTML salvas no Supabase em: debug/tags_{timestamp_erro}.html", flush=True)
                print(f"[DEBUG] Print da tela salvo no Supabase em: debug/print_{timestamp_erro}.png", flush=True)
                
                if os.path.exists(caminho_html): os.remove(caminho_html)
                if os.path.exists(caminho_print): os.remove(caminho_print)
            except Exception as erro_debug:
                print(f"[ERROR] Não foi possível extrair o HTML de debug: {erro_debug}", flush=True)

            try:
                pagina.context.clear_cookies()
                pagina.wait_for_timeout(2000)
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
            # 1. Parâmetros críticos de inicialização do Chromium para Evasão Antibot
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    # Remove a propriedade 'navigator.webdriver' nativa do Chromium
                    "--disable-blink-features=AutomationControlled",
                    # Evita o bloqueio por falta de compartilhamento de janelas virtuais
                    "--disable-infobars",
                    "--ignore-certificate-errors"
                ],
            )

            # 2. Criação do contexto mimetizando perfeitamente uma máquina desktop local e brasileira
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                accept_downloads=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                extra_http_headers={
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive"
                }
            )

            # 3. Scripts de Injeção Avançada (Garante que propriedades do JS não dedurem o Headless no Render)
            context.add_init_script("""
                // Sobrescreve o webdriver para undefined de forma definitiva
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                
                // Força a existência do objeto Chrome falso que os sites usam para checar consistência
                window.chrome = { runtime: {} };
                
                // Mocka lista de plugins comuns para evitar assinaturas vazias comuns em instâncias de nuvem
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                
                // Alinha as linguagens do navegador
                Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            """)

            page = context.new_page()
            page.set_default_timeout(60000)

            # Captura logs de erros de execução internos do próprio site (ajuda a monitorar requisições bloqueadas)
            page.on("pageerror", lambda exc: print(f"[BROWSER EXCEPTION] {exc}", flush=True))
            page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.text}" if msg.type == "error" else "", end="", flush=True))

            # Executa o fluxo de login camuflado
            _fazer_login(page, cpf, senha)

            # Acessa o menu lateral de eventos de forma resiliente
            try:
                page.get_by_test_id("entityManager").click()
                page.get_by_text("Meus Eventos").first.click()
            except:
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
            
            # Aguarda o botão final de download
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