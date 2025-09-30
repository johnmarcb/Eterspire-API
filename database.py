import sqlite3
import json

def init_database():
    """Create SQLite database and tables"""
    conn = sqlite3.connect('eterspire.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gear_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tier INTEGER,
            level INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS armor_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_set_id INTEGER,
            slot TEXT,
            quality TEXT,
            classes TEXT,
            item_name TEXT,
            hp_values TEXT,
            attack_speed_values TEXT,
            strength_values TEXT,
            FOREIGN KEY (gear_set_id) REFERENCES gear_sets(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_set_id INTEGER,
            class TEXT,
            weapon_type TEXT,
            quality TEXT,
            damage_values TEXT,
            attack_speed_values TEXT,
            vitality_values TEXT,
            FOREIGN KEY (gear_set_id) REFERENCES gear_sets(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def clear_database():
    """Clear all data from database"""
    conn = sqlite3.connect('eterspire.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM weapons')
    cursor.execute('DELETE FROM armor_variants')
    cursor.execute('DELETE FROM gear_sets')
    conn.commit()
    conn.close()

def insert_all_gear_data(all_gear_data):
    """Insert all scraped gear data into database"""
    conn = sqlite3.connect('eterspire.db')
    cursor = conn.cursor()
    
    for gear_data in all_gear_data:
        cursor.execute('''
            INSERT OR REPLACE INTO gear_sets (name, tier, level)
            VALUES (?, ?, ?)
        ''', (gear_data['name'], gear_data['tier'], gear_data.get('level')))
        
        gear_set_id = cursor.lastrowid
        if gear_set_id == 0:
            cursor.execute('SELECT id FROM gear_sets WHERE name = ?', (gear_data['name'],))
            gear_set_id = cursor.fetchone()[0]
        
        # Insert armor variants
        for armor_piece in gear_data.get('armor_pieces', []):
            slot = armor_piece['slot']
            
            for quality in ['normal', 'excellent']:
                if quality not in armor_piece:
                    continue
                
                quality_data = armor_piece[quality]
                
                # Insert each variant
                for variant in quality_data.get('variants', []):
                    cursor.execute('''
                        INSERT INTO armor_variants (
                            gear_set_id, slot, quality, classes, item_name,
                            hp_values, attack_speed_values, strength_values
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        gear_set_id, slot, quality,
                        ','.join(variant['classes']), variant['item_name'],
                        json.dumps(variant.get('hp')),
                        json.dumps(variant.get('bonus_attack_speed')),
                        json.dumps(variant.get('strength'))
                    ))
        
        # Insert weapons
        for weapon in gear_data.get('weapons', []):
            for quality in ['normal', 'excellent']:
                if quality not in weapon:
                    continue
                
                quality_data = weapon[quality]
                cursor.execute('''
                    INSERT INTO weapons (
                        gear_set_id, class, weapon_type, quality,
                        damage_values, attack_speed_values, vitality_values
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    gear_set_id, weapon['class'], weapon['weapon_type'], quality,
                    json.dumps(quality_data.get('damage')),
                    json.dumps(quality_data.get('bonus_attack_speed')),
                    json.dumps(quality_data.get('vitality'))
                ))
        
        armor_count = sum(len(piece.get('normal', {}).get('variants', [])) + 
                         len(piece.get('excellent', {}).get('variants', [])) 
                         for piece in gear_data.get('armor_pieces', []))
        
        print(f"  Inserted {gear_data['name']} (Tier {gear_data['tier']}) - Armor variants: {armor_count}, Weapons: {len(gear_data.get('weapons', []))}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    clear_database()
    
    with open('all_gear_raw.json', 'r') as f:
        all_data = json.load(f)
    
    print(f"\nInserting {len(all_data)} gear sets...")
    insert_all_gear_data(all_data)
    print("\nDone!")