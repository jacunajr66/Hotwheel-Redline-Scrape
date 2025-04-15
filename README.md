# 🏎️ Hotwheel Redline Scraper

A Python scraper that extracts and consolidates vintage Hot Wheels casting data from 
[onlineredlineguide.com](https://onlineredlineguide.com). It outputs structured CSV and JSON 
files suitable for analysis, collection tracking, or archival.

---

## 📦 Features

- Scrapes tables from individual model years and casting series
- Cleans and normalizes inconsistent naming conventions
- Combines data into a single structured dataset
- Supports parallel scraping with multithreading and multiprocessing
- Automatically logs all scraping activity and performance profiling

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/jacunajr66/hotwheel-scraper.git
cd hotwheel-scraper
```

### 2. Set Up Environment

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🛠️ Running the Scraper

```bash
python src/hotwheel_scrape.py
```

This will:
- Scrape and save per-year and per-series CSVs to `output/reports/`
- Generate a combined CSV + JSON file at `output/reports/redlines.*`
- Save logs to `output/logs/hotwheel_scrape.log`
- Save performance profile to `output/logs/hotwheel_scrape_profile.log`

---

## 🧪 Running Tests

Tests are written with `pytest`. To run them:

```bash
pytest tests/
```

Test coverage includes:
- Scraper output validation
- Error handling (timeouts, malformed tables, etc.)
- Logging and file system edge cases
- Parallel processing logic

---

## 📁 Project Structure

```
.
├── .pytest_cache
├── .venv/
├── .vscode/
│   ├── settings.json
├── output/
│   ├── reports/                  # Generated CSV and JSON files
│   └── logs/                     # Log and profiler output
├── src/
│   └── hotwheel_scrape.py        # Main scraper logic
├── tests/
│   └── test_hotwheel_scrape.py   # Unit tests
├── .gitignore
├── PYTHON_FEATURES.md
├── README.md
└── requirements.txt
```

---

## 📜 License

MIT License — use freely, modify, and share.

---

## 🙌 Credits

Built by **John Acuna**  
Data sourced from [onlineredlineguide.com](https://onlineredlineguide.com)
