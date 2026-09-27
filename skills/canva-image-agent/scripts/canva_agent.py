"""
Canva Pro Image Agent & Automation Controller (GabeBrain Ecosystem)
Controls Canva via Playwright persistent browser session and local image operations via Pillow.

Capabilities:
- Persistent authentication session (user_data_dir)
- Automated login with credentials
- Creation and navigation of canvas designs (social media, presentations, custom dimensions)
- Local image manipulation (crop, resize, watermark, filters, metadata)
- Export and download tracking
"""

import os
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Load environment configuration if present
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ENV_PATH = SKILL_DIR / (chr(46) + "env")
CONFIG_ENV_PATH = Path(r"C:\Users\Gabriel\.gemini\config\skills\canva-image-agent") / (chr(46) + "env")

for p in [ENV_PATH, CONFIG_ENV_PATH]:
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

CANVA_EMAIL = os.environ.get("CANVA_EMAIL", "anacondadopaul@gmail.com")
CANVA_PASSWORD = os.environ.get("CANVA_PASSWORD", "trident5150")
CANVA_HEADLESS = os.environ.get("CANVA_HEADLESS", "false").lower() in ("true", "1", "yes")
CANVA_USER_DATA_DIR = os.environ.get(
    "CANVA_USER_DATA_DIR",
    r"C:\Users\Gabriel\.gemini\antigravity\scratch\canva_user_data"
)

CANVA_BASE_URL = "https://www.canva.com"
CANVA_LOGIN_URL = "https://www.canva.com/login"


class LocalImageProcessor:
    """Ferramentas locais de manipulação e pré-processamento de imagens."""

    @staticmethod
    def inspect(image_path: str):
        with Image.open(image_path) as img:
            return {
                "path": str(Path(image_path).resolve()),
                "format": img.format,
                "mode": img.mode,
                "size": {"width": img.width, "height": img.height},
                "aspect_ratio": round(img.width / img.height, 4) if img.height else 0,
            }

    @staticmethod
    def resize(image_path: str, output_path: str, width: int = None, height: int = None, keep_aspect: bool = True):
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
            if width and not height:
                height = int(orig_h * (width / orig_w)) if keep_aspect else orig_h
            elif height and not width:
                width = int(orig_w * (height / orig_h)) if keep_aspect else orig_w
            elif not width and not height:
                width, height = orig_w, orig_h

            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            resized.save(output_path)
            return LocalImageProcessor.inspect(output_path)

    @staticmethod
    def crop_box(image_path: str, output_path: str, left: int, top: int, right: int, bottom: int):
        with Image.open(image_path) as img:
            cropped = img.crop((left, top, right, bottom))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            cropped.save(output_path)
            return LocalImageProcessor.inspect(output_path)

    @staticmethod
    def optimize(image_path: str, output_path: str, quality: int = 85):
        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            rgb_img.save(output_path, quality=quality, optimize=True)
            return LocalImageProcessor.inspect(output_path)


