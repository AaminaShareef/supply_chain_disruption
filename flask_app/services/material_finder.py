# flask_app/services/material_finder.py
# Identifies raw materials needed by a manufacturer.
# Layer 1 — checks lookup dictionary first (instant, free)
# Layer 2 — uses OpenRouter LLaMA if not found (free AI)

import os
import json
import requests

# --- Layer 1: Common manufacturer lookup dictionary ---
MATERIAL_LOOKUP = {
    # Metals and Mining
    'gold manufacturer':        ['gold ore', 'mercury', 'cyanide', 'copper', 'silver', 'energy', 'mining equipment'],
    'silver manufacturer':      ['silver ore', 'copper', 'lead', 'zinc', 'energy', 'mining equipment'],
    'steel manufacturer':       ['iron ore', 'coal', 'limestone', 'scrap metal', 'energy', 'manganese'],
    'aluminium manufacturer':   ['bauxite', 'alumina', 'energy', 'caustic soda', 'cryolite'],
    'copper manufacturer':      ['copper ore', 'sulfuric acid', 'energy', 'molybdenum', 'gold'],

    # Electronics
    'semiconductor manufacturer': ['silicon', 'rare earth metals', 'chemicals', 'water', 'energy', 'photoresist'],
    'battery manufacturer':     ['lithium', 'cobalt', 'nickel', 'manganese', 'graphite', 'electrolyte'],
    'electronics manufacturer': ['copper', 'silicon', 'rare earth metals', 'plastic', 'energy'],

    # Automotive
    'car manufacturer':         ['steel', 'aluminium', 'lithium', 'rubber', 'plastic', 'glass', 'copper'],
    'electric vehicle manufacturer': ['lithium', 'cobalt', 'nickel', 'steel', 'aluminium', 'copper'],

    # Pharma
    'pharmaceutical manufacturer': ['active ingredients', 'glass', 'packaging', 'cold chain', 'chemicals'],
    'vaccine manufacturer':     ['biological materials', 'glass vials', 'cold chain', 'adjuvants', 'packaging'],

    # Food
    'food manufacturer':        ['wheat', 'sugar', 'palm oil', 'packaging', 'energy', 'water'],
    'chocolate manufacturer':   ['cocoa', 'sugar', 'milk', 'palm oil', 'packaging', 'energy'],

    # Textiles
    'textile manufacturer':     ['cotton', 'polyester', 'dyes', 'water', 'energy', 'packaging'],
    'clothing manufacturer':    ['cotton', 'polyester', 'wool', 'dyes', 'packaging', 'energy'],

    # Energy
    'solar panel manufacturer': ['silicon', 'silver', 'aluminium', 'glass', 'copper', 'rare earth metals'],
    'wind turbine manufacturer':['steel', 'aluminium', 'copper', 'rare earth metals', 'fibreglass', 'energy'],
}


def find_materials_from_lookup(manufacturer: str) -> list:
    """
    Checks the lookup dictionary for known manufacturers.
    Returns materials if found, empty list if not.
    """
    key = manufacturer.lower().strip()

    # Exact match
    if key in MATERIAL_LOOKUP:
        return MATERIAL_LOOKUP[key]

    # Partial match — e.g. "gold" matches "gold manufacturer"
    for lookup_key, materials in MATERIAL_LOOKUP.items():
        if key in lookup_key or lookup_key.split()[0] in key:
            return materials

    return []


def find_materials_from_ai(manufacturer: str) -> list:
    """
    Uses OpenRouter LLaMA to identify raw materials for unknown manufacturers.
    Returns a list of raw materials.
    """
    api_key = os.getenv('OPENROUTER_API_KEY', '')

    if not api_key:
        print("[material_finder] No OpenRouter API key — using fallback.")
        return ['raw materials', 'energy', 'packaging', 'chemicals']

    prompt = f"""You are a supply chain expert.
List the 6 most critical raw materials and inputs needed to manufacture: {manufacturer}

Rules:
- Return ONLY a JSON array of strings
- Each item must be a specific raw material or input
- No explanations, no extra text
- Example: ["iron ore", "coal", "limestone", "energy", "water", "scrap metal"]

Raw materials for {manufacturer}:"""

    try:
        response = requests.post(
            url     = "https://openrouter.ai/api/v1/chat/completions",
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json = {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
            },
            timeout = 15
        )

        if response.status_code == 200:
            content  = response.json()['choices'][0]['message']['content']
            # Extract JSON array from response
            start    = content.find('[')
            end      = content.find(']') + 1
            if start != -1 and end != 0:
                materials = json.loads(content[start:end])
                print(f"[material_finder] AI identified {len(materials)} materials for '{manufacturer}'")
                return materials

    except Exception as e:
        print(f"[material_finder] AI error: {e}")

    return ['raw materials', 'energy', 'packaging', 'chemicals']


def find_materials(manufacturer: str) -> list:
    """
    Main entry point.
    Layer 1 — lookup dictionary
    Layer 2 — OpenRouter AI
    """
    print(f"[material_finder] Finding materials for: {manufacturer}")

    # Layer 1 — try lookup first
    materials = find_materials_from_lookup(manufacturer)
    if materials:
        print(f"[material_finder] Found in dictionary: {materials}")
        return materials

    # Layer 2 — use AI
    print(f"[material_finder] Not in dictionary — asking AI...")
    materials = find_materials_from_ai(manufacturer)
    return materials