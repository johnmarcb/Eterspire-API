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
    
    all_gear = []
    all_weapons = []
    all_armor = []
    
    for gear_set in gear_sets:
        gear_id = gear_set['id']
        gear_name = gear_set['name']
        
        # Get armor variants
        cursor.execute('SELECT * FROM armor_variants WHERE gear_set_id = ?', (gear_id,))
        armor_rows = cursor.fetchall()
        
        # Organize armor by slot and quality
        armor_pieces = {}
        for row in armor_rows:
            slot = row['slot']
            quality = row['quality']
            
            if slot not in armor_pieces:
                armor_pieces[slot] = {'slot': slot, 'normal': {'variants': []}, 'excellent': {'variants': []}}
            
            variant_data = {
                'classes': row['classes'].split(','),
                'item_name': row['item_name']
            }
            
            # Parse JSON arrays
            if row['hp_values']:
                variant_data['hp'] = json.loads(row['hp_values'])
            
            if row['attack_speed_values']:
                variant_data['bonus_attack_speed'] = json.loads(row['attack_speed_values'])
            
            if row['strength_values']:
                variant_data['strength'] = json.loads(row['strength_values'])
            
            armor_pieces[slot][quality]['variants'].append(variant_data)
            
            # Add to flat armor list
            flat_armor = variant_data.copy()
            flat_armor.update({
                'gear_set': gear_name,
                'tier': gear_set['tier'],
                'level': gear_set['level'],
                'slot': slot,
                'quality': quality
            })
            all_armor.append(flat_armor)
        
        # Get weapons
        cursor.execute('SELECT * FROM weapons WHERE gear_set_id = ?', (gear_id,))
        weapon_rows = cursor.fetchall()
        
        # Organize weapons
        weapons = {}
        for row in weapon_rows:
            key = (row['class'], row['weapon_type'])
            quality = row['quality']
            
            if key not in weapons:
                weapons[key] = {
                    'class': row['class'],
                    'weapon_type': row['weapon_type']
                }
            
            weapon_data = {}
            
            # Parse JSON arrays
            if row['damage_values']:
                weapon_data['damage'] = json.loads(row['damage_values'])
            
            if row['attack_speed_values']:
                weapon_data['bonus_attack_speed'] = json.loads(row['attack_speed_values'])
            
            if row['vitality_values']:
                weapon_data['vitality'] = json.loads(row['vitality_values'])
            
            weapons[key][quality] = weapon_data
            
            # Add to flat weapons list
            flat_weapon = weapon_data.copy()
            flat_weapon.update({
                'gear_set': gear_name,
                'tier': gear_set['tier'],
                'level': gear_set['level'],
                'class': row['class'],
                'weapon_type': row['weapon_type'],
                'quality': quality
            })
            all_weapons.append(flat_weapon)
        
        # Build gear set
        gear_item = {
            'name': gear_name,
            'tier': gear_set['tier'],
            'level': gear_set['level'],
            'armor_pieces': list(armor_pieces.values()),
            'weapons': list(weapons.values())
        }
        
        all_gear.append(gear_item)
    
    conn.close()
    
    # Export files
    with open('output/gear_sets.json', 'w') as f:
        json.dump(all_gear, f, indent=2)
    print(f"✓ Exported output/gear_sets.json ({len(all_gear)} gear sets)")
    
    with open('output/weapons.json', 'w') as f:
        json.dump(all_weapons, f, indent=2)
    print(f"✓ Exported output/weapons.json ({len(all_weapons)} weapon entries)")
    
    with open('output/armor.json', 'w') as f:
        json.dump(all_armor, f, indent=2)
    print(f"✓ Exported output/armor.json ({len(all_armor)} armor entries)")

if __name__ == "__main__":
    export_to_json()