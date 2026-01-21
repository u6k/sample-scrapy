import gzip

from scrapy.extensions.feedexport import FileFeedStorage


class GzipFileFeedStorage(FileFeedStorage):
    """Feed storage that always writes gzip-compressed files."""

    def open(self, spider):
        return gzip.open(self.path, "wb")
