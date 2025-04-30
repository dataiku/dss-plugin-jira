from dataiku.llm.agent_tools import BaseAgentTool
import logging
from jira_client import JiraClient
from utils import get_connection_details


class JiraCreateIssueTool(BaseAgentTool):
    def set_config(self, config, plugin_config):
        # This logger outputs the key in DEBUG mode ...
        logging.getLogger("jiraapiclient.discovery").setLevel("INFO")
        logging.info("JiraCreateIssueTool init")
        connection_details = get_connection_details(config)
        self.client = JiraClient(connection_details)
        self.client.start_session("issue")
        self.jira_project_key = config.get("jira_project_key")

    def get_descriptor(self, tool):
        return {
            "description": "This tool is a wrapper around atlassian-python-api\'s Jira issue_create API, useful when you need to create a Jira issue. The input to this tool is a dictionary containing the new issue summary and description, e.g. '{'summary':'new issue summary', 'description':'new issue description'}'",            
            "inputSchema": {
                "$id": "https://dataiku.com/agents/tools/search/input",
                "title": "Create Jira issue tool",
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The issue summary"
                    },
                    "description": {
                        "type": "string",
                        "description": "The issue description"
                    }
                },
                "required": ["summary", "description"]
            }
        }

    def create_jira_issue(self, summary: str, description: str, issue_type: str = "Task"):
        try:
            new_issue = self.client.create_issue(self.jira_project_key, summary, description, issue_type)
            return new_issue

        except Exception as exception:
            return f"Error creating issue: {str(exception)}"

    def invoke(self, input, trace):
        args = input.get("input", {})

        # Log inputs and config to trace
        trace.span["name"] = "JIRA_CREATE_ISSUE_TOOL_CALL"
        for key, value in args.items():
            trace.inputs[key] = value
        trace.attributes["config"] = self.config

        summary = args.get("summary")
        description = args.get("description")
        jira_instance_url = self.client.get_site_url()
        created_issue = self.create_jira_issue(summary, description)

        if created_issue and "errors" in created_issue:
            output_text = "There was a problem while creating the issue ticket: {}".format(
                created_issue.get("errors", {}).get("description")
            )
        else:
            output_text = f"Issue created: {created_issue.get('key')} available at {jira_instance_url}browse/{created_issue.get('key')}" if isinstance(created_issue, dict) else created_issue
        
        # Log outputs to trace
        trace.outputs["output"] = output_text

        return {
            "output": output_text
        }