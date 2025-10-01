#!/usr/bin/env python3
"""
Eterspire API Data Generator - Main Pipeline
Runs the complete data generation pipeline from wiki JSON to clean API-ready JSON files.
"""

import os
import sys
from scraper import scrape_all_files
from database import init_database, clear_database, insert_all_gear_data
from exporter import export_to_json
import json


def print_header(text):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def main():
    """Run the complete data pipeline"""
    
    print_header("🗡️  ETERSPIRE API DATA GENERATOR")
    
    # Check if manual-download folder exists
    if not os.path.exists('manual-download'):
        print("\n❌ ERROR: 'manual-download' folder not found!")
        print("\nPlease create the folder and add your wiki JSON files:")
        print("  mkdir manual-download")
        print("\nThen download gear pages from:")
        print("  https://eterspire.wiki/rest.php/v1/page/{GEAR_NAME}_Gear")
        print("\nExample: https://eterspire.wiki/rest.php/v1/page/Bronze_Gear")
        return 1
    
    # Check if there are any JSON files
    json_files = [f for f in os.listdir('manual-download') if f.endswith('.json')]
    if not json_files:
        print("\n❌ ERROR: No JSON files found in 'manual-download' folder!")
        print("\nPlease download gear pages from the wiki:")
        print("  https://eterspire.wiki/rest.php/v1/page/{GEAR_NAME}_Gear")
        print("\nSave them as: {GEAR_NAME}_Gear.json")
        print("Example: Bronze_Gear.json, Steel_Gear.json, etc.")
        return 1
    
    print(f"\n✅ Found {len(json_files)} JSON file(s) to process")
    
    # Step 1: Scrape
    print_header("STEP 1: Scraping Wiki JSON Files")
    all_data = scrape_all_files()
    
    if not all_data:
        print("\n❌ ERROR: No data was scraped!")
        return 1
    
    with open('all_gear_raw.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n✅ Successfully scraped {len(all_data)} gear set(s)")
    print(f"   Raw data saved to: all_gear_raw.json")
    
    # Step 2: Import to Database
    print_header("STEP 2: Importing to Database")
    print("Initializing database...")
    init_database()
    clear_database()
    
    print(f"Importing {len(all_data)} gear set(s)...")
    insert_all_gear_data(all_data)
    
    print("\n✅ Database import complete")
    print(f"   Database file: eterspire.db")
    
    # Step 3: Export JSON
    print_header("STEP 3: Exporting JSON Files")
    export_to_json()
    
    # Final Summary
    print_header("✅ PIPELINE COMPLETE!")
    
    print("\n📤 Output files generated:")
    print("   📁 output/items.json      - All items (armor + weapons)")
    print("   📁 output/weapons.json    - Weapons only")
    print("   📁 output/armor.json      - Armor only")
    print("   📁 output/gear_sets.json  - Hierarchical gear sets")
    
    print("\n🎮 Data is ready to use!")
    print("\n" + "=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
