import requests
import pdfplumber
import re
import json
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from config.constants import STORE_URLS
from config.paths import PDF_STORAGE_DIR, PARSED_DATA_DIR
from utilities.logger import setup_logger

class NewsletterScraper:
    def __init__(self):
        self.logger = setup_logger("newsletter_scraper")
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        # For dev: disable SSL verification (not for production!)
        self.verify_ssl = False

    def scrape_all_stores(self):
        """Scrape newsletters from all configured Norwegian stores"""
        all_deals = {}
        for store_name, base_url in STORE_URLS.items():
            try:
                self.logger.info(f"Starting scrape for {store_name}")
                if store_name in ['coop', 'rema', 'bunnpris']:
                    deals = self._scrape_pdf_newsletter(store_name, base_url)
                else:
                    deals = self._scrape_html_deals(store_name, base_url)
                all_deals[store_name] = deals
                self.logger.info(f"Successfully scraped {store_name}")
            except Exception as e:
                self.logger.error(f"Error scraping {store_name}: {e}")
                all_deals[store_name] = []
        self._save_deals(all_deals)
        return all_deals

    def _scrape_pdf_newsletter(self, store_name, base_url):
        """Scrape PDF newsletters (Coop, Rema 1000, Bunnpris)"""
        try:
            response = self.session.get(base_url, headers=self.headers, verify=self.verify_ssl)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = [link['href'] for link in soup.find_all('a', href=True) if link['href'].endswith('.pdf')]
            if not pdf_links:
                self.logger.warning(f"No PDF found for {store_name}")
                return []
            pdf_url = pdf_links[0]
            return self._download_and_parse_pdf(store_name, pdf_url)
        except requests.exceptions.SSLError as ssl_err:
            self.logger.error(f"SSL error for {store_name}: {ssl_err}")
            return []
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                self.logger.error(f"404 Not Found for {store_name}: {base_url}")
            else:
                self.logger.error(f"HTTP error for {store_name}: {http_err}")
            return []
        except Exception as e:
            self.logger.error(f"Error in PDF scraping for {store_name}: {e}")
            return []

    def _download_and_parse_pdf(self, store_name, pdf_url):
        try:
            response = self.session.get(pdf_url, headers=self.headers, verify=self.verify_ssl)
            response.raise_for_status()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = PDF_STORAGE_DIR / f"{store_name}_{timestamp}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            return self._parse_pdf(pdf_path)
        except Exception as e:
            self.logger.error(f"Error downloading/parsing PDF for {store_name}: {e}")
            return []

    def _parse_pdf(self, pdf_path):
        deals = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    matches = re.findall(r'(\w+.*?)\s+(\d{1,3}(?:,\d{2})?\s*kr)', text)
                    for match in matches:
                        product_name = match[0].strip()
                        price_text = match[1].strip()
                        try:
                            price_value = float(price_text.replace('kr', '').replace(',', '.').strip())
                        except ValueError:
                            price_value = None
                        if price_value:
                            deals.append({
                                'product': product_name,
                                'price': price_value,
                                'store': pdf_path.name.split('_')[0],
                                'source': 'newsletter_pdf',
                                'scraped_at': datetime.now().isoformat()
                            })
        except Exception as e:
            self.logger.error(f"PDF parsing error: {e}")
        return deals

    def _scrape_html_deals(self, store_name, base_url):
        try:
            response = self.session.get(base_url, headers=self.headers, verify=self.verify_ssl)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            deals = []
            # Example: update selectors for each store as needed
            if store_name == 'oda':
                products = soup.select('.product-name')
                prices = soup.select('.price')
                for prod, price in zip(products, prices):
                    try:
                        price_value = float(price.get_text().replace('kr', '').replace(',', '.').strip())
                    except ValueError:
                        price_value = None
                    if price_value:
                        deals.append({
                            'product': prod.get_text().strip(),
                            'price': price_value,
                            'store': store_name,
                            'source': 'website',
                            'scraped_at': datetime.now().isoformat()
                        })
            return deals
        except requests.exceptions.SSLError as ssl_err:
            self.logger.error(f"SSL error for {store_name}: {ssl_err}")
            return []
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                self.logger.error(f"404 Not Found for {store_name}: {base_url}")
            elif http_err.response.status_code == 403:
                self.logger.error(f"403 Forbidden for {store_name}: {base_url}")
            else:
                self.logger.error(f"HTTP error for {store_name}: {http_err}")
            return []
        except Exception as e:
            self.logger.error(f"Error in HTML scraping for {store_name}: {e}")
            return []

    def _save_deals(self, all_deals):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = PARSED_DATA_DIR / f"deals_{timestamp}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_deals, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved deals to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save deals: {e}")

if __name__ == "__main__":
    scraper = NewsletterScraper()
    scraper.scrape_all_stores()
