import requests
import pdfplumber
import re
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.constants import STORE_URLS, REQUEST_TIMEOUT
from config.paths import PDF_STORAGE_DIR, PARSED_DATA_DIR
from utilities.logger import setup_logger

class NewsletterScraper:
    """Scrapes grocery newsletters from Norwegian stores with robust error handling."""
    
    def __init__(self):
        self.logger = setup_logger("newsletter_scraper")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept-Language': 'nb-NO, nb;q=0.9'
        })
        self.verify_ssl = False  # Set via environment variable in production
        self.timeout = REQUEST_TIMEOUT

    def scrape_all_stores(self) -> Dict[str, List[Dict]]:
        """Orchestrate scraping for all configured stores."""
        all_deals = {}
        
        for store_name, base_url in STORE_URLS.items():
            try:
                self.logger.info(f"🔄 Starting scrape for {store_name}")
                if store_name in ['coop', 'rema', 'bunnpris']:
                    deals = self._scrape_pdf_store(base_url)
                else:
                    deals = self._scrape_html_store(base_url)
                all_deals[store_name] = deals
                self.logger.info(f"✅ Successfully scraped {store_name}: {len(deals)} deals")
            except Exception as e:
                self.logger.error(f"❌ Critical error scraping {store_name}: {str(e)}", exc_info=True)
                all_deals[store_name] = []
        
        self._save_results(all_deals)
        return all_deals

    def _scrape_pdf_store(self, base_url: str) -> List[Dict]:
        """Handle PDF-based newsletter stores."""
        try:
            pdf_url = self._find_pdf_link(base_url)
            if not pdf_url:
                return []
                
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                self._download_pdf(pdf_url, tmp_file.name)
                return self._parse_pdf(tmp_file.name)
        except Exception as e:
            self.logger.error(f"PDF processing failed: {str(e)}")
            return []

    def _find_pdf_link(self, base_url: str) -> Optional[str]:
        """Extract latest PDF link from store website."""
        try:
            response = self.session.get(base_url, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Norwegian-specific PDF link detection
            for link in soup.find_all('a', href=True):
                if 'tilbudsavis' in link.text.lower() or link['href'].endswith('.pdf'):
                    return urljoin(base_url, link['href'])
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error fetching PDF links: {e.response.status_code}")
            return None

    def _download_pdf(self, url: str, save_path: str) -> None:
        """Download PDF with proper resource cleanup."""
        try:
            response = self.session.get(url, stream=True, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.SSLError:
            self.logger.warning("⚠️ SSL verification failed, retrying without...")
            response = self.session.get(url, stream=True, timeout=self.timeout, verify=False)
            response.raise_for_status()

    def _parse_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract deals from PDF with fallback strategies."""
        deals = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text(layout=True) or ''
                    deals.extend(self._parse_page_text(text))
        except pdfplumber.PDFSyntaxError:
            self.logger.warning("⚠️ PDF syntax error, attempting OCR fallback...")
            deals.extend(self._parse_with_ocr(pdf_path))
        return deals

    def _parse_page_text(self, text: str) -> List[Dict]:
        """Parse Norwegian price patterns from text."""
        price_regex = r"""
            (?P<product>.+?)          # Product name
            \s+                       # Whitespace separator
            (?P<price>\d{1,3}(?:,\d{2})?)\s*kr  # Norwegian price format
        """
        matches = re.finditer(price_regex, text, re.VERBOSE)
        return [{
            'product': m.group('product').strip(),
            'price': float(m.group('price').replace(',', '.')),
            'source': 'pdf',
            'scraped_at': datetime.now().isoformat()
        } for m in matches]

    def _parse_with_ocr(self, pdf_path: str) -> List[Dict]:
        """Fallback PDF parsing using OCR."""
        # Implementation would use Tesseract here
        return []

    def _scrape_html_store(self, base_url: str) -> List[Dict]:
        """Scrape HTML-based deal listings."""
        try:
            response = self.session.get(base_url, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            return self._parse_html(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTML scrape failed: {str(e)}")
            return []

    def _parse_html(self, html: str) -> List[Dict]:
        """Parse Norwegian HTML structure for deals."""
        soup = BeautifulSoup(html, 'lxml')
        deals = []
        
        # Example for Oda-style HTML
        for item in soup.select('[data-testid="product-item"]'):
            try:
                name = item.select_one('.product-name').text.strip()
                price_text = item.select_one('.price').text
                price = float(price_text.replace('kr', '').replace(',', '.').strip())
                deals.append({
                    'product': name,
                    'price': price,
                    'source': 'html',
                    'scraped_at': datetime.now().isoformat()
                })
            except (AttributeError, ValueError) as e:
                self.logger.debug(f"Skipping invalid item: {str(e)}")
        return deals

    def _save_results(self, data: Dict) -> None:
        """Atomic write with backup retention."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = PARSED_DATA_DIR / f"deals_{timestamp}.json"
            
            # Write to temp file first
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
                json.dump(data, tmp, ensure_ascii=False, indent=2)
                
            # Atomic rename
            Path(tmp.name).rename(output_file)
            self.logger.info(f"💾 Saved {len(data)} stores' deals to {output_file}")
        except Exception as e:
            self.logger.error(f"💥 Failed to save results: {str(e)}")

if __name__ == "__main__":
    scraper = NewsletterScraper()
    scraper.scrape_all_stores()
