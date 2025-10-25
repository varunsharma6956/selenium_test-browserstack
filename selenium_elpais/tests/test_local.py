"""Local testing script for Chrome and Firefox."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from utils import ElPaisScraper, RapidTranslator, TextAnalyzer

def test_browser(browser_name):
    """Test scraping with a specific browser."""
    print(f"\n{'='*60}")
    print(f"TESTING WITH {browser_name.upper()}")
    print(f"{'='*60}\n")
    
    try:
        with ElPaisScraper(browser=browser_name, headless=True) as scraper:
            scraper.navigate_to_opinion_section()
            articles = scraper.scrape_articles(max_articles=2)  # Test with 2 articles
            
            if articles:
                print(f"✓ Successfully scraped {len(articles)} articles with {browser_name}")
                print(f"  - Sample title: {articles[0]['title'][:50]}...")
                return True
            else:
                print(f"✗ No articles found with {browser_name}")
                return False
                
    except Exception as e:
        print(f"✗ Error testing {browser_name}: {str(e)}")
        return False

def main():
    """Test locally with both Chrome and Firefox."""
    print("\n" + "="*60)
    print("LOCAL BROWSER TESTING")
    print("Testing Chrome and Firefox compatibility")
    print("="*60)
    
    # Validate config
    config.validate_config()
    
    results = {}
    
    # Test Chrome
    results['chrome'] = test_browser('chrome')
    
    # Test Firefox
    results['firefox'] = test_browser('firefox')
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}\n")
    
    for browser, success in results.items():
        status = "\u2713 PASSED" if success else "\u2717 FAILED"
        print(f"{browser.capitalize()}: {status}")
    
    print()
    
    if all(results.values()):
        print("\u2713 All local tests passed! Ready for BrowserStack.\n")
        return 0
    else:
        print("\u2717 Some tests failed. Please fix issues before BrowserStack testing.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())