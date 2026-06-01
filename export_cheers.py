from playwright.sync_api import sync_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

CPF = "044.660.179.99"
SENHA = "@Minhavida123"
EVENTO = "Pré carnaval BBO"


def bloquear_recursos(contexto):
    def handler(route):
        if route.request.resource_type in ["image", "media", "font"]:
            route.abort()
        else:
            route.continue_()

    contexto.route("**/*", handler)


def fazer_login(pagina, CPF, SENHA):

    for tentativa in range(3):
        try:
            print(f"[INFO] Tentativa login {tentativa + 1}")

            pagina.goto("https://cheers.com.br/", wait_until="domcontentloaded")

            pagina.locator("#login-btn").click(timeout=8000)

            pagina.locator("#email-input").fill(CPF, timeout=8000)

            pagina.locator("form").get_by_role(
                "button",
                name="Entrar"
            ).click(timeout=8000)

            pagina.locator("form").get_by_role(
                "button",
                name="Prefiro entrar com senha"
            ).click(timeout=8000)

            pagina.get_by_test_id("password").fill(SENHA)

            pagina.locator("form").get_by_role(
                "button",
                name="Entrar"
            ).click(timeout=8000)

            pagina.get_by_test_id("entityManager").wait_for(
                state="visible",
                timeout=15000
            )

            print("[OK] Login realizado")
            return

        except Exception as e:
            print(f"[WARN] Falha login: {e}")
            pagina.goto("https://cheers.com.br/", wait_until="domcontentloaded")

    raise Exception("Login falhou após 3 tentativas")


with sync_playwright() as p:

    navegador = p.chromium.launch(
        headless=True,
        args=["--start-maximized"]
    )

    contexto = navegador.new_context(
        viewport={"width": 1280, "height": 720},
        accept_downloads=True
    )

    bloquear_recursos(contexto)

    pagina = contexto.new_page()

    pagina.set_default_timeout(15000)

    # ==========================
    # LOGIN
    # ==========================
    fazer_login(pagina, CPF, SENHA)

    # ==========================
    # GERENCIAR
    # ==========================
    pagina.get_by_test_id("entityManager").click()

    pagina.get_by_role(
        "menuitem",
        name="Meus Eventos Minhas Páginas Á"
    ).click()

    pagina.locator("p.side-event-title").first.wait_for(state="visible")

    # ==========================
    # EVENTO
    # ==========================
    pagina.locator("p.side-event-title").first.click()

    pagina.locator(
        "a.event-list-link",
        has_text=EVENTO
    ).click()

    print(f"[OK] Evento selecionado: {EVENTO}")

    # ==========================
    # INGRESSOS
    # ==========================
    pagina.locator("span", has_text="Ingressos").first.click()

    pagina.get_by_role("link", name="Gerenciar Ingressos").click()

    print("[OK] Tela ingressos aberta")

    # ==========================
    # EXPORTAR
    # ==========================
    pagina.locator("button", has_text="Exportar").click()

    pagina.locator("#advance-btn-small-step-alert").wait_for(state="visible")

    # ==========================
    # DOWNLOAD
    # ==========================
    with pagina.expect_download() as download_info:
        pagina.locator("#advance-btn-small-step-alert").click()

    download = download_info.value

    nome_arquivo = f"{EVENTO}.xls"
    download.save_as(nome_arquivo)

    print(f"[OK] Arquivo salvo: {nome_arquivo}")

    navegador.close()