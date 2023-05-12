import argparse
import json

import requests
from parser_stenogr_rada import RadaStenoParser

parser = argparse.ArgumentParser(description="Script for parsing transcripts from rada.gov.ua",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("url", help="Transcripts URL, example: https://www.rada.gov.ua/meeting/stenogr/show/7749.html")
parser.add_argument("dest", help="Destination file location")
args = parser.parse_args()
config = vars(args)

page = requests.get(args.url)

parser = RadaStenoParser()
parser.parse_page_html(page.content)
items = parser.get_results()

with open(args.dest, 'w') as file:
    file.write(json.dumps(items, ensure_ascii=False))

print(f'Parsed {len(items)} transcript items')