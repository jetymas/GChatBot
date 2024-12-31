"""
Scraper.py

Navigates an article database and saves each article as a JSON object.

Author: Jesse Tymas
Date: 12/22/2024
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import re
import sys

# Defines the Article class
class Article:
    def __init__(self, id, title, url, content):
        self.id = id
        self.title = title
        self.url = url
        self.content = content

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--silent')

# Start the webdriver
os.environ['PATH'] += r"/drivers/chromedriver.exe"
base_url = "https://example.com/pages/"
driver = webdriver.Chrome(options=chrome_options)
driver.get(base_url)

# Create a list of all article titles and URLs from /pages/ page
def get_article_metadata():
    """
    Creates article objects from the /pages/ page.

    """
    # Wait for sidebar to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "categories"))
    )

    # Find all article elements using XPath
    articles = []

    # creates list of all article urls
    # names changed for security
    links = driver.find_elements(
        By.XPATH,
        """//ul[@id='categories']//a[
            starts-with(@href, '/pages/') and
            .//span[@class='article-title']
        ]"""
    )

    # iterates through list of links and creates Article object from url and title
    article_count = 0

    for link in links:
        try:
            # Get article title and URL
            title = link.find_element(
                By.XPATH,
                ".//span[@class='article-title']"
            ).text.strip()
            url = link.get_attribute('href')

            # Add to list of articles if both title and URL exist
            # If valid title and url are found, creates new object
            if title and url:
                articles.append(Article(article_count, title, url, None)) #assigns ID to current article count
                print(f"Found: {title} -> {url}")
                article_count += 1

        except Exception as e:
            print(f"Error processing article: {str(e)}")

    print(f"\nTotal articles found: {article_count}")
    return articles


# Function to scrape a single article
def scrape_article_content(articles, article):

    url = article.url

    try:
        driver.get(url)

        # Wait for page to load
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content_container"))
        )

        # Check for unwanted article type. If so, removes from article list and skips
        # Class name changed for security
        try:
            driver.find_element(By.CLASS_NAME, "unwanted-article-type")
            print(f"Skipping unwanted article: {article.title}")
            articles.remove(article)
            return 1
        except:
            pass

        # Get the second content block (the real one, not the loading one)
        # Class names have been changed to preserve security
        content_blocks = driver.find_elements(By.ID, "content_block")
        if len(content_blocks) > 1:
            content = content_blocks[1]  # Get the second one (real content)
            article.content = content.get_attribute("outerHTML")
            return 0
        else:
            print(f"Could not find content block at {url}")
            return 1

    except TimeoutException:
        print(f"Timeout waiting for content at {url}")
        return 1
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return 1


# Main scraping loop
def main():
    try:
        # checks for correct number of arguments
        if len(sys.argv) != 2:
            print("Usage: python scraper.py <output_directory>")
            sys.exit(1)

        # attempts to create the directory to save to
        output_dir = sys.argv[1]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Wait for user input to begin
        # Step partially changed for security
        confirm_key = input("\nComplete action, and then press any key to continue. Press x to exit:\n")
        if confirm_key == 'x':
            sys.exit(0)

        # creates list of article objects
        articles = get_article_metadata()

        # lists number of articles and confirms that user wants to proceed
        confirm_key = input("\nFound " + str(len(articles)) + " articles. Press any key to continue, or n to exit:\n")
        if confirm_key == 'n':
            sys.exit(0)
        print(
            "Scraping articles. This may take a while."
        )

        # iterates through articles
        total_articles = len(articles)
        excluded_count = 0
        for index, article in enumerate(articles, 1):

            print(f"\nScraping article {index} of {total_articles - excluded_count}, {excluded_count} excluded")

            # attempts to scrape each article
            try:
                status = scrape_article_content(articles, article)

                if status == 0:
                    # Save each article right after scraping
                    filename = f"{re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', article.title)}.json"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(article.__dict__, f, indent=4, ensure_ascii=False)

                    time.sleep(1)  # Be nice to the server
                else:
                    excluded_count += 1
                    time.sleep(0.5)

            except Exception as e:
                print(f"Error scraping {article.url}: {str(e)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()