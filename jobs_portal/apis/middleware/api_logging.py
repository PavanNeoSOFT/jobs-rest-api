import logging
import time

class APILoggingMiddleware:
    """
    Middleware for logging API requests and responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('api_logger')

    def __call__(self, request):
        start_time = time.time()

        self.logger.info(f"API Request: {request.method} {request.path} | Body: {request.body.decode('utf-8', 'ignore')}")

        response = self.get_response(request)

        duration = time.time() - start_time

        self.logger.info(
            f"API Response: {response.status_code} | Duration: {duration:.3f}s | Path: {request.path} | Response: {getattr(response, 'content', b'').decode('utf-8', 'ignore')}"
        )

        return response
