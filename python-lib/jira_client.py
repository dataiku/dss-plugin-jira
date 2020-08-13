import requests
import copy
import logging
import json
import os
import jira_api

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
        self.connection_details = connection_details
        self.api_name = api_name
        self.api_url = self.normalize_url(connection_details.get("api_url", ""))
        self.server_type = connection_details.get("server_type", "cloud")
        self.username = connection_details.get("username", "")
        self.password = connection_details.get("token", "")
        self.subdomain = connection_details.get("subdomain")
        self.ignore_ssl_check = connection_details.get("ignore_ssl_check", False)
        self.site_url = self.get_site_url()
        self.next_page_url = None
        self.api = jira_api

    def normalize_url(self, url):
        url = os.path.join(url, '')
        return url

    def start_session(self, edge_name):
        self.edge_name = edge_name
        self.edge_descriptor = self.get_edge_descriptor(edge_name)
        self.formating = self.edge_descriptor.get(self.api.COLUMN_FORMATING, [])
        self.expanding = self.edge_descriptor.get(self.api.COLUMN_EXPANDING, [])
        self.cleaning = self.edge_descriptor.get(self.api.COLUMN_CLEANING, [])
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

    def get_url(self, edge_name, item_value, queue_id):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        api_url = edge_descriptor[self.api.API]
        return api_url.format(site_url=self.site_url, resource_name=self.get_resource_name(edge_name, item_value, queue_id))

    def get_resource_name(self, edge_name, item_value, queue_id):
        if item_value is not None:
            ressource_structure = self.get_ressource_structure(edge_name)
            args = {
                "edge_name": edge_name,
                "item_value": item_value,
                "queue_id": queue_id
            }
            return ressource_structure.format(**args)
        else:
            return "{}".format(edge_name)

    def get_ressource_structure(self, edge_name):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        return edge_descriptor[self.api.API_RESOURCE]

    def get_edge(self, edge_name, item_value, data, queue_id=None, expand=[], raise_exception=True):
        self.edge_name = edge_name
        query_string = self.get_query_string(edge_name, item_value, queue_id, expand)
        response = self.get(self.get_url(edge_name, item_value, queue_id) + query_string, data)
        if response.status_code >= 400:
            error_template = self.get_error_messages_template(edge_name, response.status_code)
            jira_error_message = self.get_jira_error_message(response)
            error_message = error_template.format(edge_name=edge_name,
                                                  item_value=item_value,
                                                  queue_id=queue_id,
                                                  status_code=response.status_code,
                                                  jira_error_message=jira_error_message)
            if raise_exception:
                raise Exception("{}".format(error_message))
            else:
                return [{"error": error_message}]

        data = response.json()
        self.update_next_page(data)
        return self.filter_data(data, edge_name, item_value)

    def get_query_string(self, edge_name, item_value, queue_id, expand=[]):
        query_string_dict = self.get_query_string_dict(edge_name)
        query_string_tokens = []
        for key in query_string_dict:
            query_string_template = query_string_dict[key]
            query_string_value = query_string_template.format(edge_name=edge_name, item_value=item_value, queue_id=queue_id, expand=",".join(expand))
            if query_string_value is not None and query_string_value != "" and query_string_value != "[]":
                query_string_tokens.append("{}={}".format(key, query_string_value))
        if len(query_string_tokens) > 0:
            return "?" + "&".join(query_string_tokens)
        else:
            return ""

    def get_query_string_dict(self, edge_name):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        query_string_template = edge_descriptor.get(self.api.API_QUERY_STRING, {})
        return query_string_template

    def get_jira_error_message(self, response):
        try:
            json = response.json()
            if self.api.API_ERROR_MESSAGES in json and len(json[self.api.API_ERROR_MESSAGES]) > 0:
                return json[self.api.API_ERROR_MESSAGES][0]
            else:
                return ""
        except Exception:
            return response.text

    def get_edge_descriptor(self, edge_name):
        edge_descriptor = copy.deepcopy(self.api.edge_descriptors[self.api.API_DEFAULT_DESCRIPTOR])
        if edge_name in self.api.edge_descriptors[self.api.API_EDGE_NAME]:
            update_dict(edge_descriptor, self.api.edge_descriptors[self.api.API_EDGE_NAME][edge_name])
        return edge_descriptor

    def filter_data(self, data, edge_name, item_value):
        filtering_key = self.get_data_filter_key(edge_name)
        if isinstance(filtering_key, list):
            if item_value == "":
                filtering_key = filtering_key[FILTERING_KEY_WITHOUT_PARAMETER]
            else:
                filtering_key = filtering_key[FILTERING_KEY_WITH_PARAMETER]
        if filtering_key is None:
            return self.arrayed(data)
        else:
            return self.arrayed(data[filtering_key])

    def format_data(self, data):
        for key in self.formating:
            path = self.formating[key]
            data[key] = self.extract(data, path)
        for key in self.expanding:
            data = self.expand(data, key)
        for key in self.cleaning:
            data.pop(key, None)
        return self.escape_json(data)

    def return_data(self, data):
        return self.escape_json(data)

    def escape_json(self, data):
        for key in data:
            if isinstance(data[key], dict) or isinstance(data[key], list):
                data[key] = json.dumps(data[key])
        return data

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

    def extract(self, main_dict, path):
        pointer = main_dict
        for element in path:
            if element in pointer:
                pointer = pointer.get(element)
            else:
                return None
        return pointer

    def get_data_filter_key(self, edge_name):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        if (self.api.API_RETURN in edge_descriptor) and (200 in edge_descriptor[self.api.API_RETURN]):
            key = edge_descriptor[self.api.API_RETURN][200]
        else:
            key = None
        return key

    def get_error_messages_template(self, edge_name, status_code):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        error_messages_template = self.api.edge_descriptors[self.api.API_DEFAULT_DESCRIPTOR][self.api.API_RETURN]
        if self.api.API_RETURN in edge_descriptor:
            update_dict(error_messages_template, edge_descriptor[self.api.API_RETURN])
        if status_code in error_messages_template:
            return error_messages_template[status_code]
        else:
            return "Error {status_code} - {jira_error_message}"

    def arrayed(self, data):
        if isinstance(data, list):
            return data
        else:
            return [data]

    def get(self, url, data=None):
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
        logger.info("Access Jira on endppoint {}".format(url))
        response = requests.get(url, **args)
        return response

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

    def update_next_page(self, data):
        if self.is_last_page(data):
            self.next_page_url = None
        else:
            if self.api.JIRA_PAGING in data and self.api.JIRA_NEXT in data[self.api.JIRA_PAGING]:
                self.next_page_url = data[self.api.JIRA_PAGING][self.api.JIRA_NEXT]
            elif self.api.JIRA_OPSGENIE_PAGING in data and self.api.JIRA_NEXT in data[self.api.JIRA_OPSGENIE_PAGING]:
                self.next_page_url = data[self.api.JIRA_OPSGENIE_PAGING][self.api.JIRA_NEXT]
            else:
                self.next_page_url = None

    def is_last_page(self, data):
        if self.is_opsgenie_api():
            return self.api.JIRA_OPSGENIE_PAGING not in data or self.api.JIRA_NEXT not in data[self.api.JIRA_OPSGENIE_PAGING]
        else:
            return (self.api.JIRA_IS_LAST_PAGE in data) and (data[self.api.JIRA_IS_LAST_PAGE])

    def get_next_page(self):
        logger.info("Loading next page")
        response = self.get(self.next_page_url)
        if response.status_code >= 400:
            error_message = self.get_error_messages_template(self.edge_name, response.status_code).format(edge_name=self.edge_name)
            raise Exception("{}".format(error_message))
        data = response.json()
        self.update_next_page(data)
        return self.filter_data(data, self.edge_name, None)

    def has_next_page(self):
        return self.next_page_url is not None


def update_dict(base_dict, extended_dict):
    for key, value in extended_dict.items():
        if isinstance(value, dict):
            base_dict[key] = update_dict(base_dict.get(key, {}), value)
        else:
            base_dict[key] = value
    return base_dict
