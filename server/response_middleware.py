import json
from django.http import JsonResponse

class GlobalResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Handle JSON response
        if isinstance(response, JsonResponse):
            return response

        # Handle non-JSON responses
        try:
            response_data = json.loads(response.content.decode('utf-8'))
        except (json.JSONDecodeError, AttributeError):
            response_data = None

        # Add additional fields to the response if it's JSON
        if response_data is not None:
            return JsonResponse(
                {
                    "data": response_data,
                    "message": "Processed successfully",
                    "responseStatus": "success" if response.status_code < 400 else "fail",
                },
                status=response.status_code,
            )

        # Return original response for non-JSON content
        return response
