import asyncio
from apify import Actor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from src.spiders.rvonthego_spider import RvOnTheGoSpider

async def main():
    # Initialize the Actor
    input_data = await Actor.get_input()
    start_date = input_data.get("start_date")
    end_date = input_data.get("end_date")

    if not start_date or not end_date:
        raise ValueError("Both start_date and end_date must be provided in input.")

    # Configure Scrapy logging
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    # Pass input to spider
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    await runner.crawl(RvOnTheGoSpider, start_date=start_date, end_date=end_date)
    await runner.join()

    await Actor.exit()

if __name__ == "__main__":
    asyncio.run(main())
