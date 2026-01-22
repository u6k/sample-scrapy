import gzip

from scrapy.extensions.feedexport import S3FeedStorage


class GzipS3FeedStorage(S3FeedStorage):
    """Feed storage that writes gzip-compressed files to S3-compatible storage."""

    def open(self, spider):
        return gzip.GzipFile(fileobj=self._get_buffer(), mode="wb")
