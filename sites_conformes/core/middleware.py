from wagtail.models import Site


class IframeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.iframe = request.headers.get("Sec-Fetch-Dest") == "iframe"

        response = self.get_response(request)

        self._set_frame_ancestors(request, response)
        self._add_vary_header(response)

        return response

    def _set_frame_ancestors(self, request, response):
        try:
            site = Site.find_for_request(request)
            config = getattr(site, "sites_conformes_core_CmsDsfrConfig", None)
            if config and config.iframe_allow_origins.strip():
                origins = [o.strip() for o in config.iframe_allow_origins.splitlines() if o.strip()]
                if origins:
                    ancestors = " ".join(f"https://{o}" for o in origins)
                    value = f"'self' {ancestors}"
                else:
                    value = "'self'"
            else:
                value = "'self'"
        except Exception:
            value = "'self'"

        response.headers["Content-Security-Policy"] = f"frame-ancestors {value}"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

    def _add_vary_header(self, response):
        vary_header = response.headers.get("Vary", "")
        vary_values = [v.strip() for v in vary_header.split(",") if v.strip()]
        if "Sec-Fetch-Dest" not in vary_values:
            vary_values.append("Sec-Fetch-Dest")
            response.headers["Vary"] = ", ".join(vary_values)
