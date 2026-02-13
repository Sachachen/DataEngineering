import os

BOT_NAME = "ligue1_scraper"

SPIDER_MODULES = ["ligue1_scraper.spiders"]
NEWSPIDER_MODULE = "ligue1_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 2

# Disable cookies
COOKIES_ENABLED = False

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Configure item pipelines
ITEM_PIPELINES = {
    "ligue1_scraper.pipelines.DataCleaningPipeline": 300,
    "ligue1_scraper.pipelines.MongoDBPipeline": 400,
}

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://admin:password123@mongodb:27017/ligue1_db?authSource=admin')
MONGO_DATABASE = os.getenv('MONGO_DB', 'ligue1_db')

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Log level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
