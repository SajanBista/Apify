import scrapy
import json
import urllib.parse
import os
import asyncio
from apify import Actor
from datetime import datetime, timedelta


class RvOnTheGoSpider(scrapy.Spider):
    name = "rvonthego"

    custom_settings = {
        'RETRY_TIMES': 7,
        'RETRY_HTTP_CODES': [403],
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self, start_date=None, end_date=None, proxy=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy = proxy or os.environ.get("PROXY")

        if start_date and end_date:
            self.start_date = start_date
            self.end_date = end_date
        else:
            # default: 7 days from now for 3 days
            start = datetime.now() + timedelta(days=7)
            self.start_date = start.strftime("%Y-%m-%d")
            self.end_date = (start + timedelta(days=3)).strftime("%Y-%m-%d")

        self.start_date_2 = datetime.strptime(self.start_date, "%Y-%m-%d").strftime('%B %d %Y')
        self.end_date_2 = datetime.strptime(self.end_date, "%Y-%m-%d").strftime('%B %d %Y')
        self.start_date_1 = datetime.strptime(self.start_date, "%Y-%m-%d").strftime('%b %d, %Y')
        self.end_date_1 = datetime.strptime(self.end_date, "%Y-%m-%d").strftime('%b %d, %Y')

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    headers_direction = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        url = f'https://newbook.rvonthego.com/search/?search_type=&show_parks_near=&dates={self.start_date_1}+-+{self.end_date_1}&accommodation=all'
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            headers=self.headers,
            meta={'proxy': self.proxy} if self.proxy else {}
        )

    def parse(self, response):
        urls = response.xpath("//div[@id='newbook_crs_result_elements']/a/@href").getall()
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_campsite,
                meta={'proxy': self.proxy} if self.proxy else {}
            )

    def parse_campsite(self, response):
        location_data = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get())
        address = location_data['address']
        name = location_data['name']
        street = address['streetAddress']
        city = address['addressLocality']
        state = address['addressRegion']
        zip_code = address['postalCode']

        full_address = f'{street}, {city}, {state} {zip_code}'

        try:
            number_of_sites = response.xpath('//li[contains(@class,"resort-about__count-sites")]//text()').get('').split(':')[1].strip()
        except:
            number_of_sites = ''
        open_close = response.xpath('//li[contains(@class,"resort-about__open-close")]//text()').get('')
        age_qualified = response.xpath('//li[contains(@class,"resort-about__age-qualified")]//text()').get('') != ''

        amenities = '\n'.join(response.xpath('//div[@class="resort-amenities__item-name"]//text()').getall())
        description = ' '.join([i.strip() for i in response.xpath('//section[@id="resort-description"]//text()').getall() if i.strip()])

        slug_api = response.url.split('/')[-2].replace('-', '_')
        api_url = f'https://newbook.rvonthego.com/wp-content/plugins/newbook_crs/api_files/api_{slug_api}.php?newbook_api_action=availability_chart_responsive'
        location_url = f'https://nominatim.openstreetmap.org/search?q={full_address}&format=json'

        base_url = 'https://www.rvonthego.com/'
        direction_slug = response.xpath("//section//a[contains(text(),'get directions')]/@href").get()
        directions_url = urllib.parse.urljoin(base_url, direction_slug)

        item = {
            'url': response.url,
            'from_date': self.start_date,
            'to_date': self.end_date,
            'name': name,
            'street': street,
            'city': city,
            'state': state,
            'zip': zip_code,
            'number_of_sites': number_of_sites,
            'open_close': open_close,
            'age_qualified': str(age_qualified),
            'amenities': amenities,
            'description': description,
        }

        self.headers_direction['referer'] = response.url
        yield scrapy.Request(
            url=directions_url,
            callback=self.parse_directions,
            headers=self.headers_direction,
            meta={
                'item': item,
                'api_url': api_url,
                'proxy': self.proxy
            }
        )

    def parse_directions(self, response):
        item = response.meta['item']
        api_url = response.meta['api_url']

        coordinates = response.xpath('//strong[contains(text(),"GPS Coordinates:")]/parent::p/text()').get('').strip()
        item['coordinates'] = coordinates

        # Form data for API
        data = {
            'force_booking_channel_id': '',
            'HTTP_REFERER': 'https://rvonthego.com/',
            'discount_total_display': '0',
            'force_category_type_id': '',
            'no_billing_booking': '0',
            'discount_id': 'null',
            'facebook_user_id': '',
            'category_type_id': '',
            'owner_occupied_booking_id': '',
            'discount_code': '',
            'booking_action': '',
            'available_from': self.start_date_2,
            'available_to': self.end_date_2,
            'adults': '2',
            'children': '0',
            'equipment_id': 'new_id',
            'equipment_measurement_unit': 'ft',
            'equipment_length': '',
            'equipment_width': '',
        }

        yield scrapy.FormRequest(
            url=api_url,
            formdata=data,
            callback=self.parse_api,
            headers=self.headers,
            meta={
                'item': item,
                'proxy': self.proxy
            }
        )

    def parse_api(self, response):
        item = response.meta['item']
        sites = response.xpath('//div[@class="newbook_online_category_box newbook-panel flex-column flex-style "]')

        for site in sites:
            not_available = site.xpath('.//span[contains(text(),"Not Available")]').get()
            if not_available:
                continue

            site_name = ' '.join([i.strip() for i in site.xpath('.//h3//text()').getall() if i.strip()])
            per_night_price = site.xpath('.//div[contains(text(),"Daily")]/ancestor::tr//div[@class="per_night_pricing"]//text()').get(default='').strip()
            if not per_night_price:
                per_night_price = site.xpath('.//div[contains(text(),"Retail")]/ancestor::tr//div[@class="per_night_pricing"]//text()').get(default='').strip()
            per_week_price = site.xpath('.//div[contains(text(),"Weekly")]/ancestor::tr//div[@class="per_night_pricing"]//text()').get(default='').strip()

            final_item = {
                **item,
                'site_name': site_name,
                'per_night_price': per_night_price,
                'per_week_price': per_week_price,
            }

            # Push immediately to Apify
            asyncio.get_event_loop().create_task(Actor.push_data(final_item))
