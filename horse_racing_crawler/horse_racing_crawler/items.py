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


class HorseItem(scrapy.Item):
    horse_id = scrapy.Field()
    horse_name = scrapy.Field()
    sex = scrapy.Field()
    age = scrapy.Field()
    birthday = scrapy.Field()
    trainer_id = scrapy.Field()
    trainer_name = scrapy.Field()
    owner_id = scrapy.Field()
    owner_name = scrapy.Field()
    breeder_id = scrapy.Field()
    breeder_name = scrapy.Field()
    production = scrapy.Field()
    coat_color = scrapy.Field()
    father = scrapy.Field()
    mother = scrapy.Field()
    mother_father = scrapy.Field()


class JockeyItem(scrapy.Item):
    jockey_id = scrapy.Field()
    jockey_name = scrapy.Field()
    birthday = scrapy.Field()
    hometown = scrapy.Field()
    license_year = scrapy.Field()
    affiliation = scrapy.Field()


class TrainerItem(scrapy.Item):
    trainer_id = scrapy.Field()
    trainer_name = scrapy.Field()
    birthday = scrapy.Field()
    hometown = scrapy.Field()
    license_year = scrapy.Field()
    affiliation = scrapy.Field()
