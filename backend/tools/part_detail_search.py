from langchain.tools import Tool
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re, time, json

def extract_part_ids(text):
    return re.findall(r'PS\d+', text)

def scrape_part_details(page, part_id):
    """Scrape structured info for a single product page once already navigated"""
    def safe_text(selector):
        el = page.query_selector(selector)
        return el.inner_text().strip() if el else "Not found"

    def safe_attr(selector, attr):
        el = page.query_selector(selector)
        return el.get_attribute(attr) if el else "Not found"
    
    def safe_texts(selector):
        return [el.inner_text().strip() for el in page.query_selector_all(selector)] or ["Not found"]

    def safe_attrs(selector, attr):
        return [el.get_attribute(attr) for el in page.query_selector_all(selector)] or ["Not found"]

    troubleshooting = safe_texts("#Troubleshooting ~ div div")
    symptoms, replacements, compatible = [], [], []

    for text in troubleshooting:
        l = text.lower()
        if "fixes the following symptoms" in l:
            symptoms.extend(text.split(":\n")[-1].split(" | "))
        elif "replaces these" in l:
            replacements.extend(text.split(":\n")[-1].split(", "))
        elif "works with the following products" in l:
            compatible.extend(text.split(":\n")[-1].split(" | "))

    return {
        "url": page.url,
        "part_id": part_id,
        "title": safe_text("h1"),
        "price": safe_text("span.price__currency") + safe_text("span.js-partPrice"),
        "stock": "In Stock" if "in stock" in safe_text('#mainAddToCart [itemprop="availability"]').lower() else "Out of Stock",
        "rating": safe_attr("div.rating .rating__stars__upper", 'style').split(":")[-1] + " - (" + safe_text("span[class*='rating__count']") + ")",
        # Fragile selector, may need to be updated if the page structure changes
        "review_sample": [
            safe_attrs("div#CustomerReviews + div div.js-dataContainer div.rating div.rating__stars__upper", 'style'),
            safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.d-md-flex.mt-2.mb-4 div.pd__cust-review__submitted-review__header.mb-2"),
            safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.bold")
        ],
        "description": safe_text("#ProductDescription ~ div h2.title-md") + ": " + safe_text("#ProductDescription ~ div div[itemprop='description']"),
        "part_video": [
            "https://www.youtube.com/watch?v=" + vid_id
            for vid_id in safe_attrs('#PartVideos + div .yt-video', "data-yt-init")
        ],
        "symptoms_fixed": [s.strip() for s in symptoms if s.strip()],
        "replaces": [r.strip() for r in replacements if r.strip()],
        "compatibility_models": [c.strip() for c in compatible if c.strip()],
    }

def search_and_scrape_details(query: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            stealth_sync(page)
            print(f"\n🔍 Searching for query: {query}")
            page.goto("https://www.partselect.com/", timeout=30000)
            page.locator("#searchboxInput").fill(query)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")
            part_ids = extract_part_ids(query)
            results = []

            if not part_ids:
                # No part number in query – pick top result from search
                links = page.eval_on_selector_all("a.nf__part__detail__title", "els => els.map(el => el.href)")
                if not links:
                    return "No product found for query."
                page.goto(links[0])
                part_id = re.search(r'PS\d+', links[0])
                part_id = part_id.group() if part_id else "Unknown"
                results.append(scrape_part_details(page, part_id))
            else:
                for pid in part_ids:
                    try:
                        print(f"🔗 Looking up {pid}")
                        page.goto("https://www.partselect.com/", timeout=30000)
                        page.locator("#searchboxInput").fill(pid)
                        page.keyboard.press("Enter")
                        page.wait_for_selector(f"[data-inventory-id='{pid[2:]}']", timeout=10000)
                        results.append(scrape_part_details(page, pid))
                    except Exception as e:
                        results.append({"part_id": pid, "error": f"Failed to retrieve data: {str(e)}"})

            browser.close()
            return json.dumps(results, indent=2)

    except Exception as e:
        return f"[Playwright Error] {str(e)}"

parts_search_tool = Tool.from_function(
    name="PartDetailScraper",
    description="Use this tool to find and extract structured details about one or more part numbers (e.g., PS123456).",
    func=search_and_scrape_details,
)
