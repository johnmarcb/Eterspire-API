import sqlite3
import json
import os
import hashlib
from datetime import datetime

def normalize_id_part(text):
    """Normalize text for use in IDs"""
    # Replace slashes and special chars, capitalize properly
    return text.replace(' / ', '-').replace('/', '-').replace(' ', '-')

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
    all_items = []  # Single array for all individual items
    
    for gear_set in gear_sets:
        gear_id = gear_set['id']
        gear_name = gear_set['name']
        
        # Get bonus stats
        cursor.execute('SELECT * FROM bonus_stats WHERE gear_set_id = ?', (gear_id,))
        bonus_rows = cursor.fetchall()
        
        bonus_stats = {'normal': {}, 'excellent': {}}
        for row in bonus_rows:
            quality = row['quality']
            category = row['category']
            
            stats = {}
            if row['attack_speed_values']:
                stats['bonus_attack_speed'] = json.loads(row['attack_speed_values'])
            if row['strength_values']:
                stats['strength'] = json.loads(row['strength_values'])
            if row['vitality_values']:
                stats['vitality'] = json.loads(row['vitality_values'])
            
            bonus_stats[quality][category] = stats
        
        # Get armor pieces
        cursor.execute('SELECT * FROM armor WHERE gear_set_id = ?', (gear_id,))
        armor_rows = cursor.fetchall()
        
        armor_pieces = []
        for row in armor_rows:
            armor_piece = {
                'slot': row['slot'],
                'quality': row['quality'],
                'classes': row['classes'].split(','),
                'item_name': row['item_name']
            }
            
            if row['hp_values']:
                armor_piece['hp'] = json.loads(row['hp_values'])
            
            armor_pieces.append(armor_piece)
            
            # Create individual armor items (don't split by class, keep them together)
            classes = row['classes'].split(',')
            hp_values = json.loads(row['hp_values']) if row['hp_values'] else None
            armor_bonus = bonus_stats.get(row['quality'], {}).get('armor', {})
            
            # Generate ID: {GearSet}-{ItemName}-{Quality}
            item_id = f"{gear_name}-{normalize_id_part(row['item_name'])}-{row['quality'].capitalize()}"
            
            # Build base stats (only include non-null values)
            base = {}
            if hp_values:
                base['hp'] = hp_values
            
            # Build bonuses (only include non-null values)
            bonuses = {}
            if armor_bonus.get('bonus_attack_speed'):
                bonuses['bonus_attack_speed'] = armor_bonus.get('bonus_attack_speed')
            if armor_bonus.get('strength'):
                bonuses['strength'] = armor_bonus.get('strength')
            if armor_bonus.get('vitality'):
                bonuses['vitality'] = armor_bonus.get('vitality')
            
            item = {
                'id': item_id,
                'name': row['item_name'],
                'tier': gear_set['tier'],
                'level': gear_set['level'],
                'allowed_classes': classes,
                'type': 'armor',
                'slot': row['slot'],
                'quality': row['quality'],
                'base': base,
                'bonuses': bonuses,
                'gear_set': gear_name
            }
            
            all_items.append(item)
        
        # Get weapons
        cursor.execute('SELECT * FROM weapons WHERE gear_set_id = ?', (gear_id,))
        weapon_rows = cursor.fetchall()
        
        weapons = []
        for row in weapon_rows:
            weapon = {
                'class': row['class'],
                'weapon_type': row['weapon_type'],
                'quality': row['quality']
            }
            
            if row['damage_values']:
                weapon['damage'] = json.loads(row['damage_values'])
            if row['attack_speed']:
                weapon['attack_speed'] = row['attack_speed']
            
            weapons.append(weapon)
            
            # Create individual weapon item
            damage_values = json.loads(row['damage_values']) if row['damage_values'] else None
            weapon_bonus = bonus_stats.get(row['quality'], {}).get('weapon', {})
            
            # Generate ID: {GearSet}-{WeaponType}-{Quality}
            item_id = f"{gear_name}-{normalize_id_part(row['weapon_type'])}-{row['quality'].capitalize()}"
            
            # Build base stats (only include non-null values)
            base = {}
            if damage_values:
                base['damage'] = damage_values
            if row['attack_speed']:
                base['attack_speed'] = row['attack_speed']
            
            # Build bonuses (only include non-null values)
            bonuses = {}
            if weapon_bonus.get('bonus_attack_speed'):
                bonuses['bonus_attack_speed'] = weapon_bonus.get('bonus_attack_speed')
            if weapon_bonus.get('strength'):
                bonuses['strength'] = weapon_bonus.get('strength')
            if weapon_bonus.get('vitality'):
                bonuses['vitality'] = weapon_bonus.get('vitality')
            
            item = {
                'id': item_id,
                'name': row['weapon_type'],
                'tier': gear_set['tier'],
                'level': gear_set['level'],
                'allowed_classes': [row['class']],
                'type': 'weapon',
                'slot': row['weapon_type'],
                'quality': row['quality'],
                'base': base,
                'bonuses': bonuses,
                'gear_set': gear_name
            }
            
            all_items.append(item)
        
        # Build gear set
        gear_item = {
            'name': gear_name,
            'tier': gear_set['tier'],
            'level': gear_set['level'],
            'bonus_stats': bonus_stats,
            'armor': armor_pieces,
            'weapons': weapons
        }
        
        all_gear.append(gear_item)
    
    conn.close()
    
    # Export files
    with open('output/gear_sets.json', 'w') as f:
        json.dump(all_gear, f, indent=2)
    print(f"✓ Exported output/gear_sets.json ({len(all_gear)} gear sets)")
    
    with open('output/items.json', 'w') as f:
        json.dump(all_items, f, indent=2)
    print(f"✓ Exported output/items.json ({len(all_items)} individual items)")
    
    # Also export separated by type for convenience
    weapons_only = [item for item in all_items if item['type'] == 'weapon']
    armor_only = [item for item in all_items if item['type'] == 'armor']
    
    with open('output/weapons.json', 'w') as f:
        json.dump(weapons_only, f, indent=2)
    print(f"✓ Exported output/weapons.json ({len(weapons_only)} weapon items)")
    
    with open('output/armor.json', 'w') as f:
        json.dump(armor_only, f, indent=2)
    print(f"✓ Exported output/armor.json ({len(armor_only)} armor items)")

if __name__ == "__main__":
    export_to_json()