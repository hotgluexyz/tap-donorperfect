"""Verify count queries retain sync filters and fail without changing sync state."""

from copy import deepcopy
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import requests

from tap_donorperfect.tap import TapDonorperfect


class EstimatedRecordCountTests(unittest.TestCase):
    def setUp(self):
        self.tap = TapDonorperfect(
            config={"api_token": "test%2Btoken", "start_date": "2025-01-01T00:00:00Z"}
        )

    def test_count_preserves_joins_and_start_date(self):
        sources = {
            "donors": "dp",
            "flags": (
                "dpflags LEFT JOIN dpcodes dc ON dc.code = dpflags.flag "
                "AND dc.field_name = 'FLAG' LEFT JOIN dp ON dp.donor_id = dpflags.donor_id"
            ),
            "donor_addresses": "DPADDRESS dpa JOIN dp dp ON dpa.donor_id = dp.donor_id",
        }
        for name, source in sources.items():
            with self.subTest(stream=name):
                stream = self.tap.streams[name]
                stream._write_starting_replication_value(None)
                stream.replication_key_value = "original"
                stream.next_page_token = 200
                state = deepcopy(self.tap.state)
                response = requests.Response()
                response._content = (
                    b'<result><record><field name="estimated_count" '
                    b'id="estimated_count" value="534"/></record></result>'
                )
                with patch.object(stream, "_request", return_value=response) as request:
                    self.assertEqual(stream.get_estimated_record_count(), 534)
                request.assert_called_once()
                params = parse_qs(urlsplit(request.call_args.args[0].url).query)
                self.assertEqual(params["apikey"], ["test+token"])
                self.assertEqual(params["internal_modified_date"], ["2025-01-01 00:00:01"])
                self.assertEqual(
                    params["action"][0].strip(),
                    f"SELECT COUNT(*) AS estimated_count FROM {source} "
                    "WHERE internal_modified_date>'2025-01-01 00:00:01'",
                )
                self.assertEqual(stream.replication_key_value, "original")
                self.assertEqual(stream.next_page_token, 200)
                self.assertEqual(self.tap.state, state)

    def test_bookmark_window_and_zero_count(self):
        tap = TapDonorperfect(
            config=dict(self.tap.config),
            state={
                "bookmarks": {
                    "donors": {
                        "replication_key": "internal_modified_date",
                        "replication_key_value": "2026-09-14T22:25:10Z",
                    }
                }
            },
        )
        stream = tap.streams["donors"]
        stream._write_starting_replication_value(None)
        response = requests.Response()
        response._content = (
            b'<result><record><field name="estimated_count" '
            b'id="estimated_count" value="0"/></record></result>'
        )
        with patch.object(stream, "_request", return_value=response) as request:
            self.assertEqual(stream.get_estimated_record_count(), 0)
        params = parse_qs(urlsplit(request.call_args.args[0].url).query)
        self.assertEqual(
            params["action"][0].strip(),
            "SELECT COUNT(*) AS estimated_count FROM dp "
            "WHERE internal_modified_date>'2026-09-14 22:25:11'",
        )

    def test_failures_return_none_and_restore_state_without_logging_credentials(self):
        stream = self.tap.streams["donors"]
        stream._write_starting_replication_value(None)
        stream.replication_key_value = "original"
        for body in (
            b"<result><error>SQL error</error></result>",
            b'<result><record><field name="estimated_count" value="bad"/></record></result>',
        ):
            with self.subTest(body=body):
                response = requests.Response()
                response._content = body
                with patch.object(stream, "_request", return_value=response):
                    self.assertIsNone(stream.get_estimated_record_count())
                self.assertEqual(stream.replication_key_value, "original")
        with (
            patch.object(
                stream, "_request", side_effect=requests.RequestException("apikey=test+token")
            ),
            self.assertLogs(stream.logger, level="WARNING") as logs,
        ):
            self.assertIsNone(stream.get_estimated_record_count())
        self.assertNotIn("test+token", " ".join(logs.output))
        self.assertEqual(stream.replication_key_value, "original")
