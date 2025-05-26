import pdfplumber
import requests
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config.constants import STORE_URLS
from config.paths import PDF_STORAGE_DIR, PARSED_DATA_DIR
from utilities.logger import setup_logger, log_scrape_attempt

class NewsletterScraper:
    def __init__(self):
        self.logger = setup_logger("newsletter_scraper")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_all_stores(self):
        """Scrape newsletters from all Norwegian stores"""
        all_deals = {}
        
        for store_name, base_url in STORE_URLS.items():
            try:
                self.logger.info(f"Starting scrape for {store_name}")
                
                if store_name in ['coop', 'rema', 'bunnpris']:
                    deals = self._scrape_pdf_newsletter(store_name, base_url)
                else:
                    deals = self._scrape_html_deals(store_name, base_url)
                
                all_deals[store_name] = deals
                log_scrape_attempt(store_name, success=True)
                
            except Exception as e:
                self.logger.error(f"Error scraping {store_name}: {str(e)}")
                log_scrape_attempt(store_name, success=False, error_msg=str(e))
                all_deals[store_name] = []
        
        # Save all deals
        self._save_deals(all_deals)
        return all_deals
    
    def _scrape_pdf_newsletter(self, store_name, base_url):
        """Scrape PDF newsletters (Coop, Rema 1000, etc.)"""
        try:
            # Get the webpage
            response = self.session.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find PDF links (Norwegian stores often use specific patterns)
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf') or 'tilbud' in href.lower():
                    full_url = urljoin(base_url, href)
                    pdf_links.append(full_url)
            
            # Download and parse first PDF found
            if pdf_links:
                pdf_url = pdf_links[0]
                deals = self._download_and_parse_pdf(store_name, pdf_url)
                return deals
            else:
                self.logger.warning(f"No PDF found for {store_name}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in PDF scraping for {store_name}: {str(e)}")
            return []
    
    def _download_and_parse_pdf(self, store_name, pdf_url):
        """Download PDF and extract deals"""
        try:
            # Download PDF
            response = self.session.get(pdf_url)
            response.raise_for_status()
            
            # Save PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = PDF_STORAGE_DIR / f"{store_name}_{timestamp}.pdf"
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # Parse PDF
            deals = self._parse_pdf(pdf_path)
            
            # Add metadata
            for deal in deals:
                deal.update({
                    'store': store_name,
                    'source': 'newsletter_pdf',
                    'scraped_at': datetime.now().isoformat(),
                    'pdf_url': pdf_url
                })
            
            return deals
            
        except Exception as e:
            self.logger.error(f"Error downloading/parsing PDF: {str(e)}")
            return []
    
    def _parse_pdf(self, pdf_path):
        """Extract deals from PDF using Norwegian price patterns"""
        deals = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # Norwegian price patterns
                price_patterns = [
                    r'(\w+.*?)\s+(\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*kr)',  # "Product 29,90 kr"
                    r'(\w+.*?)\s+kr\s+(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # "Product kr 29,90"
                    r'(\w+.*?)\s+(\d+,-)',  # "Product 29,-"
                ]
                
                for pattern in price_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        product_name = match[0].strip()
                        price_text = match[1].strip()
                        
                        # Clean product name
                        product_name = re.sub(r'[^\w\s]', '', product_name)[:50]
                        
                        # Parse price
                        price_value = self._parse_norwegian_price(price_text)
                        
                        if price_value and len(product_name) > 2:
                            deals.append({
                                'product': product_name,
                                'price': price_value,
                                'original_price_text': price_text,
                                'page': page_num + 1
                            })
        
        return deals
    
    def _parse_norwegian_price(self, price_text):
        """Parse Norwegian price format (29,90 kr)"""
        try:
            # Remove 'kr' and whitespace
            clean_price = re.sub(r'kr|,|-', '.', price_text.lower())
            clean_price = re.sub(r'[^\d.]', '', clean_price)
            
            if clean_price:
                return float(clean_price)
            return None
        except:
            return None
    
    def _scrape_html_deals(self, store_name, base_url):
        """Scrape HTML-based deal pages (Oda, Wolt, etc.)"""
        try:
            response = self.session.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            deals = []
            
            # Store-specific selectors
            selectors = {
                'oda': {
                    'product': '.product-name',
                    'price': '.price'
                },
                'wolt': {
                    'product': '[data-test-id="product-name"]',
                    'price': '[data-test-id="product-price"]'
                }
            }
            
            if store_name in selectors:
                selector = selectors[store_name]
                
                products = soup.select(selector['product'])
                prices = soup.select(selector['price'])
                
                for product, price in zip(products, prices):
                    product_name = product.get_text().strip()
                    price_value = self._parse_norwegian_price(price.get_text())
                    
                    if product_name and price_value:
                        deals.append({
                            'product': product_name,
                            'price': price_value,
                            'store': store_name,
                            'source': 'website',
                            'scraped_at': datetime.now().isoformat()
                        })
            
            return deals
            
        except Exception as e:
            self.logger.error(f"Error in HTML scraping for {store_name}: {str(e)}")
            return []
    
    def _save_deals(self, all_deals):
        """Save deals to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = PARSED_DATA_DIR / f"deals_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_deals, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved deals to {output_file}")

# Test the scraper
if __name__ == "__main__":
    scraper = NewsletterScraper()
    deals = scraper.scrape_all_stores()
    print(f"Scraped deals from {len(deals)} stores")
    for store, store_deals in deals.items():
        print(f"{store}: {len(store_deals)} deals")
