# JSON2CSV

A convert to extract nested JSON data to CSV files

## Installation

    pip install -e git+https://github.com/beyondwords/json2csv.git#egg=json2csv
    cd json2csv
    pip install -r requirements.txt

## Usage

Basic (convert from a JSON file to a CSV file in same path):

    python json2csv.py /path/to/json_file.json /path/to/key_map_file.json

Specify CSV file

    python json2csv.py /path/to/json_file.json /path/to/key_map_file.json -o /some/other/file.csv


