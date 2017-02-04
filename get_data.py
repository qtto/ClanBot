# This is basically all google's code, not mine

from __future__ import print_function
import httplib2
import os
import json

from apiclient import discovery
from oauth2client import tools
from oauth2client.file import Storage

from oauth2client.service_account import ServiceAccountCredentials

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'ClanBot'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    './API_key.json', SCOPES)


async def get_data():
    http = credentials.authorize(httplib2.Http())

    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1kFeViTfq33UgGll6TptJN6qwoKmKDCUZf1L-cjK_6Fo'
    range_name =  'PublicView!B2:G502' #RSN / rank / CP / Cap status / next rank:caps / next rank:xp

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=range_name).execute()

        if result:
            with open('spreadsheet.json', 'w') as f:
                json.dump(result['values'], f)

        return result

    except Exception as e:
        print(e)
        return

if __name__ == '__main__':
    get_data()
