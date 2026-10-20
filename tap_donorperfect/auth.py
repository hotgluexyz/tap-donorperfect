"""Authentication helpers for DonorPerfect."""

import json
from typing import cast

from hotglue_singer_sdk.authenticators import OAuthAuthenticator


class DonorPerfectAuthenticator(OAuthAuthenticator):
    def update_access_token_locally(self) -> None:
        self._tap._config["access_token"] = self._tap._config["api_token"]
        with open(cast(str, self._config_file), "w") as config_file:
            json.dump(self._tap._config, config_file, indent=4)
