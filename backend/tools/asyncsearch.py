from langchain.tools import Tool
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import re, json, asyncio

def extract_part_ids(text):
    return re.findall(r'PS\d+', text)

async def scrape_part_details(page, part_id):
    async def safe_text(selector):
        el = await page.query_selector(selector)
        return (await el.inner_text()).strip() if el else "Not found"

    async def safe_attr(selector, attr):
        el = await page.query_selector(selector)
        return await el.get_attribute(attr) if el else "Not found"

    async def safe_texts(selector):
        els = await page.query_selector_all(selector)
        return [await el.inner_text() for el in els] or ["Not found"]

    async def safe_attrs(selector, attr):
        els = await page.query_selector_all(selector)
        return [await el.get_attribute(attr) for el in els] or ["Not found"]

    troubleshooting = await safe_texts("#Troubleshooting ~ div div")
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
        "title": await safe_text("h1"),
        "price": (await safe_text("span.price__currency")) + (await safe_text("span.js-partPrice")),
        "stock": "In Stock" if "in stock" in (await safe_text('#mainAddToCart [itemprop="availability"]')).lower() else "Out of Stock",
        "rating": (await safe_attr("div.rating .rating__stars__upper", 'style')).split(":")[-1] + " - (" + (await safe_text("span[class*='rating__count']")) + ")",
        "review_sample": [
            await safe_attrs("div#CustomerReviews + div div.js-dataContainer div.rating div.rating__stars__upper", 'style'),
            await safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.d-md-flex.mt-2.mb-4 div.pd__cust-review__submitted-review__header.mb-2"),
            await safe_texts("div#CustomerReviews ~ div div.js-dataContainer div.bold")
        ],
        "description": (await safe_text("#ProductDescription ~ div h2.title-md")) + ": " + (await safe_text("#ProductDescription ~ div div[itemprop='description']")),
        "part_video": [
            "https://www.youtube.com/watch?v=" + vid_id
            for vid_id in await safe_attrs('#PartVideos + div .yt-video', "data-yt-init")
        ],
        "symptoms_fixed": [s.strip() for s in symptoms if s.strip()],
        "replaces": [r.strip() for r in replacements if r.strip()],
        "compatibility_models": [c.strip() for c in compatible if c.strip()],
    }

async def search_and_scrape_details_async(query: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await stealth_async(page)
            print(f"\n🔍 Searching for query: {query}")
            await page.goto("https://www.partselect.com/", timeout=30000)
            await page.locator("#searchboxInput").fill(query)
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")

            part_ids = extract_part_ids(query)
            results = []

            if not part_ids:
                links = await page.eval_on_selector_all("a.nf__part__detail__title", "els => els.map(el => el.href)")
                if not links:
                    return "No product found for query."
                await page.goto(links[0])
                part_id_match = re.search(r'PS\d+', links[0])
                part_id = part_id_match.group() if part_id_match else "Unknown"
                results.append(await scrape_part_details(page, part_id))
            else:
                for pid in part_ids:
                    try:
                        print(f"🔗 Looking up {pid}")
                        await page.goto("https://www.partselect.com/", timeout=30000)
                        await page.locator("#searchboxInput").fill(pid)
                        await page.keyboard.press("Enter")
                        await page.wait_for_selector(f"[data-inventory-id='{pid[2:]}']", timeout=10000)
                        results.append(await scrape_part_details(page, pid))
                    except Exception as e:
                        results.append({"part_id": pid, "error": f"Failed to retrieve data: {str(e)}"})

            await browser.close()
            return json.dumps(results, indent=2)

    except Exception as e:
        return f"[Playwright Error] {str(e)}"

parts_search_tool_async = Tool.from_function(
    name="PartDetailScraper",
    description="Use this tool to find and extract structured details about one or more part numbers (e.g., PS123456).",
    func=lambda query: asyncio.run(search_and_scrape_details_async(query)),
)