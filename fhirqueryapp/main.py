# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_flex_storage_app]
import logging
import os

from flask import Flask, request
#from google.cloud import storage
#google-api-python-client

from google.auth import app_engine
from google.auth.transport import requests
from google.oauth2 import service_account
app = Flask(__name__)


# Configure this environment variable via app.yaml
#CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

from model import InputForm
from flask import Flask, render_template, request
import sys
import json
# [START healthcare_get_session]
def get_session():
    """Creates an authorized Requests Session."""

    # Explicitly use App Engine credentials. These credentials are
    # only available when running on App Engine Standard.
    credentials = app_engine.Credentials()

    # Explicitly use Compute Engine credentials. These credentials are
    # available on Compute Engine, App Engine Flexible, and Container Engine.
    session = requests.AuthorizedSession(credentials)

    return session

if 0:
    def get_session():
      """Returns an authorized API client by discovering the Healthcare API and
      creating a service object using the service account credentials JSON."""
      api_scopes = ['https://www.googleapis.com/auth/cloud-platform']
      api_version = 'v1beta1'
      discovery_api = 'https://healthcare.googleapis.com/$discovery/rest'
      service_name = 'healthcare'

      credentials = service_account.Credentials.from_service_account_file(
        service_account_json)
      scoped_credentials = credentials.with_scopes(api_scopes)

      discovery_url = '{}?labels=CHC_BETA&version={}'.format(
         discovery_api, api_version)

      return discovery.build(
        service_name,
        api_version,
        discoveryServiceUrl=discovery_url,
        credentials=scoped_credentials)

def get_resource(
    base_url,
    project_id,
    cloud_region,
    dataset_id,
    fhir_store_id,
    resource_type,
    resource_id,
):
    """Gets a FHIR resource."""
    url = "{}/projects/{}/locations/{}".format(base_url, project_id, cloud_region)

    resource_path = "{}/datasets/{}/fhirStores/{}/fhir/{}/{}".format(
        url, dataset_id, fhir_store_id, resource_type, resource_id
    )

    # Make an authenticated API request
    session = get_session()

    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}
    print("url is :{}".format(resource_path))
    response = session.get(resource_path, headers=headers)
    response.raise_for_status()

    resource = response.json()

    print("Got {} resource:".format(resource["resourceType"]))
    print(json.dumps(resource, indent=2))

    return resource

base_url = os.environ['BASE_URL']
project_id = os.environ['PROJECT_ID']
cloud_region = os.environ['REGION']
dataset_id = os.environ['DATASET_ID']
fhir_store_id = os.environ['FHIR_STORE_ID']


def queryHCapi(resource_id, resource_type):
    print("PatientId {}".format( resource_id ))
    print("ResourceType {}".format(resource_type))
    resource  = get_resource(
      base_url,
      project_id,
      cloud_region,
      dataset_id,
      fhir_store_id,
      resource_type,
      resource_id)
    return resource
#   return "Query Success"


app = Flask(__name__)

template_name = 'queryform'
@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    types = ['Patient', 'Encounter', 'Observation']

    if request.method == 'POST' and form.validate():
        print("Querying hcapi")
        result = queryHCapi(form.patientId.data, form.resourceType.data)
    else:
        print("None")
        result = None

    return render_template(template_name + '.html',
                           dropdown = types, form=form, result=result)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
