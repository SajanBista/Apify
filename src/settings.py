BOT_NAME = "rvonthego"

SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 1
RETRY_ENABLED = True
RETRY_TIMES = 7
RETRY_HTTP_CODES = [403]

LOG_LEVEL = "INFO"

FEEDS = {
    "apify_dataset": {"format": "json"}
}
