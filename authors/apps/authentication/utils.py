from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework import status

field_types = {
    'email': openapi.Schema(type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_EMAIL),
    'username': openapi.Schema(type=openapi.TYPE_STRING),
    'password': openapi.Schema(type=openapi.TYPE_STRING,
                               format=openapi.FORMAT_PASSWORD),
    'image_path': openapi.Schema(type=openapi.TYPE_STRING,
                                 format=openapi.FORMAT_BINARY),
    'title': openapi.Schema(type=openapi.TYPE_STRING),
    'body': openapi.Schema(type=openapi.TYPE_STRING),
}

to_http = {
    200: status.HTTP_200_OK,
    201: status.HTTP_201_CREATED,
    400: status.HTTP_400_BAD_REQUEST,
    404: status.HTTP_404_NOT_FOUND,
}

api_responses = {
    status.HTTP_200_OK: openapi.Response(
        description="OK"
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description="Bad Request"
    ),
    status.HTTP_404_NOT_FOUND: openapi.Response(
        description="Not Found"
    ),
    status.HTTP_201_CREATED: openapi.Response(
        description="Created"
    )
}


def swagger_body(prefix=None, fields=()):

    props = {field: field_types.get(field) for field in fields}

    return (openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                prefix: openapi.Schema(
                    required=fields,
                    type=openapi.TYPE_OBJECT,
                    properties=props
                )
            },
            )
            )


def status_codes(codes=None):
    return {to_http.get(code): api_responses.get(to_http.get(code)) for code in codes}
