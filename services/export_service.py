import os
import re
import tempfile
import unicodedata
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase import create_client
from supabase_client import supabase as supabase_client

# Inicializa Playwright uma vez para evitar relançar o processo do Chromium em cada export
_playwright = None
_browser = None

def _ensure_browser():
    global _playwright, _browser
    if _browser is not None and _playwright is not None:
        return _playwright, _browser

    _playwright = sync_playwright().start()
    # argumentos reduzem uso de recursos
    _browser = _playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"])
    return _playwright, _browser

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
            pagina.goto("https://cheers.com.br/", wait_until="domcontentloaded")
            
            pagina.locator("#login-btn").click(timeout=8000)
            pagina.locator("#email-input").fill(cpf, timeout=8000)
            
            pagina.locator("form").get_by_role("button", name="Entrar").click(timeout=8000)
            pagina.locator("form").get_by_role("button", name="Prefiro entrar com senha").click(timeout=8000)
            
            pagina.get_by_test_id("password").fill(senha)
            pagina.locator("form").get_by_role("button", name="Entrar").click(timeout=8000)
            
            pagina.get_by_test_id("entityManager").wait_for(state="visible", timeout=15000)
            print("[OK] Login realizado")
            return
        except Exception as e:
            print(f"[WARN] Falha login: {e}")
            pagina.goto("https://cheers.com.br/", wait_until="domcontentloaded")
    
    raise Exception("Login falhou após 3 tentativas")

def _limpar_nome_arquivo(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = texto.replace(' ', '_')
    texto = re.sub(r'[^a-zA-Z0-9_\-\.]', '', texto)
    return texto

def exportar_ingressos(cpf: str, senha: str, evento: str) -> str:
    navegador = None
    nome_limpo = _limpar_nome_arquivo(evento)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{nome_limpo}_{timestamp}.xls"
    
    caminho_temporario_seguro = os.path.join(tempfile.gettempdir(), nome_arquivo)

    try:
        p, navegador = _ensure_browser()
        contexto = navegador.new_context(viewport={"width": 1280, "height": 720}, accept_downloads=True)
        _bloquear_recursos(contexto)
        pagina = contexto.new_page()
        pagina.set_default_timeout(15000)

        _fazer_login(pagina, cpf, senha)

        pagina.get_by_test_id("entityManager").click()
        pagina.get_by_role("menuitem", name="Meus Eventos Minhas Páginas Á").click()
        pagina.locator("p.side-event-title").first.wait_for(state="visible")

        pagina.locator("p.side-event-title").first.click()
        
        elemento_evento = pagina.locator("a.event-list-link", has_text=evento)
        
        try:
            elemento_evento.first.wait_for(state="attached", timeout=5000)
        except:
            pass

        if elemento_evento.count() == 0:
            raise ValueError(f"Evento '{evento}' não foi encontrado na sua conta do Cheers. Verifique o nome digitado.")
        
        elemento_evento.click()
        print(f"[OK] Evento selecionado: {evento}")

        pagina.locator("span", has_text="Ingressos").first.click()
        pagina.get_by_role("link", name="Gerenciar Ingressos").click()
        print("[OK] Tela ingressos aberta")

        pagina.locator("button", has_text="Exportar").click()
        pagina.locator("#advance-btn-small-step-alert").wait_for(state="visible")

        with pagina.expect_download(timeout=60000) as download_info:
            pagina.locator("#advance-btn-small-step-alert").click()

        download = download_info.value
        
        download.save_as(caminho_temporario_seguro)
        print(f"[OK] Arquivo fixado temporariamente em: {caminho_temporario_seguro}")

        # Reutiliza cliente supabase central para reduzir overhead
        supabase = supabase_client
        caminho_storage = f"exports_cheers/{nome_arquivo}"
        with open(caminho_temporario_seguro, "rb") as f:
            supabase.storage.from_("uploads").upload(
                path=caminho_storage,
                file=f,
                file_options={"content-type": "application/vnd.ms-excel", "upsert": "true"},
            )
        print(f"[OK] Arquivo enviado ao Supabase Storage: {caminho_storage}" if 'caminpe_storage' in locals() else f"[OK] Arquivo enviado ao Supabase Storage: {caminho_storage}")
        
        return caminho_storage
    except ValueError as e_aviso:
        print(f"[AVISO] {e_aviso}")
        raise e_aviso
    except Exception as error:
        print(f"[ERROR] Falha na automação: {error}")
        raise error
    finally:
        # fecha contexto apenas; mantém o browser vivo para reuso
        try:
            contexto.close()
        except Exception:
            pass

        if os.path.exists(caminho_temporario_seguro):
            os.remove(caminho_temporario_seguro)
            print("[INFO] Arquivo temporário local deletado.")