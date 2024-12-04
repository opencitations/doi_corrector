# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import requests
from bs4 import BeautifulSoup
import json

class MetadataGatherer:

    """
    A class to process a list of DOIs, extract metadata from their web pages, and save the data to a JSON file.
    Use it by changing the tags that need to be retrieved based on the ones found in the article viewer you want to retrieve metadat from.
    """

    def __init__(self, dois):
        """
        Initialize the processor with a list of DOIs.

        """
        self.dois = dois

    @staticmethod
    def extract_metadata_from_html(content):
        """
        Extract metadata such as title, authors, bold text, and references from the HTML content.

        """
        soup = BeautifulSoup(content, 'html.parser')

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

        # Extract authors
        author_meta = soup.find('meta', {'name': 'citation_author'})
        if author_meta:
            authors = author_meta.get('content', "No Authors Found")
        else:
            authors = "No Authors Found"
            for meta in soup.find_all('meta'):
                if 'author' in str(meta).lower():
                    authors = meta.get('content', "No Authors Found")
                    break

        # Extract bold text
        p_tag = soup.find('p', class_='MsoNormal')
        bold_text = "No Bold Text Found"
        if p_tag:
            bold_tag = p_tag.find(['b', 'strong'])
            if bold_tag:
                bold_text = bold_tag.get_text(strip=True)

        # Extract references
        references = []
        reference_h2 = soup.find('h2', string=lambda s: s and 'References' in s.strip())
        if reference_h2:
            next_tag = reference_h2.find_next()
            while next_tag:
                if next_tag.name == 'div':  
                    break
                if next_tag.name == 'p' and 'MsoNormal' in next_tag.get('class', []):
                    references.append(next_tag.get_text(strip=True))
                next_tag = next_tag.find_next()

        # Compile metadata into a dictionary
        data = {
            "title": title,
            "authors": authors,
            "bold_text": bold_text,
            "references": references
        }
        return data

    @staticmethod
    def save_to_json(data, output_file):
        """
        Save data to a JSON file.

        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_file}")

    def process_dois(self, output_file="metadata_output.json"):
        """
        Process the list of DOIs, extract metadata, and save the results to a JSON file.

        """
        all_metadata = {}

        for doi in self.dois:
            doi_url = f"https://doi.org/{doi}"
            try:
                # Request the DOI page content
                response = requests.get(doi_url, timeout=10)
                response.raise_for_status()

                # Extract metadata
                metadata = self.extract_metadata_from_html(response.content)

                # Save metadata to the dictionary
                all_metadata[doi] = metadata
                print(f"Metadata extracted for DOI: {doi}")

            except requests.RequestException as e:
                # Handle errors gracefully
                print(f"Error accessing DOI {doi}: {e}")
                all_metadata[doi] = {"error": str(e)}

        # Save all metadata to a JSON file
        self.save_to_json(all_metadata, output_file)


if __name__ == "__main__":
    # Replace the list below with the DOIs you want to process, or with a file containing dois.
    example_dois = [
        "10.1234/example-doi-1",
        "10.5678/example-doi-2"
    ]

    # Create a DOIProcessor instance
    processor = MetadataGatherer(example_dois)

    # Process DOIs and save metadata to a JSON file
    processor.process_dois(output_file="insert_file_path")
