import unittest
import json
from json2csv import Json2Csv, MultiLineJson2Csv

class TestJson2Csv(unittest.TestCase):

    def test_init(self):
        key_map = {'some_header': 'some_key'}
        loader = Json2Csv(key_map)
        self.assertEquals(loader.key_map, key_map)

        self.assertRaises(ValueError, Json2Csv, None)

        self.assertRaises(ValueError, Json2Csv, {})

    def test_process_row(self):
        "Given a valid key-map and data, it should return a valid row"
        key_map = {'id': '_id', 'count': 'count'}
        loader = Json2Csv(key_map)
        test_data = json.loads('{"_id" : "Someone","count" : 1}')
        row = loader.process_row(test_data)

        self.assertIs(type(row), dict)
        self.assertIn('id', row.keys())
        self.assertIn('count', row.keys())

        self.assertEquals(row['id'], 'Someone')
        self.assertEquals(row['count'], 1)

    def test_process_row_nested_data(self):
        "Ensure that nested keys (with . notation) are processed"
        key_map = {'author': 'source.author', 'message': 'message.original'}
        loader = Json2Csv(key_map)
        test_data = json.loads('{"source": {"author": "Someone"}, "message": {"original": "Hey!", "Revised": "Hey yo!"}}')
        row = loader.process_row(test_data)

        self.assertIs(type(row), dict)
        self.assertIn('author', row.keys())
        self.assertIn('message', row.keys())

        self.assertEquals(row['author'], 'Someone')
        self.assertEquals(row['message'], 'Hey!')

    def test_process_row_array_index(self):
        "Ensure that aray indices are properly handled as part of the dot notation"
        pass

    def test_process_each(self):
        key_map = {'id': '_id', 'count': 'count'}
        loader = Json2Csv(key_map)

        test_data = json.loads('{"result":[{"_id" : "Someone","count" : 1}]}')
        loader.process_each(test_data, collection='result')

        self.assertEquals(len(loader.rows), 1)
        row = loader.rows[0]
        self.assertIs(type(row), dict)
        self.assertIn('id', row.keys())
        self.assertIn('count', row.keys())

        self.assertEquals(row['id'], 'Someone')
        self.assertEquals(row['count'], 1)

    def test_process_each_optional_key(self):
        """Ensure a key that is not always present won't prevent data extraction
        Where the data is missing, None is returned
        """
        key_map = {'id': '_id', 'count': 'count'}
        loader = Json2Csv(key_map)

        test_data = json.loads('[{"_id" : "Someone","count" : 1}, {"_id": "Another"}]')
        self.assertEquals(len(test_data), 2)
        loader.process_each(test_data)

        self.assertEquals(len(loader.rows), 2)
        second_row = loader.rows[1]
        self.assertEquals(second_row['id'], 'Another')
        self.assertIsNone(second_row['count'])

    def test_load(self):
        pass

    def test_write_csv(self):
        pass
    