from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json, time

CATEGORY_URLS = {
    "Refrigerator": "https://www.partselect.com/Refrigerator-Parts.htm",
    "Dishwasher": "https://www.partselect.com/Dishwasher-Parts.htm"
}

BRIGHTDATA_USERNAME = "brd-customer-hl_371ce300-zone-case_study_interview"
BRIGHTDATA_PASSWORD = "kgsunydu9d7z"
PROXY_SERVER = "http://brd.superproxy.io:33335"

def scrape_part_links():
    all_product_links = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            proxy={
                "server": PROXY_SERVER,
                "username": BRIGHTDATA_USERNAME,
                "password": BRIGHTDATA_PASSWORD,
            },
            headless=False
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        stealth_sync(page)
        for name, category_url in CATEGORY_URLS.items():
            print(f"🔍 Scraping {name} category from {category_url}")
            page.goto(category_url, timeout=60000)
            time.sleep(1.5)

            subcategory_links = page.eval_on_selector_all(
                "ul.nf__links li a",
                "els => els.map(el => el.href)"
            )
            print(f"📦 Found {len(subcategory_links)} subcategories in {name}")

            for sub_url in subcategory_links:
                print(f"  🔗 Visiting subcategory: {sub_url}")
                page.goto(sub_url)
                time.sleep(1)

                while True:
                    links = page.eval_on_selector_all(
                        "a.nf__part__detail__title",
                        "els => els.map(el => el.href)"
                    )
                    print(f"    ➕ Found {len(links)} product links on page.")
                    all_product_links.update(links)

                    next_button = page.query_selector("a.pagination__next")
                    if not next_button or "disabled" in (next_button.get_attribute("class") or ""):
                        break
                    next_button.click()
                    time.sleep(1.5)

        browser.close()
    return list(all_product_links)

if __name__ == "__main__":
    links = scrape_part_links()
    print(f"\n✅ Total unique product links collected: {len(links)}")
    with open("../all_product_links.json", "w") as f:
        json.dump(links, f, indent=2)
    print("💾 Saved product links to all_product_links.json")
