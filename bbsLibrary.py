
import requests
from bs4 import BeautifulSoup
import sys
import webbrowser
import time
import subprocess
import logging
import os
import re
sys.path.append('/home/ubuntu/code/local_utilities/db_connections/')
import db_connector as db_conn

logging.basicConfig(
    filename='/home/ubuntu/code/bizBuySell/log/log.log', level=logging.DEBUG)


def getLameCompanies(company):
    lameCompanies = ['vmware', 'amazon.com', 'oracle', 'meta', 'apple', 'chase', 'blue', 'Clearlink',
                     'microsoft', 'get it recruit - information technology', 'ibm', 'cloudflare', 'Salesforce',
                     'CyberCoders', 'PredICT Interactive', 'DISH', 'ServiceNow', 'Workday', 'Splunk',
                     'Amazon Web Services', 'American Partner Solutions', 'DIRECTV', 'Construction',
                     'Coalition Technologies', 'Advanced Micro Devices', 'Google', 'Zoom', 'Prudential', 'Deloitte', 'TikTok',
                     'Walmart', 'Amazon', 'Jobot', 'Canonical', 'Venmo', 'Affirm', 'The Walt Disney Company', 'Etsy', 'Loom',
                     'DoorDash', 'LinkedIn', 'Twitch', 'NetFlix', 'Zillow', 'CrowdStrike', 'Airbnb', 'The Home Depot', 'Draft Kings'
                     ]
    for word in lameCompanies:
        if re.search(r'\b' + re.escape(word) + r'\b', company, flags=re.IGNORECASE):
            return -27
    return 0

def getBadTitlePattern(title):
    """
    Returns a compiled regular expression pattern matching undesirable words/phrases in titles.
    """
    bad_words = [
        'wordpress', 'success', 'latam', 'front-end', 'structural', 'devsecops', 'c++', 'theme', 'junior'
        'platform', 'devops', 'process', 'release', 'onsite','Paralegal','Data Analyst','Tax Manager'
        'cybersecurity', 'java', 'security', 'autocad', 'estimator','Credit Risk Analyst Lead'
        'technician', 'specialist', 'servicenow', 'representative', 'designer', 'nurse','Tax Professional',
        'Junior', 'Therapist', ' GENERALIST', 'Philippines', 'Intern', '.NET','Lead Data Scientist'
        'Construction',  'Mobile', 'java', 'salesforce', 'embedded', 'administrator', 'Ruby',
        'Accountant',  'C#', 'Physician', 'MAGENTO', 'Tutor', 'Front End', 'Oracle', 'Configuration',
        'Receptionist', 'NetSuite', 'Platform', 'Cryptography', 'DBA', 'TS/SCI', 'Microsoft', 'Electrical',
        'Mechanical', 'Network', 'Frontend', 'Inspector', 'Civil', 'Trainee', 'Psychiatrist', 'Clinical', 'SharePoint',
        'Chemist', 'FileMaker', 'Behavioral', 'Azure', 'Identity and Access Management','Tax Analyst',
        'Cyber Threat Analyst','Consumer Insights Analyst','Senior Staff Data Scientist','Network Analyst'
    ]
    for word in bad_words:
        if re.search(re.escape(word), title, flags=re.IGNORECASE):
            return -57
    return 0

