"""Configuration module for El País Selenium scraper."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Rapid Translate API Configuration
RAPID_TRANSLATE_API_KEY = os.getenv('RAPID_TRANSLATE_API_KEY')
RAPID_TRANSLATE_API_HOST = os.getenv('RAPID_TRANSLATE_API_HOST')
RAPID_TRANSLATE_API_URL = os.getenv('RAPID_TRANSLATE_API_URL')

# BrowserStack Configuration
BROWSERSTACK_USERNAME = os.getenv('BROWSERSTACK_USERNAME')
BROWSERSTACK_ACCESS_KEY = os.getenv('BROWSERSTACK_ACCESS_KEY')

# El País Website
ELPAIS_OPINION_URL = os.getenv('ELPAIS_OPINION_URL', 'https://elpais.com/opinion/')

# Output Configuration
OUTPUT_DIR = PROJECT_ROOT / os.getenv('OUTPUT_DIR', 'output')
IMAGES_DIR = PROJECT_ROOT / os.getenv('IMAGES_DIR', 'output/images')
RESULTS_DIR = PROJECT_ROOT / os.getenv('RESULTS_DIR', 'output/results')
MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', 5))

# Create output directories if they don't exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Selenium Configuration
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 15
PAGE_LOAD_TIMEOUT = 30

def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if not RAPID_TRANSLATE_API_KEY:
        errors.append("RAPID_TRANSLATE_API_KEY is not set in .env file")
    
    if not BROWSERSTACK_USERNAME:
        errors.append("BROWSERSTACK_USERNAME is not set in .env file")
    
    if not BROWSERSTACK_ACCESS_KEY:
        errors.append("BROWSERSTACK_ACCESS_KEY is not set in .env file")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True