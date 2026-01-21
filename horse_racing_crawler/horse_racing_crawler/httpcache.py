import base64
import json
import os
from hashlib import sha1

from scrapy.http import Headers, HtmlResponse
from scrapy.utils.python import to_unicode


class JsonGzipCacheStorage:
    """Custom HTTP cache storage that stores responses as .json.gz files."""

    def __init__(self, settings):
        self.cache_dir = settings.get("HTTPCACHE_DIR")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def open_spider(self, spider):
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

    def close_spider(self, spider):
        return None

    def retrieve_response(self, spider, request):
        path = self._get_request_path(request)
        if not os.path.exists(path):
            return None
        with self._open(path, "rt") as handle:
            data = json.load(handle)
        headers = Headers(
            {
                key: [value.encode("latin1") for value in values]
                for key, values in data.get("headers", {}).items()
            }
        )
        body = base64.b64decode(data.get("body", ""))
        return HtmlResponse(
            url=data.get("url"),
            body=body,
            encoding=data.get("encoding"),
            request=request,
            status=data.get("status", 200),
            headers=headers,
        )

    def store_response(self, spider, request, response):
        path = self._get_request_path(request)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        headers = {
            to_unicode(key): [to_unicode(value) for value in values]
            for key, values in response.headers.items()
        }
        payload = {
            "url": response.url,
            "status": response.status,
            "headers": headers,
            "body": base64.b64encode(response.body).decode("ascii"),
            "encoding": response.encoding,
        }
        with self._open(path, "wt") as handle:
            json.dump(payload, handle, ensure_ascii=False)

    def _get_request_path(self, request):
        fingerprint = sha1(request.url.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{fingerprint}.json.gz")

    def _open(self, path, mode):
        import gzip

        return gzip.open(path, mode, encoding="utf-8")
