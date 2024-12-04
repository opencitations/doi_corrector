# Copyright (c) 2024 Salvatore Di Marzo

# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLCitationExtractor:
    """
    A class to extract citation and cited entity data using the OpenCitations Index SPARQL endpoint.
    """
    def __init__(self, endpoint_url, input_csv_path, output_directory):
        """
        Initializes the SPARQLCitationExtractor with the endpoint URL, input CSV, and output directory.
        """
        self.endpoint_url = endpoint_url
        self.input_csv_path = input_csv_path
        self.output_directory = output_directory

    def query_sparql_citing(self, cited_entity_url):
        """
        Queries the SPARQL endpoint for citing entities of a given cited entity.
        """
        sparql = SPARQLWrapper(self.endpoint_url)
        query = f"""
        PREFIX cito:<http://purl.org/spar/cito/>
        SELECT ?citation ?citing_entity WHERE {{
            ?citation a cito:Citation .
            ?citation cito:hasCitingEntity ?citing_entity .
            ?citation cito:hasCitedEntity <{cited_entity_url}>
        }}
        """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            return results['results']['bindings']
        except Exception as e:
            print(f"Error querying {cited_entity_url}: {e}")
            return None

    def query_sparql_cited(self, citing_entity_url):
        """
        Queries the SPARQL endpoint for cited entities of a given citing entity.
        """
        sparql = SPARQLWrapper(self.endpoint_url)
        query = f"""
        PREFIX cito:<http://purl.org/spar/cito/>
        SELECT ?citation ?cited_entity WHERE {{
            ?citation a cito:Citation .
            ?citation cito:hasCitedEntity ?cited_entity .
            ?citation cito:hasCitingEntity <{citing_entity_url}>
        }}
        """
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            return results['results']['bindings']
        except Exception as e:
            print(f"Error querying {citing_entity_url}: {e}")
            return None

    def extract_citing_data(self):
        """
        Extracts citing entity data from the SPARQL endpoint and saves it to a CSV file.
        """
        journal_column = pd.read_csv(self.input_csv_path, usecols=['journal'])
        citations_list = []

        for journal_url in journal_column['journal']:
            sparql_results = self.query_sparql_citing(journal_url)

            if sparql_results:
                for result in sparql_results:
                    citation = result.get('citation', {}).get('value', '')
                    citing_entity = result.get('citing_entity', {}).get('value', '')
                    citations_list.append({'journal': journal_url, 'citation': citation, 'citing_entity': citing_entity})

        results_df = pd.DataFrame(citations_list)
        results_df.to_csv(f"{self.output_directory}/sparql_results.csv", index=False)
        print("Citing entities data saved to sparql_results.csv")

    def extract_cited_data(self):
        """
        Extracts cited entity data from the SPARQL endpoint and saves it to a CSV file.
        """
        journal_column = pd.read_csv(self.input_csv_path, usecols=['journal'])
        citations_cited_list = []

        for journal_url in journal_column['journal']:
            sparql_results = self.query_sparql_cited(journal_url)

            if sparql_results:
                for result in sparql_results:
                    citation = result.get('citation', {}).get('value', '')
                    cited_entity = result.get('cited_entity', {}).get('value', '')
                    citations_cited_list.append({'journal': journal_url, 'citation': citation, 'cited_entity': cited_entity})

        results_df = pd.DataFrame(citations_cited_list)
        results_df.to_csv(f"{self.output_directory}/sparql_results_cited.csv", index=False)
        print("Cited entities data saved to sparql_results_cited.csv")

    def merge_citing_and_cited_data(self):
        """
        Merges citing and cited entity data into a single CSV file.
        """
        citing_df = pd.read_csv(f"{self.output_directory}/sparql_results.csv")
        cited_df = pd.read_csv(f"{self.output_directory}/sparql_results_cited.csv")
        merged_df = pd.merge(citing_df, cited_df, on="journal", how="outer", suffixes=('citing', 'cited'))
        merged_df.to_csv(f"{self.output_directory}/all_citations.csv", index=False)
        print("Citing and cited data merged and saved to all_citations.csv")

#To use:
if __name__ == "__main__":
    extractor = SPARQLCitationExtractor(
        endpoint_url="https://opencitations.net/index/sparql",
        input_csv_path="insert_path",
        output_directory="insert_directory"
    )
    
    extractor.extract_citing_data()
    extractor.extract_cited_data()
    extractor.merge_citing_and_cited_data()
