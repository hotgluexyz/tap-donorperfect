"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import json

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_donorperfect.tap import TapDonorperfect

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "api_token": "test-token",
}


@pytest.mark.parametrize(
    "standard_tap_test",
    get_standard_tap_tests(tap_class=TapDonorperfect, config=SAMPLE_CONFIG)[:2],
)
def test_standard_tap_features(standard_tap_test):
    """Run the SDK checks that do not require a live DonorPerfect account."""
    standard_tap_test()


def test_access_token_support_copies_api_token(tmp_path):
    """Access-token support returns DonorPerfect's static API token."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"api_token": "donorperfect-api-token"}))
    tap = TapDonorperfect(config=config_path)

    assert TapDonorperfect.fetch_access_token(tap) == {
        "access_token": "donorperfect-api-token"
    }
    assert json.loads(config_path.read_text()) == {
        "api_token": "donorperfect-api-token",
        "start_date": "2000-01-01T00:00:00Z",
        "access_token": "donorperfect-api-token",
    }
