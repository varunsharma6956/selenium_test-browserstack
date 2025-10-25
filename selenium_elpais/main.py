#!/usr/bin/env python3
"""Main script for El País Opinion section scraping and analysis."""

import sys
import json
import csv
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from utils import ElPaisScraper, RapidTranslator, TextAnalyzer

def save_results_json(articles, analysis, filename='results.json'):
    """Save results to JSON file."""
    output_path = config.RESULTS_DIR / filename
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_articles': len(articles),
        'articles': articles,
        'analysis': analysis
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\u2713 Results saved to JSON: {output_path}")

def save_results_csv(articles, filename='results.csv'):
    """Save articles to CSV file."""
    output_path = config.RESULTS_DIR / filename
    
    if not articles:
        print("\u2717 No articles to save to CSV")
        return
    
    fieldnames = ['index', 'title', 'title_english', 'author', 'date', 'content', 'url', 'image_url', 'image_path']
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for article in articles:
            row = {k: article.get(k, '') for k in fieldnames}
            writer.writerow(row)
    
    print(f"\u2713 Results saved to CSV: {output_path}")

def print_summary(articles, analysis):
    """Print execution summary."""
    print(f"\n{'='*60}")
    print("EXECUTION SUMMARY")
    print(f"{'='*60}\n")
    
    print(f"Total Articles Scraped: {len(articles)}")
    print(f"Images Downloaded: {sum(1 for a in articles if a.get('image_path'))}")
    print(f"Titles Translated: {sum(1 for a in articles if a.get('title_english'))}")
    print(f"Words Analyzed: {analysis.get('total_words_analyzed', 0)}")
    print(f"Repeated Words (>2 times): {len(analysis.get('word_frequency', {}))}")
    print()
    print(f"Output Directory: {config.OUTPUT_DIR}")
    print(f"  - Images: {config.IMAGES_DIR}")
    print(f"  - Results: {config.RESULTS_DIR}")
    print()

def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("EL PAÍS OPINION SECTION SCRAPER")
    print("Technical Assignment: Selenium + API Integration")
    print("="*60)
    
    try:
        config.validate_config()
        print("\u2713 Configuration validated\n")
        
        browser_choice = 'firefox'
        
        print(f"\nUsing browser: {browser_choice.upper()}\n")
        with ElPaisScraper(browser=browser_choice, headless=True) as scraper:
            scraper.navigate_to_opinion_section()
            articles = scraper.scrape_articles(max_articles=config.MAX_ARTICLES)
            
            if not articles:
                print("\u2717 No articles found. Exiting.")
                return
            
            scraper.print_articles()
            scraper.download_images()
        
        translator = RapidTranslator()
        articles = translator.translate_articles(articles)
        translator.print_translated_titles(articles)
        
        analysis = TextAnalyzer.analyze_articles(articles)
        print(f"\n{'='*60}")
        print("SAVING RESULTS")
        print(f"{'='*60}\n")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_results_json(articles, analysis, f'elpais_results_{timestamp}.json')
        save_results_csv(articles, f'elpais_results_{timestamp}.csv')
        
        # Print summary
        print_summary(articles, analysis)
        
        print("="*60)
        print("\u2713 EXECUTION COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n\u26a0 Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\u2717 Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()