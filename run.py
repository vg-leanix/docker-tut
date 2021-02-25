import json
import requests
from datetime import datetime
import click

# with open('credentials.json') as f:
#     data = json.load(f)

with open('ldif.json') as ldif:
    ldif = json.load(ldif)

api_token = data['leanix']['apitoken']
workspace_id = data['leanix']['workspace_id']
version = 10
timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")


auth_url = 'https://demo-eu.leanix.net/services/mtm/v1/oauth2/token'
request_url = 'https://demo-eu.leanix.net/services/integration-api/v1/synchronizationRuns'


def build_ldif(version, timestamp, ldif):
    ldif['content'][0]['data']['last_deployed'] = timestamp
    ldif['content'][0]['data']['version'] = version
    return json.dumps(ldif)


@click.command()
@click.option('-t','token', help='LeanIX API Token')
def build(token):
    response = requests.post(auth_url, auth=('apitoken', token),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header, "Content-Type":"application/json"}
    new_ldif = build_ldif(version=version, timestamp=timestamp, ldif=ldif)


    live = {'start':'true'}
    test = {'test': 'true'}
    
    r = requests.post(request_url, data=new_ldif, headers=header, params=live)

    r.raise_for_status()
    print(r.json())


if __name__ == '__main__':
    build()