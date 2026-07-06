import json

from lxml import etree  # type: ignore
import xmltodict


def get_json_path(path: str) -> str:
    if "*" not in path:
        path = f"{path}.*"
    path_parts = path.split(".")
    if len(path_parts) > 1:
        path = path.replace(".*", "[*]")
        return f"$.{path}"
    return path


def xml_to_dict(response):
    try:
        my_parser = etree.XMLParser(recover=True)
        xml = etree.fromstring(response.content, parser=my_parser)
        cleaned_xml_string = etree.tostring(xml)
        data = json.loads(json.dumps(xmltodict.parse(cleaned_xml_string)))
    except Exception:
        data = json.loads(
            json.dumps(
                xmltodict.parse(
                    response.content.decode("utf-8-sig").encode("utf-8")
                )
            )
        )
    return data
