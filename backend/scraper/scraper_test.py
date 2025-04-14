from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # or .firefox or .webkit
        context = browser.new_context()
        page = context.new_page()

        # Go to homepage
        page.goto("https://www.partselect.com/", timeout=60000)
        print("✅ Page loaded:", page.title())

        # Try to close popup if it appears
        try:
            page.wait_for_selector("#bx-close-inside-2905053", timeout=5000)
            page.click("#bx-close-inside-2905053")
            print("✅ Modal closed")
        except:
            print("⚠️ No modal found, continuing...")

        # Interact with search box
        try:
            page.fill("#searchboxInput", "5304506516")
            page.press("#searchboxInput", "Enter")
            print("✅ Search submitted")
        except Exception as e:
            print("❌ Could not search:", e)

        # Optional: Wait to view results
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    run()
