"""
Brave AI Mode API: Batch Multi-Query Example
See more at: https://apify.com/johnvc/brave-ai-mode-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/brave-ai-mode-api/input-schema?fpr=9n7kx3

This script shows the batch capability of the Brave AI Mode API on Apify: pass a
list of queries with the `queries` input and the Actor checks each one in a
single run, tagging every row with the `query` it came from. That makes it easy
to monitor AI answers across a whole topic set at once. Inputs are kept small so
your first call stays cheap.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
"""

import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

# Initialize the Apify client with your API token (read from .env)
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# Build the Actor input.
# This run uses the `queries` list to check several terms at once. Each row in
# the output carries the `query` it came from. The list is kept short (2
# queries) to keep this first run inexpensive: you are billed per query. Add
# more queries or change `country`/`language` once you know your budget.
run_input = {
    "queries": ["what is quantum computing", "how does TLS work"],
    "country": "us",     # two-letter country code, e.g. us, gb, de
    "language": "en",    # two-letter language code, e.g. en, es, de
}

# Run the Actor and wait for it to finish
run = client.actor("johnvc/brave-ai-mode-api").call(run_input=run_input)
if run is None:
    raise SystemExit("The Actor run did not return a result.")

# Read structured results from the run's default dataset
# (apify-client 3.x returns a Run object; use .default_dataset_id, not run["..."])
items = list(client.dataset(run.default_dataset_id).iterate_items())
print(f"Returned {len(items)} row(s) across {len(run_input['queries'])} queries.\n")

# Print a short report per query: whether an AI Mode answer exists and its sources.
for item in items:
    query = item.get("query", "")
    present = item.get("ai_mode_present")
    print(f"=== {query}  (AI Mode present: {present}) ===")
    markdown = item.get("markdown")
    if markdown:
        print(markdown[:300] + ("..." if len(markdown) > 300 else ""))
    for ref in item.get("references", []):
        print(f"  source: {ref.get('title')}  {ref.get('link')}")
    print()
