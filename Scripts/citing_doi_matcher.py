# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import pandas as pd
from tqdm import tqdm
import json

class DOIMatcher:
    """
    A class to process and match DOIs from a JSON file containing the citations pointing to the mashed dois and a CSV file containing the metadata of the mashed dois.
    """

    def __init__(self, csv_file, json_file, output_file):
        """
        Initializes the DOIProcessor with file paths.

        Args:
            csv_file (str): Path to the CSV file containing metadata.
            json_file (str): Path to the JSON file containing DOI references.
            output_file (str): Path to save the matched results as a CSV.
        """
        self.csv_file = csv_file
        self.json_file = json_file
        self.output_file = output_file

    def load_csv(self):
        """
        Load and preprocess the CSV file.

        Returns:
            set: A set of DOIs from the CSV file after cleaning.
        """
        # Read the CSV file into a DataFrame
        df = pd.read_csv(self.csv_file, quotechar='"', engine='python')

        # Clean the 'id' column by removing the "doi:" prefix
        df["id"] = df["id"].str.replace("doi:", "", regex=False)

        # Convert the DOIs into a set for quick lookup
        doi_set = set(df["id"].dropna())
        return doi_set

    def load_json(self):
        """
        Load the JSON file containing DOI references.

        Returns:
            dict: Parsed JSON data.
        """
        with open(self.json_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data

    def match_dois(self, doi_set, json_data):
        """
        Match DOIs from the JSON file against those in the CSV file.

        Args:
            doi_set (set): A set of DOIs from the CSV file.
            json_data (dict): The parsed JSON data.

        Returns:
            list: A list of matched DOI pairs [citing_doi, referenced_doi].
        """
        results = []

        # Iterate through the JSON data
        for entry_doi, entry_data in tqdm(json_data.items(), desc="Processing JSON entries"):
            for referenced_doi in entry_data.get('referenced_dois', []):
                # Check if the referenced DOI exists in the CSV-derived set
                if referenced_doi in doi_set:
                    results.append([entry_doi, referenced_doi])

        return results

    def save_results(self, results):
        """
        Save the matched DOIs to a CSV file.

        Args:
            results (list): Matched DOI pairs.
        """
        # Convert results to a DataFrame
        results_df = pd.DataFrame(results, columns=['doi_of_citing_entity', 'doi_of_referenced_matched'])

        # Save the DataFrame to a CSV file
        results_df.to_csv(self.output_file, index=False)

        print(f"Matched DOIs saved to {self.output_file}")

    def process(self):
        """
        Complete pipeline to load data, match DOIs, and save results.
        """
        print("Loading CSV data...")
        doi_set = self.load_csv()

        print("Loading JSON data...")
        json_data = self.load_json()

        print("Matching DOIs...")
        results = self.match_dois(doi_set, json_data)

        print(f"Total matches found: {len(results)}")

        print("Saving results...")
        self.save_results(results)


# Example Usage
if __name__ == "__main__":
    processor = DOIMatcher(
        csv_file="insert_file_path",
        json_file="insert_file_path",
        output_file="insert_file_path"
    )

    processor.process()
