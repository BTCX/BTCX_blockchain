from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.validators import ValidationError
from rest_framework import serializers
from bitcoinrpc.authproxy import JSONRPCException
from socket import error as socket_error


class CustomExceptionSeralizer(serializers.Serializer):
    error = serializers.IntegerField()
    error_message = serializers.CharField(max_length=256)


def custom_exception_handler(exc, context):
    exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        error_message = f"Input Validation Error: {str(exc)}"
    elif isinstance(exc, JSONRPCException):
        error_message = f"Wallet RPC Error: {str(exc)}"
    elif isinstance(exc, socket_error):
        error_message = f"Wallet Connection Error: {str(exc)}"
    else:
        error_message = \
            f"Internal Server Error: {context['view']}: {repr(exc)}"

    s = CustomExceptionSeralizer({
        'error': 1,
        'error_message': error_message,
    })
    r = Response(s.data)
    r.status_code = 500
    return r
