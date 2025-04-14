import os

### Just a dummy script to generate some text files for testing purposes ###

DATA_DIR = "./data/refrigerator-manuals"
os.makedirs(DATA_DIR, exist_ok=True)

docs = {
    "ps11752778.txt": """\
Part Number: PS11752778
Part Name: Ice Maker Assembly

Compatibility:
- Whirlpool WDT780SAEM1
- Whirlpool WRX735SDBM00
- Maytag MDB8959SFZ4

Installation Instructions:
1. Disconnect power and water supply.
2. Remove the ice bin and the mounting screws.
3. Detach the old assembly and plug in the new one.
4. Reinstall screws and test the new ice maker.
""",

    "troubleshooting-guide.txt": """\
Issue: Refrigerator not cooling properly

Steps to Diagnose:
1. Check if condenser coils are dirty.
2. Make sure the evaporator fan is running.
3. Verify temperature settings.
4. Test the start relay and capacitor.

Common Fixes:
- Clean coils
- Replace start relay
- Reset control board
""",

    "wdt780saem1.txt": """\
Model: Whirlpool Dishwasher WDT780SAEM1

Common Parts:
- PS11752778 (Ice Maker Assembly)
- PS5136123 (Spray Arm)
- PS389221 (Water Inlet Valve)

Tip: For compatibility, always cross-check the part number on your existing component or refer to the model label inside the door panel.
"""
}

for filename, content in docs.items():
    with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip())

print(f"✅ Dummy documents written to: {DATA_DIR}")
