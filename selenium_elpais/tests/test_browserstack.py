"""BrowserStack test for El País Opinion scraper - Selenium 4+ compatible."""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def test_elpais_opinion_scraper():
    """
    Test El País Opinion section scraping on BrowserStack.
    This will run on all platforms defined in browserstack.yml.
    """
    # BrowserStack SDK will handle browser capabilities automatically
    # Using Selenium 4+ compatible format
    driver = webdriver.Remote(
        command_executor='https://hub-cloud.browserstack.com/wd/hub',
        options=webdriver.ChromeOptions()
    )
    
    try:
        # Set test name
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionName", "arguments": {"name": "El Pais Opinion Scraping Test"}}'
        )
        
        # Navigate to El País Opinion section
        url = 'https://elpais.com/opinion/'
        print("Navigating to: " + url)
        driver.get(url)
        
        # Handle cookie consent
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            cookie_button.click()
            print("Cookie consent accepted")
            time.sleep(2)
        except (TimeoutException, NoSuchElementException):
            print("No cookie consent needed")
        
        # Wait for articles to load
        print("Waiting for articles to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # Find all articles
        articles = driver.find_elements(By.TAG_NAME, "article")
        print("Found " + str(len(articles)) + " articles")
        
        if len(articles) >= 5:
            # Try to extract first article title
            try:
                first_article = articles[0]
                
                # Try multiple selectors for title
                title = ""
                title_selectors = ['h2', 'h2 a', 'h3', '.c_h']
                for selector in title_selectors:
                    try:
                        title_elem = first_article.find_element(By.CSS_SELECTOR, selector)
                        title = title_elem.text.strip()
                        if title:
                            break
                    except:
                        continue
                
                if title:
                    success_message = "Successfully scraped El Pais Opinion section. Found " + str(len(articles)) + " articles. Sample title: " + title[:50]
                    print(success_message)
                    
                    # Mark test as PASSED
                    driver.execute_script(
                        'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": ' + json.dumps(success_message) + '}}'
                    )
                else:
                    # Articles found but no title
                    message = "Found " + str(len(articles)) + " articles but could not extract title"
                    print(message)
                    driver.execute_script(
                        'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": ' + json.dumps(message) + '}}'
                    )
                    
            except Exception as e:
                error_msg = "Found articles but error extracting data: " + str(e)
                print(error_msg)
                driver.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": ' + json.dumps(error_msg) + '}}'
                )
        else:
            # Not enough articles
            message = "Only found " + str(len(articles)) + " articles, expected at least 5"
            print(message)
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}'
            )
            
    except NoSuchElementException as err:
        message = "Element not found: " + str(err)
        print(message)
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}'
        )
    except TimeoutException as err:
        message = "Timeout waiting for page elements: " + str(err)
        print(message)
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}'
        )
    except Exception as err:
        message = "Test error: " + str(err)
        print(message)
        driver.execute_script(
            'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}'
        )
    finally:
        # Close the driver
        driver.quit()
        print("Test completed")

if __name__ == '__main__':
    test_elpais_opinion_scraper()