def get_job_details(job_url):
    """Fetches the job details page, parses it with BeautifulSoup, and extracts job title and description.

    Args:
        job_url: The URL of the job details page.

    Returns:
        A dictionary containing the extracted job title and description, or None if an error occurs.
    """
    job_details = {}
    try:
        job_details['job_url'] = job_url
        response = requests.get(job_url)
        response.raise_for_status()  # Raise an exception for unsuccessful requests
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the job title (h1 with class="node-title")
        title_element = soup.find('h1', class_='node-title')
        if title_element:
            job_details['title'] = title_element.text.strip()

        company_anchor = soup.find('div', class_='company-info')
        if company_anchor:  # Check if company_info div exists
            company_anchor = company_anchor.find('a')
            if company_anchor:  # Check if anchor tag exists within the div
                job_details['company'] = company_anchor.text.strip()
            else:
                company_name = None  # Set to None if anchor tag not found
        else:
            company_name = None  # Set to

        # Find the job description element (div with class="job-description")
        description_element = soup.find('div', class_='job-description')
        if description_element:
            job_details['description'] = description_element.text.strip()

            # Search for potential email addresses using a regular expression (limited accuracy)
            potential_emails = re.findall(
                r"[a-z0-9\.\-+_]+@[a-z0-9\.\-]+\.[a-z]{2,}", description_element.text)
            if potential_emails:
                job_details['emails'] = potential_emails
            else:
                job_details['emails'] = 0  # No emails found

        # Find company information from "company-options" class
        company_options = soup.find('div', class_='company-info')
        if company_options:
            # Extract location (might be in "company-location" or "icon-description")
            location_element = company_options.find(
                'span', class_='company-location')
            if not location_element:
                location_element = company_options.find(
                    'span', class_='icon-description')
            if location_element:
                job_details['location'] = location_element.text.strip()

        # Find the span element with class "remote"
        remote_span = soup.find('span', class_='remote')

        # Check if the element is found
        if remote_span:
            remote_text = remote_span.text.strip()
            # print(f"Found remote job listing: {remote_text}")
            job_details['is_remote'] = 1
        else:
            # print("No remote job listing found.")
            job_details['is_remote'] = 0

        # Find the span element with class "remote"
        companyAddress = soup.find('span', class_='company-address')
        if companyAddress:
            company_text = companyAddress.text.strip()
            # print(f"Found location: {company_text}")
            job_details['location'] = company_text
        else:
            print("No location job listing found.")
            job_details['location'] = "Midland"

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the job details: {e}")
    return job_details

def count_specific_words(text, word_weights):
    # Lowercase the text (optional, adjust based on your needs)
    if text is not None:
        text = text.lower()
    else:
      # Handle the case where text is None (e.g., print an error message)
        print("text is None and cannot be converted to lowercase.")
        text = "this is text"

    # Compile the regular expression to match whole words or ".net"
    word_pattern = re.compile(
        r"\b(" + "|".join(word_weights.keys()) + r")\b", re.IGNORECASE)

    # Find all words using the compiled pattern
    words = word_pattern.findall(text)

    # Count the occurrences of each word
    word_counts = {word: 0 for word in word_weights}
    for word in words:
        try:
            word_counts[word] += word_weights[word]
        except KeyError:
            # Handle missing word (e.g., print a message, log the error)
            print(f"Word '{word}' not found in word_weights dictionary")

    return word_counts

def _open_browser(url):
    try:
        chrome_path = '/usr/bin/google-chrome'  # Common path for Chrome on Linux
        # Build the complete command with Chrome path and each URL
        # command = [chrome_path] + url
        command = [chrome_path, url]  # List with two elements

        # Launch Chrome with the list of URLs using subprocess.Popen
        subprocess.Popen(command)

        # logging.info(f"Successfully opened URL: {url}")
    except Exception as e:
        # logging.error(f"Error opening URL {url}: {e}")
        print(f"Error opening URL {url}: {e}")

def printData(result_set, score=None, table='job_listings', fileName=None):
    print("Total Count ", len(result_set))
    z = 0
    for row in result_set:
        # webbrowser.open(row['job_url'])
        # time.sleep(5)
        z = z+1
        print(
            f"{row['id']} = {row['score']} | {row['title']} | {row['description']} |  {row['listing_url']}")
        print("\n")
        print(str(z) + " out of " + str(len(result_set)))
        print("\n")
        # if score:
        #     print("Search term: "+row['search_term'])
        #     print("---------------")
        #     print(row['raw_score'])
        # print("\n")

        # if table is None:
        #     q = "update job_listings set human_status = %s where id = %s;"
        # else:
        #     q = "update "+table+" set human_status = %s where id = %s;"

        # answer = str(input("(R)eviewed, (I)ssue , (A)ppiled? "))
        answer = 'chad'
        # if answer == "r":
        #     answer = "reviewed"
        # if answer == "i":
        #     answer = "issue"
        # if answer == "chad":
        #     answer = "chad_automation"
        #     # _open_browser(row['job_url'])
        #     # webbrowser.open(row['job_url'])
        #     # time.sleep(2)
        # if answer == "a":
        #     _open_browser(row['listing_url'])
        #     # webbrowser.open(row['job_url'])
        #     answer = "applied"
        fileName = "deals.txt"
        save_url_to_file(row['listing_url'], fileName)
        # args = [answer, row['id']]
        # db_conn.load_query(q, args, 86, False, DB="classAction")
        
   

