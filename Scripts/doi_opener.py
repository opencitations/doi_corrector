# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import webbrowser

class DOIOpener:
    def __init__(self, batch_data):
        self.batch_data = batch_data
    
    def process_and_open_urls(self):
        """
        Process each entry in the doi list and open the corresponding URLs and DOIs to check the dois for validation.
        """
        for entry in self.batch_data:
            # The first item in the entry is the base URL
            base_url = entry[0].strip().strip('"')
            
            # The second item is a long string of DOIs separated by commas
            dois = entry[1].strip().strip('"').split(',')
            
            # Open the base URL in the web browser
            webbrowser.open(base_url)
            
            # Open each DOI link
            for doi in dois:
                full_doi_url = "https://doi.org/" + doi.strip()
                webbrowser.open(full_doi_url)

if __name__ == "__main__":
    # Insert the list of dois here
    doi_list = []


    doi_opener = DOIOpener(doi_list)
    doi_opener.process_and_open_urls()
