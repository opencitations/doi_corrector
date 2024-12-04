# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import requests  
from bs4 import BeautifulSoup 
from doi_manager import DOIManager 
import pandas as pd 
from tqdm import tqdm  

class DOIFinder:
    """
    A class to find and extract DOI links from the entity viewer of the OpenCitations Website.
    """

    def __init__(self):
        """
        Initialize the DOIFinder class.
        """
        self.doi_manager = DOIManager() 
        self.complete_resource = []  

    def doi_to_url(self, doi):
        """
        Convert a DOI to a standard URL format.

        """
        return "https://doi.org/" + doi

    def access_doi_url(self, doi):
        """
        Access the web page of a DOI and return its content.


        """
        url = self.doi_to_url(doi)
        try:
            # Send a GET request to the DOI URL
            response = requests.get(url)
            if response.status_code == 200:
                return response.text  # Return the page content if the request is successful
            else:
                return f"Error accessing URL: {response.status_code}"  # Handle unsuccessful responses
        except Exception as e:
            # Handle exceptions, such as timeouts or connection errors
            return f"Error accessing URL: {str(e)}"
    
    def find_doi_links(self, initial_url):
        """
        Find and extract DOI links from a given URL.

        """
        try:
            # Make an HTTP request to the initial URL
            initial_response = requests.get(initial_url, timeout=10)
            
            if initial_response.status_code != 200:
                print(f"Error accessing initial page: {initial_response.status_code}")
                return []  # Return an empty list if the request fails

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(initial_response.content, 'html.parser')
            
            # Find all <a> tags in the HTML (links)
            identifier_links = soup.find_all('a')

            # Filter and clean the links that potentially contain DOIs
            doi_links = self.id_checker(identifier_links)
            
            # Analyze the filtered links and extract relevant DOI content
            saved_results = self.li_link_analyser(doi_links)
            
            print(saved_results)  # Log the found results
            return saved_results

        except Exception as e:
            # Handle exceptions and log errors
            print(f"Error: {str(e)}")
            return []
    
    def id_checker(self, identifier_links):
        """
        Filter links that potentially contain DOIs.

        """
        new_list = []
        for link in identifier_links:
            href = link.get('href', '')  
            if "/id/" in href:  
                cleaned_href = href.strip().replace('\n', '') 
                new_list.append(cleaned_href)
        print("Found DOI links.")
        return new_list

    def li_link_analyser(self, list_of_id_links):
        """
        Analyze links and extract <li> elements containing DOIs.

        Args:
            list_of_id_links (list): List of DOI-related links.

        Returns:
            list: A list of extracted DOI-related content.
        """
        extracted_content = []
        for link in list_of_id_links:
            try:
                # Access each DOI link and parse its content
                response = requests.get(link, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find all <li> elements in the page
                    li_elements = soup.find_all('li')
                    
                    # Extract text from <li> elements that contain '10.' (DOI prefix)
                    filtered_li_elements = [li.get_text(strip=True) for li in li_elements if '10.' in li.get_text()]
                    
                    # Append the extracted content
                    extracted_content.extend(filtered_li_elements)
                    self.complete_resource.append(extracted_content)
            except Exception as e:
                print(f"Error accessing page {link}: {e}")
        return extracted_content


if __name__ == "__main__":
    # Initialize the DOIFinder
    finder = DOIFinder()
    
    # Read the CSV file containing journal URLs
    journal_doi_df = pd.read_csv("insert_file_path", usecols=['journal'])

    # Iterate over each URL in the 'journal' column
    for idx, initial_url in tqdm(journal_doi_df['journal'].items(), desc="Processing journals"):
        initial_url = str(initial_url).strip()  # Clean the URL string
        
        # Check if it's a valid URL
        if initial_url and (initial_url.startswith('http://') or initial_url.startswith('https://')):
            # Find DOI links in the URL
            doi_links = finder.find_doi_links(initial_url)
            
            # Save the found DOI links (if any) into the 'journal_doi' column
            if doi_links:
                # Save the first DOI link or concatenate multiple DOIs
                journal_doi_df.at[idx, 'journal_doi'] = ", ".join(doi_links)
        else:
            print(f"Invalid URL: {initial_url}")

    # Save the updated DataFrame with the new 'journal_doi' column to a CSV file
    journal_doi_df.to_csv("insert_file_path", index=False)
    print("Updated CSV file saved.")

       
