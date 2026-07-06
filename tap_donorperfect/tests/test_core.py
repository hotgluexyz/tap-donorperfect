"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_donorperfect.tap import TapDonorperfect

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "api_token": "test-token",
}


def test_standard_tap_tests():
    tests = get_standard_tap_tests(
        TapDonorperfect,
        config=SAMPLE_CONFIG,
    )
    for test in tests:
        test()
