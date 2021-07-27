import json
import requests
from datetime import datetime
import click
import pytz

local_tz = pytz.timezone('Europe/Berlin')
# with open('credentials.json') as f:
#     data = json.load(f)

with open('ldif.json') as ldif:
    ldif = json.load(ldif)

# api_token = data['leanix']['apitoken']
# workspace_id = data['leanix']['workspace_id']
version = 10
timestamp = datetime.now()
local_timestamp = local_tz.localize(timestamp).strftime("%d-%m-%Y %H:%M")


auth_url = 'https://demo-eu.leanix.net/services/mtm/v1/oauth2/token'
request_url = 'https://demo-eu.leanix.net/services/integration-api/v1/synchronizationRuns'


@click.group()
def cli():
    pass


def build_ldif(version, timestamp, repo, ldif):
    ldif['content'][0]['data']['last_deployed'] = timestamp
    ldif['content'][0]['data']['version'] = version
    ldif['content'][0]['data']['repo'] = repo
    return json.dumps(ldif)


@click.command('date')
def print_date():
    print(local_timestamp)


@click.command('token')
@click.option('-t', 'token', help='LeanIX API Token')
@click.option('-r', 'repo', help='The Repo ID from TravisCI')
def build(token,repo):
    response = requests.post(auth_url, auth=('apitoken', token),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header, "Content-Type": "application/json"}
    new_ldif = build_ldif(version=version, timestamp=local_timestamp, ldif=ldif, repo=repo)

    live = {'start': 'true'}
    test = {'test': 'true'}

    r = requests.post(request_url, data=new_ldif, headers=header, params=live)

    r.raise_for_status()
    print(r.json())


cli.add_command(build)
cli.add_command(print_date)

if __name__ == '__main__':
    cli()
