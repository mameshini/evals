import os
import requests
from dotenv import load_dotenv

def get_caller(username, password, instance, email):
    query_params = {
        'sysparm_display_value': 'true',
        'sysparm_exclude_reference_link': 'true',
        'sysparm_limit': 1,
        'sysparm_query': f'email={email}'
    }

    url = f"https://{instance}.service-now.com/api/now/table/sys_user"
    response = requests.get(
        url,
        auth=(username, password),
        params=query_params,
        headers={'Accept': 'application/json'}
    )
    
    return response

def get_kb(username, password, instance, query_string):
    #encoded_query = f"textLIKE%{query_string}^kb_category NOT LIKE Internal Use"
    encoded_query = f"article_bodyLIKE%{query_string}%^kb_category NOT LIKE Internal Use"
    query_params = {
        'sysparm_display_value': 'true',
        'sysparm_exclude_reference_link': 'true',
        'sysparm_query': encoded_query,
        'sysparm_fields': 'number,short_description,text,sys_id,published,kb_category,kb_knowledge_base',
        'sysparm_limit': '10'
    }

    url = f"https://{instance}.service-now.com/api/now/table/kb_knowledge"
    response = requests.get(
        url,
        auth=(username, password),
        params=query_params,
        headers={'Accept': 'application/json'}
    )
    
    return response


def view_incidents(username, password, instance, caller_id):
    query_params = {
        'sysparm_display_value': 'true',
        'sysparm_exclude_reference_link': 'true',
        'sysparm_query': f'caller_id={caller_id}^ORDERBYDESCopened_at',
        'sysparm_fields': 'number,description,state,priority,opened_at,sys_id'
    }

    url = f"https://{instance}.service-now.com/api/now/table/incident"

    response = requests.get(
        url,
        auth=(username, password),
        params=query_params,
        headers={'Accept': 'application/json'}
    )
    
    return response


def view_service_requests(username, password, instance, caller_email):
    caller_id = "da1fc28a47ec1e106432b0da216d4308"
    query_params = {
        'sysparm_display_value': 'true',
        'sysparm_exclude_reference_link': 'true',
        'sysparm_query': f'requested_for={caller_id}^ORDERBYDESCopened_at',
        'sysparm_fields': 'number,short_description,cat_item,comments_and_work_notes,state,priority,opened_at,sys_id,requested_for,opened_by'
    }

    url = f"https://{instance}.service-now.com/api/now/table/sc_req_item"

    response = requests.get(
        url,
        auth=(username, password),
        params=query_params,
        headers={'Accept': 'application/json'}
    )

    return response

def main():
    load_dotenv()
    
    # ServiceNow instance details
    username = os.environ.get("SN_USERNAME")
    password = os.environ.get("SN_PASSWORD")
    email = os.environ.get("SN_EMAIL_USER")
    instance = os.environ.get("SN_INSTANCE")
    
    response = get_caller(username, password, instance, email)
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and len(data['result']) > 0:
            user = data['result'][0]
            print(f"User sys_id: {user['sys_id']}")
            print(f"User email: {user['email']}")
            print(f"User user_name: {user['user_name']}")
            print(f"First Name: {user['first_name']}")
            print(f"Last Name: {user['last_name']}")
        else:
            print("No user found with the specified email")
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.text)

    # Get service requests
    service_requests_response = view_service_requests(username, password, instance, email)
    
    if service_requests_response.status_code == 200:
        sr_data = service_requests_response.json()
        if 'result' in sr_data:
            print("\nService Requests:")
            print("------------------")
            for request in sr_data['result']:
                print(f"Request Number: {request['number']}")
                print(f"Cat Item: {request['cat_item']}")
                print(f"Short Description: {request['short_description']}")
                print(f"State: {request['state']}")
                print(f"Priority: {request['priority']}")
                print(f"Opened: {request['opened_at']}")
                print(f"Requested For: {request['requested_for']}")
                print(f"Requested By: {request['opened_by']}")
                print(f"Comments and Work Notes: {request['comments_and_work_notes']}")
                print("------------------")
    else:
        print(f"Error retrieving service requests: {service_requests_response.status_code}")

    # Get incident requests
    incidents_response = view_incidents(username, password, instance, "da1fc28a47ec1e106432b0da216d4308")
    
    if incidents_response.status_code == 200:
        incidents_data = incidents_response.json()
        if 'result' in incidents_data:
            print("\nIncident Requests:")
            print("------------------")
            for incident in incidents_data['result']:
                print(f"Incident Number: {incident['number']}")
                print(f"Description: {incident['description']}")
                print(f"State: {incident['state']}")
                print(f"Priority: {incident['priority']}")
                print(f"Opened: {incident['opened_at']}")
                print("------------------")
    else:
        print(f"Error retrieving incidents: {incidents_response.status_code}")

    # Get knowledge articles
    query = "How to reset my password"
    kb_response = get_kb(username, password, instance, query)
    
    if kb_response.status_code == 200:
        kb_data = kb_response.json()
        if 'result' in kb_data:
            print("\nKnowledge Articles Found:")
            print("------------------------")
            for article in kb_data['result']:
                print(f"Article Number: {article['number']}")
                print(f"Title: {article['short_description']}")
                print(f"Published: {article['published']}")
                print(f"Category ID: {article['kb_category']}")
                print(f"Knowledge Base ID: {article['kb_knowledge_base']}")
                print(f"Content: {article['text'][:200]}...")  # Show first 200 chars
                print("------------------------")

if __name__ == "__main__":
    main()
