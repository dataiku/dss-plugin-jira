# -*- coding: utf-8 -*-
import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_recipe_config, get_output_names_for_role
from jira_client import JiraClient
from utils import de_float_column
import pandas as pd

input_datasets_name = get_input_names_for_role('input_datasets_name')
config = get_recipe_config()

id_column_name = config.get('id_column_name')
id_list_df = dataiku.Dataset(input_datasets_name[0]).get_dataframe()
id_list_df_types = id_list_df.dtypes
de_float_column(id_list_df, id_column_name)

queue_id_column_name = config.get('queue_id_column_name', None)
de_float_column(id_list_df, queue_id_column_name)

access_type = get_recipe_config()['access_type']
connection_details = get_recipe_config()[access_type]
endpoint_name = get_recipe_config()['endpoint_name']
expand = get_recipe_config()['expand']

client = JiraClient(connection_details)
client.start_session(endpoint_name)

results = []
for index in id_list_df.index:
    jira_id = id_list_df[id_column_name][index]
    indexes_columns = {
        "jira_id": jira_id
    }
    if queue_id_column_name is not None:
        queue_id = id_list_df[queue_id_column_name][index]
        indexes_columns.update({"queue_id": queue_id})
    else:
        queue_id = None

    data = client.get_endpoint(endpoint_name, jira_id, "", expand=expand, raise_exception=False, queue_id=queue_id)
    while len(data) > 0:
        for result in data:
            record = dict(indexes_columns)
            record.update(result)
            results.append(client.format(record))
        if client.pagination.is_next_page():
            data = client.get_next_page()
        else:
            break

output_names_stats = get_output_names_for_role('jira_output')
odf = pd.DataFrame(results)

if odf.size > 0:
    jira_output = dataiku.Dataset(output_names_stats[0])
    jira_output.write_with_schema(odf)
