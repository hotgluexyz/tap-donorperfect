"""REST client handling, including DonorPerfectStream base class."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, Optional
from urllib.parse import unquote

import backoff
import requests
from hotglue_singer_sdk.authenticators import APIKeyAuthenticator
from hotglue_singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from hotglue_singer_sdk.helpers._typing import is_datetime_type
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import RESTStream

from tap_donorperfect.exceptions import TooManyRequestsError
from tap_donorperfect.utils import get_json_path, xml_to_dict


class DonorPerfectStream(RESTStream):
    """DonorPerfect stream class."""

    records_jsonpath = get_json_path("$.result.record[*]")
    error_response_json_path = get_json_path("$.$.result.field.@reason")
    rest_method = "GET"
    path = "/"
    params: list[dict[str, str]] | None = None
    replication_key = "internal_modified_date"
    next_page_token: int | None = None
    replication_key_value: str | int | None = None

    @property
    def url_base(self) -> str:
        return "https://www.donorperfect.net/prod/xmlrequest.asp"

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="apikey",
            value=unquote(self.config["api_token"]),
            location="params",
        )

    def _substitute_bracket_vars(self, path: str, context: dict) -> str:
        for full_var in re.findall(r"\{([^}]+)\}", path):
            var = full_var.strip()
            var_expr, default_value = (
                [v.strip() for v in var.split("|", 1)] if "|" in var else (var, None)
            )
            value = None
            if var_expr == "replication_key_value":
                value = self.replication_key_value
            elif var_expr == "next_page_token":
                value = self.next_page_token
            elif hasattr(self, var_expr):
                value = getattr(self, var_expr)
            if value is None and default_value is not None:
                value = default_value
            if value is not None:
                path = path.replace(f"{{{full_var}}}", str(value))
        return path

    def get_field_value(self, path: str, context: dict | None = None) -> str:
        return self._substitute_bracket_vars(path, context or {})

    def process_replication_key_value(self, value: str) -> str:
        return datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p").strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def _process_datetime_fields(self, data: dict, path: str = "") -> dict:
        result = {}
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if key == self.replication_key:
                result[key] = self.process_replication_key_value(value)
            elif isinstance(value, dict):
                result[key] = self._process_datetime_fields(value, current_path)
            elif isinstance(value, list):
                result[key] = [
                    self._process_datetime_fields(item, current_path)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        previous_token = previous_token or 0
        page_size = 100
        if len(list(self.parse_response(response))) < page_size:
            return None
        next_page_token = previous_token + page_size
        self.next_page_token = next_page_token
        return next_page_token

    def get_incremental_sync_params(self, context: dict | None) -> dict[str, Any]:
        start_date = self.get_starting_time(context, is_inclusive=True)
        formatted_start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        self.replication_key_value = formatted_start_date
        return {"internal_modified_date": formatted_start_date}

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = self.get_incremental_sync_params(context)
        if self.params:
            for param in self.params:
                value = self.get_field_value(param["value"], context or {})
                if value is not None:
                    params[param["name"]] = value
        if next_page_token:
            params["next_page_token"] = next_page_token
        return params

    def request_decorator(self, func: Callable) -> Callable:
        decorator: Callable = backoff.on_exception(
            backoff.expo,
            (
                RetriableAPIError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.RequestException,
            ),
            max_tries=7,
            factor=2,
        )(func)
        return backoff.on_exception(
            backoff.constant,
            (
                requests.exceptions.ConnectionError,
                ConnectionRefusedError,
                TooManyRequestsError,
            ),
            max_tries=15,
            interval=30,
        )(decorator)

    def response_error_message(self, response: requests.Response) -> str:
        if 400 <= response.status_code < 500:
            error_type = "Client"
        else:
            error_type = "Server"
        return (
            f"{response.status_code} {error_type} Error: "
            f"{response.reason} for path: {self.path}. Response {response.text}"
        )

    def validate_response(self, response: requests.Response) -> None:
        if response.status_code in [429]:
            raise TooManyRequestsError(response.text)
        if (
            response.status_code in self.extra_retry_statuses
            or 500 <= response.status_code < 600
        ):
            raise RetriableAPIError(self.response_error_message(response), response)
        if 400 <= response.status_code < 500:
            raise FatalAPIError(self.response_error_message(response))

    def post_process(
        self, row: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        return self._process_datetime_fields(row)

    @property
    def is_timestamp_replication_key(self) -> bool:
        if not self.replication_key:
            return False
        type_dict = self.schema.get("properties", {}).get(self.replication_key)
        return is_datetime_type(type_dict)

    def check_body_for_error(self, body: dict) -> None:
        if self.error_response_json_path:
            error_response = next(
                extract_jsonpath(self.error_response_json_path, input=body), None
            )
            if error_response:
                raise Exception(f"Error: {error_response}")

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        if "text/xml" in response.headers.get("Content-Type", ""):
            json_response = xml_to_dict(response)
            self.check_body_for_error(json_response)
            for record in extract_jsonpath(self.records_jsonpath, input=json_response):
                record = record.get("field")
                yield {field["@name"]: field["@value"] for field in record}
        else:
            self.check_body_for_error(response.json())
            yield from super().parse_response(response)
