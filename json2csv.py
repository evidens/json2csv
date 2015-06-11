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

    def load(self, json_file):
        self.process_each(json.load(json_file))

    def process_each(self, data):
        """Process each item of a json-loaded dict
        """
        if self.collection and self.collection in data:
            data = data[self.collection]

        for d in data:
            logging.info(d)
            self.rows.append(self.process_row(d))

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

    def make_strings(self):
        str_rows = []
        for row in self.rows:
            str_rows.append({k: self.make_string(val)
                             for k, val in row.items()})
        return str_rows

    def make_string(self, item):
        if isinstance(item, list) or isinstance(item, set) or isinstance(item, tuple):
            return self.SEP_CHAR.join([self.make_string(subitem) for subitem in item])
        elif isinstance(item, dict):
            return self.DICT_OPEN + self.DICT_SEP_CHAR.join([self.KEY_VAL_CHAR.join([k, self.make_string(val)]) for k, val in item.items()]) + self.DICT_CLOSE
        else:
            return unicode(item)

    def write_csv(self, filename='output.csv', make_strings=False):
        """Write the processed rows to the given filename
        """
        if (len(self.rows) <= 0):
            raise AttributeError('No rows were loaded')
        if make_strings:
            out = self.make_strings()
        else:
            out = self.rows
        with open(filename, 'wb+') as f:
            writer = csv.DictWriter(f, self.key_map.keys())
            writer.writeheader()
            writer.writerows(out)


class MultiLineJson2Csv(Json2Csv):
    def load(self, json_file):
        self.process_each(json_file)

    def process_each(self, data, collection=None):
        """Load each line of an iterable collection (ie. file)"""
        for line in data:
            d = json.loads(line)
            if self.collection in d:
                d = d[self.collection]
            self.rows.append(self.process_row(d))


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
    parser = init_parser()
    args = parser.parse_args()

    key_map = json.load(args.key_map)
    loader = None
    if args.each_line:
        loader = MultiLineJson2Csv(key_map)
    else:
        loader = Json2Csv(key_map)

    loader.load(args.json_file)

    outfile = args.output_csv
    if outfile is None:
        fileName, fileExtension = os.path.splitext(args.json_file.name)
        outfile = fileName + '.csv'

    loader.write_csv(filename=outfile, make_strings=args.strings)
