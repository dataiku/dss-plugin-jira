API = "api"
API_DEFAULT_DESCRIPTOR = "default"
API_ERROR_MESSAGES = "errorMessages"
API_QUERY_STRING = "query_string"
API_RESOURCE = "resource_name"
API_RETURN = "on_return"
COLUMN_FORMATING = "column_formating"
COLUMN_CLEANING = "column_cleaning"
COLUMN_EXPANDING = "column_expending"
DEFAULT_COLUMNS_TO_EXPAND = ["changelog", "fields", "renderedFields", "names", "schema", "operations", "editmeta", "versionedRepresentations"]
ENDPOINTS = "endpoints"
ITEM_VALUE = "{item_value}"
JIRA_BOARD_ID_404 = "Board {item_value} does not exists or the user does not have permission to view it."
JIRA_CORE_PAGINATION = {
    "skip_key": "startAt",
    "limit_key": "maxResults",
    "total_key": "total"
}
JIRA_CORE_URL = "{site_url}rest/api/3/{resource_name}"
JIRA_IS_LAST_PAGE = "isLastPage"
JIRA_LICENSE_403 = "The user does not a have valid license"
JIRA_NEXT = "next"
JIRA_OPSGENIE_402 = "The account cannot do this action because of subscription plan"
JIRA_OPSGENIE_PAGING = "paging"
JIRA_OPSGENIE_URL = "api.opsgenie.com/{resource_name}"
JIRA_PAGING = "_links"
JIRA_SERVICE_DESK_ID_404 = "Service Desk ID {item_value} does not exists"
JIRA_SERVICE_DESK_PAGINATION = {
    "next_page_key": ["_links", "next"]
}
JIRA_SERVICE_DESK_URL = "{site_url}rest/servicedeskapi/{resource_name}"
JIRA_SOFTWARE_URL = "{site_url}rest/agile/1.0/{resource_name}"
PAGINATION = "pagination"

endpoint_descriptors = {
    API_DEFAULT_DESCRIPTOR: {
        API_RESOURCE: "{endpoint_name}/{item_value}",
        API: JIRA_CORE_URL,
        API_RETURN: {
            200: None,
            401: "The user is not logged in",
            403: "The user does not have permission to complete this request",
            404: "Item {item_value} not found",
            500: "Jira Internal Server Error"
        },
        COLUMN_EXPANDING: DEFAULT_COLUMNS_TO_EXPAND,
        PAGINATION: JIRA_CORE_PAGINATION
    },
    ENDPOINTS: {
        "dashboard": {API_RETURN: {200: ["dashboards", None]}},
        "dashboard/search": {API_RETURN: {200: "values"}},
        "field": {
            API_RESOURCE: "{endpoint_name}",
        },
        "group": {
            API_RESOURCE: "{endpoint_name}/member",
            API_QUERY_STRING: {"groupname": ITEM_VALUE},
            API_RETURN: {200: "values"}
        },
        "issue": {
            API_QUERY_STRING: {"expand": "{expand}"}
        },
        "issue/createmeta": {
            API_RESOURCE: "{endpoint_name}",
            API_RETURN: {
                200: "projects"
            }
        },
        "issue(Filter)": {
            API_RESOURCE: "search",
            API_QUERY_STRING: {"jql": "filter={}".format(ITEM_VALUE), "expand": "{expand}"},
            API_RETURN: {
                200: "issues"
            }
        },
        "issue(JQL)": {
            API_RESOURCE: "search",
            API_QUERY_STRING: {"jql": ITEM_VALUE, "expand": "{expand}"},
            API_RETURN: {
                200: "issues"
            }
        },
        "project/components": {
            API_RESOURCE: "project/{item_value}/components"
        },
        "project/search": {
            API_RESOURCE: "{endpoint_name}",
            API_QUERY_STRING: {"expand": "{expand}"},
            # expand: description, projectKeyrs, lead, issueTypes, url, insight
            API_RETURN: {
                200: "values",
                404: "Item not found"
            }
        },
        "project/versions": {
            API_RESOURCE: "project/{item_value}/versions",
            API_QUERY_STRING: {"expand": "{expand}"}
            # expand: issuesstatus, operations
        },
        "search": {
            API_RESOURCE: "search",
            API_QUERY_STRING: {"jql": ITEM_VALUE, "expand": "{expand}"},
            API_RETURN: {
                200: "issues"
            }
        },
        "worklog/deleted": {},
        "worklog/list": {
            API_RESOURCE: "issue/{item_value}/worklog",
        },
        "organization": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "organization/{item_value}",
            API_RETURN: {
                200: ["values", None],
                404: "Organization ID {item_value} does not exists"
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "organization/user": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "organization/{item_value}/user",
            API_RETURN: {
                200: "values",
                404: "Organization ID {item_value} does not exists"
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "request": {
            API: JIRA_SERVICE_DESK_URL,
            API_RETURN: {
                200: ["values", None]
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "servicedesk": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "{endpoint_name}/{item_value}",
            API_RETURN: {
                200: ["values", None],
                404: JIRA_SERVICE_DESK_ID_404
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "servicedesk/customer": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/customer",
            API_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "servicedesk/organization": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/organization",
            API_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "servicedesk/queue": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/queue",
            API_RETURN: {
                200: "values",
                404: JIRA_SERVICE_DESK_ID_404
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "servicedesk/queue/issue": {
            API: JIRA_SERVICE_DESK_URL,
            API_RESOURCE: "servicedesk/{item_value}/queue/{queue_id}/issue",
            API_RETURN: {
                200: "values",
                404: "Service Desk ID {item_value} or queue ID {queue_id} do not exist"
            },
            PAGINATION: JIRA_SERVICE_DESK_PAGINATION
        },
        "board": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board",
            API_RETURN: {
                200: "values",
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
        "board/epic": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/epic",
            API_RETURN: {
                200: "values",
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
        "board/issue": {
            API: JIRA_SOFTWARE_URL,
            API_RESOURCE: "board/{item_value}/issue",
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
