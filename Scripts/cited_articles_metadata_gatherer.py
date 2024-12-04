# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import json
import requests
import csv
import time
from tqdm import tqdm
import pandas as pd

class CrossRefProcessor:
    """
    A class to handle fetching, processing, and filtering metadata from the CrossRef API.
    """
    
    def __init__(self, input_csv, output_json, output_csv, filtered_json):
        """
        Initializes the processor with file paths.
        
        Args:
            input_csv (str): Path to the input CSV file containing citing DOIs.
            output_json (str): Path to save the output JSON file.
            output_csv (str): Path to save the output CSV file.
            filtered_json (str): Path to save the filtered JSON file.
        """
        self.input_csv = input_csv
        self.output_json = output_json
        self.output_csv = output_csv
        self.filtered_json = filtered_json

    def get_crossref_data(self, doi):
        """
        Fetch metadata for a DOI using the CrossRef API taking as argument the doi and returning a dict containing metadata

        """
        url = f"https://api.crossref.org/works/{doi}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get('message', {})
            
            title = data.get("title", [""])[0] if data.get("title") else "No Title Available"
            publisher = data.get("publisher", "")
            issue = data.get("issue", "")
            date_time = data.get("created", {}).get("date-time", "")
            authors = [f"{author.get('given', '')} {author.get('family', '')}" for author in data.get("author", [])]
            references = data.get("reference", [])
            
            return {
                "doi": doi,
                "title": title,
                "publisher": publisher,
                "issue": issue,
                "date_time": date_time,
                "authors": "; ".join(authors),
                "references": references
            }
        except requests.RequestException as e:
            print(f"Error fetching CrossRef data for DOI {doi}: {e}")
            return {}

    def process_data(self):
        """
        Fetch metadata for DOIs from a CSV file and save the results as JSON and CSV.
        """
        # Load DOIs from the input CSV file
        df = pd.read_csv(self.input_csv, usecols=["doi_citing_entity"])
        
        references_data = {}
        csv_rows = []
        
        for _, row in tqdm(df.iterrows(), desc="Processing entries", total=df.shape[0]):
            primary_doi = row["doi_citing_entity"]
            crossref_data = self.get_crossref_data(primary_doi)
            
            if crossref_data:
                # Store references data in JSON format
                references_data[primary_doi] = {
                    "doi": primary_doi,
                    "referenced_entities": crossref_data.get("references", [])
                }
                
                # Prepare data for the CSV file
                csv_row = {
                    "primary_id": primary_doi,
                    "id": crossref_data.get("doi", ""),
                    "title": crossref_data.get("title", ""),
                    "author": crossref_data.get("authors", ""),
                    "pub_date": crossref_data.get("date_time", ""),
                    "venue": "",
                    "volume": crossref_data.get("volume", ""),
                    "issue": crossref_data.get("issue", ""),
                    "page": "",
                    "type": "",
                    "publisher": crossref_data.get("publisher", ""),
                    "editor": ""
                }
                csv_rows.append(csv_row)
                
                # Sleep to avoid rate-limiting
                time.sleep(0.1)
        
        # Save results to JSON
        with open(self.output_json, "w", encoding="utf-8") as jsonfile:
            json.dump(references_data, jsonfile, ensure_ascii=False, indent=4)
        
        # Save results to CSV
        fieldnames = ["primary_id", "id", "title", "author", "pub_date", "venue", "volume", "issue", "page", "type", "publisher", "editor"]
        with open(self.output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        print(f"Data saved to {self.output_json} and {self.output_csv}")

    def filter_referenced_dois(self):
        """
        Filter the referenced DOIs from the metadata JSON file and save to a new JSON file.
        """
        # Load the JSON data from the output file
        with open(self.output_json, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        
        # Initialize a new dictionary to store the filtered results
        filtered_data = {}
        
        for doi, details in data.items():
            # Create a new entry with the DOI and its referenced DOIs
            filtered_data[doi] = {"doi": doi, "referenced_dois": []}
            
            for entity in details.get("referenced_entities", []):
                if "DOI" in entity:
                    filtered_data[doi]["referenced_dois"].append(entity["DOI"])
        
        # Save the filtered results to a new JSON file
        with open(self.filtered_json, "w", encoding="utf-8") as output_file:
            json.dump(filtered_data, output_file, ensure_ascii=False, indent=4)
        
        print(f"Filtered data saved to {self.filtered_json}")

# Example usage
if __name__ == "__main__":
    processor = CrossRefProcessor(
        input_csv="insert_file_path",
        output_json="insert_file_path",
        output_csv="insert_file_path",
        filtered_json="insert_file_path"
    )
    
    # Process data and save results
    processor.process_data()
    
    # Filter and save referenced DOIs
    processor.filter_referenced_dois()
