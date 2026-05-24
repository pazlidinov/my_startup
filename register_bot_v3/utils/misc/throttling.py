from typing import Optional

def rate_limit(limit: int, key: Optional[str] = None):

    def decorator(handler):
        if not hasattr(handler, "flags"):
            handler.flags = {}

        handler.flags["rate_limit"] = limit

        if key:
            handler.flags["rate_limit_key"] = key

        return handler

    return decorator