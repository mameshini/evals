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
    encoded_query = f"textLIKEreset password^kb_category NOT LIKEInternal Use^kb_category NOT LIKELanguage Operations^kb_knowledge_base LIKEKnowledge"
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

def print_requests(username, password, instance, email):
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

def print_kb_articles(username, password, instance):
    # Get knowledge articles
    query = "password"
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


it_categories = [
    "AMIE",
    "Add Access",
    "Automation (Kofax/RPA)",
    "Azure",
    "Business Application Lifecycle Management",
    "Dashboards",
    "Deskside Support",
    "Enterprise Applications",
    "Great Plains",
    "General",
    "",
    "IT",
    "IT - Enhancement/Operational Initiatives",
    "IT Asset Offboarding",
    "IT Security",
    "IT Training",
    "Network and Telecom",
    "Non-Peoplesoft Database",
    "PeopleNet",
    "PeopleSoft",
    "PeopleSoft Database",
    "PowerBI",
    "QA",
    "Salesforce",
    "ServiceNow",
    "Standard Changes",
    "VMS Requests for MSP"
    "Support"
]

def search_catalog_items(username, password, instance, description):
    import csv

    search_terms = description.split()
    query_conditions = []
    
    for term in search_terms:
        query_conditions.append(f'descriptionLIKE%{term}')
    encoded_query = f'active=true',
    
    query_params = {
        'sysparm_display_value': 'true',
        'sysparm_exclude_reference_link': 'true',
        'sysparm_query': encoded_query,
        'sysparm_fields': 'name,short_description,description,sys_id,category,score',
        'sysparm_limit': '10000'
    }

    url = f"https://{instance}.service-now.com/api/now/table/sc_cat_item"
    response = requests.get(
        url,
        auth=(username, password),
        params=query_params,
        headers={'Accept': 'application/json'}
    )
    
    if response.status_code == 200:
        items = response.json()
        if 'result' in items:
            # Create a set of unique categories
            unique_categories = {item['category'] for item in items['result'] if item['category']}
            
            print("\nUnique Categories:")
            print("------------------")
            for category in sorted(unique_categories):
                print(category)
            print("------------------")
            print(f"Total unique categories: {len(unique_categories)}")
    else:
        print(f"Error searching catalog items: {response.status_code}")

    if response.status_code == 200:
        items = response.json()
        if 'result' in items:
            print("\nMatching Catalog Items:")
            print("------------------------")
            for item in items['result']:
                if item['category'] in it_categories:
                    if item['category'] == "" and 'Access' not in item['name']:
                                            continue
                    print(f"Name: {item['name']}")
                    print(f"Description: {item['short_description']}")
                    print(f"Category: {item['category']}")
                    # Generate direct URL to catalog item
                    item_url = f"https://{instance}.service-now.com/sp?id=sc_cat_item&sys_id={item['sys_id']}"
                    print(f"Request URL: {item_url}")
                    print("------------------------")
    else:
        print(f"Error searching catalog items: {response.status_code}")
    
    ## Save catalog items to a file in CSV format includiong the name, short description, category and URL
    if response.status_code == 200 and 'result' in items:
        with open('catalog_items.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Description', 'Category', 'URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in items['result']:
                if item['category'] in it_categories:
                    if item['category'] == "" and 'Access' not in item['name']:
                        continue
                    item_url = f"https://{instance}.service-now.com/sp?id=sc_cat_item&sys_id={item['sys_id']}"
                    writer.writerow({
                        'Name': item['name'],
                        'Description': item['short_description'],
                        'Category': item['category'],
                        'URL': item_url
                    })
    
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

    print("\nSearching catalog items...")
    search_description = ""  # Example search term
    search_catalog_items(username, password, instance, search_description)


if __name__ == "__main__":
    main()
