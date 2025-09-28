from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

# Map error codes to friendly messages
messages = {
    status.HTTP_401_UNAUTHORIZED: "Authentication required. Please log in to get a token.",
    status.HTTP_403_FORBIDDEN: "You don’t have permission to perform this action.",
    status.HTTP_404_NOT_FOUND: "The resource you are looking for does not exist.",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Method not allowed on this endpoint.",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "Unsupported media type. Use application/json.",
    status.HTTP_429_TOO_MANY_REQUESTS: "Too many requests. Please slow down.",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Something went wrong on our end. Please try again later.",
}

def custom_exception_handler(exc, context):
    # DRF's default handler
    response = exception_handler(exc, context)

    # If DRF handled it, customize the response
    if response is not None:
        code = response.status_code
        # If it's one we want to customize
        if code in messages:
            return Response({"error": messages[code]}, status=code)

        # Otherwise, fallback to DRF’s default with added status code
        response.data['status_code'] = code
        return response

    # If DRF couldn't handle it (e.g., truly unhandled exception)
    return Response(
        {"error": "Unexpected server error. Please try again later."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
