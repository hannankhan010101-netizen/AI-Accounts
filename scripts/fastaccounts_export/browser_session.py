"""Playwright browser session: login, navigation, cookie capture."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from modules_manifest import ModuleDef

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    base_url: str
    email: str
    password: str
    headless: bool = True
    nav_timeout_ms: int = 60_000
    page_delay_ms: int = 300


@dataclass
class BrowserSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    config: SessionConfig
    auth_tokens: dict[str, str] = field(default_factory=dict)

    def close(self) -> None:
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def cookies_as_dict(self) -> dict[str, str]:
        return {c["name"]: c["value"] for c in self.context.cookies()}

    def wait_settle(self) -> None:
        self.page.wait_for_timeout(self.config.page_delay_ms)
        try:
            self.page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass


def create_session(config: SessionConfig) -> BrowserSession:
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=config.headless)
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    )
    context.set_default_timeout(config.nav_timeout_ms)
    page = context.new_page()
    return BrowserSession(playwright=pw, browser=browser, context=context, page=page, config=config)


def _fill_login_form(page: Page, email: str, password: str) -> None:
    """Fill email/password on FastAccounts login page."""
    email_selectors = [
        'input[type="email"]',
        'input[name="email"]',
        'input[name="Email"]',
        'input[id*="email" i]',
        'input[placeholder*="email" i]',
    ]
    password_selectors = [
        'input[type="password"]',
        'input[name="password"]',
        'input[name="Password"]',
    ]

    email_el = None
    for sel in email_selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            email_el = loc
            break
    if email_el is None:
        raise RuntimeError("Could not find email input on login page")

    pwd_el = None
    for sel in password_selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            pwd_el = loc
            break
    if pwd_el is None:
        raise RuntimeError("Could not find password input on login page")

    email_el.fill(email)
    pwd_el.fill(password)

    submit_selectors = [
        'button:has-text("LOGIN")',
        'button:has-text("Login")',
        'input[type="submit"]',
        'button[type="submit"]',
    ]
    for sel in submit_selectors:
        btn = page.locator(sel).first
        if btn.count() > 0 and btn.is_visible():
            btn.click()
            return
    page.keyboard.press("Enter")


def select_company_if_needed(page: Page) -> None:
    """Select first company when on /main/companies picker."""
    if "companies" not in page.url:
        return

    company_id = page.evaluate("""() => {
        const html = document.documentElement.innerHTML;
        const m = html.match(/chooseCompany\\('(\\d+)'\\)/);
        return m ? m[1] : null;
    }""")
    if company_id:
        page.evaluate(f"chooseCompany('{company_id}')")
        page.wait_for_timeout(6000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        logger.info("Selected company %s -> %s", company_id, page.url)
        return

    for sel in ["table tbody tr td:nth-child(2)", "table tbody tr"]:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0:
                loc.click(timeout=5000)
                page.wait_for_timeout(6000)
                logger.info("Selected company via %s -> %s", sel, page.url)
                return
        except Exception:
            continue
    logger.warning("Could not select company on %s", page.url)


def login(session: BrowserSession) -> None:
    """Navigate to base URL and authenticate."""
    page = session.page
    cfg = session.config
    url = cfg.base_url.rstrip("/") + "/"
    logger.info("Navigating to %s", url)
    page.goto(url, wait_until="networkidle", timeout=cfg.nav_timeout_ms)
    page.wait_for_timeout(1500)
    email_sel = 'input[type="email"], input[name="email"], input[name="Email"], input[id*="email" i]'
    try:
        page.wait_for_selector(email_sel, timeout=cfg.nav_timeout_ms)
    except Exception:
        pass

    _fill_login_form(page, cfg.email, cfg.password)
    page.wait_for_timeout(1500)

    # Confirm dialog if present
    try:
        confirm = page.locator('button:has-text("Confirm"), .modal button:has-text("Confirm")').first
        if confirm.count() > 0 and confirm.is_visible(timeout=2000):
            confirm.click()
    except Exception:
        pass

    _wait_for_app_shell(page, cfg.nav_timeout_ms)
    select_company_if_needed(page)
    _wait_for_app_shell(page, cfg.nav_timeout_ms)
    logger.info("Login successful — app shell detected at %s", page.url)


def _wait_for_app_shell(page: Page, timeout_ms: int) -> None:
    """Wait until post-login UI is visible."""
    markers = [
        "text=Dashboard",
        "text=Bank",
        "text=Sales",
        "text=Purchases",
        ".sidebar",
        "#sidebar",
        '[class*="sidebar"]',
        '[class*="SideBar"]',
        "nav",
    ]
    last_err: Exception | None = None
    for marker in markers:
        try:
            page.wait_for_selector(marker, timeout=timeout_ms // len(markers) + 5000)
            return
        except Exception as exc:
            last_err = exc

    if "login" in page.url.lower() and page.locator('input[type="password"]').count() > 0:
        raise RuntimeError("Login failed — still on login page. Check credentials.")
    if last_err:
        logger.warning("App shell markers not found; continuing at %s", page.url)


def _expand_sidebar_group(page: Page, group_label: str) -> None:
    """Expand a collapsible sidebar group if needed."""
    patterns = [
        f'.sidebar-nav >> text="{group_label}"',
        f'.sidebar >> text="{group_label}"',
        f'nav >> text="{group_label}"',
        f'[class*="sidebar"] >> text="{group_label}"',
        f'a:has-text("{group_label}")',
    ]
    for pat in patterns:
        loc = page.locator(pat).first
        if loc.count() == 0:
            continue
        try:
            if loc.is_visible(timeout=2000):
                loc.click()
                page.wait_for_timeout(400)
                return
        except Exception:
            continue


def _click_nav_item(page: Page, label: str) -> bool:
    """Click a navigation link by visible text."""
    selectors = [
        f'.sidebar-nav a:has-text("{label}")',
        f'.sidebar-menu a:has-text("{label}")',
        f'nav a:has-text("{label}")',
        f'.sidebar a:has-text("{label}")',
        f'[class*="sidebar"] a:has-text("{label}")',
        f'a:text-is("{label}")',
        f'li >> a:has-text("{label}")',
    ]
    for sel in selectors:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=2000):
                loc.click()
                return True
        except Exception:
            continue
    return False


def navigate_to_module(session: BrowserSession, module: ModuleDef) -> str:
    """Navigate to module via direct URL (preferred) or sidebar/settings."""
    page = session.page
    cfg = session.config

    if module.direct_path:
        url = cfg.base_url.rstrip("/") + "/" + module.direct_path.lstrip("/")
        logger.info("Navigating directly to %s", url)
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=cfg.nav_timeout_ms)
                session.wait_settle()
                return page.url
            except Exception as exc:
                last_err = exc
                logger.warning("Navigation attempt %d failed for %s: %s", attempt + 1, module.key, exc)
                page.wait_for_timeout(3000)
        raise last_err or RuntimeError(f"Navigation failed for {module.key}")

    path = module.path
    if module.category == "settings":
        open_settings_menu(session)
        _click_nav_item(page, path[0])
    elif len(path) == 1:
        _click_nav_item(page, path[0])
    else:
        _expand_sidebar_group(page, path[0])
        page.wait_for_timeout(400)
        if not _click_nav_item(page, path[1]):
            page.locator(f'a:has-text("{path[1]}")').first.click(timeout=8000, force=True)

    session.wait_settle()
    return page.url


def open_settings_menu(session: BrowserSession) -> None:
    """Open the Settings mega-menu overlay."""
    page = session.page
    gear_selectors = [
        '[title*="Settings" i]',
        '[aria-label*="Settings" i]',
        'i.fa-cog',
        'i.fa-gear',
        '.fa-cogs',
        'button:has-text("Settings")',
        '[class*="settings"]',
        'text=Settings >> nth=0',
    ]
    for sel in gear_selectors:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=1500):
                loc.click()
                page.wait_for_timeout(500)
                return
        except Exception:
            continue
    # Fallback: try header user menu
    for sel in ['[class*="user"]', '[class*="profile"]', '.dropdown-toggle']:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=1000):
                loc.click()
                page.wait_for_timeout(300)
                if _click_nav_item(page, "Settings"):
                    return
        except Exception:
            continue
    logger.warning("Could not open Settings menu — attempting direct link click")


def discover_sidebar_links(session: BrowserSession) -> list[dict[str, Any]]:
    """Collect visible sidebar link texts not in manifest."""
    page = session.page
    links: list[dict[str, Any]] = []
    for sel in ['nav a', '.sidebar a', '[class*="sidebar"] a']:
        for el in page.locator(sel).all():
            try:
                text = (el.inner_text() or "").strip()
                href = el.get_attribute("href") or ""
                if text and len(text) < 80:
                    links.append({"text": text, "href": href})
            except Exception:
                continue
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in links:
        key = item["text"]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def capture_auth_from_response(session: BrowserSession, url: str, body: Any) -> None:
    """Extract auth tokens from JSON responses when present."""
    if not isinstance(body, dict):
        return
    for key in ("ApiToken", "apiToken", "token", "accessToken", "access_token"):
        val = body.get(key)
        if isinstance(val, str) and val:
            session.auth_tokens[key] = val
