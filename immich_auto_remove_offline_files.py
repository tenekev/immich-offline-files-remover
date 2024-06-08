#!/usr/bin/env python3

import argparse
import requests
import logging, sys
from urllib.parse import urlparse


class CustomLogger(logging.Logger):
  def __init__(self, name, level=logging.NOTSET):
    super().__init__(name, level)

  def set_indent_level(self, indent_level):
    for handler in self.handlers:
      if isinstance(handler, IndentHandler):
        handler.indent_level = indent_level
      return self

  def log_with_indent(self, level, msg, *args, **kwargs):
    self.log(level, msg, *args, **kwargs)
    return self

class IndentHandler(logging.StreamHandler):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.indent_level = 0
        
  def set_indent_level(self, indent_level):
    self.indent_level = indent_level

  def emit(self, record):
    record.msg = '   ' * self.indent_level + '└─ ' + record.msg
    super().emit(record)

def custom_logger():
  log_format = '%(asctime)s - %(levelname)s - %(message)s'
  
  logger = CustomLogger(__name__)
  
  formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
  
  handler = IndentHandler(sys.stdout)
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  
  return logger

def parse_arguments():
  parser = argparse.ArgumentParser(description='Fetch file report and delete orphaned media assets from Immich.')
  parser.add_argument('--api_key', help='Immich API key for authentication', nargs='?', default=None)
  parser.add_argument('--api_url', help='Full address for Immich, including protocol and port', nargs='?', default=None)
  parser.add_argument('--offline_threshold', help='If offline files exceed threshold, cleaner will not proceed with cleaning', nargs='?', default=100)
  return parser.parse_args()

def main():

  logger = custom_logger()

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
  immich_api_url_ass = f'{immich_api_url}/asset'
  immich_api_url_libs = f'{immich_api_url}/library'
  
  headers = {
    'x-api-key': api_key,
    'Accept': 'application/json'
  }

  logger.set_indent_level(0).log_with_indent(logging.INFO, f'Retrieving list of Immich libraries...')
  
  try:
    response_libraries = requests.request("GET", immich_api_url_libs, headers=headers)
    response_libraries.raise_for_status()

    external_libraries = [x for x in response_libraries.json() if x["type"] == "EXTERNAL"]

    logger.set_indent_level(0).log_with_indent(
      logging.INFO, f'{len(external_libraries)} external libraries found.'
    )
    
    for library in external_libraries:

      logger.set_indent_level(1).log_with_indent(
        logging.INFO, f'Searching for Offline files in {library["name"]} ({library["id"]})...'
      )
      
      response_assets = requests.request("GET", immich_api_url_ass, headers=headers)
      response_assets.raise_for_status()
      
      offline_files = [x for x in response_assets.json() if x["isOffline"] == True and x["libraryId"] == library["id"]]

      logger.set_indent_level(2).log_with_indent(
        logging.INFO, f'{len(offline_files)} offline files found.'
      )
      
      for asset in offline_files:

        logger.set_indent_level(3).log_with_indent(
          logging.INFO, f'{asset["originalFileName"]} ({asset["id"]}) {asset["originalPath"]}'
        )

      if len(offline_files) == 0:
        logger.set_indent_level(2).log_with_indent(
          logging.INFO, f'➡️  Skipping cleaning beacuse there are no offline files.'
        )
  
      elif len(offline_files) >= int(args.offline_threshold):
        logger.set_indent_level(2).log_with_indent(
          logging.WARNING, f'⚠️  There are {len(offline_files)} offline files which is more than the desired threshold of {args.offline_threshold}! Skipping cleaning! Check if the external libraries are available before manual cleaning!'
        )

      else:
        logger.set_indent_level(2).log_with_indent(
          logging.INFO, f'🗑️  Attempting to clean library...'
        )

        immich_api_url_offline = f'{api_url}/library/{library["id"]}/removeOffline'

        try:
          cleaning_response = requests.request("POST", immich_api_url_offline, headers=headers)
          cleaning_response.raise_for_status()
          
          logger.set_indent_level(3).log_with_indent(
            logging.INFO, f'🟢 Cleaned library "{library["name"]}"'
          )
        
        except requests.exceptions.RequestException as e:
          logger.set_indent_level(3).log_with_indent(
            logging.ERROR, f'🔴 Failed to clean library "{library["name"]}": \n{str(e)}'
          )
          return
  
  except requests.exceptions.RequestException as e:
    logger.set_indent_level(1).log_with_indent(
      logging.ERROR, f'Failed to fetch libraries: \n{str(e)}'
    )
    return

if __name__ == '__main__':
  main()