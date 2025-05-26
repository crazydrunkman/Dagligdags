import logging
import json
from datetime import datetime
from pathlib import Path
from config.paths import LOG_DIR

def setup_logger(name="dagligdags", log_level=logging.INFO):
    """Set up logging configuration"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_scrape_attempt(store_name, success=True, error_msg=None):
    """Log scraping attempts"""
    logger = setup_logger("scraper")
    
    if success:
        logger.info(f"Successfully scraped {store_name}")
    else:
        logger.error(f"Failed to scrape {store_name}: {error_msg}")

def log_user_action(user_id, action, details=None):
    """Log user actions for analytics"""
    logger = setup_logger("user_analytics")
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'action': action,
        'details': details or {}
    }
    
    logger.info(json.dumps(log_entry))

def log_deal_match(user_id, deals_found, match_score):
    """Log deal matching results"""
    logger = setup_logger("matching")
    
    logger.info(f"User {user_id}: Found {deals_found} deals, avg score: {match_score:.2f}")
