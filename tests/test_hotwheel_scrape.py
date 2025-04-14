from unittest.mock import patch, MagicMock
import os
import pandas as pd
import pytest
import sys
import tempfile

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from hotwheel_scrape import (
    scrape_url,
    create_csv_files,
    create_combined_csv_file,
    create_years_dict,
    create_series_dict,
    wrapper_create_csv_files,
)

# Sample HTML table for mocking
HTML_TABLE = """
<table>
  <tr><th>Name</th></tr>
  <tr><td>Snake</td></tr>
  <tr><td>Mongoose</td></tr>
</table>
"""


@pytest.fixture
def tmp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@patch("hotwheel_scrape.requests.get")
@patch("hotwheel_scrape.os.makedirs")
def test_scrape_url_success(mock_makedirs, mock_get, tmp_output_dir):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = HTML_TABLE
    mock_get.return_value = mock_response

    outfile = os.path.join(tmp_output_dir, "test_output.csv")
    df = scrape_url("https://fakeurl.com", 0, outfile, "Casting")

    assert df is not None
    assert "Casting" in df.columns
    assert "Snake" in df["Casting"].values
    assert os.path.exists(outfile)


@patch("hotwheel_scrape.requests.get")
def test_scrape_url_no_table(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>No table here</body></html>"
    mock_get.return_value = mock_response

    result = scrape_url("https://fakeurl.com", 0, "irrelevant.csv", "Casting")
    assert result is None


@patch("hotwheel_scrape.requests.get")
def test_scrape_url_invalid_url(mock_get):
    mock_get.side_effect = Exception("Connection error")
    result = scrape_url("https://invalidurl.com", 0, "dummy.csv", "Casting")
    assert result is None


@patch("hotwheel_scrape.requests.get")
def test_scrape_url_timeout(mock_get):
    from requests.exceptions import Timeout

    mock_get.side_effect = Timeout("Request timed out")
    result = scrape_url("https://slowurl.com", 0, "dummy.csv", "Casting")
    assert result is None


@patch("hotwheel_scrape.requests.get")
def test_scrape_url_empty_table(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<table></table>"
    mock_get.return_value = mock_response

    result = scrape_url("https://fakeurl.com", 0, "dummy.csv", "Casting")
    assert result is None


@patch("hotwheel_scrape.scrape_url")
def test_create_csv_files(mock_scrape):
    mock_df = pd.DataFrame({"Casting": ["Mongoose", "Snake"]})
    mock_scrape.return_value = mock_df

    data_dict = {"year": ["1968"], "table_index": [0]}
    result_df = create_csv_files("Casting", data_dict, "Year")

    assert not result_df.empty
    assert "Casting" in result_df.columns
    assert "Year" in result_df.columns


def test_create_combined_csv_file(tmp_output_dir):
    df1 = pd.DataFrame(
        {
            "Casting": ["Mongoose", "Snake"],
            "Year": ["1968", "1969"],
            "Series": [None, None],
        }
    )
    df2 = pd.DataFrame(
        {
            "Casting": ["Mongoose", "Snake"],
            "Year": [None, None],
            "Series": ["snake_mongoose", "snake_mongoose"],
        }
    )

    out_csv = os.path.join(tmp_output_dir, "redlines.csv")
    out_json = out_csv.replace(".csv", ".json")

    with patch("hotwheel_scrape.OUTPUT_DIR", tmp_output_dir):
        create_combined_csv_file("Casting", df1, df2)

        assert os.path.exists(out_csv)
        assert os.path.exists(out_json)


def test_create_combined_csv_file_with_empty_df(tmp_output_dir):
    df1 = pd.DataFrame(columns=["Casting", "Year", "Series"])
    df2 = pd.DataFrame(columns=["Casting", "Year", "Series"])

    with patch("hotwheel_scrape.OUTPUT_DIR", tmp_output_dir):
        create_combined_csv_file("Casting", df1, df2)
        assert os.path.exists(os.path.join(tmp_output_dir, "redlines.csv"))


@patch("hotwheel_scrape.os.makedirs")
def test_file_write_permission_error(mock_makedirs):
    mock_makedirs.side_effect = PermissionError("Permission denied")
    result = scrape_url("https://fakeurl.com", 0, "/forbidden/test.csv", "Casting")
    assert result is None


@patch("hotwheel_scrape.logger.exception")
def test_logging_exception_on_error(mock_exception):
    with patch("hotwheel_scrape.requests.get", side_effect=Exception("Boom!")):
        scrape_url("https://fakeurl.com", 0, "dummy.csv", "Casting")

    mock_exception.assert_called_once()


def test_create_years_dict():
    years = create_years_dict()
    assert "year" in years
    assert "table_index" in years
    assert len(years["year"]) == 10


def test_create_series_dict():
    series = create_series_dict()
    assert "series" in series
    assert "table_index" in series
    assert len(series["series"]) == 7


@patch("hotwheel_scrape.create_csv_files")
def test_wrapper_create_csv_files(mock_create):
    mock_create.return_value = pd.DataFrame({"Casting": ["Test"]})
    result = wrapper_create_csv_files(
        ("Casting", {"year": ["1968"], "table_index": [0]}, "Year")
    )
    assert not result.empty


@patch("hotwheel_scrape.scrape_url")
def test_create_csv_files_with_failure(mock_scrape):
    mock_scrape.side_effect = [None, pd.DataFrame({"Casting": ["Valid"]})]

    data_dict = {"year": ["1968", "1969"], "table_index": [0, 0]}
    result_df = create_csv_files("Casting", data_dict, "Year")

    assert not result_df.empty
    assert "Casting" in result_df.columns
