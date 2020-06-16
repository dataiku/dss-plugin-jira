import requests
import copy
import logging
import json
import os

JIRA_CORE_URL = "{site_url}rest/api/3/{resource_name}"
JIRA_SERVICE_DESK_URL = "{site_url}rest/servicedeskapi/{resource_name}"
JIRA_SOFTWARE_URL = "{site_url}rest/agile/1.0/{resource_name}"
JIRA_OPSGENIE_URL = "api.opsgenie.com/{resource_name}"
JIRA_SERVICE_DESK_ID_404 = "Service Desk ID {item_value} does not exists"
JIRA_BOARD_ID_404 = "Board {item_value} does not exists or the user does not have permission to view it."
JIRA_LICENSE_403 = "The user does not a have valid license"
JIRA_OPSGENIE_402 = "The account cannot do this action because of subscription plan"
API_DEFAULT_DESCRIPTOR = "default"
API_EDGE_NAME = "edge_name"
API_RETURN = "on_return"
API_RESOURCE = "resource_name"
API = "api"
API_QUERY_STRING = "query_string"
JIRA_IS_LAST_PAGE = "isLastPage"
JIRA_OPSGENIE_PAGING = "paging"
JIRA_PAGING = "_links"
JIRA_NEXT = "next"
API_ERROR_MESSAGES = "errorMessages"
COLUMN_FORMATING = "column_formating"
COLUMN_CLEANING = "column_cleaning"
COLUMN_EXPANDING = "column_expending"
ITEM_VALUE = "{item_value}"
DEFAULT_COLUMNS_TO_EXPAND = ["changelog", "fields", "renderedFields", "names", "schema", "operations", "editmeta", "versionedRepresentations"]

# OAuth
# https://your-domain.atlassian.net/{api} to https://api.atlassian.com/ex/jira/{cloudid}/{api}.
# https://your-domain.atlassian.net/rest/{type}/{version}/{operation} with https://api.atlassian.com/jira/{type}/{version}/cloud/{cloudId}/{operation}

