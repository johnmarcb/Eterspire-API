import subprocess

def run_pipeline():
    """Run the complete scraping pipeline"""
    
    print("="*60)
    print("ETERSPIRE API DATA PIPELINE")
    print("="*60)
    
    # Step 1: Scrape local files from manual-download folder
    print("\n[1/3] Scraping HTML files from manual-download/...")
    result = subprocess.run(['python', 'scraper.py'], capture_output=False)
    if result.returncode != 0:
        print("Error in scraping step")
        return
    
    # Step 2: Load to database
    print("\n[2/3] Loading data into database...")
    result = subprocess.run(['python', 'database.py'], capture_output=False)
    if result.returncode != 0:
        print("Error in database step")
        return
    
    # Step 3: Export JSON
    print("\n[3/3] Exporting to JSON...")
    result = subprocess.run(['python', 'exporter.py'], capture_output=False)
    if result.returncode != 0:
        print("Error in export step")
        return
    
    print("\n" + "="*60)
    print("COMPLETE! Check output/ folder for your API files")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()