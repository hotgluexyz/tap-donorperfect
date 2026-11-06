from hotglue_smoke_test.vcr.tap import VCRTapTestRunner


class ConnectorTapTestRunner(VCRTapTestRunner):
    # Base header filters suffice; API keys use api_token in config and apikey in queries.
    TOKEN_KEYS = [*VCRTapTestRunner.TOKEN_KEYS, "api_token", "apikey"]
    PRESERVE_KEYS = {"internal_modified_date"}

    def module(self) -> str:
        return "tap_donorperfect.tap"

    def launch(self):
        from tap_donorperfect.tap import TapDonorperfect

        TapDonorperfect.cli()


if __name__ == "__main__":
    ConnectorTapTestRunner.main()
