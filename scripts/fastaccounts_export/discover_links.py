"""Discover FastAccounts module URLs from logged-in sidebar."""
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).parent / ".env")
BASE = "https://my.fastaccounts.io"

links: list[dict] = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(BASE + "/", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)
    page.wait_for_selector('input[type="email"], input[name="email"]', timeout=60000)
    page.locator('input[type="email"], input[name="email"]').first.fill(os.environ["FA_EMAIL"])
    page.locator('input[type="password"]').first.fill(os.environ["FA_PASSWORD"])
    page.locator('button:has-text("LOGIN")').first.click()
    page.wait_for_timeout(5000)
    print("URL after login:", page.url)
    if "companies" in page.url:
        page.wait_for_selector("table tbody tr", timeout=30000)
        cid = page.evaluate("""() => {
            const html = document.documentElement.innerHTML;
            const m = html.match(/chooseCompany\\('(\\d+)'\\)/);
            return m ? m[1] : null;
        }""")
        if cid:
            page.evaluate(f"chooseCompany('{cid}')")
            page.wait_for_timeout(8000)
    # collect all internal links
    hrefs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href]'))
            .map(a => ({ text: (a.innerText||'').trim().replace(/\\s+/g,' '), href: a.href }))
            .filter(x => x.href.includes('my.fastaccounts.io') && x.text.length > 0 && x.text.length < 60);
    }""")
    links.extend(hrefs)
    # hover sidebar icons to reveal submenus
    for icon in page.locator('.sidebar-nav li, .sidebar-menu li, nav li').all()[:20]:
        try:
            icon.hover(timeout=1000)
            page.wait_for_timeout(300)
        except Exception:
            pass
    hrefs2 = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href]'))
            .map(a => ({ text: (a.innerText||'').trim().replace(/\\s+/g,' '), href: a.href }))
            .filter(x => x.href.includes('my.fastaccounts.io/index.php') && x.text.length > 0);
    }""")
    links.extend(hrefs2)
    browser.close()

seen = set()
unique = []
for item in links:
    key = (item["text"].lower(), item["href"])
    if key not in seen:
        seen.add(key)
        unique.append(item)

out = Path(__file__).parent / "output" / "discovered_links.json"
out.write_text(json.dumps(unique, indent=2), encoding="utf-8")
print(f"Found {len(unique)} links -> {out}")
for u in sorted(unique, key=lambda x: x["text"])[:80]:
    path = u["href"].replace(BASE + "/", "")
    print(f"  {u['text'][:40]:40} {path}")
