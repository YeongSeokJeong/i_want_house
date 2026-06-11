from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jeonseloop.watchlist import WatchlistError, load_watchlist


class WatchlistTests(unittest.TestCase):
    def test_loads_sample_watchlist(self) -> None:
        watchlist = load_watchlist(ROOT / "config" / "watchlist.yaml")

        self.assertEqual(watchlist.version, 1)
        self.assertEqual(len(watchlist.complexes), 1)
        self.assertEqual(watchlist.complexes[0].complex_id, "sample-apt")
        self.assertGreaterEqual(watchlist.request_interval_seconds, 2)

    def test_rejects_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "watchlist.yaml"
            path.write_text("complexes:\n  - complex_id: bad\n", encoding="utf-8")

            with self.assertRaises(WatchlistError):
                load_watchlist(path)

    def test_empty_watchlist_is_valid_but_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "watchlist.yaml"
            path.write_text("complexes: []\n", encoding="utf-8")

            watchlist = load_watchlist(path)

        self.assertEqual(watchlist.complexes, ())


if __name__ == "__main__":
    unittest.main()
