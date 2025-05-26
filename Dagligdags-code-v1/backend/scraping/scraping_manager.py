# backend/scraping/scraping_manager.py

import traceback
from datetime import datetime
from backend.scraping.newsletter_scraper import NewsletterScraper
from backend.scraping.database_scraper import DatabaseScraper
from utilities.logger import setup_logger

class ScrapingManager:
    def __init__(self):
        self.logger = setup_logger("scraping_manager")
        self.newsletter_scraper = NewsletterScraper()
        self.database_scraper = DatabaseScraper()

    def run_daily_scrape(self):
        """Run all scraping tasks for the day and log results."""
        self.logger.info("Starting daily scraping tasks...")

        try:
            self.logger.info("Scraping newsletters...")
            newsletter_results = self.newsletter_scraper.scrape_all_stores()
            self.logger.info(f"Newsletter scraping complete. {len(newsletter_results)} stores scraped.")
        except Exception as e:
            self.logger.error(f"Error scraping newsletters: {e}")
            self.logger.error(traceback.format_exc())

        try:
            self.logger.info("Scraping product/nutrition databases...")
            db_results = self.database_scraper.scrape_all_databases()
            self.logger.info(f"Database scraping complete. {len(db_results)} databases scraped.")
        except Exception as e:
            self.logger.error(f"Error scraping databases: {e}")
            self.logger.error(traceback.format_exc())

        self.logger.info("All scraping tasks finished at " + datetime.now().isoformat())

    def run_newsletter_scrape(self):
        """Run only the newsletter scraper."""
        self.logger.info("Running newsletter scraper only...")
        try:
            return self.newsletter_scraper.scrape_all_stores()
        except Exception as e:
            self.logger.error(f"Error in newsletter scraper: {e}")
            self.logger.error(traceback.format_exc())
            return {}

    def run_database_scrape(self):
        """Run only the database scraper."""
        self.logger.info("Running database scraper only...")
        try:
            return self.database_scraper.scrape_all_databases()
        except Exception as e:
            self.logger.error(f"Error in database scraper: {e}")
            self.logger.error(traceback.format_exc())
            return {}

# For manual testing
if __name__ == "__main__":
    manager = ScrapingManager()
    manager.run_daily_scrape()