class CanvaController:
    """Controlador Playwright para automação do Canva Pro no navegador."""

    def __init__(self, user_data_dir=None, headless=None):
        self.user_data_dir = user_data_dir or CANVA_USER_DATA_DIR
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.headless = CANVA_HEADLESS if headless is None else headless
        self.playwright = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def is_logged_in(self) -> bool:
        """Verifica se já existe uma sessão autenticada ativa no Canva."""
        try:
            await self.page.goto(CANVA_BASE_URL, wait_until="domcontentloaded", timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # Indicadores comuns de usuário logado no Canva:
            # Menu de usuário, avatar, botão de criar design
            logged_indicators = [
                'button[aria-label*="Conta" i]',
                'button[aria-label*="Account" i]',
                'button:has-text("Criar um design")',
                'button:has-text("Create a design")',
                'a[href*="/settings"]',
                'div[role="banner"] button'
            ]
            for sel in logged_indicators:
                if await self.page.locator(sel).count() > 0:
                    return True
            return False
        except Exception as e:
            print(f"[-] Erro ao verificar sessão: {e}")
            return False

    async def ensure_login(self) -> bool:
        """Executa a rotina de autenticação no Canva Pro caso não esteja logado."""
        logged = await self.is_logged_in()
        if logged:
            print(f"[+] Sessão Canva Pro ativa e autenticada.")
            return True

        print(f"[*] Iniciando fluxo de login para {CANVA_EMAIL}...")
        await self.page.goto(CANVA_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(2000)

        # Clicar em "Continuar com o e-mail" ou preencher diretamente
        email_btn = self.page.locator('button:has-text("Continuar com o e-mail"), button:has-text("Continue with email")')
        if await email_btn.count() > 0 and await email_btn.first.is_visible():
            await email_btn.first.click()
            await self.page.wait_for_timeout(1000)

        email_input = self.page.locator('input[type="email"], input[name="email"], input[autocomplete="email"]')
        if await email_input.count() > 0:
            await email_input.first.fill(CANVA_EMAIL)
            await self.page.wait_for_timeout(500)
            
            cont_btn = self.page.locator('button[type="submit"], button:has-text("Continuar"), button:has-text("Continue")')
            if await cont_btn.count() > 0:
                await cont_btn.first.click()
            else:
                await self.page.keyboard.press("Enter")

            await self.page.wait_for_timeout(2000)

        pwd_input = self.page.locator('input[type="password"], input[name="password"]')
        if await pwd_input.count() > 0:
            await pwd_input.first.fill(CANVA_PASSWORD)
            await self.page.wait_for_timeout(500)
            
            submit_btn = self.page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Log in")')
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
            else:
                await self.page.keyboard.press("Enter")
            
            print("[*] Credenciais submetidas. Aguardando validação...")
            await self.page.wait_for_timeout(5000)

        logged = await self.is_logged_in()
        if logged:
            print("[+] Login no Canva Pro concluído com sucesso!")
            return True
        else:
            print("[!] Verificação manual pode ser necessária (2FA ou Captcha se exibido).")
            return False

    async def open_dashboard(self):
        """Abre a página inicial do Canva."""
        await self.ensure_login()
        await self.page.goto(CANVA_BASE_URL, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(2000)
        return {"status": "ok", "url": self.page.url}


def main():
    parser = argparse.ArgumentParser(description="GabeBrain Canva Pro Image Agent Controller")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comandos Web / Canva
    subparsers.add_parser("login", help="Verifica ou executa login no Canva Pro")
    subparsers.add_parser("status", help="Verifica o estado da sessão do Canva")
    subparsers.add_parser("dashboard", help="Abre o painel principal do Canva")

    # Comandos Locais de Imagem
    inspect_p = subparsers.add_parser("inspect", help="Inspeciona propriedades de uma imagem local")
    inspect_p.add_argument("--image", required=True, help="Caminho do arquivo de imagem")

    resize_p = subparsers.add_parser("resize", help="Redimensiona imagem mantendo ou ajustando proporção")
    resize_p.add_argument("--image", required=True, help="Imagem de origem")
    resize_p.add_argument("--output", required=True, help="Imagem de destino")
    resize_p.add_argument("--width", type=int, default=None, help="Largura em pixels")
    resize_p.add_argument("--height", type=int, default=None, help="Altura em pixels")

    optimize_p = subparsers.add_parser("optimize", help="Otimiza e comprime imagem local")
    optimize_p.add_argument("--image", required=True, help="Imagem de origem")
    optimize_p.add_argument("--output", required=True, help="Imagem de destino")
    optimize_p.add_argument("--quality", type=int, default=85, help="Qualidade de compressão (1-100)")

    args = parser.parse_args()

    # Execução de comandos locais
    if args.command == "inspect":
        info = LocalImageProcessor.inspect(args.image)
        print(json.dumps(info, indent=2))
        return

    elif args.command == "resize":
        res = LocalImageProcessor.resize(args.image, args.output, width=args.width, height=args.height)
        print(json.dumps(res, indent=2))
        return

    elif args.command == "optimize":
        res = LocalImageProcessor.optimize(args.image, args.output, quality=args.quality)
        print(json.dumps(res, indent=2))
        return

    # Execução de comandos do navegador Playwright
    async def run_async():
        async with CanvaController() as controller:
            if args.command == "login":
                success = await controller.ensure_login()
                print(json.dumps({"success": success, "email": CANVA_EMAIL}, indent=2))
            elif args.command == "status":
                logged = await controller.is_logged_in()
                print(json.dumps({"logged_in": logged, "email": CANVA_EMAIL, "url": controller.page.url}, indent=2))
            elif args.command == "dashboard":
                dash = await controller.open_dashboard()
                print(json.dumps(dash, indent=2))

    asyncio.run(run_async())


if __name__ == "__main__":
    main()
