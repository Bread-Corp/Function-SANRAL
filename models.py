# ==================================================================================================
#
# File: SANRALLambda/models.py
#
# Description:
# This module defines the data structures (models) for representing tender information
# sourced from the South African National Roads Agency (SANRAL). It is unique because
# it combines data from an initial API call with data scraped from a secondary details page.
#
# The classes defined here are:
#   - SupportingDoc: A simple class to represent a downloadable document linked to a tender.
#   - TenderBase: An abstract base class defining the common interface for all tenders.
#   - SanralTender: A concrete class for SANRAL tenders. Its `from_api_response` method
#     contains complex logic to parse initial data, scrape a details URL for more info,
#     and then combine the results into a single, structured object.
#
# ==================================================================================================

# --- Import necessary libraries ---
from abc import ABC, abstractmethod
from datetime import datetime
from bs4 import BeautifulSoup # For parsing HTML from the details page.
import requests # For making the secondary HTTP request to the details page.
import re # For using regular expressions to find URLs and emails.
import html # For unescaping HTML entities (e.g., &amp; -> &).
import logging

# ==================================================================================================
# Class: SupportingDoc
# Purpose: Represents a single supporting document associated with a tender.
# ==================================================================================================
class SupportingDoc:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def to_dict(self):
        return {"name": self.name, "url": self.url}

# ==================================================================================================
# Class: TenderBase (Abstract Base Class)
# ==================================================================================================
class TenderBase(ABC):
    def __init__(self, title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list = None, tags: list = None):
        self.title = title
        self.description = description
        self.source = source
        self.published_date = published_date
        self.closing_date = closing_date
        self.supporting_docs = supporting_docs if supporting_docs is not None else []
        self.tags = tags if tags is not None else []

    @classmethod
    @abstractmethod
    def from_api_response(cls, response_item: dict):
        pass

    def to_dict(self):
        # The base to_dict method has an error for serializing tags, so we will
        # override it in the child class to handle simple string lists.
        return {
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "publishedDate": self.published_date.isoformat() if self.published_date else None,
            "closingDate": self.closing_date.isoformat() if self.closing_date else None,
            "supporting_docs": [doc.to_dict() for doc in self.supporting_docs],
            "tags": self.tags # Correctly handle tags as a list of strings.
        }

