import json
import os
import re
from bs4 import BeautifulSoup

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
    """Extract all numeric values from text, including negatives and percentages"""
    # Remove percentage signs before parsing
    text = text.replace('%', '')
    pattern = r'-?\d+\.?\d*K?'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    values = []
    for match in matches:
        val = parse_number(match)
        if val is not None:
            values.append(val)
    
    return values if values else None

def scrape_gear_html(filename):
    """Scrape a single gear HTML file - can contain multiple gear sets"""
    
    filepath = os.path.join('manual-download', filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tables in the document
    tables = soup.find_all('table', class_='wikitable')
    
    if not tables:
        print(f"  WARNING: No tables found")
        return []
    
    # Dictionary to hold multiple gear sets, keyed by gear name
    gear_sets = {}
    
    # Process each table
    for table in tables:
        caption = table.find('caption')
        if not caption:
            continue
        
        caption_text = caption.get_text().strip()
        
        # Determine if this is armor or weapons table
        is_armor = 'Armor' in caption_text
        is_weapon = 'Weapon' in caption_text
        
        if not (is_armor or is_weapon):
            continue
        
        # Extract gear name from caption (e.g., "Bronze Armor (Tier 1)" -> "Bronze")
        name_match = re.match(r'(\w+)\s+(Armor|Weapons?)', caption_text)
        if not name_match:
            continue
        
        gear_name = name_match.group(1)
        
        # Extract tier from caption (e.g., "Bronze Armor (Tier 1)")
        tier_match = re.search(r'Tier\s+(\d+)', caption_text)
        tier = int(tier_match.group(1)) if tier_match else None
        
        # Create gear set entry if it doesn't exist
        if gear_name not in gear_sets:
            gear_sets[gear_name] = {
                "name": gear_name,
                "tier": tier,
                "level": None,
                "bonus_stats": {
                    "normal": {"armor": {}, "weapon": {}},
                    "excellent": {"armor": {}, "weapon": {}}
                },
                "armor": [],
                "weapons": []
            }
        
        # Update tier if we have it
        if tier and not gear_sets[gear_name]['tier']:
            gear_sets[gear_name]['tier'] = tier
        
        # Get reference to this gear set
        gear_data = gear_sets[gear_name]
        
        # Get all rows (skip header row)
        rows = table.find('tbody').find_all('tr')[1:]  # Skip header
        
        # Process armor table
        if is_armor:
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue
                
                item_name = cells[0].get_text().strip()
                quality = cells[1].get_text().strip().lower()
                slot = cells[2].get_text().strip().lower()
                classes_text = cells[3].get_text().strip()
                hp_text = cells[4].get_text().strip()
                attack_speed_text = cells[5].get_text().strip()
                strength_text = cells[6].get_text().strip()
                
                # Strip gear prefix from item name (e.g., "Bronze Helm" -> "Helm")
                if gear_data['name'] and item_name.startswith(gear_data['name'] + ' '):
                    item_name = item_name[len(gear_data['name']) + 1:]
                
                # Parse classes
                classes = [c.strip() for c in classes_text.split('/')]
                
                # Parse HP values
                hp_values = extract_all_stat_values(hp_text)
                
                # Store armor piece
                armor_piece = {
                    'slot': slot,
                    'quality': quality,
                    'classes': classes,
                    'item_name': item_name,
                    'hp': hp_values
                }
                gear_data['armor'].append(armor_piece)
                
                # Store bonus stats (attack speed and strength are bonuses for armor)
                if quality not in gear_data['bonus_stats']:
                    gear_data['bonus_stats'][quality] = {'armor': {}, 'weapon': {}}
                
                if 'armor' not in gear_data['bonus_stats'][quality]:
                    gear_data['bonus_stats'][quality]['armor'] = {}
                
                # Collect bonus attack speed values
                bonus_attack_speed = extract_all_stat_values(attack_speed_text)
                if bonus_attack_speed:
                    if 'bonus_attack_speed' not in gear_data['bonus_stats'][quality]['armor']:
                        gear_data['bonus_stats'][quality]['armor']['bonus_attack_speed'] = bonus_attack_speed
                
                # Collect strength values
                strength = extract_all_stat_values(strength_text)
                if strength:
                    if 'strength' not in gear_data['bonus_stats'][quality]['armor']:
                        gear_data['bonus_stats'][quality]['armor']['strength'] = strength
        
        # Process weapons table
        elif is_weapon:
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue
                
                item_name = cells[0].get_text().strip()
                quality = cells[1].get_text().strip().lower()
                class_name = cells[2].get_text().strip()
                damage_text = cells[3].get_text().strip()
                attack_speed_text = cells[4].get_text().strip()
                bonus_attack_speed_text = cells[5].get_text().strip()
                vitality_text = cells[6].get_text().strip()
                
                # Strip gear prefix from item name (e.g., "Bronze Bardiche" -> "Bardiche")
                if gear_data['name'] and item_name.startswith(gear_data['name'] + ' '):
                    item_name = item_name[len(gear_data['name']) + 1:]
                
                # Parse damage values
                damage_values = extract_all_stat_values(damage_text)
                
                # Parse attack speed (base stat, not bonus)
                attack_speed = None
                if attack_speed_text != '-':
                    attack_speed_val = parse_number(attack_speed_text)
                    if attack_speed_val:
                        attack_speed = attack_speed_val
                
                # Store weapon
                weapon = {
                    'class': class_name,
                    'weapon_type': item_name,
                    'quality': quality,
                    'damage': damage_values
                }
                
                if attack_speed:
                    weapon['attack_speed'] = attack_speed
                
                gear_data['weapons'].append(weapon)
                
                # Store bonus stats (bonus attack speed and vitality are bonuses for weapons)
                if quality not in gear_data['bonus_stats']:
                    gear_data['bonus_stats'][quality] = {'armor': {}, 'weapon': {}}
                
                if 'weapon' not in gear_data['bonus_stats'][quality]:
                    gear_data['bonus_stats'][quality]['weapon'] = {}
                
                # Collect bonus attack speed values
                bonus_attack_speed = extract_all_stat_values(bonus_attack_speed_text)
                if bonus_attack_speed:
                    if 'bonus_attack_speed' not in gear_data['bonus_stats'][quality]['weapon']:
                        gear_data['bonus_stats'][quality]['weapon']['bonus_attack_speed'] = bonus_attack_speed
                
                # Collect vitality values
                vitality = extract_all_stat_values(vitality_text)
                if vitality:
                    if 'vitality' not in gear_data['bonus_stats'][quality]['weapon']:
                        gear_data['bonus_stats'][quality]['weapon']['vitality'] = vitality
    
    # Set level based on tier for each gear set (manual mapping or extraction)
    level_mapping = {
        1: 1, 2: 10, 3: 20, 4: 30, 5: 40, 6: 50, 7: 60, 8: 70,
        9: 80, 10: 90, 11: 100, 12: 110, 13: 120, 14: 130, 15: 140, 16: 150
    }
    
    for gear_set in gear_sets.values():
        if gear_set['tier']:
            gear_set['level'] = level_mapping.get(gear_set['tier'], 160 if gear_set['tier'] >= 17 else None)
    
    # Return list of all gear sets found in this file
    return list(gear_sets.values())

def scrape_all_files():
    """Scrape all HTML files in manual-download folder"""
    
    download_folder = 'manual-download'
    
    if not os.path.exists(download_folder):
        print(f"Error: {download_folder} folder doesn't exist")
        return []
    
    html_files = [f for f in os.listdir(download_folder) if f.endswith('.html')]
    
    if not html_files:
        print(f"No HTML files found in {download_folder}")
        return []
    
    print(f"Found {len(html_files)} HTML files")
    
    all_gear_data = []
    seen_names = set()
    
    for filename in html_files:
        print(f"\nProcessing: {filename}")
        try:
            # scrape_gear_html now returns a list of gear sets
            gear_sets = scrape_gear_html(filename)
            
            if not gear_sets:
                print(f"  WARNING: No gear sets found in {filename}")
                continue
            
            # Process each gear set found in this file
            for gear_data in gear_sets:
                if gear_data['name'] in seen_names:
                    print(f"  SKIPPED - Duplicate of {gear_data['name']}")
                    continue
                
                seen_names.add(gear_data['name'])
                all_gear_data.append(gear_data)
                print(f"  ✓ {gear_data['name']}: Tier {gear_data['tier']} | Level {gear_data['level']} | Armor: {len(gear_data['armor'])} pieces | Weapons: {len(gear_data['weapons'])}")
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