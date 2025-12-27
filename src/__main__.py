import asyncio
from apify import Actor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from src.spiders.rvonthego_spider import RvOnTheGoSpider


async def main():
    # ✅ MUST be first
    await Actor.init()

    # Read input
    input_data = await Actor.get_input() or {}
    start_date = input_data.get("start_date")
    end_date = input_data.get("end_date")

    if not start_date or not end_date:
        raise ValueError("start_date and end_date are required")

    # Configure Scrapy logging
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    settings = get_project_settings()

    # Pass arguments into spider
    runner = CrawlerRunner(settings)
    await runner.crawl(
        RvOnTheGoSpider,
        start_date=start_date,
        end_date=end_date
    )

    await Actor.exit()


if __name__ == "__main__":
    asyncio.run(main())