# ==================================================================================================
# Class: SanralTender
# Purpose: A concrete implementation for SANRAL-specific tenders.
# ==================================================================================================
class SanralTender(TenderBase):
    def __init__(
        self,
        # --- Base fields ---
        title: str, description: str, source: str, published_date: datetime, closing_date: datetime, supporting_docs: list, tags: list,
        # --- SANRAL-specific fields ---
        tender_number: str,
        category: str,
        region: str,
        email: str,
        full_notice_text: str,
    ):
        super().__init__(title, description, source, published_date, closing_date, supporting_docs, tags)
        self.tender_number = tender_number
        self.category = category
        self.region = region
        self.email = email
        self.full_notice_text = full_notice_text

    @classmethod
    def from_api_response(cls, response_item: list):
        """
        Factory method to create a SanralTender object. This is a complex process involving
        parsing an initial list, scraping a URL found within it, and combining the data.

        Args:
            response_item (list): A list containing initial tender data from the SANRAL API.
                                  Example: ['<a href="/url">Tender XYZ</a>', 'Category', 'Region', 'Desc', 'Full Text', '2023/12/31 14:00']

        Returns:
            SanralTender or None: An instance of the class, or None if validation fails.
        """
        # --- Initial Validation ---
        if not isinstance(response_item, list) or len(response_item) < 6:
            return None # Skip invalid or incomplete items.

        # --- Helper function for robust date parsing ---
        def parse_sanral_date(date_str: str):
            if not date_str or not isinstance(date_str, str):
                return None
            
            cleaned_str = date_str.strip()
            # A list of possible date formats found in the SANRAL data.
            formats_to_try = ['%Y/%m/%d %H:%M', '%d/%m/%Y', '%d %B %Y. %HH%M']
            
            for fmt in formats_to_try:
                try:
                    # Special handling for formats containing 'H' (e.g., '14H00').
                    if 'H' in fmt:
                        return datetime.strptime(cleaned_str.replace('.', '').replace('H', ''), fmt)
                    return datetime.strptime(cleaned_str, fmt)
                except (ValueError, TypeError):
                    continue # Try the next format if the current one fails.
            return None # Return None if no formats match.

        # --- Step 1: Parse the initial API data (the input list) ---
        title_html = html.unescape(response_item[0])
        url, tender_number = None, "N/A"
        # Use regex to find the href (URL) and text (tender number) inside the <a> tag.
        match = re.search(r'href="([^"]+)">\s*(.*?)\s*</a>', title_html, re.IGNORECASE)
        if match:
            url_path = match.group(1)
            if url_path:
                # Construct the full, absolute URL.
                url = f"https://www.nra.co.za{url_path}"
            tender_number = ' '.join(match.group(2).split()) # Clean up whitespace.

        # Extract initial data from the list, cleaning it up.
        initial_description = ' '.join(html.unescape(response_item[3]).split()).replace('Tender Notice:', '').strip()
        
        # Set default values which may be overwritten by the scraper.
        title = tender_number
        description = initial_description
        full_notice_text = ' '.join(html.unescape(response_item[4]).split())
        email = ''
        pub_date = None
        close_date = parse_sanral_date(response_item[5])

        # --- Step 2: If a URL was found, scrape the details page for more accurate data ---
        if url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                detail_page_response = requests.get(url, headers=headers, timeout=15)
                detail_page_response.raise_for_status()
                soup = BeautifulSoup(detail_page_response.text, 'html.parser')
                
                # Scrape the page title from the <h2> tag inside the 'page-header' div.
                header_div = soup.find('div', class_='page-header')
                if header_div and header_div.find('h2'):
                    title = header_div.find('h2').get_text(strip=True)

                # Scrape the description from the first <h3> tag.
                h3_tag = soup.find('h3')
                if h3_tag:
                    description = h3_tag.get_text(strip=True)
                
                # Scrape the full notice text.
                notice_label_cell = soup.find('td', string=re.compile(r'^\s*Tender Notice:\s*$', re.IGNORECASE))
                if notice_label_cell:
                    content_cell = notice_label_cell.find_next_sibling('td')
                    if content_cell:
                        full_notice_text = content_cell.get_text(separator=' ', strip=True)

                # Scrape the published date ('Create Date').
                create_date_th = soup.find('th', string=re.compile(r'^\s*Create Date\s*$', re.IGNORECASE))
                if create_date_th:
                    date_td = create_date_th.find_next_sibling('td')
                    if date_td:
                        pub_date_str = date_td.get_text(strip=True)
                        try:
                            # Parse the date using its specific format.
                            pub_date = datetime.strptime(pub_date_str, '%B %d, %Y')
                        except (ValueError, TypeError):
                            logging.warning(f"Could not parse scraped published date for {tender_number}: {pub_date_str}")
            
            except (requests.exceptions.RequestException, Exception) as e:
                # If scraping fails, log a warning and continue with the initial, less detailed data.
                logging.warning(f"Could not scrape detail page for {tender_number}, using summary data. Error: {e}")

        # --- Step 3: Final Data Processing ---
        # Find all email addresses in the full notice text and take the last one found.
        emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_notice_text)
        if emails_found:
            email = emails_found[-1].lower()
        
        # Create a supporting document link to the details page.
        doc_list = []
        if url:
            doc_list.append(SupportingDoc(name="Tender Details", url=url))

        # --- Step 4: Create and return the final object ---
        return cls(
            title=title.title(),
            description=description.title(),
            source="SANRAL",
            published_date=pub_date,
            closing_date=close_date,
            supporting_docs=doc_list,
            tags=[], # Initialize with an empty list.
            tender_number=tender_number.upper(),
            category=response_item[1].strip().title(),
            region=response_item[2].strip().title(),
            email=email,
            full_notice_text=full_notice_text.title()
        )

    def to_dict(self):
        """
        Serializes the SanralTender object to a dictionary.
        """
        data = super().to_dict()
        data.update({
            "tenderNumber": self.tender_number,
            "category": self.category,
            "region": self.region,
            "email": self.email,
            "fullNoticeText": self.full_notice_text
        })
        return data