import os
import re

import scrapy

from horse_racing_crawler.items import ShutubaItem


class NetkeibaSpider(scrapy.Spider):
    name = "NetkeibaSpider"
    allowed_domains = ["race.netkeiba.com", "db.netkeiba.com"]

    def __init__(self, race_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not race_id:
            raise ValueError("race_id is required")
        self.race_id = race_id

    def start_requests(self):
        os.makedirs(os.getenv("OUTPUT_DIR", "./output"), exist_ok=True)
        url = f"https://race.netkeiba.com/race/shutuba.html?race_id={self.race_id}"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        rows = response.css("table.Shutuba_Table tr")
        for row in rows:
            horse_name = self._get_text(row, "td.Horse_Info a::text")
            if not horse_name:
                continue
            bracket_number = self._get_text(row, "td.Waku span::text")
            horse_number = self._get_text(row, "td.Umaban span::text")
            horse_link = row.css("td.Horse_Info a::attr(href)").get()
            jockey_link = row.css("td.Jockey a::attr(href)").get()
            trainer_link = row.css("td.Trainer a::attr(href)").get()

            horse_id = self._extract_id(horse_link, r"/horse/(\d+)/")
            jockey_id = self._extract_id(jockey_link, r"/jockey/(\d+)/")
            trainer_id = self._extract_id(trainer_link, r"/trainer/(\d+)/")

            jockey_name = self._get_text(row, "td.Jockey a::text")
            trainer_name = self._get_text(row, "td.Trainer a::text")
            jockey_weight = self._get_text(row, "td.Weight::text")

            horse_weight_text = self._get_text(row, "td.Horse_Weight::text")
            horse_weight, horse_weight_diff = self._parse_weight(horse_weight_text)

            if horse_link:
                yield response.follow(horse_link, callback=self.parse_horse)
            if jockey_link:
                yield response.follow(jockey_link, callback=self.parse_jockey)
            if trainer_link:
                yield response.follow(trainer_link, callback=self.parse_trainer)

            yield ShutubaItem(
                race_id=self.race_id,
                bracket_number=self._to_int(bracket_number),
                horse_number=self._to_int(horse_number),
                horse_id=horse_id,
                horse_name=horse_name,
                jockey_weight=self._to_float(jockey_weight),
                jockey_id=jockey_id,
                jockey_name=jockey_name,
                trainer_id=trainer_id,
                trainer_name=trainer_name,
                horse_weight=horse_weight,
                horse_weight_diff=horse_weight_diff,
            )

    def parse_horse(self, response):
        return None

    def parse_jockey(self, response):
        return None

    def parse_trainer(self, response):
        return None

    def _get_text(self, row, selector):
        value = row.css(selector).get()
        if value is None:
            return None
        value = value.strip()
        return value or None

    def _extract_id(self, url, pattern):
        if not url:
            return None
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def _parse_weight(self, text):
        if not text:
            return None, None
        match = re.search(r"(\d+)(?:\(([-+]?\d+)\))?", text)
        if not match:
            return None, None
        weight = self._to_int(match.group(1))
        diff = self._to_int(match.group(2)) if match.group(2) else None
        return weight, diff

    def _to_int(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _to_float(self, value):
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None
