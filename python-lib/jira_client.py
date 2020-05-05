import requests
import copy
import logging

JIRA_CORE_URL = "https://{site_url}/rest/api/3/{resource_name}"
JIRA_SERVICE_DESK_URL = "https://{site_url}/rest/servicedeskapi/{resource_name}"
JIRA_SOFTWARE_URL = "https://{site_url}/rest/agile/1.0/{resource_name}"
JIRA_OPSGENIE_URL = "https://api.opsgenie.com/{resource_name}"
JIRA_SERVICE_DESK_ID_404 = "Service Desk ID {item_value} does not exists"
JIRA_BOARD_ID_404 = "Board {item_value} does not exists or the user does not have permission to view it."
JIRA_LICENSE_403 = "The user does not a have valid license"
JIRA_OPSGENIE_402 = "The account cannot do this action because of subscription plan"
JIRA_DEFAULT_DESCRIPTOR = "default"
JIRA_EDGE_NAME = "edge_name"
JIRA_RETURN = "on_return"
JIRA_RESOURCE = "resource_name"
JIRA_API = "api"
JIRA_IS_LAST_PAGE = "isLastPage"
JIRA_QUERY_STRING = "query_string"
JIRA_OPSGENIE_PAGING = "paging"
JIRA_PAGING = "_links"
JIRA_NEXT = "next"
JIRA_ERROR_MESSAGES = "errorMessages"
COLUMN_FORMATING = "column_formating"
COLUMN_CLEANING = "column_cleaning"
COLUMN_EXPANDING = "column_expending"

# OAuth
# https://your-domain.atlassian.net/{api} to https://api.atlassian.com/ex/jira/{cloudid}/{api}.
# https://your-domain.atlassian.net/rest/{type}/{version}/{operation} with https://api.atlassian.com/jira/{type}/{version}/cloud/{cloudId}/{operation}

