import unittest

from pytrackdat.generation import design_to_relation_fields, GenerationError


class TestDesignFileParsing(unittest.TestCase):
    def test_two_auto_keys(self):
        with self.assertRaises(GenerationError):
            with open("./tests/design_files/two_auto_keys.csv") as tf:
                design_to_relation_fields(tf, False)
