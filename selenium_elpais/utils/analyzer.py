"""Text analysis module for word frequency analysis."""

import re
from collections import Counter

class TextAnalyzer:
    """Analyzer for text processing and word frequency analysis."""
    
    @staticmethod
    def clean_text(text):
        """
        Clean text by removing punctuation and converting to lowercase.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    @staticmethod
    def get_words(text):
        """
        Extract words from text.
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of words
        """
        cleaned = TextAnalyzer.clean_text(text)
        return cleaned.split()
    
    @staticmethod
    def analyze_word_frequency(articles, min_count=3):
        """
        Analyze word frequency across article titles.
        
        Args:
            articles (list): List of article dictionaries
            min_count (int): Minimum count for a word to be included (default: 3, means >2)
            
        Returns:
            dict: Dictionary of words and their counts
        """
        print(f"\n{'='*60}")
        print(f"ANALYZING TRANSLATED HEADERS (Words repeated more than 2 times)")
        print(f"{'='*60}\n")
        
        # Collect all words from translated titles
        all_words = []
        for article in articles:
            title_en = article.get('title_english', '')
            if title_en:
                words = TextAnalyzer.get_words(title_en)
                all_words.extend(words)
        
        # Count word frequencies
        word_counts = Counter(all_words)
        
        # Filter words that appear more than min_count-1 times (i.e., >= min_count)
        repeated_words = {word: count for word, count in word_counts.items() 
                         if count >= min_count}
        
        # Sort by count (descending)
        repeated_words = dict(sorted(repeated_words.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True))
        
        return repeated_words
    
    @staticmethod
    def print_word_frequency(word_counts):
        """
        Print word frequency analysis results.
        
        Args:
            word_counts (dict): Dictionary of words and their counts
        """
        if not word_counts:
            print("\u26a0 No words found that repeat more than 2 times.")
            print("This is normal if article titles are very diverse.\n")
            return
        
        print(f"Found {len(word_counts)} word(s) repeated more than 2 times:\n")
        
        for word, count in word_counts.items():
            print(f"  '{word}': {count} occurrences")
        
        print()
    
    @staticmethod
    def analyze_articles(articles):
        """
        Complete analysis of articles.
        
        Args:
            articles (list): List of article dictionaries
            
        Returns:
            dict: Analysis results including word frequency
        """
        # Analyze word frequency (words appearing more than 2 times)
        word_frequency = TextAnalyzer.analyze_word_frequency(articles, min_count=3)
        
        # Print results
        TextAnalyzer.print_word_frequency(word_frequency)
        
        return {
            'word_frequency': word_frequency,
            'total_articles': len(articles),
            'total_words_analyzed': sum(len(TextAnalyzer.get_words(a.get('title_english', ''))) 
                                       for a in articles)
        }