from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.http import JsonResponse


class RejectInvalidatedToken:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Path", request.path)
        if request.user.is_anonymous and request.path == '/api/v1/password/change/':            
            return JsonResponse({"error": "Token has been invalidated"}, status=401)
            
        return self.get_response(request)