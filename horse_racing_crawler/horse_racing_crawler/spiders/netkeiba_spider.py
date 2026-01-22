import os
import re

import scrapy

from horse_racing_crawler.items import HorseItem, JockeyItem, ShutubaItem, TrainerItem


class NetkeibaSpider(scrapy.Spider):
    name = "NetkeibaSpider"
    allowed_domains = ["race.netkeiba.com", "db.netkeiba.com"]

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("start_url is required")
        self.start_url = start_url
        self.start_url_type = self._classify_start_url(start_url)
        if not self.start_url_type:
            raise ValueError(f"Unsupported start_url: {start_url}")
        if self.start_url_type == "shutuba":
            self.race_id = self._extract_id(start_url, r"[?&]race_id=(\d+)")
            if not self.race_id:
                raise ValueError("start_url must include race_id for shutuba pages")
        else:
            self.race_id = None

    def start_requests(self):
        os.makedirs(os.getenv("OUTPUT_DIR", "./output"), exist_ok=True)
        callback_map = {
            "shutuba": self.parse,
            "horse": self.parse_horse,
            "jockey": self.parse_jockey,
            "trainer": self.parse_trainer,
        }
        callback = callback_map[self.start_url_type]
        yield scrapy.Request(self.start_url, callback=callback)

    def parse(self, response):
        rows = response.xpath(
            "//table[contains(@class,'ShutubaTable')]//tr[contains(@class,'HorseList')]"
        )
        for row in rows:
            horse_name = self._get_xpath_text(
                row,
                "normalize-space(.//span[contains(@class,'HorseName')]/a/text()[1])",
            )
            if not horse_name:
                continue

            bracket_number = self._get_xpath_text(
                row,
                "normalize-space(.//td[starts-with(@class,'Waku')]/span/text())",
            )
            horse_number = self._get_xpath_text(
                row,
                "normalize-space(.//td[starts-with(@class,'Umaban')]/text())",
            )
            horse_link = row.xpath(
                ".//span[contains(@class,'HorseName')]/a/@href"
            ).get()
            jockey_link = row.xpath(".//td[contains(@class,'Jockey')]/a/@href").get()
            trainer_link = row.xpath(".//td[contains(@class,'Trainer')]/a/@href").get()

            horse_id = self._extract_id(horse_link, r"/horse/(\d+)/")
            jockey_id = self._extract_id(
                jockey_link, r"/jockey/(?:result/recent/)?(\d+)/"
            )
            trainer_id = self._extract_id(
                trainer_link, r"/trainer/(?:result/recent/)?(\d+)/"
            )

            jockey_weight = self._get_xpath_text(
                row,
                "normalize-space(.//td[contains(@class,'Barei')]/following-sibling::td[1]/text())",
            )
            jockey_name = self._get_xpath_text(
                row, "normalize-space(.//td[contains(@class,'Jockey')]/a/text())"
            )
            trainer_name = self._get_xpath_text(
                row, "normalize-space(.//td[contains(@class,'Trainer')]/a/text())"
            )

            horse_weight_text = self._get_xpath_text(
                row, "normalize-space(.//td[contains(@class,'Weight')]/text()[1])"
            )
            horse_weight_diff_text = self._get_xpath_text(
                row, "normalize-space(.//td[contains(@class,'Weight')]/small/text())"
            )
            horse_weight = None
            if horse_weight_text and horse_weight_text not in ("計不", "--"):
                horse_weight = self._to_int(horse_weight_text)

            horse_weight_diff = None
            if horse_weight_diff_text:
                diff_clean = horse_weight_diff_text.strip().lstrip("(").rstrip(")")
                horse_weight_diff = self._to_int(diff_clean)

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

    def _get_text(self, row, selector):
        value = row.css(selector).get()
        if value is None:
            return None
        value = value.strip()
        return value or None

    def _get_xpath_text(self, row, selector):
        value = row.xpath(selector).get()
        if value is None:
            return None
        value = value.strip()
        return value or None

    def _extract_id(self, url, pattern):
        if not url:
            return None
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def _classify_start_url(self, url):
        if re.search(r"^https?://race\.netkeiba\.com/race/shutuba\.html", url):
            return "shutuba"
        if re.search(r"^https?://db\.netkeiba\.com/horse/\d+/", url):
            return "horse"
        if re.search(r"^https?://db\.netkeiba\.com/jockey/(?:result/recent/)?\d+/", url):
            return "jockey"
        if re.search(r"^https?://db\.netkeiba\.com/trainer/(?:result/recent/)?\d+/", url):
            return "trainer"
        return None

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

    def _get_profile_value(self, row):
        texts = [
            text.strip()
            for text in row.css("td::text, td *::text").getall()
            if text.strip()
        ]
        return " ".join(texts) if texts else None

    def _find_profile_row(self, response, label):
        for row in response.css("table.db_prof_table tr"):
            row_label = self._get_text(row, "th::text")
            if row_label == label:
                return row
        return None

    def parse_horse(self, response):
        """
        @url https://db.netkeiba.com/horse/2021110048/
        @returns items 1 1
        @scrapes horse_id horse_name sex age birthday trainer_id trainer_name owner_id owner_name breeder_id breeder_name production coat_color father mother mother_father
        """
        horse_id = self._extract_id(response.url, r"/horse/(\d+)/")
        horse_name = (
            self._get_text(response, "div.horse_title h1::text")
            or self._get_text(response, "div.horse_title h1 span::text")
        )
        sex = None
        age = None
        sex_age_text = " ".join(
            text.strip()
            for text in response.css(
                "div.horse_title p::text, div.horse_title p span::text"
            ).getall()
            if text.strip()
        )
        match = re.search(r"(牡|牝|セ)\s*(\d+)", sex_age_text)
        if match:
            sex = match.group(1)
            age = self._to_int(match.group(2))

        birthday_row = self._find_profile_row(response, "生年月日")
        trainer_row = self._find_profile_row(response, "調教師")
        owner_row = self._find_profile_row(response, "馬主")
        breeder_row = self._find_profile_row(response, "生産者")
        production_row = self._find_profile_row(response, "産地")
        coat_row = self._find_profile_row(response, "毛色")
        father_row = self._find_profile_row(response, "父")
        mother_row = self._find_profile_row(response, "母")
        mother_father_row = self._find_profile_row(response, "母父")

        trainer_link = trainer_row.css("td a::attr(href)").get() if trainer_row else None
        owner_link = owner_row.css("td a::attr(href)").get() if owner_row else None
        breeder_link = breeder_row.css("td a::attr(href)").get() if breeder_row else None

        yield HorseItem(
            horse_id=horse_id,
            horse_name=horse_name,
            sex=sex,
            age=age,
            birthday=self._get_profile_value(birthday_row) if birthday_row else None,
            trainer_id=self._extract_id(trainer_link, r"/trainer/(\d+)/"),
            trainer_name=(
                self._get_text(trainer_row, "td a::text")
                if trainer_row
                else None
            )
            or (self._get_profile_value(trainer_row) if trainer_row else None),
            owner_id=self._extract_id(owner_link, r"/owner/(\d+)/"),
            owner_name=(self._get_text(owner_row, "td a::text") if owner_row else None)
            or (self._get_profile_value(owner_row) if owner_row else None),
            breeder_id=self._extract_id(breeder_link, r"/breeder/(\d+)/"),
            breeder_name=(
                self._get_text(breeder_row, "td a::text") if breeder_row else None
            )
            or (self._get_profile_value(breeder_row) if breeder_row else None),
            production=self._get_profile_value(production_row) if production_row else None,
            coat_color=self._get_profile_value(coat_row) if coat_row else None,
            father=self._get_profile_value(father_row) if father_row else None,
            mother=self._get_profile_value(mother_row) if mother_row else None,
            mother_father=self._get_profile_value(mother_father_row)
            if mother_father_row
            else None,
        )

    def parse_jockey(self, response):
        """
        @url https://db.netkeiba.com/jockey/result/recent/01163/
        @returns items 1 1
        @scrapes jockey_id jockey_name birthday hometown license_year affiliation
        """
        jockey_id = self._extract_id(response.url, r"/jockey/(\d+)/")
        jockey_name = (
            self._get_text(response, "div.db_main h1::text")
            or self._get_text(response, "div.db_main h1 span::text")
        )

        birthday_row = self._find_profile_row(response, "生年月日")
        hometown_row = self._find_profile_row(response, "出身地")
        license_row = self._find_profile_row(response, "初免許年")
        affiliation_row = self._find_profile_row(response, "所属")

        yield JockeyItem(
            jockey_id=jockey_id,
            jockey_name=jockey_name,
            birthday=self._get_profile_value(birthday_row) if birthday_row else None,
            hometown=self._get_profile_value(hometown_row) if hometown_row else None,
            license_year=self._get_profile_value(license_row) if license_row else None,
            affiliation=self._get_profile_value(affiliation_row) if affiliation_row else None,
        )

    def parse_trainer(self, response):
        """
        @url https://db.netkeiba.com/trainer/result/recent/01075/
        @returns items 1 1
        @scrapes trainer_id trainer_name birthday hometown license_year affiliation
        """
        trainer_id = self._extract_id(response.url, r"/trainer/(\d+)/")
        trainer_name = (
            self._get_text(response, "div.db_main h1::text")
            or self._get_text(response, "div.db_main h1 span::text")
        )

        birthday_row = self._find_profile_row(response, "生年月日")
        hometown_row = self._find_profile_row(response, "出身地")
        license_row = self._find_profile_row(response, "初免許年")
        affiliation_row = self._find_profile_row(response, "所属")

        yield TrainerItem(
            trainer_id=trainer_id,
            trainer_name=trainer_name,
            birthday=self._get_profile_value(birthday_row) if birthday_row else None,
            hometown=self._get_profile_value(hometown_row) if hometown_row else None,
            license_year=self._get_profile_value(license_row) if license_row else None,
            affiliation=self._get_profile_value(affiliation_row) if affiliation_row else None,
        )
