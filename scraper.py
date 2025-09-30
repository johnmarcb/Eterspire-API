from bs4 import BeautifulSoup
import re
import json
import os

def extract_gear_name_from_filename(filename):
    """Extract gear set name from filename"""
    name = filename.replace('.html', '').replace(' - Eterspire Wiki', '').replace(' Gear', '')
    return name.strip()

def scrape_gear_page(filename):
    """Scrape a single gear page"""
    
    filepath = os.path.join('manual-download', filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract gear name from filename
    gear_name = extract_gear_name_from_filename(filename)
    
    # Try to extract tier from page content
    content = soup.find('div', {'id': 'mw-content-text'})
    tier = None
    if content:
        text = content.get_text()
        tier_match = re.search(r'Tier\s+(\d+)', text)
        if tier_match:
            tier = int(tier_match.group(1))
    
    gear_data = {
        "name": gear_name,
        "tier": tier,
        "bonus_stats": [],
        "armor": [],
        "weapons": []
    }
    
    tables = soup.find_all('table', class_='wikitable')
    print(f"\n{gear_name}: Found {len(tables)} tables")
    
    for idx, table in enumerate(tables):
        prev_heading = table.find_previous(['h1', 'h2', 'h3'])
        heading_text = prev_heading.get_text(strip=True) if prev_heading else ""
        
        # Parse Bonus Stats
        if "Bonus Stats" in heading_text or idx == 0:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    item_type = cols[0].get_text(strip=True)
                    gear_data["bonus_stats"].append({
                        "item_type": item_type,
                        "raw_stats": [col.get_text(strip=True) for col in cols[1:]]
                    })
        
        # Parse Armors
        elif "All Classes Armors" in heading_text or "Armors" in heading_text:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    warrior_items = cols[0].get_text(strip=True)
                    sorcerer_items = cols[1].get_text(strip=True)
                    hp_values = cols[2].get_text(strip=True)
                    
                    hp_nums = re.findall(r'\d+', hp_values)
                    if len(hp_nums) >= 3:
                        hp_min, hp_mid, hp_max = int(hp_nums[0]), int(hp_nums[1]), int(hp_nums[2])
                        is_excellent = "Ex." in warrior_items
                        quality = "excellent" if is_excellent else "normal"
                        
                        warrior_items = warrior_items.replace("Ex.", "").strip()
                        sorcerer_items = sorcerer_items.replace("Ex.", "").strip()
                        
                        gear_data["armor"].append({
                            "classes": ["Guardian", "Warrior", "Rogue"],
                            "items": warrior_items,
                            "quality": quality,
                            "hp_min": hp_min,
                            "hp_mid": hp_mid,
                            "hp_max": hp_max
                        })
                        
                        gear_data["armor"].append({
                            "classes": ["Sorcerer"],
                            "items": sorcerer_items,
                            "quality": quality,
                            "hp_min": hp_min,
                            "hp_mid": hp_mid,
                            "hp_max": hp_max
                        })
        
        # Parse Weapons
        elif "Weapons" in heading_text:
            class_name = None
            if "Guardian" in heading_text:
                class_name = "Guardian"
            elif "Rogue" in heading_text:
                class_name = "Rogue"
            elif "Warrior" in heading_text:
                class_name = "Warrior"
            elif "Sorcerer" in heading_text:
                class_name = "Sorcerer"
            
            if class_name:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        weapon_name = cols[0].get_text(strip=True)
                        damage_text = cols[1].get_text(strip=True)
                        
                        dmg_nums = re.findall(r'\d+', damage_text)
                        if len(dmg_nums) >= 3:
                            dmg_min, dmg_mid, dmg_max = int(dmg_nums[0]), int(dmg_nums[1]), int(dmg_nums[2])
                            is_excellent = "Ex." in weapon_name
                            quality = "excellent" if is_excellent else "normal"
                            weapon_name = weapon_name.replace("Ex.", "").strip()
                            
                            gear_data["weapons"].append({
                                "name": weapon_name,
                                "class": class_name,
                                "quality": quality,
                                "damage_min": dmg_min,
                                "damage_mid": dmg_mid,
                                "damage_max": dmg_max
                            })
    
    return gear_data
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
    seen_names = set()  # Track processed gear names
    
    for filename in html_files:
        print(f"\nProcessing: {filename}")
        try:
            gear_data = scrape_gear_page(filename)
            
            # Check for duplicates
            if gear_data['name'] in seen_names:
                print(f"  SKIPPED - Duplicate of {gear_data['name']}")
                continue
            
            seen_names.add(gear_data['name'])
            all_gear_data.append(gear_data)
            print(f"  Armor: {len(gear_data['armor'])} | Weapons: {len(gear_data['weapons'])}")
        except Exception as e:
            print(f"  Error: {e}")
    
    return all_gear_data

if __name__ == "__main__":
    print("Scraping all gear pages...\n")
    
    all_data = scrape_all_files()
    
    # Save combined output
    with open('all_gear_raw.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Scraped {len(all_data)} gear sets")
    print(f"Data saved to all_gear_raw.json")