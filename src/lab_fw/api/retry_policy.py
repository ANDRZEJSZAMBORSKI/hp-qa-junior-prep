import httpx

from lab_fw.core.errors import ApiError, HttpStatusError

def should_retry(exc: ApiError) -> bool:
    if isinstance(exc, HttpStatusError):
        response = getattr(exc, "response", None)
        request = getattr(response, "request", None)
        method = getattr(request, "method", None)

        if method != "GET":
            return False

        status = getattr(response, "status_code", None)
        return status in (429, 503)

    cause = exc.__cause__

    if not isinstance(cause, httpx.HTTPError):
        return False

    request = getattr(cause, "request", None)
    method = getattr(request, "method", None)

    return method == "GET"