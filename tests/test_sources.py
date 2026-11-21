from __future__ import annotations

import shutil
from pathlib import Path
import tempfile
import unittest

from check_sources import load_sources

DATA = Path(__file__).resolve().parents[1] / 'data'


class ExchangeTests(unittest.TestCase):
    def test_example_is_readable(self):
        tables = load_sources(DATA)
        self.assertTrue(all(tables.values()))
        self.assertEqual({r['board'] for r in tables['scores'] if r['engine'] == 'old'}, {r['id'] for r in tables['boards']})
        self.assertEqual({r['board'] for r in tables['scores'] if r['engine'] == 'new'}, {r['id'] for r in tables['boards']})
        self.assertTrue(all(0 < float(r['probability']) <= 1 and set(r['positive'].split(',')) <= set(r['known'].split(',')) for r in tables['audits']))
        self.assertTrue(any(r['job'] for r in tables['stations']))

    def test_duplicate_identity_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / 'copies'
            shutil.copytree(DATA, duplicate)
            path = duplicate / 'ontology.csv'
            rows = path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(rows + [rows[1]]) + '\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '标识为空或重复'):
                load_sources(duplicate)
