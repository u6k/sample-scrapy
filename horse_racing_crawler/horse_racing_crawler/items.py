import scrapy


class ShutubaItem(scrapy.Item):
    race_id = scrapy.Field()
    bracket_number = scrapy.Field()
    horse_number = scrapy.Field()
    horse_id = scrapy.Field()
    horse_name = scrapy.Field()
    jockey_weight = scrapy.Field()
    jockey_id = scrapy.Field()
    jockey_name = scrapy.Field()
    trainer_id = scrapy.Field()
    trainer_name = scrapy.Field()
    horse_weight = scrapy.Field()
    horse_weight_diff = scrapy.Field()
