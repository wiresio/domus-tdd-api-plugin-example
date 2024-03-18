import json
import pytest
import re

from jsoncomparison import Compare

from tdd import CONFIG
from tdd.tests.conftest import (  # noqa: F401
    assert_only_on_known_errors,
    SparqlGraph,
    mock_sparql_empty_endpoint,
    test_client,
)

from tdd_api_plugin_example.tests.test_example import DATA_PATH

CONFIG["LIMIT_BATCH_TDS"] = 15
CONFIG["CHECK_SCHEMA"] = True
CONFIG["PERIOD_CLEAR_EXPIRE_TD"] = 0
CONFIG["OVERWRITE_DISCOVERY"] = True


def remove_skolemized_blank_node_values(json_str):
    json_str = re.sub(r"https?\:\/\/rdf?lib[^\"]+", "", json_str)
    json_str = re.sub(r"\"idShort\": \"[^\"]+\"", '"idShort": ""', json_str)
    return json.loads(json_str)


@pytest.fixture
def mock_sparql_example_and_td(httpx_mock):
    graph = SparqlGraph("td_example.trig", format="trig", data_path=DATA_PATH)
    httpx_mock.add_callback(graph.custom)


def test_POST_td(test_client, mock_sparql_empty_endpoint):  # noqa: F811
    with open(DATA_PATH / "small-td.json") as fp:
        data = fp.read()
        uri = "urn:node:test"
        post_response = test_client.post(
            "/things", data=data, content_type="application/json"
        )
        assert post_response.status_code == 201
        assert post_response.headers["Location"] == uri
    td_response = test_client.get(f"/things/{uri}")
    assert td_response.status_code == 200
    td = td_response.json
    del td["registration"]
    diff = Compare().check(json.loads(data), td)
    assert_only_on_known_errors(diff)

    example_response = test_client.get(f"/example/{uri}")
    assert example_response.status_code == 200
    with open(DATA_PATH / "example.json") as fp:
        example = remove_skolemized_blank_node_values(json.dumps(example_response.json))
        target_example = remove_skolemized_blank_node_values(fp.read())
        diff = Compare().check(target_example, example)
        assert diff == {}


def test_DELETE_things(test_client, mock_sparql_example_and_td):  # noqa: F811
    uri = "urn:node:test"
    get_response = test_client.get(f"/things/{uri}")
    assert get_response.status_code == 200
    get_example_response = test_client.get(f"/example/{uri}")
    assert get_example_response.status_code == 200
    test_client.delete(f"/things/{uri}")
    get_response = test_client.get(f"/things/{uri}")
    assert get_response.status_code == 404
    get_example_response = test_client.get(f"/example/{uri}")
    assert get_example_response.status_code == 404


def test_DELETE_aas(test_client, mock_sparql_example_and_td):  # noqa: F811
    uri = "urn:node:test"
    get_response = test_client.get(f"/things/{uri}")
    assert get_response.status_code == 200
    get_aas_response = test_client.get(f"/example/{uri}")
    assert get_aas_response.status_code == 200
    test_client.delete(f"/example/{uri}")
    get_response = test_client.get(f"/things/{uri}")
    assert get_response.status_code == 404
    get_aas_response = test_client.get(f"/example/{uri}")
    assert get_aas_response.status_code == 404
