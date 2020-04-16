# -*- coding: utf-8 -*-
import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_recipe_config, get_output_names_for_role
from jira_client import JiraClient
import pandas as pd

input_A_names = get_input_names_for_role('input_A_role')

id_column_name = get_recipe_config()['id_column_name']
id_column_name_2 = get_recipe_config().get('id_column_name_2', None)

access_type = get_recipe_config()['access_type']
connection_details = get_recipe_config()[access_type]
edge_name = get_recipe_config()['edge_name']

client = JiraClient(connection_details)

id_list = dataiku.Dataset(input_A_names[0])
id_list_df = id_list.get_dataframe()
results = []
for index, row in id_list_df.iterrows():
    if id_column_name_2 is None:
        queue_id = None
    else:
        queue_id = row[id_column_name_2]
    data = client.get_edge(edge_name, row[id_column_name], "", queue_id=queue_id)
    while len(data) > 0:
        for result in data:
            results.append(result)
        if client.has_next_page():
            data = client.get_next_page()
        else:
            break

output_names_stats = get_output_names_for_role('jira_output')
odf = pd.DataFrame(results)

if odf.size > 0:
    jira_output = dataiku.Dataset(output_names_stats[0])
    jira_output.write_with_schema(odf)
