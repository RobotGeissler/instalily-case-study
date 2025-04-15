import asyncio
import json
import re
from urllib.parse import quote_plus
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from langchain.tools import Tool
from tools.asyncsearch import search_and_scrape_details_async  # assuming same directory structure

async def general_part_search(query: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            page = await context.new_page()

            await stealth_async(page)

            print(f"\n🔍 Performing general search: {query}")

            def build_facet_url(query: str) -> str:
                base_url = "https://www.partselect.com/facetsearch/"
                query_parts = query.split()
                brand = query_parts[0] if len(query_parts) > 0 else ""
                modeltype = "Refrigerator" if "fridge" in query else "Dishwasher"
                parttype = " ".join(query_parts[2:])
                params = f"?brand={quote_plus(brand)}&modeltype={quote_plus(modeltype)}&parttype={quote_plus(parttype)}"
                return base_url + params

            search_url = build_facet_url(query)
            print(f"🔗 Building facet URL: {search_url}")
            await page.goto(search_url, timeout=30000)
            await page.wait_for_load_state("networkidle")

            try:
                part_links = await page.query_selector_all("div.smart-search__parts a")
                if not part_links:
                    return "No results found."

                first_part_url = await part_links[0].get_attribute("href")
                if not first_part_url:
                    return "No valid part link found."

                full_url = f"https://www.partselect.com{first_part_url}"
                print(f"🔗 Navigating to first part URL: {full_url}")

                part_id_match = re.search(r'PS\d+', full_url)
                part_id = part_id_match.group() if part_id_match else "Unknown"
                print(f"🔍 Extracted part ID: {part_id}")

                return await search_and_scrape_details_async(part_id)

            except Exception as e:
                return f"[Playwright Error - General Search] {str(e)}"
            finally:
                await browser.close()

    except Exception as e:
        return f"[Playwright Init Error] {str(e)}"
    
# inside general_search_tool wrapper
async def general_search_wrapper(input_str: str) -> str:
    if "PS" in input_str.upper() or re.match(r"\b[A-Z]{3,}\d{3,}\b", input_str):  # crude model match
        return "❌ General search not used for part numbers or model numbers. Please use another tool."
    return await general_part_search(input_str)

    
from langchain_core.tools import tool

@tool
async def brand_appliance_product_search_tool(query: str) -> str:
    """Use this tool to search PartSelect for a part based on a natural language query if no part number is given."""
    return await general_search_wrapper(query)


if __name__ == "__main__":
    result = asyncio.run(general_part_search("Whirlpool fridge ice maker"))
    print(result)