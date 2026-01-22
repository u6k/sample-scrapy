import base64
import gzip
import io
import json
import os
from hashlib import sha1

import boto3
from botocore.exceptions import ClientError
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
        return gzip.open(path, mode, encoding="utf-8")


class S3JsonGzipCacheStorage:
    """HTTP cache storage backed by S3-compatible storage."""

    def __init__(self, settings):
        self.bucket = settings.get("S3_BUCKET")
        self.prefix = settings.get("S3_HTTP_CACHE_PREFIX", "httpcache")
        self.shard_depth = settings.getint("HTTPCACHE_S3_SHARD_DEPTH", 1)
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.get("S3_ENDPOINT_URL"),
            aws_access_key_id=settings.get("S3_ACCESS_KEY_ID"),
            aws_secret_access_key=settings.get("S3_SECRET_ACCESS_KEY"),
            region_name=settings.get("S3_REGION_NAME"),
        )
        if not self.bucket:
            raise ValueError("S3_BUCKET is required for S3 HTTP cache storage.")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def open_spider(self, spider):
        return None

    def close_spider(self, spider):
        return None

    def retrieve_response(self, spider, request):
        key = self._get_request_key(request)
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                return None
            raise
        body = response["Body"].read()
        data = json.loads(gzip.decompress(body).decode("utf-8"))
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
        key = self._get_request_key(request)
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
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb") as handle:
            handle.write(data)
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=buffer.getvalue(),
            ContentType="application/json",
            ContentEncoding="gzip",
        )

    def _get_request_key(self, request):
        fingerprint = sha1(request.url.encode("utf-8")).hexdigest()
        parts = []
        if self.prefix:
            parts.append(self.prefix.strip("/"))
        if self.shard_depth > 0:
            for index in range(self.shard_depth):
                parts.append(fingerprint[index * 2 : index * 2 + 2])
        parts.append(f"{fingerprint}.json.gz")
        return "/".join(parts)
