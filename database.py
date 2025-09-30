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
            tier INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS armor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_set_id INTEGER,
            classes TEXT,
            item_name TEXT,
            quality TEXT,
            hp_min INTEGER,
            hp_mid INTEGER,
            hp_max INTEGER,
            FOREIGN KEY (gear_set_id) REFERENCES gear_sets(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gear_set_id INTEGER,
            name TEXT,
            class TEXT,
            quality TEXT,
            damage_min INTEGER,
            damage_mid INTEGER,
            damage_max INTEGER,
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
    cursor.execute('DELETE FROM gear_sets')
    conn.commit()
    conn.close()

def insert_all_gear_data(all_gear_data):
    """Insert all scraped gear data into database"""
    conn = sqlite3.connect('eterspire.db')
    cursor = conn.cursor()
    
    for gear_data in all_gear_data:
        cursor.execute('''
            INSERT OR REPLACE INTO gear_sets (name, tier)
            VALUES (?, ?)
        ''', (gear_data['name'], gear_data['tier']))
        
        gear_set_id = cursor.lastrowid
        if gear_set_id == 0:
            cursor.execute('SELECT id FROM gear_sets WHERE name = ?', (gear_data['name'],))
            gear_set_id = cursor.fetchone()[0]
        
        for armor in gear_data['armor']:
            cursor.execute('''
                INSERT INTO armor (gear_set_id, classes, item_name, quality, hp_min, hp_mid, hp_max)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (gear_set_id, ','.join(armor['classes']), armor['items'], 
                  armor['quality'], armor['hp_min'], armor['hp_mid'], armor['hp_max']))
        
        for weapon in gear_data['weapons']:
            cursor.execute('''
                INSERT INTO weapons (gear_set_id, name, class, quality, damage_min, damage_mid, damage_max)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (gear_set_id, weapon['name'], weapon['class'], weapon['quality'],
                  weapon['damage_min'], weapon['damage_mid'], weapon['damage_max']))
        
        print(f"  Inserted {gear_data['name']}")
    
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