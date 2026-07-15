class IframeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.iframe = request.headers.get("Sec-Fetch-Dest") == "iframe"
        response = self.get_response(request)
        vary_header = response.headers.get("Vary", "")
        vary_values = [v.strip() for v in vary_header.split(",") if v.strip()]
        if "Sec-Fetch-Dest" not in vary_values:
            vary_values.append("Sec-Fetch-Dest")
            response.headers["Vary"] = ", ".join(vary_values)
        return response
