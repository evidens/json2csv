# JSON2CSV

A convert to extract nested JSON data to CSV files

## Installation

    git clone https://github.com/beyondwords/json2csv.git
    cd json2csv
    pip install -r requirements.txt

## Usage

Basic (convert from a JSON file to a CSV file in same path):

    python json2csv.py /path/to/json_file.json /path/to/outline_file.json

Specify CSV file

    python json2csv.py /path/to/json_file.json /path/to/outline_file.json -o /some/other/file.csv


For this JSON file:

    {
      "nodes": [
        {"source": {"author": "Someone"}, "message": {"original": "Hey!", "Revised": "Hey yo!"}},
        {"source": {"author": "Another"}, "message": {"original": "Howdy!", "Revised": "Howdy partner!"}},
        {"source": {"author": "Me too"}, "message": {"original": "Yo!", "Revised": "Yo, 'sup?"}}
      ]
    }

Use this outline file:

    {
      "map": [
        ["author", "source.author"],
        ["message", "message.original"]
      ],
      "collection": "nodes"
    }



