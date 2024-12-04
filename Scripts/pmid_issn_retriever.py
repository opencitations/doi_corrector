# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm


class JournalIdentifierExtractor:
    """
    A class to extract identifiers from journals urls and save them to a JSON file.
    """

    def __init__(self, csv_path, output_path):
        """
        Initialize the extractor with input and output paths.

        """
        self.csv_path = csv_path
        self.output_path = output_path
        self.results = {}  # Dictionary to store extraction results
        self.journal_urls = self._load_journal_urls()  # Load journal URLs from the CSV file

    def _load_journal_urls(self):
        """
        Load journal URLs from the specified CSV file.


        """
        try:
            # Read the CSV file and extract the 'journal' column as a list
            journal_doi_df = pd.read_csv(self.csv_path, usecols=['journal'])
            return journal_doi_df['journal'].tolist()
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

    def get_identifiers_from_journal(self, url):
        """
        Access the given journal URL and extract related identifiers.


        """
        identifiers = []
        try:
            # Send a GET request to the journal URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for HTTP status codes >= 400
            soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

            # Locate the "identifier" section in the page
            identifier_section = soup.find('dt', class_="bg-info", string="identifier")
            if identifier_section:
                # Find the associated <ul> tag containing identifiers
                ul_tag = identifier_section.find_next_sibling('dd').find(
                    'ul', rel="http://purl.org/spar/datacite/hasIdentifier"
                )
                if ul_tag:
                    # Collect all links within the <ul> tag
                    for link in ul_tag.find_all('a'):
                        identifier_url = link.get('href')  # Get the 'href' attribute of the <a> tag
                        identifiers.append(identifier_url)  # Append the link to the list
        except Exception as e:
            # Log errors encountered while processing the journal URL
            print(f"Error processing {url}: {e}")
        return identifiers

    def get_id_from_identifier_page(self, identifier_url):
        """
        Access the identifier URL and extract the associated ID.


        """
        try:
            # Send a GET request to the identifier URL
            response = requests.get(identifier_url)
            response.raise_for_status()  # Raise an error for HTTP status codes >= 400
            soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

            # Locate the "id" section in the page
            id_section = soup.find('dt', class_="bg-info", string="id")
            if id_section:
                # Find the associated <ul> tag containing the ID
                ul_tag = id_section.find_next_sibling('dd').find(
                    'ul', rel="http://www.essepuntato.it/2010/06/literalreification/hasLiteralValue"
                )
                if ul_tag:
                    # Extract the text inside the first <li> tag
                    li_tag = ul_tag.find('li')
                    if li_tag:
                        return li_tag.get_text(strip=True)  # Return the text content of the <li> tag
        except Exception as e:
            # Log errors encountered while accessing the identifier URL
            print(f"Error accessing {identifier_url}: {e}")
        return None

    def process_journals(self):
        """
        Process each journal URL to extract identifiers and associated IDs.

        """
        for journal_url in tqdm(self.journal_urls, desc="Processing journals"):
            # Skip processing if the URL is empty or invalid
            if not isinstance(journal_url, str) or not journal_url.strip():
                continue

            # Get all identifier URLs from the current journal page
            journal_identifiers = self.get_identifiers_from_journal(journal_url)
            self.results[journal_url] = []  # Initialize an empty list for storing results for the current journal

            # Process each identifier URL found in the journal page
            for identifier_url in journal_identifiers:
                retrieved_id = self.get_id_from_identifier_page(identifier_url)  # Extract the ID from the identifier page
                if retrieved_id:
                    # Append the identifier URL and its associated ID to the results
                    self.results[journal_url].append({
                        "identifier_url": identifier_url,
                        "id": retrieved_id
                    })

    def save_results(self):
        """
        Save the extracted results to the specified JSON file.
        """
        try:
            with open(self.output_path, 'w', encoding='utf-8') as json_file:
                # Write the results dictionary to the JSON file in a human-readable format
                json.dump(self.results, json_file, indent=4)
            print(f"Data saved to {self.output_path}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def run(self):
        """
        Run the entire extraction process: process journals and save results.
        """
        self.process_journals()
        self.save_results()


if __name__ == "__main__":
    # Initialize the extractor with input CSV and output JSON paths
    extractor = JournalIdentifierExtractor(
        csv_path="insert_file_path",
        output_path="insert_file_path"
    )
    extractor.run()  # Run the extraction process
