import json
from flask import Blueprint, request, Response

from tdd.common import (
    delete_id,
)
from tdd.utils import (
    POSSIBLE_MIMETYPES,
    negociate_mime_type,
    update_collection_etag,
)
from tdd.errors import WrongMimeType

from domus_tdd_api_plugin_plugin_example.example import (
    get_example_description,
    validate_example,
    put_example_json_in_sparql,
    put_example_rdf_in_sparql,
)


blueprint = Blueprint("domus_tdd_api_plugin_plugin_example", __name__, url_prefix="/example")


@blueprint.route("/", methods=["GET"])
def hello_world():
    return "HELLO I AM ON EXAMPLE PLUGIN"


@blueprint.route("/<id>", methods=["DELETE"])
def delete_route_example(id):
    # use the generic delete_id since it removes
    # all graphs which contains data for this id
    # for all the format
    response = delete_id(id)
    if response.status_code in [200, 204]:
        update_collection_etag()
    return response


@blueprint.route("/<id>", methods=["GET"])
def describe_example(id):
    # negociate mimetype wanted
    mime_type_negociated = negociate_mime_type(
        request, default_mimetype="application/example+json"
    )
    # get "example" with the negociated mimetype
    description = get_example_description(id, mime_type_negociated)
    return Response(json.dumps(description), content_type=mime_type_negociated)


@blueprint.route("/<id>", methods=["PUT"])
def create_example(id):
    mimetype = request.content_type
    if mimetype == "application/example+json":
        json_ld_content = request.get_data()
        content = validate_example(json_ld_content, uri=id)
        uri = put_example_json_in_sparql(content, uri=id)
    elif mimetype in POSSIBLE_MIMETYPES:
        rdf_content = request.get_data()
        uri = put_example_rdf_in_sparql(rdf_content, mimetype)
    else:
        raise WrongMimeType(mimetype)

    update_collection_etag()
    return Response(status=201, headers={"Location": uri})


@blueprint.route("/", methods=["POST"])
def create_anonymous_aas():
    mimetype = request.content_type
    if mimetype == "application/json":
        mimetype = "application/example+json"
    if mimetype == "application/example+json":
        json_ld_content = request.get_data()
        content = validate_example(json_ld_content)
        uri = put_example_json_in_sparql(content, delete_if_exists=False)
    elif mimetype in POSSIBLE_MIMETYPES:
        content = request.get_data()
        updated, uri = put_example_rdf_in_sparql(
            content, mimetype, delete_if_exists=False
        )
    else:
        raise WrongMimeType(mimetype)
    update_collection_etag()
    return Response(status=201, headers={"Location": uri})
