import tempfile
import unittest
from pathlib import Path
from pipeline import publish, transform

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.source = self.root / 'input.csv'
    def write(self, rows):
        self.source.write_text('date,region,megawatt_hours\n' + rows)
    def test_decimal_total(self):
        self.write('2026-01-01,A,0.1\n2026-01-01,B,0.2\n')
        self.assertEqual(transform(self.source)['total_megawatt_hours'], '0.3')
    def test_duplicates_rejected(self):
        self.write('2026-01-01,A,1\n2026-01-01,A,2\n')
        with self.assertRaises(ValueError): transform(self.source)
    def test_nonfinite_rejected(self):
        self.write('2026-01-01,A,NaN\n')
        with self.assertRaises(ValueError): transform(self.source)
    def test_bad_date_rejected(self):
        self.write('2026-02-30,A,1\n')
        with self.assertRaises(ValueError): transform(self.source)
    def test_failed_validation_preserves_output(self):
        out = self.root / 'out.json'; out.write_text('previous')
        self.write('2026-01-01,A,-1\n')
        with self.assertRaises(ValueError): publish(self.source, out)
        self.assertEqual(out.read_text(), 'previous')
    def test_valid_dataset_published(self):
        self.write('2026-01-01,A,1\n'); out = self.root / 'out.json'
        self.assertEqual(publish(self.source, out)['record_count'], 1)
        self.assertTrue(out.exists())
