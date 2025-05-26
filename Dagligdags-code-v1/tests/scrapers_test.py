import pytest
from backend.scraping.newsletter_scraper import NewsletterScraper

def test_coop_scraping():
    scraper = NewsletterScraper()
    deals = scraper.scrape_store('coop')
    assert len(deals) > 0, "Coop scraping should return deals"
