"""Check the published track's geometry and deliberately limited data export."""
import json
import math
from pathlib import Path
import unittest


class HikeDataTests(unittest.TestCase):
    def test_track_summary_and_public_fields(self):
        source = Path(__file__).resolve().parents[1] / 'static/posts/26-11-16-marmolada/route.json'
        data = json.loads(source.read_text())
        self.assertEqual(set(data), {'summary', 'coordinates', 'distanceKm'})
        self.assertEqual(set(data['summary']), {'date', 'distanceKm', 'ascentM', 'descentM',
            'elapsedSeconds', 'minElevationM', 'maxElevationM', 'highestIndex', 'bounds'})
        points = data['coordinates']
        distances = data['distanceKm']
        summary = data['summary']
        self.assertEqual(len(points), len(distances))
        self.assertGreater(len(points), 1000)
        self.assertEqual(distances, sorted(distances))
        self.assertAlmostEqual(distances[-1], summary['distanceKm'], places=2)
        self.assertEqual(points[summary['highestIndex']][2], summary['maxElevationM'])
        self.assertEqual(summary['date'], '2026-08-09')
        self.assertEqual(summary['ascentM'], 1887)
        for lon, lat, elevation in points:
            self.assertTrue(all(math.isfinite(value) for value in (lon, lat, elevation)))
            self.assertTrue(summary['bounds'][0][0] <= lon <= summary['bounds'][1][0])
            self.assertTrue(summary['bounds'][0][1] <= lat <= summary['bounds'][1][1])
            self.assertTrue(summary['minElevationM'] <= elevation <= summary['maxElevationM'])


if __name__ == '__main__':
    unittest.main()
