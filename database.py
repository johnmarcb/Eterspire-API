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
        CREATE TABLE IF NOT EXISTS bonus_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_set_id INTEGER,
            quality TEXT,
            category TEXT,
            attack_speed_values TEXT,
            strength_values TEXT,
            vitality_values TEXT,
            FOREIGN KEY (gear_set_id) REFERENCES gear_sets(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS armor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_set_id INTEGER,
            slot TEXT,
            quality TEXT,
            classes TEXT,
            item_name TEXT,
            hp_values TEXT,
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
            attack_speed INTEGER,
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
    cursor.execute('DELETE FROM armor')
    cursor.execute('DELETE FROM bonus_stats')
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
        
        # Insert bonus stats
        for quality in ['normal', 'excellent']:
            for category in ['armor', 'weapon']:
                stats = gear_data.get('bonus_stats', {}).get(quality, {}).get(category, {})
                if stats:
                    cursor.execute('''
                        INSERT INTO bonus_stats (
                            gear_set_id, quality, category,
                            attack_speed_values, strength_values, vitality_values
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        gear_set_id, quality, category,
                        json.dumps(stats.get('bonus_attack_speed')),
                        json.dumps(stats.get('strength')),
                        json.dumps(stats.get('vitality'))
                    ))
        
        # Insert armor pieces
        for armor_piece in gear_data.get('armor', []):
            cursor.execute('''
                INSERT INTO armor (
                    gear_set_id, slot, quality, classes, item_name, hp_values
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                gear_set_id,
                armor_piece['slot'],
                armor_piece['quality'],
                ','.join(armor_piece['classes']),
                armor_piece['item_name'],
                json.dumps(armor_piece.get('hp'))
            ))
        
        # Insert weapons
        for weapon in gear_data.get('weapons', []):
            cursor.execute('''
                INSERT INTO weapons (
                    gear_set_id, class, weapon_type, quality,
                    damage_values, attack_speed
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                gear_set_id,
                weapon['class'],
                weapon['weapon_type'],
                weapon['quality'],
                json.dumps(weapon.get('damage')),
                weapon.get('attack_speed')
            ))
        
        print(f"  Inserted {gear_data['name']} (Tier {gear_data['tier']}) - Armor: {len(gear_data.get('armor', []))} slots, Weapons: {len(gear_data.get('weapons', []))}")
    
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