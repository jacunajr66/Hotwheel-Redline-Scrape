# Standard library
import concurrent.futures
import cProfile
import io
import logging
import multiprocessing
import os
import sys

# Third-party
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

# Constants
BASE_URL = "https://onlineredlineguide.com"
OUTPUT_DIR = "output/reports"
LOG_FILE_PATH = "output/logs/hotwheel_scrape.log"


def setup_logging():
    """Set up the logging configuration."""

    # Define the base and subdirectory paths
    base_dir = "output"
    subdirs = ["reports", "logs"]

    # Create the base directory and subdirectories if they don't exist
    if not os.path.exists(base_dir):
        for subdir in subdirs:
            os.makedirs(os.path.join(base_dir, subdir))

    logging.basicConfig(
        level=logging.INFO,  # Set logging level to INFO
        format="%(asctime)s - PID=%(process)d TID=%(thread)d - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Log to standard output
            logging.FileHandler(LOG_FILE_PATH),  # Log to a file
        ],
    )


# Initialize logging configuration
setup_logging()
logger = logging.getLogger(__name__)


def log_message(msg):
    """Log messages with standard format."""
    logger.info(msg)


def scrape_url(url, table_index, outfile, main_column_name):
    """Scrape a URL, extract a table, and return a cleaned DataFrame."""
    try:
        log_message(f"Fetching URL: {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if table is None:
            log_message(f"No table found at {url}.")
            raise ValueError(f"No table found at {url}")

        df = pd.read_html(io.StringIO(str(table)))[table_index]

        # Special handling for snake_mongoose
        if "snake_mongoose" in outfile:
            df.iloc[:, 1] = np.nan

        df = df.stack().reset_index(drop=True).to_frame(name=main_column_name)
        df = df.sort_values(by=main_column_name)

        rename_map = {
            "Mongoose 2": "Mongoose II",
            "Snake 2": "Snake II",
            "Mongoose II Funny Car": "Mongoose II",
            "Snake II Funny Car": "Snake II",
            "Mongoose Funny Car": "Mongoose",
            "Snake Funny Car": "Snake",
            "Mongoose Funny Rail Dragster": "Mongoose Rail Dragster",
            "Alive 55": "Alive '55",
            "King Cuda": "King 'Cuda",
            "Grasshopper": "Grass Hopper",
        }

        df[main_column_name] = df[main_column_name].replace(rename_map)
        df = df.drop_duplicates()

        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        df.to_csv(outfile, index=False)

        log_message(f"Data saved to {outfile}.")
        return df.copy()

    except requests.RequestException as e:
        log_message(f"Error fetching the URL {url}: {e}")
    except ValueError as e:
        log_message(f"ValueError: {e}")
    except Exception:
        logger.exception(f"Unexpected error processing {url}")

    return None


def create_csv_files(main_column_name, data_dict, dict_key):
    """Create CSV files from scraped data and return a combined DataFrame."""
    all_df = []

    def thread_target(url, table_index, outfile, main_column_name):
        return scrape_url(url, table_index, outfile, main_column_name)

    try:
        log_message(f"Starting CSV creation for {dict_key}.")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            future_dict = {}

            for row in zip(*data_dict.values()):
                year_or_series, table_index = row
                outfile = f"{OUTPUT_DIR}/hotwheels-{year_or_series}.csv"
                url = f"{BASE_URL}/{year_or_series}.html"

                future = executor.submit(
                    thread_target, url, table_index, outfile, main_column_name
                )
                futures.append(future)
                future_dict[future] = year_or_series

            for future in concurrent.futures.as_completed(futures):
                df = future.result()
                if df is not None:
                    df[dict_key] = future_dict[future]
                    all_df.append(df)

    except Exception:
        log_message("Error occurred during CSV creation.")

    return pd.concat(all_df, ignore_index=True) if all_df else pd.DataFrame()


def create_combined_csv_file(main_column_name, all_years_df, all_series_df):
    """Create a combined CSV file from two DataFrames."""
    expected_columns = {main_column_name, "Year", "Series"}
    combined_columns = set(all_years_df.columns).union(all_series_df.columns)

    if not expected_columns.issubset(combined_columns):
        log_message("Missing expected columns. Skipping CSV and JSON creation.")
        return

    all_df = pd.concat([all_years_df, all_series_df], ignore_index=True)

    all_df = (
        all_df.groupby(main_column_name)
        .agg(
            {
                "Year": lambda x: sorted(set(x.dropna())),
                "Series": lambda x: sorted(set(x.dropna())),
            }
        )
        .reset_index()
    )

    csv_outfile = f"{OUTPUT_DIR}/redlines.csv"
    json_outfile = csv_outfile.replace(".csv", ".json")

    os.makedirs(os.path.dirname(csv_outfile), exist_ok=True)
    all_df.sort_values(by=main_column_name, inplace=True)
    all_df.to_csv(csv_outfile, index=False)

    log_message(f"CSV saved to {csv_outfile}.")
    all_df.to_json(json_outfile, orient="records", indent=4)
    log_message(f"JSON saved to {json_outfile}.")


def create_years_dict():
    return {
        "year": [str(year) for year in range(1968, 1978)],
        "table_index": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    }


def create_series_dict():
    return {
        "series": [
            "customs",
            "gran_prix",
            "heavyweights",
            "spoilers",
            "super_chromes",
            "snake_mongoose",
            "classics",
        ],
        "table_index": [0] * 7,
    }


def wrapper_create_csv_files(file_info):
    """Wrapper function to call create_csv_files."""
    main_column_name, data_dict, dict_key = file_info
    return create_csv_files(main_column_name, data_dict, dict_key)


def main():
    main_column_name = "Casting"
    years_dict = create_years_dict()
    series_dict = create_series_dict()

    with multiprocessing.Pool() as pool:
        log_message("Starting multiprocessing pool.")

        # Pass the function directly to pool.map()
        all_years_df = pool.map(
            wrapper_create_csv_files, [(main_column_name, years_dict, "Year")]
        )
        all_series_df = pool.map(
            wrapper_create_csv_files, [(main_column_name, series_dict, "Series")]
        )

    log_message("Creating combined CSV and JSON files...")
    create_combined_csv_file(main_column_name, all_years_df[0], all_series_df[0])
    log_message("Finished creating combined files.")


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()

    with open("output/logs/hotwheel_scrape_profile.log", "w") as f:
        sys.stdout = f
        profiler.print_stats(sort="time")
        sys.stdout = sys.__stdout__
