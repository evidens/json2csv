import unittest
import json
from json2csv import Json2Csv, MultiLineJson2Csv
from gen_outline import make_outline


class TestJson2Csv(unittest.TestCase):

    def test_init(self):
        outline = {'map': [['some_header', 'some_key']]}
        loader = Json2Csv(outline)
        self.assertIn('some_header', loader.key_map)

        self.assertRaises(ValueError, Json2Csv, None)

        self.assertRaises(ValueError, Json2Csv, {})

    def test_process_row(self):
        """Given a valid key-map and data, it should return a valid row"""
        outline = {'map': [['id', '_id'], ['count', 'count']]}
        loader = Json2Csv(outline)
        test_data = json.loads('{"_id" : "Someone","count" : 1}')
        row = loader.process_row(test_data)

        self.assertIs(type(row), dict)
        self.assertIn('id', row.keys())
        self.assertIn('count', row.keys())

        self.assertEquals(row['id'], 'Someone')
        self.assertEquals(row['count'], 1)

    def test_process_row_nested_data(self):
        """Ensure that nested keys (with . notation) are processed"""
        key_map = {"map": [['author', 'source.author'], ['message', 'message.original']]}
        loader = Json2Csv(key_map)
        test_data = json.loads(
            '{"source": {"author": "Someone"}, "message": {"original": "Hey!", "Revised": "Hey yo!"}}'
        )
        row = loader.process_row(test_data)

        self.assertIs(type(row), dict)
        self.assertIn('author', row.keys())
        self.assertIn('message', row.keys())

        self.assertEquals(row['author'], 'Someone')
        self.assertEquals(row['message'], 'Hey!')

    def test_process_row_array_index(self):
        """Ensure that array indices are properly handled as part of the dot notation"""
        pass

    def test_process_each(self):
        outline = {'map': [['id', '_id'], ['count', 'count']], 'collection': 'result'}
        loader = Json2Csv(outline)

        test_data = json.loads('{"result":[{"_id" : "Someone","count" : 1}]}')
        loader.process_each(test_data)

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
        outline = {'map': [['id', '_id'], ['count', 'count'], ['tags_0', 'tags.0']]}
        loader = Json2Csv(outline)

        test_data = json.loads('''[
          {"_id": "Someone","count": 1, "tags": ["super"]},
          {"_id": "Another", "tags": []}]''')
        self.assertEquals(len(test_data), 2)
        loader.process_each(test_data)

        self.assertEquals(len(loader.rows), 2)
        second_row = loader.rows[1]
        self.assertEquals(second_row['id'], 'Another')
        # works for missing dict keys
        self.assertIsNone(second_row['count'])
        # and missing list indices
        self.assertIsNone(second_row['tags_0'])

    def test_load_json(self):
        outline = {"map": [['author', 'source.author'], ['message', 'message.original']], "collection": "nodes"}
        loader = Json2Csv(outline)
        with open('fixtures/data.json') as f:
            loader.load(f)

        first_row = loader.rows[0]
        self.assertEqual(first_row['author'], 'Someone')
        second_row = loader.rows[1]
        self.assertEqual(second_row['author'], 'Another')
        third_row = loader.rows[2]
        self.assertEqual(third_row['author'], 'Me too')

    def test_load_bare_json(self):
        outline = {"map": [['author', 'source.author'], ['message', 'message.original']]}
        loader = Json2Csv(outline)
        with open('fixtures/bare_data.json') as f:
            loader.load(f)

        first_row = loader.rows[0]
        self.assertEqual(first_row['author'], 'Someone')
        second_row = loader.rows[1]
        self.assertEqual(second_row['author'], 'Another')
        third_row = loader.rows[2]
        self.assertEqual(third_row['author'], 'Me too')

    def test_write_csv(self):
        pass


class TestMultiLineJson2Csv(unittest.TestCase):

    def test_line_delimited(self):
        outline = {"map": [['author', 'source.author'], ['message', 'message.original']]}
        loader = MultiLineJson2Csv(outline)
        with open('fixtures/line_delimited.json') as f:
            loader.load(f)

        first_row = loader.rows[0]
        self.assertEqual(first_row['author'], 'Someone')
        second_row = loader.rows[1]
        self.assertEqual(second_row['author'], 'Another')
        third_row = loader.rows[2]
        self.assertEqual(third_row['author'], 'Me too')


class TestGenOutline(unittest.TestCase):

    def test_basic(self):
        with open('fixtures/data.json') as json_file:
            outline = make_outline(json_file, False, 'nodes')
            expected = {
                'collection': 'nodes',
                'map': [
                    ('message_Revised', 'message.Revised'),
                    ('message_original', 'message.original'),
                    ('source_author', 'source.author'),
                ]
            }
            self.assertEqual(outline, expected)

    def test_deeply_nested(self):
        with open('fixtures/deeply_nested.json') as json_file:
            outline = make_outline(json_file, False, 'nodes')
            expected = {
                'collection': 'nodes',
                'map': [
                    ('one_0_two_0_three_0', 'one.0.two.0.three.0'),
                    ('one_0_two_0_three_1', 'one.0.two.0.three.1'),
                    ('one_0_two_0_three_2', 'one.0.two.0.three.2'),
                    ('one_0_two_1_three_0', 'one.0.two.1.three.0'),
                    ('one_0_two_1_three_1', 'one.0.two.1.three.1'),
                    ('one_0_two_1_three_2', 'one.0.two.1.three.2'),
                ]
            }
            self.assertEqual(outline, expected)

    def test_different_keys_per_row(self):
        "Outline should contain the union of the keys."
        with open('fixtures/different_keys_per_row.json') as json_file:
            outline = make_outline(json_file, False, 'nodes')
            expected = {
                'collection': 'nodes',
                'map': [
                    ('tags_0', 'tags.0'),
                    ('tags_1', 'tags.1'),
                    ('tags_2', 'tags.2'),
                    ('that', 'that'),
                    ('theother', 'theother'),
                    ('this', 'this'),
                ]
            }
            self.assertEqual(outline, expected)

    def test_line_delimited(self):
        with open('fixtures/line_delimited.json') as json_file:
            outline = make_outline(json_file, True, None)
            expected = {
                'map': [
                    ('message_Revised', 'message.Revised'),
                    ('message_original', 'message.original'),
                    ('source_author', 'source.author'),
                ]
            }
            self.assertEqual(outline, expected)
