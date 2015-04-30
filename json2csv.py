#!/usr/bin/env python

import unicodecsv as csv
import json
import operator
import os
from collections import OrderedDict
import logging

logging.basicConfig(level=logging.DEBUG)


class Json2Csv(object):
    """Process a JSON object to a CSV file"""
    collection = None
    rows = None

    def __init__(self, outline):
        if not type(outline) is dict:
            raise ValueError('You must pass in an outline for JSON2CSV to follow')
        elif 'map' not in outline or len(outline['map']) < 1:
            raise ValueError('You must specify at least one value for "map"')

        self.key_map = self.process_key_map(outline['map'])
        if 'collection' in outline:
            self.collection = outline['collection']

    @staticmethod
    def process_key_map(raw_map):
        key_map = OrderedDict()
        for header, key in raw_map:
            key_map[header] = Json2Csv.make_key_drilldown(key)

        return key_map

    @staticmethod
    def make_key_drilldown(key):
        splits = key.split('.')
        splits = [int(s) if s.isdigit() else s for s in splits]

        return splits

    @staticmethod
    def process_each(data, key_map, collection=None):
        """Process each item of a json-loaded dict
        """
        rows = []

        if collection and collection in data:
            data = data[collection]

        for d in data:
            logging.info(d)
            rows.append(Json2Csv.process_row(d, key_map))

        return rows

    @staticmethod
    def process_row(row, key_map):
        """Process a row of json data against the key map
        """
        result = {}

        for header, keys in key_map.items():
            try:
                result[header] = reduce(operator.getitem, keys, row)
            except (KeyError, TypeError):
                result[header] = None

        return result

    def load_json(self, data):
        self.rows = self.process_each(data, self.key_map, self.collection)

    def load(self, json_file):
        self.load_json(json.load(json_file))

    def write_csv(self, filename='output.csv'):
        """Write the processed rows to the given filename
        """
        if len(self.rows) <= 0:
            raise AttributeError('No rows were loaded')
        with open(filename, 'wb+') as f:
            writer = csv.DictWriter(f, self.key_map.keys())
            writer.writeheader()
            writer.writerows(self.rows)


class MultiLineJson2Csv(Json2Csv):
    def load(self, json_file):
        self.process_each(json_file)

    def process_each(self, data, collection=None):
        """Load each line of an iterable collection (ie. file)"""
        for line in data:
            d = json.loads(line)
            if self.collection in data:
                data = data[self.collection]
            self.rows.append(self.process_row(d))


def init_parser():
    import argparse
    parser = argparse.ArgumentParser(description="Converts JSON to CSV")
    parser.add_argument('json_file', type=argparse.FileType('r'), help="Path to JSON data file to load")
    parser.add_argument('key_map', type=argparse.FileType('r'), help="File containing JSON key-mapping file to load")
    parser.add_argument('-e', '--each-line', action="store_true", default=False,
                        help="Process each line of JSON file separately")
    parser.add_argument('-o', '--output-csv', type=str, default=None,
                        help="Path to csv file to output")

    return parser


def main(args):
    """Load a JSON file and output to a CSV
    """
    key_map = json.load(args.key_map)
    if args.each_line:
        loader = MultiLineJson2Csv(key_map)
    else:
        loader = Json2Csv(key_map)

    loader.load(args.json_file)

    outfile = args.output_csv
    if outfile is None:
        file_name, ext = os.path.splitext(args.json_file.name)
        outfile = file_name + '.csv'

    loader.write_csv(filename=outfile)

if __name__ == '__main__':
    main(init_parser().parse_args())
