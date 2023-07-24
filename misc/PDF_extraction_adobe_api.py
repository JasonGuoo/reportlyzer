import requests
import json

# Set up your credentials
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
organization_id = 'YOUR_ORGANIZATION_ID'
account_id = 'YOUR_ACCOUNT_ID'

# Set up the API endpoint
base_url = 'https://api.adobe.io'
pdf_services_api_path = '/api/extract'
pdf_services_api_version = 'v1'
pdf_services_endpoint = f'{base_url}{pdf_services_api_path}/{pdf_services_api_version}'

# Set up the input file
input_file_name = 'input.pdf'

# Set up the output file
output_file_name = 'output.json'

def main():
    # Get an access token
    access_token = get_access_token()

    # Set up the headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-api-key': client_id,
        'x-ims-org-id': organization_id,
        'x-ims-account-id': account_id,
        'Content-Type': 'application/pdf'
    }

    # Read the input file
    with open(input_file_name, 'rb') as input_file:
        input_file_content = input_file.read()

    # Call the API
    response = requests.post(pdf_services_endpoint, headers=headers, data=input_file_content)

    # Check the response status
    if response.status_code == 200:
        # Get the response body
        response_body = response.json()

        # Write the output file
        with open(output_file_name, 'w') as output_file:
            json.dump(response_body, output_file, indent=2)
        print(f'Wrote output to {output_file_name}')
    else:
        print(f'Error: {response.status_code}')

def get_access_token():
    # Set up the OAuth endpoint
    oauth_endpoint = f'https://ims-na1.adobelogin.com/ims/exchange/jwt/'

    # Set up the JWT payload
    jwt_payload = {
        'exp': int(time.time()) + 60 * 60,
        'iss': organization_id,
        'sub': account_id,
        'https://ims-na1.adobelogin.com/s/ent_documentcloud_sdk': True,
        'aud': f'https://ims-na1.adobelogin.com/c/{client_id}'
    }

    # Create the JWT
    jwt_token = jwt.encode(jwt_payload, client_secret, algorithm='RS256')

    # Set up the request body
    request_body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'jwt_token': jwt_token.decode('utf-8')
    }

    # Call the OAuth endpoint
    response = requests.post(oauth_endpoint, data=request_body)

    # Check the response status
    if response.status_code == 200:
        # Get the access token from the response body
        response_body = response.json()
        access_token = response_body['access_token']
        return access_token
    else:
        print(f'Error: {response.status_code}')
