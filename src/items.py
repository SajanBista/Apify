import scrapy


class RvOnTheGoItem(scrapy.Item):
    url = scrapy.Field()
    from_date = scrapy.Field()
    to_date = scrapy.Field()
    name = scrapy.Field()
    street = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip = scrapy.Field()
    number_of_sites = scrapy.Field()
    open_close = scrapy.Field()
    age_qualified = scrapy.Field()
    amenities = scrapy.Field()
    coordinates = scrapy.Field()
    site_name = scrapy.Field()
    per_night_price = scrapy.Field()
    per_week_price = scrapy.Field()
