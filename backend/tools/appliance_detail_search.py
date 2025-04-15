from playwright.sync_api import sync_playwright
import json, time, re

def lookup_appliance_model(model: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://www.partselect.com/", timeout=30000)
            page.locator("#searchboxInput").fill(model)
            page.keyboard.press("Enter")
            time.sleep(2)

            # Attempt to extract brand from breadcrumb
            breadcrumb_brand = page.query_selector("li[data-position='3'] a")
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
                    ps_number = div.query_selector("span:has-text('PartSelect #:')")
                    ps_text = ps_number.inner_text().split(":")[-1].strip() if ps_number else ""
                    mf_number = div.query_selector("span:has-text('Manufacturer #:')")
                    mf_text = mf_number.inner_text().split(":")[-1].strip() if mf_number else ""
                    price_currency = div.query_selector("span.price__currency")
                    price_val = div.query_selector("span.js-partPrice")
                    price = f"{price_currency.inner_text()}{price_val.inner_text()}" if price_currency and price_val else "Not found"
                    stock = div.query_selector(".ps-stock")
                    stock_status = stock.inner_text().strip() if stock else "Unknown"

                    compatible_parts.append({
                        "part_url": full_url,
                        "rating": rating.split(":")[-1].strip(),
                        "partselect_number": ps_text,
                        "manufacturer_number": mf_text,
                        "price": price,
                        "stock": stock_status
                    })
                except Exception as e:
                    compatible_parts.append({"error": f"Error parsing part block: {str(e)}"})

            # Try getting symptoms and linked part fixes
            symptom_data = []
            symptom_divs = page.query_selector_all("#Symptoms ~ div a")

            for a in symptom_divs:
                try:
                    descr = a.query_selector("div.symptoms__descr")
                    descr_text = descr.inner_text().strip() if descr else "No description"

                    part_info_div = a.query_selector("div.symptom__parts")
                    part_info_text = part_info_div.inner_text().strip() if part_info_div else ""
                    fixed = "fixed by" in part_info_text.lower() and "these parts" in part_info_text.lower()

                    symptom_data.append({
                        "symptom": descr_text,
                        "fixed": fixed
                    })
                except Exception as e:
                    symptom_data.append({"error": f"Error parsing symptom block: {str(e)}"})

            result = {
                "model": model,
                "brand": brand_name,
                "brand_url": brand_url,
                "model_url": page.url,
                # "compatible_parts": compatible_parts,
                # "symptoms": symptom_data or "None listed"
            }

            browser.close()
            return json.dumps(result, indent=2)

    except Exception as e:
        return f"[Playwright Error] {str(e)}"


if __name__ == "__main__":
    test_model = "WDT780SAEM1"
    print(lookup_appliance_model(test_model))
