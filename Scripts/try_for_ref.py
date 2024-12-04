# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import requests
from bs4 import BeautifulSoup
import urllib3
import PyPDF2
import io
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This script can only be used with a semiautomatic approach due to the various structures of html pages, and pdf file. Change the tags that you are looking for in the html page based on the structure of the page you can see from the inspector, this way you can gather metadata for articles that come from the sae journal which usually share the same structure for their article viewers. 

class DOIProcessor:
    """
    A class to process DOIs, extract metadata from HTML or PDF content, and save the results as JSON.
    """

    def __init__(self):
        self.doi_base_url = "https://doi.org/"  # Base URL for constructing DOI links

    def get_content_from_doi(self, doi_url):
        """
        Retrieve content from the given DOI URL.

        """
        try:
            response = requests.get(doi_url, verify=False)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            if 'application/pdf' in content_type:
                return 'pdf', response.content
            else:
                return 'html', response.text
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred for {doi_url}: {err}")
        except Exception as err:
            print(f"Other error occurred for {doi_url}: {err}")
        return None, None

    def extract_info_from_html(self, html_content):
        """
        Extract metadata from HTML content.

        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title_tag = soup.find('h1', class_='page_title')
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        # Extract authors and affiliations
        authors = []
        author_list = soup.find_all('li')
        for author in author_list:
            name = author.find('span', class_='name').get_text(strip=True) if author.find('span', class_='name') else "No name"
            affiliation = author.find('span', class_='affiliation').get_text(strip=True) if author.find('span', class_='affiliation') else "No affiliation"
            authors.append(f"{name} ({affiliation})")

        # Extract bold text
        bold_texts = [bold.get_text(strip=True) for bold in soup.find_all('b')]

        # Extract references
        references = []
        reference_section = soup.find('section', class_='item references')
        if reference_section:
            reference_paragraphs = reference_section.find_all('p')
            for ref in reference_paragraphs:
                ref_text = ref.get_text(strip=True).split('\n')  # Split references based on new lines
                references.extend(ref_text)  # Extend the list with each reference

        # Return extracted information
        return title, ', '.join(authors), ', '.join(bold_texts), [ref.strip() for ref in references if ref.strip()]

    def extract_text_from_pdf(self, pdf_content):
        """
        Extract text from PDF content.

        """
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Error while extracting text from PDF: {e}")
            return None

    def extract_references_from_pdf_text(self, text):
        """
        Extract references from the text of a PDF document.

        """
        refs_start = text.lower().find("references")
        if refs_start != -1:
            return text[refs_start:]  # Return text starting from "References"
        return "No references found in PDF"

    def process_doi(self, doi):
        """
        Process a single DOI, extracting relevant metadata.


        """
        doi_url = self.doi_base_url + doi
        content_type, content = self.get_content_from_doi(doi_url)

        if content_type == 'html':
            return self.extract_info_from_html(content)
        elif content_type == 'pdf':
            pdf_text = self.extract_text_from_pdf(content)
            if pdf_text:
                ref_text = self.extract_references_from_pdf_text(pdf_text)
                return "PDF Document", "N/A", "N/A", ref_text
            else:
                return "PDF Document", "N/A", "N/A", "Failed to extract text"
        else:
            return "Unknown", "N/A", "N/A", "Failed to retrieve content"

    def process_dois_and_save_to_json(self, dois, output_file):
        """
        Process a list of DOIs and save the extracted metadata to a JSON file.

        """
        all_metadata = []

        for doi in dois:
            title, authors, bold_text, ref_text = self.process_doi(doi)

            # Debug print statements
            print(f"DOI: {doi}")
            print(f"  Title: {title}")
            print(f"  Authors: {authors}")
            print(f"  Bold Text: {bold_text}")
            print(f"  Reference Text: {ref_text}")

            metadata = {
                'DOI': doi,
                'Title': title,
                'Authors': authors,
                'Bold Text': bold_text,
                'Reference Text': ref_text
            }

            all_metadata.append(metadata)

        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_metadata, jsonfile, ensure_ascii=False, indent=4)

        print(f"Data saved to {output_file}")


if __name__ == "__main__":
    # Insert the list of DOIs to process
    dois = []

    output_file = "insert_file_path"

    # Initialize DOIProcessor and process the DOIs
    processor = DOIProcessor()
    processor.process_dois_and_save_to_json(dois, output_file)
