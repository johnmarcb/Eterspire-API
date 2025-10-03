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
- [Credits](#credits)

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

### Step 1: Download Wiki Page

You need to manually download the HTML GearDatabase page from the Eterspire Wiki.

1. **Create the download folder** (if it doesn't exist):

   ```bash
   mkdir -p manual-download
   ```

2. **Download the GearDatabase page**:

   Visit the GearDatabase page in your browser:

   ```
   https://eterspire.wiki/index.php/GearDatabase
   ```

3. **Save the HTML file** in the `manual-download/` folder:

   - Right-click on the page → "Save As" → "Webpage, HTML Only"
   - Save as: `GearDatabase.html`
   - Full path: `manual-download/GearDatabase.html`

   > **Note:** The page contains HTML tables with all gear data (armor and weapons) organized by tier.

### Step 2: Run the Pipeline

#### Option A: Run Manually (One-time)

Once you have the `GearDatabase.html` file in `manual-download/`, run the complete pipeline:

```bash
python main.py
```

This will run all three steps (scraping → database → exporting) automatically.

Or run the individual scripts as needed:

```bash
# Run scraper to extract data from HTML
python scraper.py

# Load data into SQLite database
python database.py

# Export to JSON files
python exporter.py
```

#### Option B: Auto-Watch Mode (Recommended) 🔥

Start the file watcher to automatically run the pipeline whenever files are added or updated in `manual-download/`:

```bash
python watch.py
```

The watcher will:
- ✅ Monitor the `manual-download/` folder for changes
- ✅ Automatically run the pipeline when HTML files are added or updated
- ✅ Debounce rapid changes to avoid multiple runs
- ✅ Skip temporary/hidden files

**Perfect for:**
- Updating the GearDatabase.html file regularly
- Adding new wiki pages to parse
- Iterative development

Press `Ctrl+C` to stop watching.

## Output Files

The pipeline generates the following files in the `output/` directory:

- `items.json` - Flat list of all individual items (armor + weapons)
- `weapons.json` - All weapon items only
- `armor.json` - All armor items only
- `gear_sets.json` - Hierarchical collection organized by gear set with bonus stats

## Data Structure

### Individual Item Object

```json
{
    "id": "Bronze-Helm-Normal",
    "name": "Helm",
    "tier": 1,
    "level": 1,
    "allowed_classes": [
      "Guardian",
      "Warrior",
      "Rogue"
    ],
    "type": "armor",
    "slot": "helm",
    "quality": "normal",
    "base": {
      "hp": [
        4,
        5,
        6,
        7
      ]
    },
    "bonuses": {
      "bonus_attack_speed": [
        -2,
        -1,
        0,
        1,
        2
      ],
      "strength": [
        -1,
        0,
        1
      ]
    },
    "gear_set": "Bronze"
  },
```

## Project Structure

```
eterspire-api/
├── scraper.py              # HTML parser - extracts data from wiki tables
├── database.py             # SQLite database loader
├── exporter.py             # JSON exporter
├── requirements.txt        # Python dependencies
├── manual-download/        # Downloaded wiki HTML file (you create this)
│   └── GearDatabase.html   # Main gear database page
├── output/                 # Generated JSON files (created by exporter)
│   ├── items.json          # All items combined
│   ├── weapons.json        # Weapons only
│   ├── armor.json          # Armor only
│   └── gear_sets.json      # Hierarchical gear sets
├── all_gear_raw.json       # Raw scraped data (intermediate)
└── eterspire.db            # SQLite database (intermediate)
```

## In Progress Items

- Create a parser for rings
- Test with ring wiki table formats
- Include upgrade tiers data tables (this will be wayyyy later)

## Known Issues

### ⚠️ Manual Download Required

**Due to Eterspire Wiki's Cloudflare protection, automated scraping via Selenium or other web automation tools is not feasible.** The wiki employs anti-bot measures that make direct scraping extremely challenging.

**Current Solution:** Manual download of the HTML GearDatabase page (see [Step 1](#step-1-download-wiki-page) above)

Once downloaded, the HTML tables are parsed efficiently using BeautifulSoup to extract all gear data.

**Have an automated solution?** Please open an issue or pull request! The community would benefit from an automated download solution.

---

## Credits

### 🙏 Special Thanks

This project wouldn't have been possible without the incredible **Eterspire Wiki community**!

**Massive appreciation to:**

- **All wiki founders** who took the initiative to create [eterspire.wiki](https://eterspire.wiki) and establish a central knowledge hub for the community
- **Every contributor** who has meticulously documented items, stats, mechanics, and strategies
- **Active editors** who continuously update the wiki with new content, corrections, and improvements
- **The Eterspire community** for their ongoing support, feedback, and collaborative spirit

Your dedication to documenting this game has created an invaluable resource that benefits players worldwide. This API simply transforms your hard work into a more accessible format.

**Thank you for building and maintaining such a comprehensive knowledge base!** 🎮✨

---

## Contributing

Contributions are welcome! Especially solutions for the Cloudflare issue. Please feel free to:

- Open issues for bugs or feature requests
- Submit pull requests with improvements
- Share workarounds for the scraping challenge

---

**Note:** This tool is for personal/educational use. Please respect the Eterspire Wiki's terms of service and rate limits when downloading data.