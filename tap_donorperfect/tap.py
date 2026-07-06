"""DonorPerfect tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th

from tap_donorperfect.streams import (
    DonorAddressesStream,
    DonorsStream,
    FlagsStream,
)

STREAM_TYPES = [
    DonorsStream,
    FlagsStream,
    DonorAddressesStream,
]


class TapDonorperfect(Tap):
    name = "tap-donorperfect"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_token",
            th.StringType,
            required=True,
            description="DonorPerfect API key",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
            default="2000-01-01T00:00:00Z",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapDonorperfect.cli()
