from langchain.tools import Tool
from playwright.sync_api import sync_playwright
import time, json

def search_and_scrape_part_details(query: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True,
                                        args=["--disable-blink-features=AutomationControlled"])
            page = browser.new_page()
            print(f"\n🔍 Searching for part: {query}")
            page.goto("https://www.partselect.com/", timeout=30000)
            page.locator("#searchboxInput").fill(query)
            page.keyboard.press("Enter")
            
            part_id = ''.join(filter(str.isdigit, query.split()[0]))
            print(f"🔍 Searching for part ID: {part_id}")
            page.wait_for_selector(f"[data-inventory-id='{part_id}']", timeout=10000)

            def safe_text(selector):
                el = page.query_selector(selector)
                return el.inner_text().strip() if el else "Not found"

            def safe_attr(selector, attr):
                el = page.query_selector(selector)
                return el.get_attribute(attr) if el else "Not found"
            
            def safe_texts(selector):
                elements = page.query_selector_all(selector)
                if not elements:
                    return ["Not found"]
                return [el.inner_text().strip() for el in elements]

            def safe_attrs(selector, attr):
                elements = page.query_selector_all(selector)
                if not elements:
                    return ["Not found"]
                return [el.get_attribute(attr) for el in elements]

            troubleshooting = safe_texts("#Troubleshooting ~ div div")
            symptoms_fixed = []
            replaces = []
            compatibility_models = []

            for text in troubleshooting:
                lower = text.lower()

                if "fixes the following symptoms" in lower:
                    symptoms_fixed.extend(text.split(":\n")[-1].split(" | "))

                elif "replaces these" in lower:
                    replaces.extend(text.split(":\n")[-1].split(", "))

                elif "works with the following products" in lower:
                    compatibility_models.extend(text.split(":\n")[-1].split(" | "))

            # Final cleanup
            symptoms_fixed = [s.strip() for s in symptoms_fixed if s.strip()]
            replaces = [r.strip() for r in replaces if r.strip()]
            compatibility_models = [c.strip() for c in compatibility_models if c.strip()]

            result = {
                "url": page.url,
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "part_id": part_id,
                "title": safe_text("h1"),
                "price": safe_text("span.price__currency") + safe_text("span.js-partPrice"),
                "stock": "In Stock" if "in stock" in safe_text('#mainAddToCart [itemprop="availability"]').lower() else "Out of Stock",
                "rating": safe_attr("div.rating .rating__stars__upper", 'style').split(":")[-1]+" - ("+safe_text("span[class*='rating__count']")+")",
                "review_sample": [
                    list(map(lambda s: s.split(":")[-1], 
                             safe_attrs("div#CustomerReviews + div div.js-dataContainer div.rating div.rating__stars__upper", 'style'))),
                    safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.d-md-flex.mt-2.mb-4 div.pd__cust-review__submitted-review__header.mb-2"),
                    safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.bold"),
                    safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.js-searchKeys"),],
                "description": safe_text("#ProductDescription ~ div h2.title-md") + ": " + safe_text("#ProductDescription ~ div div[itemprop='description']"),
                "part_video": list(map(lambda s: "https://www.youtube.com/watch?v=" + s, safe_attrs('#PartVideos + div .yt-video', "data-yt-init"))),
                "symptoms_fixed": symptoms_fixed,
                "replaces": replaces,
                "compatibility_models": compatibility_models,
                # "common_questions": [el.inner_text().strip() for el in page.query_selector_all("#qa .question")]
            }

            browser.close()
            return json.dumps(result, indent=2)

    except Exception as e:
        return f"[Playwright Error] {str(e)}"

search_tool = Tool.from_function(
    name="PartDetailScraper",
    description="Search PartSelect.com for a part number and return structured details like price, stock, rating, symptoms fixed, etc.",
    func=search_and_scrape_part_details,
)
