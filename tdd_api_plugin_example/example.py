import json
from copy import copy
from rdflib import Graph
from rdflib.exceptions import ParserError

from tdd.common import (
    put_rdf_in_sparql,
    put_json_in_sparql,
    get_id_description,
    frame_nt_content,
)
from tdd.context import get_context
from tdd.utils import uri_to_base
from tdd.errors import RDFValidationError, JSONDecodeError

EXAMPLE_CONTEXT = {"example": "https://example.td/"}
EXAMPLE_ONTOLOGY = {"prefix": "example", "base": "https://example.td/"}


def get_example_description(uri, content_type="application/example+json"):
    # regarding the content_type parameter it can be an other format
    if not content_type.endswith("json"):
        return get_id_description(uri, content_type, EXAMPLE_ONTOLOGY)
    content = get_id_description(uri, "application/n-triples", EXAMPLE_ONTOLOGY)
    original_context = get_context(uri, EXAMPLE_ONTOLOGY)
    jsonld_response = frame_example_nt_content(uri, content, original_context)

    return jsonld_response


def frame_example_nt_content(uri, nt_content, original_context):
    context = copy(original_context)
    context.append({"@base": uri_to_base(uri)})
    context.append(EXAMPLE_CONTEXT)

    frame = {
        "@context": context,
        "id": uri,
    }

    str_json_framed = frame_nt_content(uri, nt_content, frame).decode("utf-8")
    result = json.loads(str_json_framed)

    try:
        del result["@context"]
    except KeyError:
        pass
    result["@context"] = original_context
    return result


def put_example_rdf_in_sparql(rdf_content, mimetype, uri=None, delete_if_exists=True):
    uri = uri if uri is not None else "https://example.td/test"
    g = Graph()
    try:
        g.parse(data=rdf_content, format=mimetype)
    except (SyntaxError, ParserError):
        raise RDFValidationError(f"The RDF triples are not well formatted ({mimetype})")

    put_rdf_in_sparql(
        g,
        uri,
        [EXAMPLE_CONTEXT],
        delete_if_exists,
        EXAMPLE_ONTOLOGY,
    )
    return uri


def validate_example(str_content, uri=None):
    try:
        # consider this is a json format
        json_content = json.loads(str_content)
    except json.decoder.JSONDecodeError as exc:
        raise JSONDecodeError(exc)
    # check somethings on the json_content before return
    if json_content is None:  # dumb test for example
        raise Exception
    return json_content


def put_example_json_in_sparql(content, uri=None, delete_if_exists=True):
    uri = uri if uri is not None else "urn:node:test"
    put_json_in_sparql(content, uri, [], delete_if_exists, EXAMPLE_ONTOLOGY)
    return uri


def td_to_example(uri):
    # get all content from this sepcific URI from example format
    content = get_id_description(uri, "application/n-triples", {"prefix": "td"})

    # this graph can be used to generate data
    # here we return a hard coded example
    g = Graph().parse(data=content, format="nt").skolemize()  # noqa: F841

    # generate example object from fetched TD
    # here just export a simple triple
    data = f"<{uri}> a <https://example.td/Test>."

    return put_example_rdf_in_sparql(
        data, "text/turtle", uri=uri, delete_if_exists=False
    )
