import requests
import copy
import logging

JIRA_CORE_URL = "https://{site_url}/rest/api/3/{resource_name}"
JIRA_SERVICE_DESK_URL = "https://{site_url}/rest/servicedeskapi/{resource_name}"
JIRA_SOFTWARE_URL = "https://{site_url}/rest/agile/1.0/{resource_name}"
JIRA_SERVICE_DESK_ID_404 = "Service Desk ID {item_value} does not exists"
JIRA_BOARD_ID_404 = "Board {item_value} does not exists or the user does not have permission to view it."
JIRA_LICENSE_403 = "The user does not a have valid license"
JIRA_DEFAULT_DESCRIPTOR = "default"
JIRA_EDGE_NAME = "edge_name"
JIRA_RETURN = "on_return"
JIRA_RESOURCE = "resource_name"
JIRA_API = "api"
JIRA_IS_LAST_PAGE = "isLastPage"

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
        "group": {JIRA_RETURN: {200: "users"}},
        "field": {
            JIRA_RESOURCE: "{edge_name}",
        },
        "jql/match": {JIRA_RETURN: {200: "matches"}},
        "search": {JIRA_RETURN: {200: "issues"}},
        "worklog/list": {},
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
            }
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

    def __init__(self, connection_details):
        logger.info("JiraClient init")
        self.connection_details = connection_details
        self.username = connection_details.get("username", "")
        self.password = connection_details.get("token", "")
        self.subdomain = connection_details.get("subdomain")
        self.site_url = self.get_site_url()
        self.next_page_url = None

    def get_site_url(self):
        return self.JIRA_SITE_URL.format(subdomain=self.subdomain)

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
        response = self.get(self.get_url(edge_name, item_value, queue_id), data)
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

    def get_jira_error_message(self, response):
        json = response.json()
        if "errorMessages" in json and len(json['errorMessages']) > 0:
            return json['errorMessages'][0]
        else:
            return ""

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
        headers = {}
        headers["X-ExperimentalApi"] = "opt-in"
        response = requests.get(url, auth=(self.username, self.password), data=data, headers=headers)
        return response

    def update_next_page(self, data):
        if self.is_last_page(data):
            self.next_page_url = None
        else:
            if "_links" in data and "next" in data["_links"]:
                self.next_page_url = data["_links"]["next"]
            else:
                self.next_page_url = None

    def is_last_page(self, data):
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
