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

   > Tip: Right-click the page → Save As → JSON file, or copy the JSON and save it manually.

### Step 2: Run the Pipeline

Once you have all the gear set JSON files in `manual-download/`, simply run:
