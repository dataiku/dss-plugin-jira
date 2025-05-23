import requests
import copy
import logging
import json
import os
import jira_api as api
from pagination import Pagination
from utils import extract_data_with_json_path

FILTERING_KEY_WITHOUT_PARAMETER = 0
FILTERING_KEY_WITH_PARAMETER = 1

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='jira plugin %(levelname)s - %(message)s')


class JiraClient(object):

    JIRA_SITE_URL = "https://{subdomain}.atlassian.net/"
    OPSGENIE_SITE_URL = "https://{subdomain}.opsgenie.com/"

    def __init__(self, connection_details, api_name="jira"):
        logger.info("JiraClient init")
        self.api_name = api_name
        self.api_url = normalize_url(connection_details.get("api_url", ""))
        self.server_type = connection_details.get("server_type", "cloud")
        self.username = connection_details.get("username", "")
        self.password = connection_details.get("token", "")
        self.subdomain = connection_details.get("subdomain")
        self.ignore_ssl_check = connection_details.get("ignore_ssl_check", False)
        self.site_url = self.get_site_url()
        self.params = {}
        self.pagination = Pagination()

    def start_session(self, endpoint_name):
        self.endpoint_name = endpoint_name
        self.endpoint_descriptor = self.get_endpoint_descriptor(endpoint_name)
        self.formating = self.endpoint_descriptor.get(api.COLUMN_FORMATING, [])
        self.expanding = self.endpoint_descriptor.get(api.COLUMN_EXPANDING, [])
        self.cleaning = self.endpoint_descriptor.get(api.COLUMN_CLEANING, [])
        if self.formating == [] and self.expanding == [] and self.cleaning == []:
            self.format = self.return_data
        else:
            self.format = self.format_data

    def get_site_url(self):
        if self.is_opsgenie_api():
            return self.OPSGENIE_SITE_URL.format(subdomain=self.subdomain)
        else:
            if self.server_type == "cloud":
                return self.JIRA_SITE_URL.format(subdomain=self.subdomain)
            else:
                return self.api_url

    def is_opsgenie_api(self):
        return self.api_name == "opsgenie"

    def get_url(self, endpoint_name, item_value, queue_id):
        api_url = self.endpoint_descriptor[api.API]
        return api_url.format(site_url=self.site_url, resource_name=self.get_resource_name(endpoint_name, item_value, queue_id))

    def get_resource_name(self, endpoint_name, item_value, queue_id):
        if item_value is not None:
            ressource_structure = self.get_ressource_structure()
            args = {
                "endpoint_name": endpoint_name,
                "item_value": item_value,
                "queue_id": queue_id
            }
            return ressource_structure.format(**args)
        else:
            return "{}".format(endpoint_name)

    def get_ressource_structure(self):
        return self.endpoint_descriptor[api.API_RESOURCE]

    def get_endpoint(self, endpoint_name, item_value, data, queue_id=None, expand=[], raise_exception=True):
        self.endpoint_name = endpoint_name
        self.params = self.get_params(endpoint_name, item_value, queue_id, expand)
        url = self.get_url(endpoint_name, item_value, queue_id)
        self.start_paging(counting_key=self.get_data_filter_key(), url=url)
        response = self.get(url, data, params=self.params)
        if response.status_code >= 400:
            self.pagination.set_error_flag(True)
            error_template = self.get_error_messages_template(response.status_code)
            jira_error_message = self.get_jira_error_message(response)
            error_message = error_template.format(endpoint_name=endpoint_name,
                                                  item_value=item_value,
                                                  queue_id=queue_id,
                                                  status_code=response.status_code,
                                                  jira_error_message=jira_error_message)
            if raise_exception:
                raise Exception("{}".format(error_message))
            else:
                return [{"error": error_message}]

        data = response.json()
        self.pagination.update_next_page(data)
        return self.filter_data(data, item_value)

    def start_paging(self, counting_key, url):
        pagination_config = self.get_pagination_config()
        self.pagination.configure_paging(pagination_config)
        self.pagination.reset_paging(counting_key=self.get_data_filter_key(), url=url)

    def get_params(self, endpoint_name, item_value, queue_id, expand=[]):
        ret = {}
        query_string_dict = self.get_query_string_dict()
        for key in query_string_dict:
            query_string_template = query_string_dict[key]
            query_string_value = query_string_template.format(endpoint_name=endpoint_name, item_value=item_value, queue_id=queue_id, expand=",".join(expand))
            ret.update({key: query_string_value})
        return ret

    def get_query_string_dict(self):
        query_string_template = self.endpoint_descriptor.get(api.API_QUERY_STRING, {})
        return query_string_template

    def get_pagination_config(self):
        pagination_config = self.endpoint_descriptor.get(api.PAGINATION, {})
        return pagination_config

    @staticmethod
    def get_jira_error_message(response):
        try:
            json = response.json()
            if api.API_ERROR_MESSAGES in json and len(json[api.API_ERROR_MESSAGES]) > 0:
                return json[api.API_ERROR_MESSAGES][0]
            else:
                return ""
        except Exception:
            return response.text

    def get_endpoint_descriptor(self, endpoint_name):
        endpoint_descriptor = copy.deepcopy(api.endpoint_descriptors[api.API_DEFAULT_DESCRIPTOR])
        if endpoint_name in api.endpoint_descriptors[api.ENDPOINTS]:
            update_dict(endpoint_descriptor, api.endpoint_descriptors[api.ENDPOINTS][endpoint_name])
        return endpoint_descriptor

    def filter_data(self, data, item_value):
        filtering_key = self.get_data_filter_key()
        if isinstance(filtering_key, list):
            if item_value == "":
                filtering_key = filtering_key[FILTERING_KEY_WITHOUT_PARAMETER]
            else:
                filtering_key = filtering_key[FILTERING_KEY_WITH_PARAMETER]
        if filtering_key is None:
            return arrayed(data)
        else:
            return arrayed(extract_data_with_json_path(data, filtering_key))

    def format_data(self, data):
        for key in self.formating:
            path = self.formating[key]
            data[key] = extract(data, path)
        for key in self.expanding:
            data = self.expand(data, key)
        for key in self.cleaning:
            data.pop(key, None)
        return escape_json(data)

    def return_data(self, data):
        return escape_json(data)

    def expand(self, dictionary, key_to_expand):
        if key_to_expand in dictionary:
            self.dig(dictionary, dictionary[key_to_expand], [key_to_expand])
            dictionary.pop(key_to_expand, None)
        return dictionary

    def dig(self, dictionary, element_to_expand, path_to_element):
        if not isinstance(element_to_expand, dict):
            dictionary["_".join(path_to_element)] = element_to_expand
        else:
            for key in element_to_expand:
                new_path = copy.deepcopy(path_to_element)
                new_path.append(key)
                self.dig(dictionary, element_to_expand[key], new_path)

    def get_data_filter_key(self):
        if (api.API_RETURN in self.endpoint_descriptor) and (200 in self.endpoint_descriptor[api.API_RETURN]):
            key = self.endpoint_descriptor[api.API_RETURN][200]
        else:
            key = None
        return key

    def get_error_messages_template(self, status_code):
        error_messages_template = api.endpoint_descriptors[api.API_DEFAULT_DESCRIPTOR][api.API_RETURN]
        if api.API_RETURN in self.endpoint_descriptor:
            update_dict(error_messages_template, self.endpoint_descriptor[api.API_RETURN])
        if status_code in error_messages_template:
            return error_messages_template[status_code]
        else:
            return "Error {status_code} - {jira_error_message}"

    def get(self, url, data=None, params=None):
        params = {} if params is None else params
        args = {}
        headers = self.get_headers()
        if headers is not None:
            args.update({"headers": headers})
        auth = self.get_auth()
        if auth is not None:
            args.update({"auth": auth})
        if data is not None:
            args.update({"data": data})
        if self.ignore_ssl_check:
            args.update({"verify": False})
        params.update(self.pagination.get_params())
        if params != {}:
            args.update({"params": params})
        logger.info("Access Jira on endppoint {}".format(url))
        response = requests.get(url, **args)
        return response

    def post(self, url, data=None, json=None, params=None):
        headers = self.get_headers()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        headers.pop('X-ExperimentalApi', None)
        auth = self.get_auth()
        response = requests.post(url, params=params, auth=auth, data=data, json=json, headers=headers)
        return response

    def create_issue(self, jira_project_key, summary, description, issue_type):
        issue_data = {
            'project': {'key': jira_project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type}
        }
        json = {
            "fields": issue_data,
        }
        # This data form does not work on v3
        url = "/".join([self.get_site_url(), "rest/api/2/issue"])
        response = self.post(url=url, json=json)
        json_response = response.json()
        return json_response

    def get_auth(self):
        if self.is_opsgenie_api():
            return None
        else:
            return (self.username, self.password)

    def get_headers(self):
        headers = {}
        headers["X-ExperimentalApi"] = "opt-in"
        if self.is_opsgenie_api():
            headers["Authorization"] = self.get_auth_headers()
        return headers

    def get_auth_headers(self):
        return "GenieKey {}".format(self.password)

    def get_next_page(self):
        logger.info("Loading next page")
        response = self.get(self.pagination.get_next_page_url(), params=self.params)
        if response.status_code >= 400:
            error_message = self.get_error_messages_template(response.status_code).format(endpoint_name=self.endpoint_name)
            raise Exception("{}".format(error_message))
        data = response.json()
        self.pagination.update_next_page(data)
        return self.filter_data(data, None)


def update_dict(base_dict, extended_dict):
    for key, value in extended_dict.items():
        if isinstance(value, dict):
            base_dict[key] = update_dict(base_dict.get(key, {}), value)
        else:
            base_dict[key] = value
    return base_dict


def normalize_url(url):
    url = os.path.join(url, '')
    return url


def extract(main_dict, path):
    pointer = main_dict
    for element in path:
        if element in pointer:
            pointer = pointer.get(element)
        else:
            return None
    return pointer


def escape_json(data):
    for key in data:
        if isinstance(data[key], dict) or isinstance(data[key], list):
            data[key] = json.dumps(data[key])
    return data


def arrayed(data):
    if isinstance(data, list):
        return data
    else:
        return [data]
