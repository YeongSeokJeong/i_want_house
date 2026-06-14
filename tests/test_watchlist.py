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

    def test_rejects_request_interval_below_minimum(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "watchlist.yaml"
            path.write_text("request_interval_seconds: 1\ncomplexes: []\n", encoding="utf-8")

            with self.assertRaises(WatchlistError):
                load_watchlist(path)

    def test_empty_watchlist_is_valid_but_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "watchlist.yaml"
            path.write_text("complexes: []\n", encoding="utf-8")

            watchlist = load_watchlist(path)

        self.assertEqual(watchlist.complexes, ())

    def test_loads_inline_lists_and_quoted_comment_characters(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "watchlist.yaml"
            path.write_text(
                """
version: 1
request_interval_seconds: 2
complexes:
  - complex_id: quoted-apt
    name: "Sample: Apartment #1" # trailing comments are ignored
    area_m2: 59.5
    target_price_krw: 650000000
    urgent_discount_ratio: 0.08
    exclude: ["basement", "auction # review", "tenant: occupied"]
""".lstrip(),
                encoding="utf-8",
            )

            watchlist = load_watchlist(path)

        target = watchlist.complexes[0]
        self.assertEqual(target.name, "Sample: Apartment #1")
        self.assertEqual(target.exclude, ("basement", "auction # review", "tenant: occupied"))

    def test_rejects_malformed_inline_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "watchlist.yaml"
            path.write_text(
                """
complexes:
  - complex_id: bad
    name: Bad Apartment
    area_m2: 84
    target_price_krw: 700000000
    exclude: ["basement", ]
""".lstrip(),
                encoding="utf-8",
            )

            with self.assertRaises(WatchlistError):
                load_watchlist(path)


if __name__ == "__main__":
    unittest.main()
