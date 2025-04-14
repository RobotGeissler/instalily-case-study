from playwright.sync_api import sync_playwright

BRIGHTDATA_USERNAME = "brd-customer-hl_371ce300-zone-case_study_interview"
BRIGHTDATA_PASSWORD = "kgsunydu9d7z"
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
