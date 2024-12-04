import requests
import json
from tqdm import tqdm
import webbrowser

class DOIValidator:
    def __init__(self, doi_list):
        self.doi_list = doi_list
        self.opencitations_base_url = "https://opencitations.net/meta/api/v1/metadata/doi:"
        self.crossref_base_url = "https://api.crossref.org/works/"
        self.results = []

    def get_opencitations_metadata(self, doi):
        """Retrieve metadata from OpenCitations API for a given DOI."""
        try:
            response = requests.get(self.opencitations_base_url + doi)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]  # Access the first item in the OpenCitations response
        except Exception as e:
            print(f"Error fetching OpenCitations data for DOI {doi}: {e}")
        return None

    def get_crossref_metadata(self, doi):
        """Retrieve metadata from CrossRef API for a given DOI."""
        try:
            response = requests.get(self.crossref_base_url + doi)
            response.raise_for_status()
            data = response.json()
            if "message" in data:
                return data["message"]  # Access CrossRef metadata in "message"
        except Exception as e:
            print(f"Error fetching CrossRef data for DOI {doi}: {e}")
        return None

    def validate_doi(self, doi, opencitations_data, crossref_data):
        """Compare metadata between OpenCitations and CrossRef to validate DOI."""
        # Extract title and author from OpenCitations data
        opencitations_title = opencitations_data.get("title", "").lower()
        opencitations_author = opencitations_data.get("author", "").lower()
        opencitations_publisher = opencitations_data.get("publisher", "").lower()
        
        # Extract title, author, and publisher from CrossRef data
        crossref_title = crossref_data.get("title", [""])[0].lower() if crossref_data.get("title") else ""
        crossref_author = ", ".join([author["given"] + " " + author["family"] for author in crossref_data.get("author", [])]).lower()
        crossref_publisher = crossref_data.get("publisher", "").lower()
        
        # Validation checks for title, author, and publisher
        title_match = opencitations_title == crossref_title
        author_match = opencitations_author in crossref_author if opencitations_author else True
        publisher_match = opencitations_publisher == crossref_publisher

        # Return a validation result
        return {
            "doi": doi,
            "opencitations_title": opencitations_title,
            "crossref_title": crossref_title,
            "title_match": title_match,
            "opencitations_author": opencitations_author,
            "crossref_author": crossref_author,
            "author_match": author_match,
            "opencitations_publisher": opencitations_publisher,
            "crossref_publisher": crossref_publisher,
            "publisher_match": publisher_match,
            "valid": title_match or (author_match and publisher_match)
        }

    def validate_doi_list(self):
        """Validate all DOIs in the provided list and store results."""
        for doi in tqdm(self.doi_list, desc="Validating DOIs"):
            # Retrieve metadata from both APIs
            opencitations_data = self.get_opencitations_metadata(doi)
            crossref_data = self.get_crossref_metadata(doi)

            # Check if data was successfully retrieved from both sources
            if opencitations_data and crossref_data:
                # Compare metadata and validate DOI
                validation_result = self.validate_doi(doi, opencitations_data, crossref_data)
                self.results.append(validation_result)
            else:
                self.results.append({
                    "doi": doi,
                    "error": "Data retrieval failed for one or both APIs"
                })
    def open_dois(self):
        base_url = "https://doi.org/"
        for doi in doi_list:
            full_doi_url = base_url + doi.strip()
            print(f"Opening: {full_doi_url}")  # Optional: for debugging or confirmation
            webbrowser.open(full_doi_url)


    def save_results(self, output_file="doi_validation_results.json"):
        """Save validation results to a JSON file."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=4)
        print(f"Validation results saved to {output_file}")


doi_list = [
    "10.5055/jom"
]


validator = DOIValidator(doi_list)
# validator.open_dois()
validator.validate_doi_list()
validator.save_results("doi_validation_results.json")
