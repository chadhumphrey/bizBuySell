import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re
import sys
sys.path.append('/home/ubuntu/code/local_utilities/db_connections/')
import db_connector as db_conn
import concurrent.futures

class BizBuySellScraper:
    STATES = [
        'alabama', 'alaska', 'arizona', 'arkansas', 
        'california', 'colorado', 'connecticut', 
        'delaware', 'florida', 'georgia', 
        'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 
        'kansas', 'kentucky', 
        'louisiana', 
        'maine', 'maryland', 'massachusetts', 'michigan', 
        'minnesota', 'mississippi', 'missouri', 'montana', 
        'nebraska', 'nevada', 'new-hampshire', 'new-jersey', 
        'new-mexico', 'new-york', 'north-carolina', 'north-dakota', 
        'ohio', 'oklahoma', 'oregon', 
        'pennsylvania', 
        'rhode-island', 
        'south-carolina', 'south-dakota', 
        'tennessee', 'texas', 
        'utah', 'vermont', 'virginia', 
        'washington', 'west-virginia', 'wisconsin', 'wyoming',
        'district-of-columbia'
    ]
    
    def __init__(self,state, start_page=1, end_page=200):
        """
        Initialize the scraper with page range and database connection
        
        :param start: Starting page number
        :param end: Ending page number (inclusive)
        """
        self.base_url = f"https://www.bizbuysell.com/businesses-for-sale/"
        self.start_urls = [f"{self.base_url}{i}" for i in range(start_page, end_page + 1)]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
     

    def generate_urls(self, start, end):
        """
        Generate list of URLs to scrape
        
        :param start: Starting page number
        :param end: Ending page number (inclusive)
        :return: List of full URLs
        """
        start_urls = []
        for i in range(start, end + 1):
            url = f"{self.base_url}{i}"
            start_urls.append(url)
        return start_urls

 
   
    def parse_business_listing(self, listing):
        """
        Extract details from an individual business listing
        
        :param listing: BeautifulSoup element of a single listing
        :return: Dictionary of business details
        """
        try:
            # Extract title
            title = listing.find('h3', class_='title')
            title = title.text.strip() if title else 'N/A'

            # Extract location
            location = listing.find('p', class_='location')
            location = location.text.strip() if location else 'N/A'

            # Extract description
            description = listing.find('p', class_='description')
            description = description.text.strip() if description else 'N/A'

            # Extract asking price
            asking_price_elem = listing.find('p', class_='asking-price')
            asking_price = asking_price_elem.find('span').next_sibling.strip() if asking_price_elem else 'N/A'
            # Remove '$' and ',' for numeric conversion
            asking_price = float(re.sub(r'[,$]', '', str(asking_price))) if asking_price != 'N/A' else None

            # Extract cash flow
            cash_flow_elem = listing.find('p', class_='cash-flow-on-mobile')
            cash_flow = cash_flow_elem.text.replace('Cash Flow: ', '').strip() if cash_flow_elem else 'N/A'
            # Remove '$' and ',' for numeric conversion
            cash_flow = float(re.sub(r'[,$]', '', str(cash_flow))) if cash_flow != 'N/A' else None

            # Extract image URL
            image = listing.find('img', class_='image')
            image_url = image.get('src') if image else 'N/A'

            # Extract listing URL
            listing_url = listing.get('href') if listing.get('href') else 'N/A'

            return {
                'title': title,
                'location': location,
                'description': description,
                'asking_price': asking_price,
                'cash_flow': cash_flow,
                'image_url': image_url,
                'listing_url': listing_url
            }
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None

    def scrape_state(self):
        """
        Scrape business listings from predefined URLs
        
        :return: List of business dictionaries
        """
        all_businesses = []
        
        for url in self.start_urls:
            try:
                # Add random delay to avoid getting blocked
                time.sleep(random.uniform(30, 120))
                
                # Send GET request
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find business listing containers
                business_listings = soup.find_all('a', class_='diamond')
                
                for listing in business_listings:
                    business = self.parse_business_listing(listing)
                    if business:
                        all_businesses.append(business)
                        
                        # Insert into database using load_query method
                        insert_query = '''
                        INSERT ignore INTO listingsBizBuySell
                        (title, location, description, asking_price, cash_flow, image_url, listing_url) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        '''
                        args = (
                            business['title'], 
                            business['location'], 
                            business['description'], 
                            business['asking_price'], 
                            business['cash_flow'], 
                            business['image_url'], 
                            business['listing_url']
                        )
                        db_conn.load_query(insert_query,args,LineNumber=188,printOutPut=False,DB="SAM")
                
                print(f"Scraped URL {url}: {len(business_listings)} listings found")
                
            except requests.RequestException as e:
                print(f"Error scraping URL {url}: {e}")
        
        return all_businesses

def scrape_all_states():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(BizBuySellScraper(state).scrape_state) 
            for state in BizBuySellScraper.STATES
        ]
        
        # Wait for all futures to complete
        concurrent.futures.wait(futures)


def main():
    scrape_all_states()

if __name__ == "__main__":
    main()