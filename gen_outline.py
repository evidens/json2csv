#!/usr/bin/env python

import json
import os, os.path

def key_paths(d):
    def helper(path, x):
        if isinstance(x, dict):
            for k, v in x.iteritems():
                for ret in helper(path + [k], v):
                    yield ret
        elif isinstance(x, list):
            for i, item in enumerate(x):
                for ret in helper(path + [i], item):
                    yield ret
        else:
            yield path
    return helper([], d)

def line_iter(f):
    for line in f:
        yield json.loads(line)

def coll_iter(f, coll_key):
    data = json.load(f)
    for obj in data[coll_key]:
        yield obj

def gather_key_map(iterator):
    key_map = {}
    for d in iterator:
        for path in key_paths(d):
            key_map[tuple(path)] = True
    return key_map

def path_join(path, sep='.'):
    return sep.join(str(k) for k in path)

def key_map_to_list(key_map):
    # We convert to strings *after* sorting so that array indices come out
    # in the correct order.
    return [(path_join(k, '_'), path_join(k)) for k in sorted(key_map.keys())]

def make_outline(json_file, each_line, collection_key):
    if each_line:
        iterator = line_iter(json_file)
    else:
        iterator = coll_iter(json_file, collection_key)

    key_map = gather_key_map(iterator)
    outline = {'map': key_map_to_list(key_map)}
    if collection_key:
        outline['collection'] = collection_key

    return outline

def init_parser():
    import argparse
    parser = argparse.ArgumentParser(description="Generate an outline file for json2csv.py")
    parser.add_argument('json_file', type=argparse.FileType('r'),
                        help="Path to JSON data file to analyze")
    parser.add_argument('-o', '--output-file', type=str, default=None,
                        help="Path to outline file to output")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--each-line', action="store_true", default=False,
                       help="Process each line of JSON file separately")
    group.add_argument('-c', '--collection', type=str, default=None,
                       help="Key in JSON of array to process", metavar="KEY")

    return parser

def main():
    parser = init_parser()
    args = parser.parse_args()
    outline = make_outline(args.json_file, args.each_line, args.collection)
    outfile = args.output_file
    if outfile is None:
        fileName, fileExtension = os.path.splitext(args.json_file.name)
        outfile = fileName + '.outline.json'

    with open(outfile, 'w') as f:
        json.dump(outline, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()
