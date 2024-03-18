import json
import pytest
from pathlib import Path
from jsoncomparison import Compare

from tdd.tests.conftest import (  # noqa: F401
    SparqlGraph,
    test_client,
    mock_sparql_empty_endpoint,
)


DATA_PATH = Path("tdd_api_plugin_example") / "tests" / "data"


@pytest.fixture
def mock_sparql_with_one_example(httpx_mock):
    graph = SparqlGraph("example.trig", format="trig", data_path=DATA_PATH)
    httpx_mock.add_callback(graph.custom)


def test_GET_example_OK(test_client, mock_sparql_with_one_example):  # noqa: F811
    example_id = "urn:node:test"
    with open(DATA_PATH / "example.json") as fp:
        already_present_example = json.load(fp)
    get_response = test_client.get(f"/example/{example_id}")
    assert get_response.status_code == 200
    example = get_response.json
    diff = Compare().check(already_present_example, example)
    assert len(diff) == 0


def test_PUT_example_ok(test_client, mock_sparql_empty_endpoint):  # noqa: F811
    with open(DATA_PATH / "example.json") as fp:
        example_id = "urn:node:test"
        put_response = test_client.put(
            f"/example/{example_id}",
            data=fp.read(),
            content_type="application/example+json",
        )
        assert put_response.status_code == 201
        assert put_response.headers["Location"] == example_id
        get_response = test_client.get(f"/example/{example_id}")
        assert get_response.status_code == 200


def test_PUT_example_bad_content_type(test_client):  # noqa: F811
    with open(DATA_PATH / "example.json") as fp:
        put_response = test_client.put(
            "/example/urn:test:coucou",
            data=fp.read(),
            content_type="text/poulet-xml",
        )
        assert put_response.status_code == 400
        assert "Wrong MimeType" in put_response.json["title"]