jira_api = {
    API_DEFAULT_DESCRIPTOR: {
        API_RESOURCE: "{edge_name}/{item_value}",
        API: JIRA_CORE_URL,
        API_RETURN: {
            200: None,
            401: "The user is not logged in",
            403: "The user does not have permission to complete this request",
            404: "Not found",
            500: "Jira Internal Server Error"
        },
        COLUMN_EXPANDING: DEFAULT_COLUMNS_TO_EXPAND
    },
    "edge_name": {
        "issue": {
            API_QUERY_STRING: {"expand": "{expand}"}
        },
        "issue/createmeta": {
            API_RESOURCE: "{edge_name}",
            API_RETURN: {
                200: "projects"
            }
        },
        "dashboard": {API_RETURN: {200: ["dashboards", None]}},
        "dashboard/search": {API_RETURN: {200: "values"}},
        "group": {
            API_RESOURCE: "{edge_name}/member",
            API_QUERY_STRING: {"groupname": ITEM_VALUE},
            API_RETURN: {200: "values"}
        },
        "field": {
            API_RESOURCE: "{edge_name}",
        },
        "search": {
            API_RESOURCE: "search",
            API_QUERY_STRING: {"jql": ITEM_VALUE, "expand": "{expand}"},
            API_RETURN: {
                200: "issues"
            }
        },
        "worklog/list": {
            API_RESOURCE: "issue/{item_value}/worklog",
        },
        "worklog/deleted": {},
        "organization": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "organization",
            API_RETURN: {
                200: "values",
                404: "Organization ID {item_value} does not exists"
            }
        },
        "organization/user": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "organization/{item_value}/user",
            API_RETURN: {
                200: "values",
                404: "Organization ID {item_value} does not exists"
            }
        },
        "servicedesk/organization": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/organization",
            API_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "request": {
            API: JIRA_SERVICE_DESK_URL,
            API_RETURN: {
                200: ["values", None]
            }
        },
        "servicedesk": {
            API: JIRA_SERVICE_DESK_URL,
            API_RETURN: {
                200: ["values", None],
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "servicedesk/customer": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/customer",
            API_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "servicedesk/queue": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/queue",
            API_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "servicedesk/queue/issue": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/queue/{queueId}/issue",
            API_RETURN: {
                200: "values",
                404: "Service Desk ID {item_value} or queue ID {queueId} do not exist"
            }
        },
        "board": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board",
            API_RETURN: {
                200: "values",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/epic": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/epic",
            API_RETURN: {
                200: "values",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/issue": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/issue",
            API_RETURN: {
                200: "issues",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/backlog": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/backlog",
            API_RETURN: {
                200: "issues",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/epic/none/issue": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/epic/none/issue",
            API_RETURN: {
                200: "issues",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/project": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/project",
            API_RETURN: {
                200: "values"
            }
        },
        "board/project/full": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/project/full",
            API_RETURN: {
                200: "values",
                403: JIRA_LICENSE_403
            }
        },
        "board/sprint": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/sprint",
            API_RETURN: {
                200: "values",
                403: JIRA_LICENSE_403
            }
        },
        "board/version": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/version",
            API_RETURN: {
                200: "values",
                403: JIRA_LICENSE_403
            }
        },
        "epic/none/issue": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "epic/none/issue",
            API_RETURN: {
                200: "issues"
            }
        },
        "alerts": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v2/alerts",
            API_QUERY_STRING: {
                "query": ITEM_VALUE
            },
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            },
            COLUMN_FORMATING: {
                "integration_type": ["integration", "type"],
                "integration_id": ["integration", "id"],
                "integration_name": ["integration", "name"]
            },
            COLUMN_CLEANING: ["integration"]
        },
        "incidents": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v1/incidents",
            API_QUERY_STRING: {
                "query": ITEM_VALUE
            },
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        },
        "users": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v2/users",
            API_QUERY_STRING: {
                "query": ITEM_VALUE
            },
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            },
            COLUMN_FORMATING: {
                "country": ["userAddress", "country"],
                "state": ["userAddress", "state"],
                "line": ["userAddress", "line"],
                "zip_code": ["userAddress", "zipCode"],
                "city": ["userAddress", "city"],
                "role": ["role", "id"]
            },
            COLUMN_CLEANING: ["userAddress"]
        },
        "teams": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v2/teams",
            API_QUERY_STRING: {
                "query": ITEM_VALUE
            },
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            },
            COLUMN_EXPANDING: DEFAULT_COLUMNS_TO_EXPAND.append("links")
        },
        "schedules": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v2/schedules",
            API_QUERY_STRING: {
                "query": ITEM_VALUE
            },
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        },
        "escalations": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v2/escalations",
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        },
        "services": {
            API: JIRA_OPSGENIE_URL,
            API_RESOURCE: "v1/services",
            API_QUERY_STRING: {"query": ITEM_VALUE},
            API_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        }
    }
}

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

    def normalize_url(self, url):
        url = os.path.join(url, '')
        return url

    def start_session(self, edge_name):
        self.edge_name = edge_name
        self.edge_descriptor = self.get_edge_descriptor(edge_name)
        self.formating = self.edge_descriptor.get(COLUMN_FORMATING, [])
        self.expanding = self.edge_descriptor.get(COLUMN_EXPANDING, [])
        self.cleaning = self.edge_descriptor.get(COLUMN_CLEANING, [])
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

    def get_url(self, edge_name, item_value, queueId):
        EDGE_DESCRIPTOR = self.get_edge_descriptor(edge_name)
        API_URL = EDGE_DESCRIPTOR[API]
        return API_URL.format(site_url=self.site_url, resource_name=self.get_resource_name(edge_name, item_value, queueId))

    def get_resource_name(self, edge_name, item_value, queueId):
        if item_value is not None:
            ressource_structure = self.get_ressource_structure(edge_name)
            args = {
                "edge_name": edge_name,
                "item_value": item_value,
                "queueId": queueId
            }
            return ressource_structure.format(**args)
        else:
            return "{}".format(edge_name)

    def get_ressource_structure(self, edge_name):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        return edge_descriptor[API_RESOURCE]

    def get_edge(self, edge_name, item_value, data, queue_id=None, expand=[]):
        self.edge_name = edge_name
        query_string = self.get_query_string(edge_name, item_value, queue_id, expand)
        response = self.get(self.get_url(edge_name, item_value, queue_id) + query_string, data)
        if response.status_code >= 400:
            error_template = self.get_error_messages_template(edge_name, response.status_code)
            jira_error_message = self.get_jira_error_message(response)
            error_message = error_template.format(edge_name=edge_name,
                                                  item_value=item_value,
                                                  queueId=queue_id,
                                                  status_code=response.status_code,
                                                  jira_error_message=jira_error_message)
            raise Exception("{}".format(error_message))

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
        query_string_template = edge_descriptor.get(API_QUERY_STRING, {})
        return query_string_template

    def get_jira_error_message(self, response):
        try:
            json = response.json()
            if API_ERROR_MESSAGES in json and len(json[API_ERROR_MESSAGES]) > 0:
                return json[API_ERROR_MESSAGES][0]
            else:
                return ""
        except Exception:
            return response.text

    def get_edge_descriptor(self, edge_name):
        edge_descriptor = copy.deepcopy(jira_api[API_DEFAULT_DESCRIPTOR])
        if edge_name in jira_api[API_EDGE_NAME]:
            update_dict(edge_descriptor, jira_api[API_EDGE_NAME][edge_name])
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
        if (API_RETURN in edge_descriptor) and (200 in edge_descriptor[API_RETURN]):
            key = edge_descriptor[API_RETURN][200]
        else:
            key = None
        return key

    def get_error_messages_template(self, edge_name, status_code):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        error_messages_template = jira_api[API_DEFAULT_DESCRIPTOR][API_RETURN]
        if API_RETURN in edge_descriptor:
            update_dict(error_messages_template, edge_descriptor[API_RETURN])
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
            if JIRA_PAGING in data and JIRA_NEXT in data[JIRA_PAGING]:
                self.next_page_url = data[JIRA_PAGING][JIRA_NEXT]
            elif JIRA_OPSGENIE_PAGING in data and JIRA_NEXT in data[JIRA_OPSGENIE_PAGING]:
                self.next_page_url = data[JIRA_OPSGENIE_PAGING][JIRA_NEXT]
            else:
                self.next_page_url = None

    def is_last_page(self, data):
        if self.is_opsgenie_api():
            return JIRA_OPSGENIE_PAGING not in data or JIRA_NEXT not in data[JIRA_OPSGENIE_PAGING]
        else:
            return (JIRA_IS_LAST_PAGE in data) and (data[JIRA_IS_LAST_PAGE])

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
