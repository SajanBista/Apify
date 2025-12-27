import asyncio
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from src.spiders.rvonthego_spider import RvOnTheGoSpider
from apify import Actor

async def run_scraper(input_data):
    # Configure logging
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    # Scrapy settings
    settings = get_project_settings()

    # Pass input dates to spider
    start_date = input_data.get("start_date")
    end_date = input_data.get("end_date")
    proxy = input_data.get("proxy")  # Optional local proxy

    runner = CrawlerRunner(settings)

    # Crawl the spider with user-provided dates
    await runner.crawl(RvOnTheGoSpider, start_date=start_date, end_date=end_date, proxy=proxy)
    await runner.join()
