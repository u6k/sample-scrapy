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
    horse_id = scrapy.Field(required=True)
    horse_name = scrapy.Field()
    birth_date = scrapy.Field()
    sex = scrapy.Field()
    coat_color = scrapy.Field()
    affiliation = scrapy.Field()
    trainer_id = scrapy.Field()
    trainer_name = scrapy.Field()
    owner_name = scrapy.Field()
    breeder_name = scrapy.Field()
    birthplace = scrapy.Field()
    sire_name = scrapy.Field()
    dam_name = scrapy.Field()
    dam_sire_name = scrapy.Field()
    total_starts = scrapy.Field()
    wins = scrapy.Field()
    seconds = scrapy.Field()
    thirds = scrapy.Field()
    fourths = scrapy.Field()
    earnings = scrapy.Field()


class JockeyItem(scrapy.Item):
    jockey_id = scrapy.Field(required=True)
    jockey_name = scrapy.Field()
    birth_date = scrapy.Field()
    affiliation = scrapy.Field()
    license_year = scrapy.Field()
    total_starts = scrapy.Field()
    wins = scrapy.Field()
    seconds = scrapy.Field()
    thirds = scrapy.Field()
    earnings = scrapy.Field()


class TrainerItem(scrapy.Item):
    trainer_id = scrapy.Field(required=True)
    trainer_name = scrapy.Field()
    birth_date = scrapy.Field()
    affiliation = scrapy.Field()
    license_year = scrapy.Field()
    total_starts = scrapy.Field()
    wins = scrapy.Field()
    seconds = scrapy.Field()
    thirds = scrapy.Field()
    earnings = scrapy.Field()
