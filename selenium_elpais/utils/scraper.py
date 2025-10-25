"""El País web scraper module using Selenium."""

import time
import os
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

import config

class ElPaisScraper:
    """Scraper for El País Opinion section."""
    
    def __init__(self, browser='chrome', headless=True):
        self.browser_type = browser
        self.headless = headless
        self.driver = None
        self.articles = []
        
    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        if self.browser_type.lower() == 'chrome':
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--lang=es-ES')
            options.add_experimental_option('prefs', {'intl.accept_languages': 'es,es-ES'})
            
            try:
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                print("ChromeDriver installation failed: " + str(e))
                print("Trying alternative method...")
                try:
                    self.driver = webdriver.Chrome(options=options)
                except Exception as e2:
                    print("Chrome setup failed completely. Error: " + str(e2))
                    print("Please use Firefox instead by changing browser='firefox' in main.py")
                    raise
            
        elif self.browser_type.lower() == 'firefox':
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')
            options.set_preference('intl.accept_languages', 'es-ES, es')
            
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
        
        else:
            raise ValueError("Unsupported browser: " + self.browser_type)
        
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
        self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        print("✓ " + self.browser_type.capitalize() + " WebDriver initialized")
        
    def navigate_to_opinion_section(self):
        """Navigate to El País Opinion section."""
        print("\nNavigating to: " + config.ELPAIS_OPINION_URL)
        self.driver.get(config.ELPAIS_OPINION_URL)
        
        time.sleep(3)
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            accept_button.click()
            print("\u2713 Accepted cookie consent")
            time.sleep(2)
        except (TimeoutException, NoSuchElementException):
            print("\u2713 No cookie consent needed")
        
        print("\u2713 Successfully loaded: " + self.driver.title)
        
    def scrape_articles(self, max_articles=5):
        """Scrape articles from the Opinion section."""
        print("\n" + "="*60)
        print("SCRAPING " + str(max_articles) + " ARTICLES FROM OPINION SECTION")
        print("="*60 + "\n")
        
        article_selectors = [
            "article",
            "article.c",
            "article.c_a",
            "div[data-dtm-region='articulo']",
            "section article",
            "main article"
        ]
        
        articles_elements = []
        for selector in article_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) >= max_articles:
                    articles_elements = elements
                    print("\u2713 Found " + str(len(elements)) + " articles using selector: " + selector)
                    break
            except Exception as e:
                continue
        
        if not articles_elements:
            print("\u26a0 Could not find articles with standard selectors, trying alternative approach...")
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            articles_elements = [link for link in all_links if link.get_attribute('href') and '/opinion/' in link.get_attribute('href')][:max_articles]
        
        for idx, article_element in enumerate(articles_elements[:max_articles], 1):
            try:
                print(f"Processing article {idx}...")
                article_data = self._extract_article_data(article_element, idx)
                if article_data:
                    self.articles.append(article_data)
                    print("\u2713 Article " + str(idx) + " scraped successfully")
                else:
                    print(f"\u26a0 Article {idx} - no data extracted")
            except Exception as e:
                print("\u2717 Error scraping article " + str(idx) + ": " + str(e))
                continue
        
        print("\n\u2713 Total articles scraped: " + str(len(self.articles)))
        return self.articles
    
    def _extract_article_data(self, element, index):
        """Extract data from a single article element."""
        article_data = {
            'index': index,
            'title': '',
            'content': '',
            'author': '',
            'date': '',
            'url': '',
            'image_url': '',
            'image_path': ''
        }
        
        title_selectors = ['h2', 'h2.c_h', 'h2 a', '.c_h', 'header h2', 'h3']
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                article_data['title'] = title_elem.text.strip()
                if article_data['title']:
                    break
            except:
                continue
        
        try:
            link = element.find_element(By.TAG_NAME, 'a')
            article_data['url'] = link.get_attribute('href')
        except:
            pass
        
        content_selectors = ['p', '.c_d', 'div.c_d', 'header p', 'article p']
        for selector in content_selectors:
            try:
                content_elem = element.find_element(By.CSS_SELECTOR, selector)
                article_data['content'] = content_elem.text.strip()
                if article_data['content']:
                    break
            except:
                continue
        
        author_selectors = ['.c_a_a', 'span.c_a_a', '.author', 'span.author', '[data-dtm-region="autor"]']
        for selector in author_selectors:
            try:
                author_elem = element.find_element(By.CSS_SELECTOR, selector)
                article_data['author'] = author_elem.text.strip()
                if article_data['author']:
                    break
            except:
                continue
        
        date_selectors = ['time', '.c_a_d', 'span.c_a_d', '.date', '[datetime]']
        for selector in date_selectors:
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, selector)
                article_data['date'] = date_elem.text.strip()
                if article_data['date']:
                    break
            except:
                continue
        
        image_selectors = ['img', 'figure img', 'picture img', '.c_m img']
        for selector in image_selectors:
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, selector)
                img_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                if img_url and not img_url.endswith('.svg'):
                    article_data['image_url'] = img_url
                    break
            except:
                continue
        
        if article_data['url'] and not article_data['content']:
            article_data['content'] = self._scrape_full_article(article_data['url'])
        
        return article_data if article_data['title'] else None
    
    def _scrape_full_article(self, url):
        """Scrape the full article content from its page."""
        try:
            self.driver.execute_script("window.open('" + url + "', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
            content_selectors = [
                'article p',
                '.a_c p',
                '.article-body p',
                '[data-dtm-region="articulo_cuerpo"] p'
            ]
            
            content_paragraphs = []
            for selector in content_selectors:
                try:
                    paragraphs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    content_paragraphs = [p.text.strip() for p in paragraphs if p.text.strip()]
                    if content_paragraphs:
                        break
                except:
                    continue
            
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return ' '.join(content_paragraphs[:3]) if content_paragraphs else ''
            
        except Exception as e:
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return ''
    
    def download_images(self):
        """Download images for scraped articles."""
        print("\n" + "="*60)
        print("DOWNLOADING ARTICLE IMAGES")
        print("="*60 + "\n")
        
        for article in self.articles:
            if article['image_url']:
                try:
                    filename = "article_" + str(article['index']) + ".jpg"
                    filepath = config.IMAGES_DIR / filename
                    
                    response = requests.get(article['image_url'], timeout=10)
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        article['image_path'] = str(filepath)
                        print("\u2713 Downloaded image for Article " + str(article['index']) + ": " + filename)
                    else:
                        print("\u2717 Failed to download image for Article " + str(article['index']) + " (Status: " + str(response.status_code) + ")")
                except Exception as e:
                    print("\u2717 Error downloading image for Article " + str(article['index']) + ": " + str(e))
            else:
                print("\u26a0 No image available for Article " + str(article['index']))
    
    def print_articles(self):
        """Print scraped articles in Spanish."""
        print("\n" + "="*60)
        print("SCRAPED ARTICLES (IN SPANISH)")
        print("="*60 + "\n")
        
        for article in self.articles:
            separator = '\u2501' * 60
            print(separator)
            print("Artículo " + str(article['index']) + ":")
            print(separator)
            print("Título: " + article['title'])
            if article['author']:
                print("Autor: " + article['author'])
            if article['date']:
                print("Fecha: " + article['date'])
            if article['content']:
                content_preview = article['content'][:300]
                if len(article['content']) > 300:
                    content_preview += '...'
                print("Contenido: " + content_preview)
            if article['url']:
                print("URL: " + article['url'])
            print()
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("\n\u2713 WebDriver closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