def save_url_to_file(url, filename):
    """Saves a URL to a text file.

    Args:
        url: The URL to save.
        filename: The name of the file to save to (default: "job_urls.txt").
    """
    filename = "/home/ubuntu/code/bizBuySell/"+filename
    with open(filename, "a") as f:
        f.write(url + "\n")

def cleanOutMysql(table='job_listings'):
    technologies = ["%.Net%", "%.NET%", "%.net%", "%Marketing%", "%SEO%", "%Machinist%", "%Mulesoft%",
                    "%Assurance%", "%Construction%", "%Reliability%", "%MUMPs%", "%MERN%"
                    ]

    for technology in technologies:
        if table is None:
            q = f"update job_listings set score = -100 where title like %s"
        else:
            q = f"update "+table+" set score = -100 where title like %s"

        db_conn.load_query(q, args=technology, LineNumber=27,
                           printOutPut=False, DB="classAction")

def cleanOutMysqlCompany(table='job_listings'):
    technologies = ["LTIMindtree%", "Outlier%", "Apple%", "%Microsoft%", "%Google%", "%The Walt Disney Company%", "%Equifax%", "%Advanced Micro Devices%", "%Mulesoft%",
                    "%Oracle%", "%Autodesk%", '%Autodesk%', '%Canonical%', '%Coinbase%'
                    "%GitHub%", "%Twitch%", "%DATADOG%", "%PNC Financial Services Group%"]
    for technology in technologies:
        # q = f"update `job_listings` set score = -101 where company like '{technology}'"
        if table is None:
            q = f"update job_listings set score = -100 where company like %s"
        else:
            q = f"update "+table+" set score = -100 where company like %s"
        db_conn.load_query(q, args=technology, LineNumber=27,
                           printOutPut=True, DB="classAction")

def cleanOutMysqlLocation(table='job_listings'):
    technologies = ["India%", "%Microsoft%", "%Google%", "%The Walt Disney Company%", "%Equifax%", "%Advanced Micro Devices%", "%Mulesoft%",
                    "%Oracle%", "%Autodesk%", 'Autodesk%', '%Okta%']
    for technology in technologies:
        if table is None:
            q = f"update job_listings set score = -100 where location like %s"
        else:
            q = f"update "+table+" set score = -100 where location like %s"
        db_conn.load_query(q, args=technology, LineNumber=27,
                           printOutPut=True, DB="classAction")

def get_job_urls(url):
    """Fetches the job search page, parses it with BeautifulSoup, and extracts URLs near Apply buttons.

    Args:
        url: The URL of the Built In job search page.

    Returns:
        A list of job URLs found on the page.
    """
    job_urls = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for unsuccessful requests
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all elements with text "Apply"
        apply_elements = soup.find_all('span', string='Apply')

        # Extract job URLs from the parent element's href attribute
        for element in apply_elements:
            parent = element.parent
            if parent.has_attr('href'):
                job_urls.append("https://builtin.com" + parent['href'])
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
    return job_urls


def open_urls_from_file(file_path, firefox_path, max_urls=20):
    """
    Downloads the HTML content from a list of URLs in a text file, searches for specific keywords in class="company-info" and class="company-title",
    and "Sorry, this job was removed" in class="remove-text", asks the user if they want to delete the URL if an offending word is found,
    and opens the URL if no offending words are found.

    Args:
        file_path (str): Path to the text file containing URLs.
        firefox_path (str): Path to the Firefox executable.
        max_urls (int, optional): Maximum number of URLs to process (defaults to 20).
    """
    # subprocess.Popen([firefox_path, url])
    try:
        # Open the text file in read mode
        with open(file_path, 'r') as url_file:
            # Read each URL line by line and strip any trailing whitespace
            urls = [line.strip() for line in url_file.readlines()]

        # Limit URLs to a maximum number
        urls_to_process = urls[:max_urls]
        urls_to_remove = []

        # Process each URL
        for url in urls_to_process:
          
            # Open the URL in the browser if no offending text is found
            subprocess.Popen([firefox_path, url])
            print("Opening and removing URL because it is legitimate: ", url)
            urls_to_remove.append(url)             

        # # Update the file content by removing the URLs
        # remaining_urls = [url for url in urls if url not in urls_to_remove]
        # with open(file_path, 'w') as url_file:
        #     url_file.write('\n'.join(remaining_urls))

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"Error processing URLs: {e}")
