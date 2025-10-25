"""Rapid Translate API integration module."""

import requests
import time
import config

class RapidTranslator:
    """Translator using Rapid Translate Multi Traduction API."""
    
    def __init__(self):
        """Initialize the translator with API credentials."""
        self.api_url = config.RAPID_TRANSLATE_API_URL
        self.api_key = config.RAPID_TRANSLATE_API_KEY
        self.api_host = config.RAPID_TRANSLATE_API_HOST
        
        self.headers = {
            'Content-Type': 'application/json',
            'x-rapidapi-host': self.api_host,
            'x-rapidapi-key': self.api_key
        }
    
    def translate_text(self, text, source_lang='es', target_lang='en'):
        """
        Translate text using Rapid Translate API.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code (default: 'es' for Spanish)
            target_lang (str): Target language code (default: 'en' for English)
            
        Returns:
            str: Translated text or original text if translation fails
        """
        try:
            payload = {
                "from": source_lang,
                "to": target_lang,
                "q": text
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # The API returns the translated text in different formats
                # Try to extract it
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
                elif isinstance(result, dict):
                    # Try common keys
                    for key in ['translatedText', 'translated', 'translation', 'data', 'result']:
                        if key in result:
                            translated = result[key]
                            if isinstance(translated, list) and translated:
                                return translated[0]
                            return str(translated)
                return str(result)
            else:
                print(f"\u2717 Translation API error: {response.status_code}")
                return text
                
        except Exception as e:
            print(f"\u2717 Translation error: {str(e)}")
            return text
    
    def translate_articles(self, articles):
        """
        Translate article titles from Spanish to English.
        
        Args:
            articles (list): List of article dictionaries
            
        Returns:
            list: Articles with translated titles
        """
        print(f"\n{'='*60}")
        print("TRANSLATING ARTICLE TITLES (Spanish to English)")
        print(f"{'='*60}\n")
        
        for article in articles:
            if article['title']:
                print(f"Translating Article {article['index']}...")
                print(f"  Original (ES): {article['title']}")
                
                translated_title = self.translate_text(article['title'])
                article['title_english'] = translated_title
                
                print(f"  Translated (EN): {translated_title}")
                print()
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
        
        print("\u2713 All titles translated")
        return articles
    
    def print_translated_titles(self, articles):
        """Print translated article titles."""
        print(f"\n{'='*60}")
        print("TRANSLATED ARTICLE TITLES")
        print(f"{'='*60}\n")
        
        for article in articles:
            print(f"Article {article['index']}:")
            print(f"  English: {article.get('title_english', 'N/A')}")
            print()