# ________________________________________
# Docs: 
# 1. web-browser lib: https://docs.python.org/3/library/webbrowser.html
# 2. MSAL: https://msal-python.readthedocs.io/en/latest/#api-reference 
# 3. github sample code: https://github.com/Azure-Samples/ms-identity-python-daemon/blob/master/1-Call-MsGraph-WithSecret/confidential_client_secret_sample.py
# 4. Bearer Token docs: https://oauth.net/2/bearer-tokens/
# ________________________________________

from msal import ConfidentialClientApplication
import requests
import json
from dotenv import load_dotenv
import os

tenant = "value"
app_id = "value"
secret = "value"

# https://msal-python.readthedocs.io/en/latest/#msal.ClientApplication.params.authority
login_url = f'https://login.microsoftonline.com/{tenant}'

# scopes (list[str]) – (Required) Scopes requested to access a protected API (a resource)
SCOPE = ["https://graph.microsoft.com/.default"]

endpoint = "https://graph.microsoft.com/v1.0/users"

load_dotenv()

APP_ID = os.getenv('app')
SECRET = os.getenv('secret')
tenant = os.getenv('tenant_id')

app = ConfidentialClientApplication(client_id = app_id, client_credential=secret, 
                                    authority=login_url)

client = ConfidentialClientApplication(client_id = APP_ID, client_credential=SECRET, 
                                    authority=login_url)

# token = app.acquire_token_for_client(scopes=SCOPE)
token = client.acquire_token_for_client(scopes=SCOPE)
#print(token['access_token'])
print(token)

# what successful response looks like: https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow#successful-response-1

if token != None:
    # Calling graph using the access token
    graph_data = requests.get(  # Use token to call downstream service
        endpoint,
        headers={'Authorization': 'Bearer ' + token['access_token']}, ).json()
    print("Graph API call result: ")
    print(json.dumps(graph_data, indent=2))
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))
