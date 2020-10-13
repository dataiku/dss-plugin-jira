# -*- coding: utf-8 -*-
import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_recipe_config, get_output_names_for_role
from jira_client import JiraClient
import pandas as pd

input_datasets_name = get_input_names_for_role('input_datasets_name')
id_column_name = get_recipe_config()['id_column_name']
access_type = get_recipe_config()['access_type']
connection_details = get_recipe_config()[access_type]
endpoint_name = get_recipe_config()['endpoint_name']
expand = get_recipe_config()['expand']

client = JiraClient(connection_details)
client.start_session(endpoint_name)

id_list = dataiku.Dataset(input_datasets_name[0])
id_list_df = id_list.get_dataframe()
results = []
for index, row in id_list_df.iterrows():
    data = client.get_endpoint(endpoint_name, row[id_column_name], "", expand=expand, raise_exception=False)
    while len(data) > 0:
        for result in data:
            results.append(client.format(result))
        if client.pagination.is_next_page():
            data = client.get_next_page()
        else:
            break

output_names_stats = get_output_names_for_role('jira_output')
odf = pd.DataFrame(results)

if odf.size > 0:
    jira_output = dataiku.Dataset(output_names_stats[0])
    jira_output.write_with_schema(odf)
