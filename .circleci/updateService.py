import requests
import sys
import json
import os

# Base-URL of TSI HMCM Service
base_url = "https://srv01.dev.mcm.t-systems-service.com"

def login_HMCM():
    # Body includes credentials to log-in to HMCM platform
    body = {'email': os.environ['USER_MAIL'],'password': os.environ['USER_PASSWD']}
    # Send a request to the login endpoint of HMCM platform
    login_request = requests.post(base_url + "/api/v1/catalog/login", json = body)
    # For successful API call, response code will be 200 (OK)
    if(login_request.ok):
        # Parse responce body
        loginData = login_request.json()
        # Return login token
        return loginData['token']
    else:
      # If response code is not ok (200), print the resulting http error code with description
        raise Exception('Login Failed:' + str(login_request.status_code))

def updateService(auth_token):
    # Load service.json file to get description of service
    with open('service.json') as service_description:
        service = json.load(service_description)
    # Prepare request body to update service. Most of the parameters are identical to the service.json file.
    # However, we need to inject the repo link and branch from CircleCI environment variables
    body = {'name': service['name'],'version': service['version'],'description': service['description'],'sourceurl': os.environ['REPO'],'branchtag': os.environ['BRANCH']}
    # Update an existing service, identified by the serviceID in service.json. This method requires a valid auth token which was created in the login_HMCM() function
    update_request = requests.put(base_url + "/api/v1/catalog/service/" + service['serviceid'], headers={'Authorization': 'Bearer ' + auth_token}, json = body)
    # For successful API call, response code will be 200 (OK)
    if(update_request.ok):
        # Parse responce body
        updateData = update_request.json()
        print(updateData)
        # Return login token
        return {"serviceid": service['serviceid'], "landscapeid": service['landscapeid'], "serviceVersionid": service['version']}
    else:
      # If response code is not ok (200), print the resulting http error code with description
        raise Exception('ServiceUpdate Failed:' + str(update_request.status_code))

def createPublication(auth_token, serviceData):
    # Send request to create a new publication of the updated service, the JSON body was already prepared by the updateService() function
    publication_request = requests.post(base_url + "/api/v1/catalog/publish", headers={'Authorization': 'Bearer ' + auth_token}, json = serviceData)
    # For successful API call, response code will be 200 (OK)
    if(publication_request.ok):
        return publication_request.ok
    else:
      # If response code is not ok (200), print the resulting http error code with description
        raise Exception('Publication Failed:' + str(publication_request.status_code))


# Execute functions
token = login_HMCM()
serviceData = updateService(token)
publication = createPublication(token, serviceData),
sys.exit()
