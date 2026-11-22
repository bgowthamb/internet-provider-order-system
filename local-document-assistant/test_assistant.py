import tempfile
import unittest
from pathlib import Path
from assistant import index_folder, answer, search


class TestAssistant(unittest.TestCase):
    def test_local_lookup_and_no_match(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'sample.txt').write_text('Demo membership reference: EXAMPLE-123', encoding='utf-8')
            passages, warnings = index_folder(folder)
            self.assertFalse(warnings)
            self.assertEqual(len(search('membership reference', passages)), 1)
            self.assertIn('EXAMPLE-123', answer('membership reference', passages))
            self.assertIn('sample.txt', answer('membership reference', passages))
            self.assertIn('No matching', answer('banana', passages))
