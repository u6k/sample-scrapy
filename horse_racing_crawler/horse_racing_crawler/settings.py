import os

BOT_NAME = "horse_racing_crawler"

SPIDER_MODULES = ["horse_racing_crawler.spiders"]
NEWSPIDER_MODULE = "horse_racing_crawler.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 3.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_REGION_NAME = os.getenv("S3_REGION_NAME", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_HTTP_CACHE_PREFIX = os.getenv("S3_HTTP_CACHE_PREFIX", "httpcache")
S3_FEEDS_PREFIX = os.getenv("S3_FEEDS_PREFIX", "feeds")
HTTPCACHE_S3_SHARD_DEPTH = 1

if not S3_BUCKET:
    raise ValueError("S3_BUCKET is required for output and HTTP cache storage.")

FEEDS = {
    f"s3://{S3_BUCKET}/{S3_FEEDS_PREFIX}/race_%(race_id)s.json.gz": {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
        "overwrite": True,
    }
}

FEED_STORAGES = {
    "s3": "horse_racing_crawler.feed_storage.GzipS3FeedStorage",
}

HTTPCACHE_ENABLED = True
HTTPCACHE_STORAGE = "horse_racing_crawler.httpcache.S3JsonGzipCacheStorage"

AWS_ENDPOINT_URL = S3_ENDPOINT_URL
AWS_ACCESS_KEY_ID = S3_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = S3_SECRET_ACCESS_KEY
AWS_REGION_NAME = S3_REGION_NAME
