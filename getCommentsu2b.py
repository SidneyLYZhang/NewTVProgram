import httplib2
import os
import sys

from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main():
  service = build('translate', 'v2', developerKey='AIzaSyC6WerHxYiaEcqE0eHLEZ6kgJ2KJzEEUks')
  print(service.translations().list(
      source='en',
      target='fr',
      q=['flower', 'car']
    ).execute())

main()