jira_api = {
    JIRA_DEFAULT_DESCRIPTOR: {
        JIRA_RESOURCE: "{edge_name}/{item_value}",
        JIRA_API: JIRA_CORE_URL,
        JIRA_RETURN: {
            200: None,
            401: "The user is not logged in",
            403: "The user does not have permission to complete this request",
            404: "Not found",
            500: "Jira Internal Server Error"
        }
    },
    "edge_name": {
        "issue": {},
        "issue/createmeta": {
            JIRA_RESOURCE: "{edge_name}",
            JIRA_RETURN: {
                200: "projects"
            }
        },
        "dashboard": {JIRA_RETURN: {200: ["dashboards", None]}},
        "dashboard/search": {JIRA_RETURN: {200: "values"}},
        "group": {
            JIRA_RESOURCE: "{edge_name}/member",
            JIRA_QUERY_STRING: {"groupname": "{item_value}"},
            JIRA_RETURN: {200: "values"}
        },
        "field": {
            JIRA_RESOURCE: "{edge_name}",
        },
        "search": {
            JIRA_RESOURCE: "search",
            JIRA_QUERY_STRING: {"jql": "{item_value}"},
            JIRA_RETURN: {
                200: "issues"
            }
        },
        "worklog/list": {
            JIRA_RESOURCE: "issue/{item_value}/worklog",
        },
        "worklog/deleted": {},
        "organization": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RETURN: {
                200: ["values", None],
                404: "Organization ID {item_value} does not exists"
            }
        },
        "organization/user": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RESOURCE: "organization/{item_value}/user",
            JIRA_RETURN: {
                200: ["values", None],
                404: "Organization ID {item_value} does not exists"
            }
        },
        "servicedesk/organization": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RESOURCE: "servicedesk/{item_value}/organization",
            JIRA_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "request": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RETURN: {
                200: ["values", None]
            }
        },
        "servicedesk": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RETURN: {
                200: ["values", None],
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "servicedesk/customer": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RESOURCE: "servicedesk/{item_value}/customer",
            JIRA_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "servicedesk/queue": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RESOURCE: "servicedesk/{item_value}/queue",
            JIRA_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            }
        },
        "servicedesk/queue/issue": {
            JIRA_API: JIRA_SERVICE_DESK_URL,
            JIRA_RESOURCE: "servicedesk/{item_value}/queue/{queueId}/issue",
            JIRA_RETURN: {
                200: "values",
                404: "Service Desk ID {item_value} or queue ID {queueId} do not exist"
            },
            COLUMN_EXPANDING: ["fields"]
        },
        "board": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board",
            JIRA_RETURN: {
                200: "values",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/epic": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/epic",
            JIRA_RETURN: {
                200: "values",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/issue": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/issue",
            JIRA_RETURN: {
                200: "issues",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/backlog": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/backlog",
            JIRA_RETURN: {
                200: "issues",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/epic/none/issue": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/epic/none/issue",
            JIRA_RETURN: {
                200: "issues",
                404: JIRA_BOARD_ID_404
            }
        },
        "board/project": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/project",
            JIRA_RETURN: {
                200: "values"
            }
        },
        "board/project/full": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/project/full",
            JIRA_RETURN: {
                200: "values",
                403: JIRA_LICENSE_403
            }
        },
        "board/sprint": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/sprint",
            JIRA_RETURN: {
                200: "values",
                403: JIRA_LICENSE_403
            }
        },
        "board/version": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "board/{item_value}/version",
            JIRA_RETURN: {
                200: "values",
                403: JIRA_LICENSE_403
            }
        },
        "epic/none/issue": {
            JIRA_API: JIRA_SOFTWARE_URL,
            JIRA_RESOURCE: "epic/none/issue",
            JIRA_RETURN: {
                200: "issues"
            }
        },
        "alerts": {
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v2/alerts",
            JIRA_QUERY_STRING: {
                "query": "{item_value}"
            },
            JIRA_RETURN: {
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
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v1/incidents",
            JIRA_QUERY_STRING: {
                "query": "{item_value}"
            },
            JIRA_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        },
        "users": {
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v2/users",
            JIRA_QUERY_STRING: {
                "query": "{item_value}"
            },
            JIRA_RETURN: {
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
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v2/teams",
            JIRA_QUERY_STRING: {
                "query": "{item_value}"
            },
            JIRA_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            },
            COLUMN_EXPANDING: ["links"]
        },
        "schedules": {
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v2/schedules",
            JIRA_QUERY_STRING: {
                "query": "{item_value}"
            },
            JIRA_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        },
        "escalations": {
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v2/escalations",
            JIRA_RETURN: {
                200: "data",
                402: JIRA_OPSGENIE_402
            }
        },
        "services": {
            JIRA_API: JIRA_OPSGENIE_URL,
            JIRA_RESOURCE: "v1/services",
            JIRA_QUERY_STRING: {"query": "{item_value}"},
            JIRA_RETURN: {
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

    JIRA_SITE_URL = "{subdomain}.atlassian.net"
    OPSGENIE_SITE_URL = "{subdomain}.opsgenie.com"

    def __init__(self, connection_details, api_name="jira"):
        logger.info("JiraClient init")
        self.connection_details = connection_details
        self.api_name = api_name
        self.username = connection_details.get("username", "")
        self.password = connection_details.get("token", "")
        self.subdomain = connection_details.get("subdomain")
        self.site_url = self.get_site_url()
        self.next_page_url = None

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
            return self.JIRA_SITE_URL.format(subdomain=self.subdomain)

    def is_opsgenie_api(self):
        return self.api_name == "opsgenie"

    def get_url(self, edge_name, item_value, queueId):
        EDGE_DESCRIPTOR = self.get_edge_descriptor(edge_name)
        API_URL = EDGE_DESCRIPTOR[JIRA_API]
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
        return edge_descriptor[JIRA_RESOURCE]

    def get_edge(self, edge_name, item_value, data, queue_id=None):
        self.edge_name = edge_name
        query_string = self.get_query_string(edge_name, item_value, queue_id)
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

    def get_query_string(self, edge_name, item_value, queue_id):
        query_string_dict = self.get_query_string_dict(edge_name)
        query_string_tokens = []
        for key in query_string_dict:
            query_string_template = query_string_dict[key]
            query_string_value = query_string_template.format(edge_name=edge_name, item_value=item_value, queue_id=queue_id)
            query_string_tokens.append("{}={}".format(key, query_string_value))
        if len(query_string_tokens) > 0:
            return "?" + "&".join(query_string_tokens)
        else:
            return ""

    def get_query_string_dict(self, edge_name):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        query_string_template = edge_descriptor.get(JIRA_QUERY_STRING, {})
        return query_string_template

    def get_jira_error_message(self, response):
        try:
            json = response.json()
            if JIRA_ERROR_MESSAGES in json and len(json[JIRA_ERROR_MESSAGES]) > 0:
                return json[JIRA_ERROR_MESSAGES][0]
            else:
                return ""
        except Exception:
            return response.text

    def get_edge_descriptor(self, edge_name):
        edge_descriptor = copy.deepcopy(jira_api[JIRA_DEFAULT_DESCRIPTOR])
        if edge_name in jira_api[JIRA_EDGE_NAME]:
            update_dict(edge_descriptor, jira_api[JIRA_EDGE_NAME][edge_name])
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
        return data

    def return_data(self, data):
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
        if (JIRA_RETURN in edge_descriptor) and (200 in edge_descriptor[JIRA_RETURN]):
            key = edge_descriptor[JIRA_RETURN][200]
        else:
            key = None
        return key

    def get_error_messages_template(self, edge_name, status_code):
        edge_descriptor = self.get_edge_descriptor(edge_name)
        error_messages_template = jira_api[JIRA_DEFAULT_DESCRIPTOR][JIRA_RETURN]
        if JIRA_RETURN in edge_descriptor:
            update_dict(error_messages_template, edge_descriptor[JIRA_RETURN])
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
