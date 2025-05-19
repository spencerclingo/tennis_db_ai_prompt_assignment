import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_conference_urls(start_year, end_year):
    """
    Generate URLs for all General Conferences from start_year to end_year.
    Returns a list of (url, year, month) tuples.
    """
    base_url = 'https://www.churchofjesuschrist.org/study/general-conference/{year}/{month}?lang=eng'
    conference_urls = []
    for year in range(start_year, end_year + 1):
        for month in ['04', '10']:
            url = base_url.format(year=year, month=month)
            conference_urls.append((url, str(year), month))
    return conference_urls

def get_talk_urls(conference_url, year, month, session):
    """
    Fetch talk URLs from a conference page, excluding session videos.
    Returns a list of (url, talk_number) tuples.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    try:
        response = session.get(conference_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except requests.RequestException as e:
        logging.error(f"Error accessing {conference_url}: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    talk_urls = []
    seen_urls = set()
    talk_counter = 1
    
    # Extended list of session-related slugs to filter out
    session_slugs = [
        'saturday-morning', 'saturday-afternoon', 'sunday-morning', 'sunday-afternoon',
        'general-womens-session', 'priesthood-session', 'women-session', 'womens-session',
        'general-conference', 'session', 'video', 'all-sessions', 'full-session'
    ]
    
    for link in soup.select('div.talk-list a[href*="/study/general-conference/"], article a[href*="/study/general-conference/"]'):
        href = link.get('href')
        if not href or 'lang=eng' not in href:
            continue
        
        # Normalize URL
        parsed_url = urlparse('https://www.churchofjesuschrist.org' + href)
        canonical_url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
        
        if canonical_url in seen_urls:
            logging.warning(f"Duplicate URL found: {canonical_url}")
            continue
        seen_urls.add(canonical_url)
        
        # Validate talk URL
        match = re.search(r'/(\d{4})/(\d{2})/(.+)', parsed_url.path)
        if not match:
            logging.warning(f"Invalid talk URL format: {href}")
            continue
        
        url_year, url_month, slug = match.groups()
        
        # Skip known session pages and any slug containing session-related terms
        if any(session_slug in slug.lower() for session_slug in session_slugs):
            logging.debug(f"Skipping session URL: {canonical_url}")
            continue
        
        # Quick check to verify if the page is likely a talk (has speaker or content)
        try:
            talk_response = session.get(canonical_url, headers=headers, timeout=5)
            talk_response.raise_for_status()
            talk_response.encoding = 'utf-8'
            talk_soup = BeautifulSoup(talk_response.text, 'html.parser')
            
            # Check for speaker or content to confirm it's a talk
            has_speaker = talk_soup.find("p", {"class": "author-name"}) is not None
            has_content = talk_soup.find("div", {"class": "body-block"}) is not None
            if not (has_speaker or has_content):
                logging.debug(f"Skipping non-talk URL (no speaker/content): {canonical_url}")
                continue
        except requests.RequestException as e:
            logging.warning(f"Error checking {canonical_url}: {e}")
            continue
        
        talk_urls.append((canonical_url, str(talk_counter).zfill(2)))
        talk_counter += 1
    
    logging.info(f"Found {len(talk_urls)} talk URLs for {year}-{month}")
    return talk_urls

def scrape_talk(talk_url, year, month, talk_number, session):
    """
    Scrape metadata and transcript for a single talk, skipping invalid entries.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    start_time = time.time()  # Track request start time
    try:
        response = session.get(talk_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except requests.RequestException as e:
        logging.error(f"Error accessing {talk_url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')

    def clean_text(text):
        if not text:
            return text
        text = text.replace('â\x80\x99', "'").replace('â\x80\x9c', '"').replace('â\x80\x9d', '"').replace('Â', ' ')
        text = text.encode('ascii', 'ignore').decode('ascii')
        return text.strip()

    def clean_author_name(text):
        if not text:
            return text
        # Replace non-breaking spaces and other special characters
        text = text.replace('\u00a0', ' ').replace('Â', ' ')
        # Fix missing space after middle initial (e.g., "RussellM. Nelson" -> "Russell M. Nelson")
        text = re.sub(r'([A-Za-z])\.([A-Za-z])', r'\1. \2', text)
        # Apply general cleaning
        text = clean_text(text)
        return text.strip()

    title_tag = soup.find("h1")
    title = clean_text(title_tag.text) if title_tag else "No Title Found"

    author_tag = soup.find("p", {"class": "author-name"})
    speaker = clean_author_name(author_tag.text) if author_tag else "No Speaker Found"

    calling_tag = soup.find("p", {"class": "author-role"})
    calling = clean_text(calling_tag.text) if calling_tag else "No Calling Found"

    content_array = soup.find("div", {"class": "body-block"})
    content = "\n\n".join(clean_text(paragraph.text) for paragraph in content_array.find_all("p")) if content_array else "No Content Found"

    # Skip entries that are likely session pages (no speaker or content)
    if speaker == "No Speaker Found" and content == "No Content Found":
        logging.debug(f"Skipping invalid talk (no speaker/content): {talk_url}")
        return None

    # Log time taken for this talk
    elapsed_time = time.time() - start_time
    logging.debug(f"Processed {talk_url} in {elapsed_time:.2f} seconds")

    year = re.search(r'/(\d{4})/', talk_url).group(1)
    season = "April" if "/04/" in talk_url else "October"

    return {
        "title": title,
        "speaker": speaker,
        "calling": calling,
        "year": year,
        "season": season,
        "url": talk_url,
        "talk": content,
    }

# Main execution
talks_data = []
session = requests.Session()

for conf_url, year, month in get_conference_urls(2018, 2025):
    talk_urls = get_talk_urls(conf_url, year, month, session)
    for url, talk_number in talk_urls:
        talk = scrape_talk(url, year, month, talk_number, session)
        if talk:
            talks_data.append(talk)

session.close()

logging.info(f"Scraped {len(talks_data)} talks")

# Save to CSV
talks_df = pd.DataFrame(talks_data)
talks_df.to_csv('talks.csv', index=False)