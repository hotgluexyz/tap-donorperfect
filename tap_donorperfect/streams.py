"""Stream type classes for tap-donorperfect."""

from __future__ import annotations

from hotglue_singer_sdk import typing as th

from tap_donorperfect.client import DonorPerfectStream


class DonorsStream(DonorPerfectStream):
    name = "donors"
    primary_keys = ["donor_id"]
    replication_key = "internal_modified_date"
    schema = th.PropertiesList(
        th.Property("donor_id", th.StringType),
        th.Property("first_name", th.StringType),
        th.Property("last_name", th.StringType),
        th.Property("middle_name", th.StringType),
        th.Property("suffix", th.StringType),
        th.Property("title", th.StringType),
        th.Property("salutation", th.StringType),
        th.Property("prof_title", th.StringType),
        th.Property("opt_line", th.StringType),
        th.Property("address", th.StringType),
        th.Property("address2", th.StringType),
        th.Property("city", th.StringType),
        th.Property("state", th.StringType),
        th.Property("zip", th.StringType),
        th.Property("country", th.StringType),
        th.Property("address_type", th.StringType),
        th.Property("fax_phone", th.StringType),
        th.Property("mobile_phone", th.StringType),
        th.Property("email", th.StringType),
        th.Property("org_rec", th.StringType),
        th.Property("donor_type", th.StringType),
        th.Property("nomail", th.StringType),
        th.Property("nomail_reason", th.StringType),
        th.Property("narrative", th.StringType),
        th.Property("tag_date", th.StringType),
        th.Property("initial_gift_date", th.StringType),
        th.Property("last_contrib_date", th.StringType),
        th.Property("last_contrib_amt", th.StringType),
        th.Property("ytd", th.StringType),
        th.Property("ly_ytd", th.StringType),
        th.Property("ly2_ytd", th.StringType),
        th.Property("ly3_ytd", th.StringType),
        th.Property("ly4_ytd", th.StringType),
        th.Property("ly5_ytd", th.StringType),
        th.Property("ly6_ytd", th.StringType),
        th.Property("cytd", th.StringType),
        th.Property("ly_cytd", th.StringType),
        th.Property("ly2_cytd", th.StringType),
        th.Property("ly3_cytd", th.StringType),
        th.Property("ly4_cytd", th.StringType),
        th.Property("ly5_cytd", th.StringType),
        th.Property("ly6_cytd", th.StringType),
        th.Property("autocalc1", th.StringType),
        th.Property("autocalc2", th.StringType),
        th.Property("autocalc3", th.StringType),
        th.Property("gift_total", th.StringType),
        th.Property("gifts", th.StringType),
        th.Property("max_date", th.StringType),
        th.Property("max_amt", th.StringType),
        th.Property("avg_amt", th.StringType),
        th.Property("yrs_donated", th.StringType),
        th.Property("created_by", th.StringType),
        th.Property("created_date", th.StringType),
        th.Property("modified_by", th.StringType),
        th.Property("modified_date", th.StringType),
        th.Property("donor_rcpt_type", th.StringType),
        th.Property("address3", th.StringType),
        th.Property("address4", th.StringType),
        th.Property("ukcounty", th.StringType),
        th.Property("gift_aid_eligible", th.StringType),
        th.Property("initial_temp_record_id", th.StringType),
        th.Property("frequent_temp_record_id", th.StringType),
        th.Property("recent_temp_record_id", th.DateTimeType),
        th.Property("import_id", th.StringType),
        th.Property("receipt_delivery", th.StringType),
        th.Property("no_email", th.StringType),
        th.Property("CC_donor_import_time", th.StringType),
        th.Property("cc_contact_id", th.StringType),
        th.Property("wl_import_id", th.StringType),
        th.Property("WL_Action", th.StringType),
        th.Property("geocoding_lattitude", th.StringType),
        th.Property("geocoding_longitude", th.StringType),
        th.Property("quickbooks_customer_id", th.StringType),
        th.Property("dp_record_type", th.StringType),
        th.Property("DPI_RFM_ASOFDATE", th.StringType),
        th.Property("DPI_RQUINTILE", th.StringType),
        th.Property("DPI_FQUINTILE", th.StringType),
        th.Property("DPI_MQUINTILE", th.StringType),
        th.Property("DPI_RFM_COMB", th.StringType),
        th.Property("DPI_RFM_P_SEG", th.StringType),
        th.Property("DPI_RFM_U_SEG", th.StringType),
        th.Property("DPI_RFM_AFP", th.StringType),
        th.Property("internal_modified_date", th.DateTimeType),
        th.Property("address_id", th.StringType),
    ).to_dict()
    params = [
        {
            "name": "action",
            "value": "select * FROM dp WHERE {replication_key}>'{replication_key_value}' ORDER BY {replication_key} DESC OFFSET {next_page_token | 0} ROWS FETCH NEXT 100 ROWS ONLY;",
        }
    ]


