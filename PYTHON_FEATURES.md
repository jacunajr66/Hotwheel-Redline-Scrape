# 🏎️ Python Features Illustrated in Hotwheel Scraper

## 📘 Overview of `hotwheel_scrape.py`

This Python script demonstrates a wide range of practical Python features and best practices. Below is 
a summary of the key concepts and tools used throughout the project.

---

## 🔍 Key Concepts and Tools

### 1. Logging
- Utilizes Python’s `logging` module with custom configuration.
- Logs are sent to both the console and a log file.
- Includes detailed context in log messages: process ID (PID), thread ID (TID), timestamp, and log level.

### 2. Web Scraping (`BeautifulSoup`)
- Uses BeautifulSoup to parse HTML content.
- Fetches pages using the `requests` library.
- Extracts and cleans table data, storing it in a `pandas` DataFrame.

### 3. Data Manipulation (`pandas`)
- Uses `pandas` for reading, cleaning, transforming, and saving data.
- Handles renaming, stacking, deduplication, and sorting of data.

### 4. Asynchronous Execution (`concurrent.futures`)
- Employs `ThreadPoolExecutor` for concurrent scraping tasks.
- Uses futures and `as_completed` to gather results efficiently.

### 5. Multiprocessing
- Uses `multiprocessing.Pool` to parallelize scraping for different datasets.
- Improves performance by utilizing multiple CPU cores.

### 6. Error Handling
- Implements `try-except` blocks for robust exception management.
- Catches:
  - `requests.RequestException` for network errors
  - `ValueError` for missing/invalid tables
  - General exceptions for unknown failures

### 7. Performance Profiling (`cProfile`)
- Profiles the script’s execution using `cProfile`.
- Outputs performance stats to a log file for analysis.

### 8. File and Directory Management
- Uses `os.makedirs` to ensure required directories exist.
- Saves data using `DataFrame.to_csv()` and `to_json()`.

### 9. Functional Programming
- Modular function design:
  - `scrape_url()` handles URL scraping
  - `create_csv_files()` organizes file generation
  - `create_combined_csv_file()` merges and exports final datasets
- `wrapper_create_csv_files()` simplifies multiprocessing input

### 10. Helper Utilities
- `create_years_dict()` and `create_series_dict()` generate structured input data.
- Uses dictionary unpacking and `zip()` to iterate data rows.

### 11. Constants and Configuration
- Defines constants like `BASE_URL`, `OUTPUT_DIR`, and `LOG_FILE_PATH` for easier maintenance and 
configuration.

### 12. Pythonic Constructs
- List comprehensions for generating year/series lists.
- Data sorting and aggregation with `groupby()` and `agg()`.

### 13. Virtual Environment Usage
- Project is designed to be run within a Python virtual environment.
- Ensures isolated dependencies using `venv`.
- Users are instructed to install dependencies via `pip install -r requirements.txt` 
after activating the environment.

### 14. Data Storage
- Outputs data in both `.csv` and `.json` formats using `pandas`' built-in methods.

### 15. Best Practices
- Code is modular, readable, and maintainable.
- Clear separation of concerns across functions.
- Includes structured logging and comprehensive error handling.

---

## 🧠 Summary of Core Python Concepts Used
- Logging (`logging`)
- Web scraping (`requests`, `BeautifulSoup`)
- Concurrent execution (`ThreadPoolExecutor`)
- Parallel processing (`multiprocessing.Pool`)
- Data wrangling (`pandas`)
- Performance profiling (`cProfile`)
- Robust error handling
- File I/O and directory management
- Virtual environments (`venv`)
- Lambda functions and function wrapping
- List and dictionary comprehensions

This script is a well-structured example of using Python for data scraping, transformation, 
and export — applying multiple powerful features to build a scalable and reliable data pipeline.
