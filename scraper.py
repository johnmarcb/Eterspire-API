import json
import os
import re

def parse_number(text):
    """Parse a number that might be in K notation or negative"""
    text = text.strip()
    if text == '-' or not text:
        return None
    
    # Handle K notation (e.g., "10.9K")
    if 'K' in text.upper():
        text = text.upper().replace('K', '')
        try:
            return int(float(text) * 1000)
        except:
            return None
    
    try:
        return int(text)
    except:
        return None

def extract_all_stat_values(text):
    """Extract all numeric values from text, including negatives"""
    pattern = r'-?\d+\.?\d*K?'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    values = []
    for match in matches:
        val = parse_number(match)
        if val is not None:
            values.append(val)
    
    return values if values else None

def parse_wikitext_table(table_text):
    """Parse a wikitext table into rows of cells"""
    rows = []
    current_row = []
    
    lines = table_text.split('\n')
    for line in lines:
        line = line.strip()
        
        if line.startswith('|-'):
            if current_row:
                rows.append(current_row)
            current_row = []
        elif line.startswith('|') and not line.startswith('|}') and not line.startswith('|-'):
            if line.count('|') > 1:
                cell = line.split('|')[-1].strip()
            else:
                cell = line[1:].strip()
            
            if not line.startswith('!'):
                current_row.append(cell)
    
    if current_row:
        rows.append(current_row)
    
    return rows

# Fixed attack speeds for each weapon type
WEAPON_ATTACK_SPEEDS = {
    # Guardian weapons
    'Widesword': 129,
    'Battleaxe': 123,
    'Bardiche': 117,
    'Mace': 111,
    'Warhammer': 106,
    # Warrior weapons
    'Longsword': 175,
    'Claymore': 164,
    'Trident': 153,
    'Halberd': 144,
    'Broadsword': 136,
    # Rogue weapons
    'Dagger': 246,
    'Curved Dagger': 223,
    'Short Sword': 205,
    'Sword': 189
}

