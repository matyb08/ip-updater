import requests
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime

DYNU_DNS_USERNAME = os.environ['DYNU_DNS_USERNAME']
DYNU_DNS_PASSWORD = os.environ['DYNU_DNS_PASSWORD']
DYNU_DNS_HOSTNAME = os.environ['DYNU_DNS_HOSTNAME']
IP_CHANGELIST_LOG_PATH = '/var/log/my-logs/ip-changelist.txt'

# ! UNCOMMENT FOR TESTING !
# IP_CHANGELIST_LOG_PATH = '/test/ip-changelist.txt'

def log_to_file(msg):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(IP_CHANGELIST_LOG_PATH, 'a') as changelist:
        changelist.write(f'{time} {msg}\n')


try:
    with open('ip.txt', 'r') as ip:
        last_ip = ip.read()

except FileNotFoundError:
    last_ip = 'N/A'

new_ip = requests.get('https://myexternalip.com/raw').text
if new_ip != last_ip:
    log_to_file(f'change detected: from {last_ip} to {new_ip}')

    # Change DNS record
    response = requests.get(
        f'https://api.dynu.com/nic/update?hostname={DYNU_DNS_HOSTNAME}&myip={new_ip}',
        auth=HTTPBasicAuth(DYNU_DNS_USERNAME, DYNU_DNS_PASSWORD)
    )

    if response.text.startswith('good'):
        with open('ip.txt', 'w') as ip:
            ip.write(new_ip)

        log_to_file(f'changed A record on DNS to {new_ip}')
    elif response.text.startswith('nochg'):
        log_to_file(f'same A record already set on DNS ({new_ip})')
    else:
        log_to_file(f'failed to change A record on DNS to {new_ip}')
