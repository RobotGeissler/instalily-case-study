from playwright.sync_api import sync_playwright
import os
### Note to self - was dumb and committed my username and password to the repo. I have removed it now, but if you see this, please remove it from the commit history.
with open(".env", "r") as f:
    for line in f:
        if line.startswith("BRIGHTDATA_USERNAME"):
            BRIGHTDATA_USERNAME = line.split("=")[1].strip()
        elif line.startswith("BRIGHTDATA_PASSWORD"):
            BRIGHTDATA_PASSWORD = line.split("=")[1].strip()
BRIGHTDATA_USERNAME = os.getenv("BRIGHTDATA_USERNAME", BRIGHTDATA_USERNAME)
BRIGHTDATA_PASSWORD = os.getenv("BRIGHTDATA_PASSWORD", BRIGHTDATA_PASSWORD)
PROXY_SERVER = "http://brd.superproxy.io:33335"

def test_proxy():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            proxy={
                "server": PROXY_SERVER,
                "username": BRIGHTDATA_USERNAME,
                "password": BRIGHTDATA_PASSWORD
            },
            headless=False
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.goto("https://geo.brdtest.com/welcome.txt", timeout=60000)
        print("✅ Page title:", page.title())
        print("✅ Body:", page.text_content("body"))
        browser.close()

if __name__ == "__main__":
    test_proxy()