def scrape_gear_json(filename):
    """Scrape a single gear JSON file"""
    
    filepath = os.path.join('manual-download', filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    source = data.get('source', '')
    
    if not source:
        print(f"  WARNING: No source field found")
        return None
    
    gear_name = data.get('title', '').replace(' Gear', '')
    
    # Extract tier
    tier = None
    tier_match = re.search(r'Tier\s+(\d+)', source)
    if tier_match:
        tier = int(tier_match.group(1))
    else:
        # Manual tier mapping for gear sets without explicit tier
        tier_mapping = {
            'Bronze': 1, 'Steel': 2, 'Sunstone': 3, 'Bloodchrome': 4, 
            'Meteor': 5, 'Onyx': 6, 'Lypriptite': 7, 'Azurite': 8,
            'Emerald': 9, 'Citrine': 10, 'Kunzite': 11, 'Aquamarine': 12,
            'Jade': 13, 'Zircon': 14, 'Topaz': 15, 'Rhodonite': 16
        }
        tier = tier_mapping.get(gear_name)
    
    # Extract level
    level = None
    level_match = re.search(r'level\s+(\d+)', source, re.IGNORECASE)
    if level_match:
        level = int(level_match.group(1))
    
    # Apply conditional: if tier >= 17 and no level found, set to 160
    if tier is not None and tier >= 17 and level is None:
        level = 160
    
    gear_data = {
        "name": gear_name,
        "tier": tier,
        "level": level,
        "bonus_stats": {
            "normal": {},
            "excellent": {}
        },
        "armor": [],
        "weapons": []
    }
    
    # Parse bonus stats (global for the gear set)
    bonus_match = re.search(r'=== Bonus Stats ===\s*\{\|(.*?)\n\|\}', source, re.DOTALL)
    if bonus_match:
        table_text = bonus_match.group(1)
        rows = parse_wikitext_table(table_text)
        
        for row in rows:
            if len(row) >= 2:
                item_type = re.sub(r'<[^>]+>', '', row[0]).strip()
                
                # Determine if it's armor or weapon, and quality
                is_armor = 'Armor' in item_type
                is_excellent = 'Excellent' in item_type
                quality = 'excellent' if is_excellent else 'normal'
                category = 'armor' if is_armor else 'weapon'
                
                if category not in gear_data['bonus_stats'][quality]:
                    gear_data['bonus_stats'][quality][category] = {}
                
                # Attack speed
                if len(row) > 1:
                    speed = extract_all_stat_values(row[1])
                    if speed:
                        gear_data['bonus_stats'][quality][category]['bonus_attack_speed'] = speed
                
                # Strength
                if len(row) > 2 and row[2].strip() != '-':
                    strength = extract_all_stat_values(row[2])
                    if strength:
                        gear_data['bonus_stats'][quality][category]['strength'] = strength
                
                # Vitality
                if len(row) > 3 and row[3].strip() != '-':
                    vitality = extract_all_stat_values(row[3])
                    if vitality:
                        gear_data['bonus_stats'][quality][category]['vitality'] = vitality
    
    # Parse armor table - Excellent items are separate objects
    armor_match = re.search(r'=== All Classes Armors ===\s*\{\|(.*?)\n\|\}', source, re.DOTALL)
    if armor_match:
        table_text = armor_match.group(1)
        rows = parse_wikitext_table(table_text)
        
        # Store armor pieces directly
        armor_pieces = []
        
        for row in rows:
            if len(row) >= 3:
                warrior_text = re.sub(r"'''", '', row[0]).strip()
                sorcerer_text = re.sub(r"'''", '', row[1]).strip()
                hp_text = re.sub(r'<[^>]+>', '', row[2]).strip()
                
                is_excellent = "Ex." in warrior_text
                quality = 'excellent' if is_excellent else 'normal'
                
                warrior_text = warrior_text.replace("Ex.", "").strip()
                sorcerer_text = sorcerer_text.replace("Ex.", "").strip()
                
                hp = extract_all_stat_values(hp_text)
                
                if not hp:
                    continue
                
                warrior_items = [item.strip() for item in warrior_text.split('/')]
                sorcerer_items = [item.strip() for item in sorcerer_text.split('/')]
                
                slot_map = {
                    'Helm': 'helm', 'Gauntlets': 'gauntlets', 'Greaves': 'greaves',
                    'Platemail': 'chest', 'Platelegs': 'legs', 'Shield': 'shield',
                    'Thread Helm': 'helm', 'Gloves': 'gloves', 'Boots': 'boots',
                    'ThreadTop': 'chest', 'Thread Top': 'chest',
                    'ThreadBottom': 'legs', 'Thread Bottom': 'legs',
                    'Gilded Spellbook': 'offhand'
                }
                
                for w_item, s_item in zip(warrior_items, sorcerer_items):
                    slot = slot_map.get(w_item, w_item.lower().replace(' ', '_'))
                    
                    # Create warrior armor piece
                    armor_pieces.append({
                        'slot': slot,
                        'quality': quality,
                        'classes': ['Guardian', 'Warrior', 'Rogue'],
                        'item_name': w_item,
                        'hp': hp
                    })
                    
                    # Create sorcerer armor piece
                    armor_pieces.append({
                        'slot': slot,
                        'quality': quality,
                        'classes': ['Sorcerer'],
                        'item_name': s_item,
                        'hp': hp
                    })
        
        gear_data['armor'] = armor_pieces
    
    # Parse weapons - Excellent items are separate objects
    weapons = []
    
    for class_name in ["Guardian", "Rogue", "Warrior", "Sorcerer"]:
        # More flexible regex to handle variable whitespace
        weapon_match = re.search(rf'===\s+{class_name} Weapons\s+===\s*\{{\|(.*?)\n\|\}}', source, re.DOTALL)
        if weapon_match:
            table_text = weapon_match.group(1)
            rows = parse_wikitext_table(table_text)
            
            for row in rows:
                if len(row) >= 2:
                    weapon_name = re.sub(r"'''", '', row[0]).strip()
                    damage_text = re.sub(r'<[^>]+>', '', row[1]).strip()
                    
                    # Check for asterisk (means only available in excellent)
                    has_asterisk = '*' in weapon_name
                    weapon_name = weapon_name.replace('*', '').strip()
                    
                    is_excellent = "Ex." in weapon_name or has_asterisk
                    quality = 'excellent' if is_excellent else 'normal'
                    weapon_name = weapon_name.replace("Ex.", "").strip()
                    
                    damage = extract_all_stat_values(damage_text)
                    
                    if not damage:
                        continue
                    
                    # Get fixed attack speed for this weapon type
                    attack_speed = WEAPON_ATTACK_SPEEDS.get(weapon_name)
                    
                    weapon = {
                        'class': class_name,
                        'weapon_type': weapon_name,
                        'quality': quality,
                        'damage': damage
                    }
                    
                    # Add attack speed if found
                    if attack_speed:
                        weapon['attack_speed'] = attack_speed
                    
                    weapons.append(weapon)
    
    gear_data['weapons'] = weapons
    
    return gear_data

def scrape_all_files():
    """Scrape all JSON files in manual-download folder"""
    
    download_folder = 'manual-download'
    
    if not os.path.exists(download_folder):
        print(f"Error: {download_folder} folder doesn't exist")
        return []
    
    json_files = [f for f in os.listdir(download_folder) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {download_folder}")
        return []
    
    print(f"Found {len(json_files)} JSON files")
    
    all_gear_data = []
    seen_names = set()
    
    for filename in json_files:
        print(f"\nProcessing: {filename}")
        try:
            gear_data = scrape_gear_json(filename)
            
            if not gear_data:
                continue
            
            if gear_data['name'] in seen_names:
                print(f"  SKIPPED - Duplicate of {gear_data['name']}")
                continue
            
            seen_names.add(gear_data['name'])
            all_gear_data.append(gear_data)
            print(f"  Tier: {gear_data['tier']} | Level: {gear_data['level']} | Armor: {len(gear_data['armor'])} slots | Weapons: {len(gear_data['weapons'])}")
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    return all_gear_data

if __name__ == "__main__":
    print("Scraping all gear pages...\n")
    
    all_data = scrape_all_files()
    
    with open('all_gear_raw.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Scraped {len(all_data)} gear sets")
    print(f"Data saved to all_gear_raw.json")