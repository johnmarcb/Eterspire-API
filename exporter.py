import sqlite3
import json
import os

def export_to_json():
    """Export database to JSON files for API"""
    conn = sqlite3.connect('eterspire.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    os.makedirs('output', exist_ok=True)
    
    # Get all gear sets
    cursor.execute('SELECT * FROM gear_sets')
    gear_sets = cursor.fetchall()
    
    all_weapons = []
    all_armor = []
    all_items = []
    
    for gear_set in gear_sets:
        gear_id = gear_set['id']
        gear_name = gear_set['name']
        
        # Get armor for this gear set
        cursor.execute('SELECT * FROM armor WHERE gear_set_id = ?', (gear_id,))
        armor_rows = cursor.fetchall()
        
        armor_list = []
        for armor_row in armor_rows:
            armor_dict = {
                "classes": armor_row['classes'].split(','),
                "item_name": armor_row['item_name'],
                "quality": armor_row['quality'],
                "hp_min": armor_row['hp_min'],
                "hp_mid": armor_row['hp_mid'],
                "hp_max": armor_row['hp_max']
            }
            armor_list.append(armor_dict)
            
            # Add to all_armor with gear_set info
            armor_with_set = armor_dict.copy()
            armor_with_set['gear_set'] = gear_name
            armor_with_set['tier'] = gear_set['tier']
            all_armor.append(armor_with_set)
        
        # Get weapons for this gear set
        cursor.execute('SELECT * FROM weapons WHERE gear_set_id = ?', (gear_id,))
        weapon_rows = cursor.fetchall()
        
        weapon_list = []
        for weapon_row in weapon_rows:
            weapon_dict = {
                "name": weapon_row['name'],
                "class": weapon_row['class'],
                "quality": weapon_row['quality'],
                "damage_min": weapon_row['damage_min'],
                "damage_mid": weapon_row['damage_mid'],
                "damage_max": weapon_row['damage_max']
            }
            weapon_list.append(weapon_dict)
            
            # Add to all_weapons with gear_set info
            weapon_with_set = weapon_dict.copy()
            weapon_with_set['gear_set'] = gear_name
            weapon_with_set['tier'] = gear_set['tier']
            all_weapons.append(weapon_with_set)
        
        # Build complete gear set object
        all_items.append({
            "name": gear_name,
            "tier": gear_set['tier'],
            "armor": armor_list,
            "weapons": weapon_list
        })
    
    conn.close()
    
    # Export 3 files
    with open('output/items.json', 'w') as f:
        json.dump(all_items, f, indent=2)
    print(f"✓ Exported output/items.json ({len(all_items)} gear sets)")
    
    with open('output/weapons.json', 'w') as f:
        json.dump(all_weapons, f, indent=2)
    print(f"✓ Exported output/weapons.json ({len(all_weapons)} weapons)")
    
    with open('output/armor.json', 'w') as f:
        json.dump(all_armor, f, indent=2)
    print(f"✓ Exported output/armor.json ({len(all_armor)} armor pieces)")

if __name__ == "__main__":
    export_to_json()