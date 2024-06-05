#!/usr/bin/env python3

import argparse
import requests
from urllib.parse import urlparse
from halo import Halo

def parse_arguments():
  parser = argparse.ArgumentParser(description='Fetch file report and delete orphaned media assets from Immich.')
  parser.add_argument('--api_key', help='Immich API key for authentication', nargs='?', default=None)
  parser.add_argument('--api_url', help='Full address for Immich, including protocol and port', nargs='?', default=None)
  return parser.parse_args()

def main():
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
  spinner = Halo(text='Retrieving list of Immich libraries...', spinner='dots')
  spinner.start()
  try:
    response = requests.request("GET", immich_api_url_libs, headers=headers)
    response.raise_for_status()
    spinner.succeed('External libraries found:')
  except requests.exceptions.RequestException as e:
    spinner.fail(f'Failed to fetch libraries: {str(e)}')
    return
  
  for library in ( x for x in response.json() if x['type'] == 'EXTERNAL' ):
    immich_api_url_offline = f'{api_url}/library/{library["id"]}/removeOffline'

    spinner2 = Halo(text=f'Cleaning "{library["name"]}" [{library["id"]}]', spinner='dots')
    spinner2.start()
    try:
      response = requests.request("POST", immich_api_url_offline, headers=headers)
      response.raise_for_status()
      spinner2.succeed(f'Cleaned "{library["name"]}" [{library["id"]}]')
    
    except requests.exceptions.RequestException as e:
      spinner2.fail(f'Failed "{library["name"]}" [{library["id"]}]')
      return
  print()

if __name__ == '__main__':
  main()