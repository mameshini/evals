import os
import requests
import pytest
import logging
from dotenv import load_dotenv

def test_get_caller():
    logger = logging.getLogger("kernel")
    load_dotenv()

    # ServiceNow instance details
    username = os.environ.get("SN_USERNAME")
    password = os.environ.get("SN_PASSWORD")
    email = os.environ.get("SN_EMAIL_USER")   # Replace with System.User.PrincipalName
    
    query_params = {
        'sysparm_display_value': 'true',
        'sysparm_exclude_reference_link': 'true',
        'sysparm_limit': 1,
        'sysparm_query': f'email={email}^user_nameISEMPTY'
    }

    # Make the REST API call
    url = f"https://{os.environ.get('SN_INSTANCE')}.service-now.com/api/now/table/sys_user"
    response = requests.get(
        url,
        auth=(username, password),
        params=query_params,
        headers={'Accept': 'application/json'}
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert 'result' in data
    
    if len(data['result']) > 0:
        user = data['result'][0]
        # Verify key fields are present
        assert 'sys_id' in user
        assert 'email' in user
        assert 'first_name' in user
        assert 'last_name' in user
