import numpy as np


def de_float_column(dataframe, column_name):
    if column_name is None:
        return
    if dataframe[column_name].dtypes == np.float64:
        dataframe[column_name] = dataframe[column_name].fillna(-1)
        dataframe[column_name] = dataframe[column_name].astype(int)
        dataframe[column_name] = dataframe[column_name].astype(str)
        dataframe[column_name] = dataframe[column_name].replace('-1', np.nan)


def extract_data_with_json_path(data, json_path):
    if not json_path:
        return data
    keys = json_path.split(".")
    for key in keys:
        data = data.get(key, {})
    return data


def get_connection_details(config):
    access_type = config.get("access_type", "token_access")
    connection_details = config.get(access_type)
    return connection_details