class FlagsStream(DonorPerfectStream):
    name = "flags"
    primary_keys = ["donor_id", "flag"]
    replication_key = "internal_modified_date"
    schema = th.PropertiesList(
        th.Property("donor_id", th.StringType),
        th.Property("flag", th.StringType),
        th.Property("import_id", th.StringType),
        th.Property("description", th.StringType),
        th.Property("internal_modified_date", th.DateTimeType),
    ).to_dict()
    params = [
        {
            "name": "action",
            "value": "SELECT dpflags.*, dc.description, dp.internal_modified_date FROM dpflags LEFT JOIN dpcodes dc ON dc.code = dpflags.flag LEFT JOIN dp ON dp.donor_id = dpflags.donor_id WHERE {replication_key}>'{replication_key_value}' ORDER BY {replication_key} DESC OFFSET {next_page_token | 0} ROWS FETCH NEXT 100 ROWS ONLY;",
        }
    ]


class DonorAddressesStream(DonorPerfectStream):
    name = "donor_addresses"
    primary_keys = ["address_id"]
    replication_key = "internal_modified_date"
    schema = th.PropertiesList(
        th.Property("address_id", th.StringType),
        th.Property("donor_id", th.StringType),
        th.Property("opt_line", th.StringType),
        th.Property("address", th.StringType),
        th.Property("address2", th.StringType),
        th.Property("city", th.StringType),
        th.Property("state", th.StringType),
        th.Property("zip", th.StringType),
        th.Property("country", th.StringType),
        th.Property("address_type", th.StringType),
        th.Property("getmail", th.StringType),
        th.Property("created_by", th.StringType),
        th.Property("created_date", th.DateTimeType),
        th.Property("modified_by", th.StringType),
        th.Property("modified_date", th.DateTimeType),
        th.Property("use_main_name", th.StringType),
        th.Property("use_main_address", th.StringType),
        th.Property("title", th.StringType),
        th.Property("first_name", th.StringType),
        th.Property("last_name", th.StringType),
        th.Property("seasonal_from_date", th.DateTimeType),
        th.Property("seasonal_to_date", th.DateTimeType),
        th.Property("suffix", th.StringType),
        th.Property("prof_title", th.StringType),
        th.Property("salutation", th.StringType),
        th.Property("email", th.StringType),
        th.Property("fax_phone", th.StringType),
        th.Property("mobile_phone", th.StringType),
        th.Property("start_date", th.DateTimeType),
        th.Property("end_date", th.DateTimeType),
        th.Property("address3", th.StringType),
        th.Property("address4", th.StringType),
        th.Property("ukcounty", th.StringType),
        th.Property("import_id", th.StringType),
        th.Property("middle_name", th.StringType),
        th.Property("org_rec", th.StringType),
        th.Property("no_email", th.StringType),
        th.Property("cc_contact_id", th.StringType),
        th.Property("wl_import_id", th.StringType),
        th.Property("geocoding_lattitude", th.StringType),
        th.Property("geocoding_longitude", th.StringType),
        th.Property("internal_modified_date", th.DateTimeType),
    ).to_dict()
    params = [
        {
            "name": "action",
            "value": "SELECT dpa.*, dp.internal_modified_date as internal_modified_date FROM DPADDRESS dpa JOIN dp dp ON dpa.donor_id = dp.donor_id WHERE {replication_key}>'{replication_key_value}' ORDER BY {replication_key} DESC OFFSET {next_page_token | 0} ROWS FETCH NEXT 100 ROWS ONLY;",
        }
    ]
