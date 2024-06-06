#!/usr/bin/env python3

import argparse
import requests
import logging, sys, datetime
from urllib.parse import urlparse

# Function to format the log messages with date and time
class DateTimeFormatter(logging.Formatter):
  def formatTime(self, record, datefmt=None):
    dt = datetime.datetime.fromtimestamp(record.created)
    if datefmt:
      s = dt.strftime(datefmt)
    else:
      s = dt.isoformat(sep=' ', timespec='seconds')
    return s

# Set up logging to output to stdout with date and time
logging.basicConfig(
  stream=sys.stdout, 
  level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s'
)

# Update the formatter to include date and time
for handler in logging.getLogger().handlers:
  handler.setFormatter(DateTimeFormatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s'
  ))


def parse_arguments():
  parser = argparse.ArgumentParser(description='Fetch file report and delete orphaned media assets from Immich.')
  parser.add_argument('--api_key', help='Immich API key for authentication', nargs='?', default=None)
  parser.add_argument('--api_url', help='Full address for Immich, including protocol and port', nargs='?', default=None)
  return parser.parse_args()

def main():
  
  logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

  args = parse_arguments()

  # Prompt for admin API key if not provided
  api_key = args.api_key if args.api_key else input('Enter the Immich API key: ')

  # Prompt for Immich API address if not provided
  api_url = args.api_url if args.api_url else input('Enter the full web address for Immich, including protocol and port: ')
  
  if not api_key:
    print("API key is required")
    return
  if not api_url:
    print("API URL is required")
    return

  immich_parsed_url = urlparse(api_url)
  immich_base_url = f'{immich_parsed_url.scheme}://{immich_parsed_url.netloc}'
  immich_api_url = f'{immich_base_url}/api'
  immich_api_url_libs = f'{immich_api_url}/library'
  
  headers = {
    'x-api-key': api_key,
    'Accept': 'application/json'
  }

  print()
  logging.info('Retrieving list of Immich libraries...')

  try:
    response = requests.request("GET", immich_api_url_libs, headers=headers)
    response.raise_for_status()
    logging.info('External libraries found:')
  except requests.exceptions.RequestException as e:
    logging.error(f'Failed to fetch libraries: {str(e)}')
    return
  
  for library in ( x for x in response.json() if x['type'] == 'EXTERNAL' ):
    immich_api_url_offline = f'{api_url}/library/{library["id"]}/removeOffline'

    logging.info(f'Cleaning "{library["name"]}" [{library["id"]}]')
    try:
      response = requests.request("POST", immich_api_url_offline, headers=headers)
      response.raise_for_status()
      logging.info(f'Cleaned  "{library["name"]}" [{library["id"]}]')
    
    except requests.exceptions.RequestException as e:
      logging.error(f'Failed "{library["name"]}" [{library["id"]}]')
      return

  print()

if __name__ == '__main__':
  main()