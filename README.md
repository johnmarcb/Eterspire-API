# Eterspire API Data Generator

A data pipeline that scrapes, processes, and exports Eterspire game data from the wiki into clean, structured JSON files suitable for API consumption.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Output Files](#output-files)
- [Data Structure](#data-structure)
- [Project Structure](#project-structure)
- [Known Issues & Workarounds](#known-issues--workarounds)

## Overview

This tool converts Eterspire wiki pages into structured JSON data, creating individual item objects with all their stats, bonuses, and metadata. Perfect for building game databases, APIs, or companion tools.

## Features

- **Clean Item IDs**: Human-readable IDs like `Bronze-Helm-Normal`
- **Separate Quality Items**: Normal and Excellent items are distinct objects
- **Fixed Attack Speeds**: Pre-calculated for each weapon type
- **No Null Pollution**: Only includes relevant stats for each item
- **Hierarchical Exports**: Both flat item lists and gear set collections
- **Class-Based Filtering**: Easy to query items by allowed classes

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   **Windows:**
   ```cmd
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Download Wiki Pages

You need to manually download the JSON data for each gear set from the Eterspire Wiki.

1. **Create the download folder** (if it doesn't exist):
   ```bash
   mkdir -p manual-download
   ```

2. **Download each gear set page**:
   
   Visit the following URL pattern in your browser:
   ```
   https://eterspire.wiki/rest.php/v1/page/{GEAR_NAME}_Gear
   ```
   
   **Examples:**
   - Bronze: `https://eterspire.wiki/rest.php/v1/page/Bronze_Gear`
   - Steel: `https://eterspire.wiki/rest.php/v1/page/Steel_Gear`
   - Sunstone: `https://eterspire.wiki/rest.php/v1/page/Sunstone_Gear`

3. **Save each file** in the `manual-download/` folder:
   - Save as: `{GEAR_NAME}_Gear.json`
   - Example: `Bronze_Gear.json`, `Steel_Gear.json`, etc.
   
   > **Tip:** Right-click the page → Save As → JSON file, or copy the JSON and save it manually.

### Step 2: Run the Pipeline

Once you have all the gear set JSON files in `manual-download/`, run:

```bash
python main.py
```

The script will process all downloaded files and generate structured JSON output in the `output/` directory.

## Output Files

The pipeline generates the following files in the `output/` directory:

- `all_items.json` - Flat list of all individual items
- `gear_sets.json` - Hierarchical collection organized by gear set
- `items_by_class.json` - Items filtered and grouped by character class
- `items_by_type.json` - Items organized by equipment slot/type

## Data Structure

### Individual Item Object
```json
{
  "id": "Bronze-Helm-Normal",
  "name": "Bronze Helm",
  "quality": "Normal",
  "type": "Helm",
  "gearSet": "Bronze",
  "requiredLevel": 1,
  "defense": 10,
  "allowedClasses": ["Warrior", "Knight"],
  "setBonus": {
    "2": "+5 Defense",
    "4": "+10% HP"
  }
}
```

## Project Structure

```
eterspire-api-generator/
├── main.py                 # Main pipeline script
├── requirements.txt        # Python dependencies
├── manual-download/        # Downloaded wiki JSON files (you create this)
│   ├── Bronze_Gear.json
│   ├── Steel_Gear.json
│   └── ...
└── output/                 # Generated JSON files (created by script)
    ├── all_items.json
    ├── gear_sets.json
    ├── items_by_class.json
    └── items_by_type.json
```

## Known Issues

### ⚠️ Cloudflare Protection Issue

**Unfortunately, due to Eterspire Wiki's aggressive Cloudflare protection, automated scraping via Selenium or other web automation tools is currently not possible.** The wiki employs anti-bot measures that make direct scraping extremely challenging.

**Current Workaround:** Manual download of JSON files (see [Step 1](#step-1-download-wiki-pages) above)

**Have a solution?** Please open an issue or pull request! The community would greatly benefit from an automated scraping solution.

---

## Contributing

Contributions are welcome! Especially solutions for the Cloudflare issue. Please feel free to:
- Open issues for bugs or feature requests
- Submit pull requests with improvements
- Share workarounds for the scraping challenge


---

**Note:** This tool is for personal/educational use. Please respect the Eterspire Wiki's terms of service and rate limits when downloading data.