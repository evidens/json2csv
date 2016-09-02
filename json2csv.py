#!/usr/bin/env python

try:
    import unicodecsv as csv
except ImportError:
    import csv

import json
import operator
import os
from collections import OrderedDict
import logging

logging.basicConfig(level=logging.DEBUG)

class Json2Csv(object):
    """Process a JSON object to a CSV file"""
    collection = None

    # Better for single-nested dictionaries
    SEP_CHAR = ', '
    KEY_VAL_CHAR = ': '
    DICT_SEP_CHAR = '\r'
    DICT_OPEN = ''
    DICT_CLOSE = ''

    # Better for deep-nested dictionaries
    # SEP_CHAR = ', '
    # KEY_VAL_CHAR = ': '
    # DICT_SEP_CHAR = '; '
    # DICT_OPEN = '{ '
    # DICT_CLOSE = '} '

    def __init__(self, outline):
        self.rows = []

        if not isinstance(outline, dict):
            raise ValueError('You must pass in an outline for JSON2CSV to follow')
        elif 'map' not in outline or len(outline['map']) < 1:
            raise ValueError('You must specify at least one value for "map"')

        key_map = OrderedDict()
        for header, key in outline['map']:
            splits = key.split('.')
            splits = [int(s) if s.isdigit() else s for s in splits]
            key_map[header] = splits

        self.key_map = key_map
        if 'collection' in outline:
            self.collection = outline['collection']

    def iterate_json(self, json_file):
        json_data = json.load(json_file)

        if self.collection and self.collection in json_data:
            json_data = json_data[self.collection]

        for item in json_data:
            yield item

    def transcribe(self, json_file, csv_writer, to_strings=True):
        for item in self.iterate_json(json_file):
            logging.info(item)
            row = self.process_row(item)

            if to_strings:
                row = {k: self.make_string(val) for k, val in row.items()}

            csv_writer.writerow(row)

    def process_row(self, item):
        """Process a row of json data against the key map
        """
        row = {}

        for header, keys in self.key_map.items():
            try:
                row[header] = reduce(operator.getitem, keys, item)
            except (KeyError, IndexError, TypeError):
                row[header] = None

        return row

    def make_string(self, item):
        if isinstance(item, list) or isinstance(item, set) or isinstance(item, tuple):
            return self.SEP_CHAR.join([self.make_string(subitem) for subitem in item])
        elif isinstance(item, dict):
            return self.DICT_OPEN + self.DICT_SEP_CHAR.join([self.KEY_VAL_CHAR.join([k, self.make_string(val)]) for k, val in item.items()]) + self.DICT_CLOSE
        else:
            return unicode(item)


class MultiLineJson2Csv(Json2Csv):
    def iterate_json(self, json_file):
        """Load each line of a Mongo-like JSON file separately"""
        for line in json_file:
            item = json.loads(line)

            if self.collection and self.collection in item:
                item = item[self.collection]

            yield item




def init_parser():
    import argparse
    parser = argparse.ArgumentParser(description="Converts JSON to CSV")
    parser.add_argument('json_file', type=argparse.FileType('r'),
                        help="Path to JSON data file to load")
    parser.add_argument('key_map', type=argparse.FileType('r'),
                        help="File containing JSON key-mapping file to load")
    parser.add_argument('-e', '--each-line', action="store_true", default=False,
                        help="Process each line of JSON file separately")
    parser.add_argument('-o', '--output-csv', type=str, default=None,
                        help="Path to csv file to output")
    parser.add_argument(
        '--strings', help="Convert lists, sets, and dictionaries fully to comma-separated strings.", action="store_true", default=True)

    return parser

if __name__ == '__main__':
    args = init_parser().parse_args()

    key_map = json.load(args.key_map)

    if args.each_line:
        loader = MultiLineJson2Csv(key_map)
    else:
        loader = Json2Csv(key_map)

    output_csv = args.output_csv
    if output_csv is None:
        file_name, ext = os.path.splitext(args.json_file.name)
        output_csv = file_name + '.csv'

    with open(output_csv, 'wb+') as f:
        writer = csv.DictWriter(f, loader.key_map.keys())
        writer.writeheader()

        loader.transcribe(args.json_file, writer, args.strings)
