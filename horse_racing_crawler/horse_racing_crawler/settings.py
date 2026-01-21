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

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
CACHE_DIR = os.getenv("CACHE_DIR", "./httpcache")

FEEDS = {
    f"{OUTPUT_DIR}/race_%(race_id)s.json.gz": {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
        "overwrite": True,
    }
}

FEED_STORAGES = {
    "file": "horse_racing_crawler.feed_storage.GzipFileFeedStorage",
}

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = CACHE_DIR
HTTPCACHE_STORAGE = "horse_racing_crawler.httpcache.JsonGzipCacheStorage"
