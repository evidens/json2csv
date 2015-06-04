# JSON2CSV

A converter to extract nested JSON data to CSV files.

Created specifically to convert multi-line Mongo query results to a single CSV (since data nerds like CSV).

## Installation

    git clone https://github.com/evidens/json2csv.git
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

## Generating outline files

To automatically generate an outline file from a json file:

    python gen_outline.py --collection nodes /path/to/the.json

This will generate an outline file with the union of all keys in the json
collection at `/path/to/the.outline.json`.  You can specify the output file
with the `-o` option, as above.

