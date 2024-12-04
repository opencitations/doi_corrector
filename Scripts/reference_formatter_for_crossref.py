# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
import json
import re

class ReferenceProcessor:
    """
    A class to process and format references in a JSON file.
    It can extract DOI, PMID, or title from references and optionally remove titles from the processed data.
    """

    def __init__(self, input_file, output_file):
        """
        Initialize the ReferenceProcessor with input and output file paths.

        """
        self.input_file = input_file
        self.output_file = output_file

    @staticmethod
    def extract_reference_info(reference):
        """
        Extract DOI, PMID, or title from a reference string.

        """
        # Patterns to match PMID and DOI
        pmid_pattern = r'\bPMID[:\s]?(\d+)\b'
        doi_pattern = r'(10\.\d{4,9}/[^\s:,\);]+)(?=PMID|$)'

        # Extract PMID
        pmid_match = re.search(pmid_pattern, reference)
        pmid = pmid_match.group(1) if pmid_match else None

        # Extract DOI
        doi_match = re.search(doi_pattern, reference)
        doi = doi_match.group(0) if doi_match else None

        # Extract title if DOI and PMID are not found
        if not pmid and not doi:
            title_start = reference.find(")") + 1
            title = reference[title_start:].strip()
            return {"title": title}

        # Construct the result dictionary
        result = {}
        if pmid:
            result["pmid"] = pmid
        if doi:
            result["doi"] = doi
        return result

    def process_references(self):
        """
        Process references in the input JSON file and save the updated data to the output file.

        """
        # Load the JSON data
        with open(self.input_file, 'r', encoding="utf-8") as f:
            data = json.load(f)

        # Process each entry and extract reference information
        for entry in data.values():
            updated_references = []
            for ref in entry.get("references", []):
                ref_info = self.extract_reference_info(ref)
                updated_references.append(ref_info)

            # Update the references in the entry
            entry["references"] = updated_references

        # Save the updated JSON data to the output file
        with open(self.output_file, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Processed references saved to {self.output_file}")

    #This method is optional and so I leave it in a comment; it can be used to remove the titles from the gathered references since it is difficult to retrieve metadata with a Title via the Crossref Api 

    # @staticmethod
    # def remove_titles(json_data):
    #     """
    #     Remove the 'title' key from references in the JSON data.

    #     """
    #     for entry in json_data.values():
    #         references = entry.get("references", [])
    #         for reference in references:
    #             if "title" in reference:
    #                 del reference["title"]
    #     return json_data

    # def finalize_references(self, final_output_file):
    #     """
    #     Remove titles from the references and save the final JSON data to a new file.

    #     """
    #     # Load processed JSON data
    #     with open(self.output_file, 'r', encoding='utf-8') as f:
    #         json_data = json.load(f)

    #     # Remove titles from the references
    #     updated_json_data = self.remove_titles(json_data)

    #     # Save the final JSON data
    #     with open(final_output_file, 'w', encoding='utf-8') as f:
    #         json.dump(updated_json_data, f, indent=4)

    #     print(f"Finalized JSON data saved to {final_output_file}")


# Main script execution
if __name__ == "__main__":
    # File paths
    initial_input_file = "insert_file_path"
    processed_output_file = "insert_file_path"
    final_output_file = "insert_file_path"

    # Initialize the ReferenceProcessor
    processor = ReferenceProcessor(initial_input_file, processed_output_file)

    # Process references to extract DOI, PMID, or title
    processor.process_references()

    # Finalize references by removing titles
    processor.finalize_references(final_output_file)
