from playwright.sync_api import sync_playwright
from langchain.tools import Tool
import json, time, re

def lookup_appliance_model(model: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://www.partselect.com/", timeout=30000)
            page.locator("#searchboxInput").fill(model)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")

            # Attempt to extract brand from breadcrumb
            breadcrumb_brand = page.query_selector("header div.container.extended li a[data-position='3']")
            brand_name = breadcrumb_brand.inner_text().strip() if breadcrumb_brand else "Unknown"
            brand_href = breadcrumb_brand.get_attribute("href") if breadcrumb_brand else None
            brand_url = f"https://www.partselect.com{brand_href}" if brand_href else None

            # Locate compatible parts section
            parts_container = page.query_selector("#Parts ~ div ~ div")  # 2nd sibling after #Parts
            part_divs = parts_container.query_selector_all("div.col-md-6.mb-3") if parts_container else []

            compatible_parts = []
            for div in part_divs:
                try:
                    link_el = div.query_selector("a")
                    part_url = link_el.get_attribute("href") if link_el else ""
                    full_url = f"https://www.partselect.com{part_url}" if part_url else ""
                    rating_style = div.query_selector("div.rating__stars__upper")
                    rating = rating_style.get_attribute("style") if rating_style else "Not found"
                    ps_number = div.query_selector("div div div div:has-text('PartSelect #:')")
                    ps_text = ps_number.inner_text().split(":")[-1].strip() if ps_number else ""
                    mf_number = div.query_selector("div div div div:has-text('Manufacturer #:')")
                    mf_text = mf_number.inner_text().split(":")[-1].strip() if mf_number else ""
                    # This is kind of a hack, but it works for now
                    descr = div.query_selector("div div div")
                    descr = descr.inner_text().split(":")[-1].split("\n")[1].strip() if mf_number else ""
                    price_div = div.query_selector("div.mega-m__part__price")
                    price = price_div.inner_text().strip() if price_div else "Not found"
                    stock = div.query_selector("div.mega-m__part__avlbl")
                    stock_status = stock.inner_text().strip() if stock else "Unknown"

                    compatible_parts.append({
                        "part_url": full_url,
                        "rating": rating.split(":")[-1].strip(),
                        "partselect_number": ps_text,
                        "manufacturer_number": mf_text,
                        "description": descr,
                        "price": price,
                        "stock": stock_status
                    })
                except Exception as e:
                    compatible_parts.append({"error": f"Error parsing part block: {str(e)}"})

            # Try getting symptoms and linked part fixes
            symptom_data = []
            symptom_divs = page.query_selector_all("#Symptoms ~ div a.symptoms")

            for a in symptom_divs:
                try:
                    # print(a.inner_text())
                    descr = a.query_selector("div.symptoms__descr")
                    descr_text = descr.inner_text().strip() if descr else "No description"

                    part_info_div = a.query_selector("div.symptoms__parts div")
                    part_info_text = part_info_div.inner_text().strip() if part_info_div else ""
                    fixed = "fixed by" in part_info_text.lower() and "these parts" in part_info_text.lower()

                    symptom_data.append({
                        "symptom": descr_text,
                        "fixed": fixed
                    })
                except Exception as e:
                    symptom_data.append({"error": f"Error parsing symptom block: {str(e)}"})

            # Try getting videos
            video_data = []
            video_container = page.query_selector("#Videos + div.row.mega-m__videos")
            # > div is used to select direct children only - this avoids hidden elements
            video_divs = video_container.query_selector_all("> div") if video_container else []

            for div in video_divs:
                try:
                    video_link = div.query_selector("div.yt-video")
                    video_url = video_link.get_attribute("data-yt-init") if video_link else ""
                    video_text = div.query_selector("h3")
                    video_title = video_text.inner_text().strip() if video_link else "No title"
                    video_data.append({
                        "video_title": video_title,
                        "video_url": f"https://www.youtube.com/watch?v={video_url}" if video_url else "Not found"
                    })
                except Exception as e:
                    video_data.append({"error": f"Error parsing video block: {str(e)}"})

            # Repair stories
            repair_story_data = []
            repair_story_container = page.query_selector("#main")

            for div in repair_story_container.query_selector_all("div.repair-story"):
                try:
                    story_title = div.query_selector("a.repair-story__title")
                    story_title_text = story_title.inner_text().strip() if story_title else "No title"
                    story_link = div.query_selector("div.repair-story__parts a")
                    story_url = "https://www.partselect.com" + story_link.get_attribute("href") if story_link else ""
                    story_text = div.inner_text().strip() if story_link else "No title"
                    story_text = " \n ".join(story_text.split("\n")[:-1]) if story_text else "No title"
                    repair_story_data.append({
                        "story_title": story_title_text,
                        "story_url": story_url,
                        "story_text": story_text
                    })
                except Exception as e:
                    repair_story_data.append({"error": f"Error parsing repair story block: {str(e)}"})

            result = {
                "model": model,
                "brand": brand_name,
                "brand_url": brand_url,
                "model_url": page.url,
                "videos": video_data,
                "compatible_parts": compatible_parts,
                "symptoms": symptom_data or "None listed",
                "repair_stories": repair_story_data or "None listed"
            }

            browser.close()
            return json.dumps(result, indent=2)

    except Exception as e:
        return f"[Playwright Error] {str(e)}"


appliance_search_tool = Tool.from_function(
    func=lookup_appliance_model,
    name="appliance_search_tool",
    description="Searches for appliance model details on PartSelect. Returns a JSON string with model details."
)

if __name__ == "__main__":
    test_model = "WDT780SAEM1"
    print(lookup_appliance_model(test_model))
