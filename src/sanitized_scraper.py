"""
Scraper.py

Navigates an article database and saves each article as a JSON object.
Requires manual login.

Author: Jesse Tymas
Date: 12/22/2024
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

# Initialize WebDriver and navigate to the first article
os.environ['PATH'] += r"/drivers/chromedriver.exe"
base_url = "https://[REDACTED].com/docs/"
driver = webdriver.Chrome()
driver.get(base_url)

# Create a list of all article titles and URLs from /docs/ page
def get_article_metadata():
    """
    Creates article objects from the /docs/ page.

    """
    # Wait for sidebar to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "categories"))
    )

    # Find all article elements using XPath
    articles = []

    # creates list of all article urls
    links = driver.find_elements(
        By.XPATH,
        """//ul[@id='categories']//a[
            starts-with(@href, '/docs/') and
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
def scrape_article_content(url):

    # pause
    time.sleep(1)

    try:
        driver.get(url)
        content_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "[REDACTED]"))
        )
        return content_div.get_attribute("outerHTML")
    except TimeoutException:
        print(f"Timeout waiting for content at {url}")
        return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None


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

        # waits for user to log in
        input("Log in, and then press the Enter key to continue.")

        # creates list of article objects
        articles = get_article_metadata()

        # lists number of articles and confirms that user wants to proceed
        confirm_key = input("\nFound " + str(len(articles)) + " articles. Press y to confirm, or n to exit:")
        if (confirm_key == 'n'):
            sys.exit(0)
        print(
            "Scraping articles. This may take a while. Please be patient."
        )

        # iterates through articles
        total_articles = len(articles)
        for index, article in enumerate(articles, 1):
            print(f"\nScraping article {index} of {total_articles}")
            # attempts to scrape each article
            try:
                article.content = scrape_article_content(article.url)

                # Save each article right after scraping
                filename = f"{article.title}.json"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(article.__dict__, f, indent=4, ensure_ascii=False)

                time.sleep(1)  # Be nice to the server
            except Exception as e:
                print(f"Error scraping {article.url}: {str(e)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()