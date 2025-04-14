from search import search_tool  # or from your actual file if different

if __name__ == "__main__":
    part_number = "PS11752778"  # You can test with any valid part number
    result = search_tool.run(part_number)
    print("\n🔎 Search Result:\n", result)
