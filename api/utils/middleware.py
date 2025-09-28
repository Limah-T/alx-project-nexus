from .helper_functions import get_client_ip
from django.core.cache import cache
from django.http import JsonResponse
import time

class IPTrackingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 60
        self.window = 300

    def __call__(self, request):
        ip_address = get_client_ip(request)
        now = time.time()
        address = f"rt_{ip_address}"
        ip_key = cache.get(address, [])

        requests = [ts for ts in ip_key if now - ts < self.window]
        if len(requests) >= self.rate_limit:
            return JsonResponse({'error': 'Too many requests at a time!'}, status=429)
        requests.append(now)
        cache.set(address, requests, self.window)
        response = self.get_response(request)
        return response    
    