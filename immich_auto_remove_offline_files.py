#!/usr/bin/env python3

import argparse
import logging, sys

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

logging.basicConfig(
  stream=sys.stdout, 
  level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
  parser = argparse.ArgumentParser(description='Fetch file report and delete orphaned media assets from Immich.')
  parser.add_argument('--api_key', help='Immich API key for authentication', nargs='?', default=None)
  parser.add_argument('--api_url', help='Full address for Immich, including protocol and port', nargs='?', default=None)
  parser.add_argument('--offline_threshold', help='If offline files exceed threshold, cleaner will not proceed with cleaning', nargs='?', default=100)
  return parser.parse_args()

class Immich():
  def __init__(self, url: str, key: str):
    self.api_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}/api'
    self.headers = {
      'x-api-key': key,
      'Accept': 'application/json'
    }
    self.assets = list()
    self.libraries = list()
  
  def fetchAssets(self, size: int = 1000) -> list:
    payload = {
      'size' : size,
      'page' : 1,
      #'withExif': True,
      'withStacked': True
    }
    assets_total = list()

    logger.info(f'⬇️  Fetching assets: ')
    logger.info(f'   Page size: {size}')

    while payload["page"] != None:

      session = Session()
      retry = Retry(connect=3, backoff_factor=0.5)
      adapter = HTTPAdapter(max_retries=retry)
      session.mount('http://', adapter)
      session.mount('https://', adapter)

      response = session.post(f"{self.api_url}/search/metadata", headers=self.headers, json=payload)

      if not response.ok:
        logger.error('   Error:', response.status_code, response.text)

      assets_total = assets_total + response.json()['assets']['items']
      payload["page"] = response.json()['assets']['nextPage']
    
    self.assets = assets_total
    
    logger.info(f'   Pages: {payload["page"]}')   
    logger.info(f'   Assets: {len(self.assets)}')
    
    return self.assets

  def fetchLibraries(self) -> list:
    logger.info('⬇️  Fetching libraries: ')

    session = Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(f"{self.api_url}/libraries", headers=self.headers)

    if not response.ok:
      logger.error('   Error:', response.status_code, response.text)

    self.libraries = response.json()

    for lib in self.libraries:
      logger.info(f'     {lib["id"]} {lib["name"]}')
    logger.info(f'   Libraries: {len(self.libraries)}')

    return self.libraries

  def removeOfflineFiles(self, library_id: str) -> None:
    session = Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.post(f"{self.api_url}/libraries/{library_id}/removeOffline", headers=self.headers)

    if response.ok:
      logger.info("  🟢 Success!")
    else:
      logger.error(f"  🔴 Error! {response.status_code} {response.text}") 

def main():
  args = parse_arguments()

  # Prompt for admin API key if not provided
  api_key = args.api_key if args.api_key else input('Enter the Immich API key: ')

  # Prompt for Immich API address if not provided
  api_url = args.api_url if args.api_url else input('Enter the full web address for Immich, including protocol and port: ')

  # Set default offline_threshold of 50 files. If there are More than 50 files missing, the cleaner will skip the cleaning and issue a warning. This is in case the External Library goes offline and all assets get flagged.
  offline_threshold = args.offline_threshold if args.offline_threshold else 100

  if not api_key:
    print("API key is required")
    return
  if not api_url:
    print("API URL is required")
    return

  logger.info('============== INITIALIZING ==============')
  
  immich = Immich(api_url, api_key)
  immich.fetchLibraries()
  immich.fetchAssets()

  for library in immich.libraries:
    
    offline = 0
    logger.info(f'Offline Assets in "{library["name"]}":')
    
    for asset in immich.assets:
      if asset["libraryId"] == library["id"]:
        if asset["isOffline"] == True:
          
          offline += 1
          logger.info(f'     ⭕ {asset["id"]} {asset["originalPath"]}')

    if offline >= int(offline_threshold):
      logger.warning(f'⚠️  There are {offline} offline files which is more than the desired threshold of {offline_threshold}! Skipping cleaning! Check if the external libraries are available before manual cleaning!')
    
    elif offline > 0:
      logger.info(f'  🚮 Removing {offline} files.')
      immich.removeOfflineFiles(library["id"]);
    
    else:
      logger.info(f'  ➡️  Skipping cleaning beacuse there are no offline files.')

if __name__ == '__main__':
  main()