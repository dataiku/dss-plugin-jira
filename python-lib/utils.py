import numpy as np


def de_float_column(dataframe, column_name):
    if column_name is None:
        return
    if dataframe[column_name].dtypes == np.float64:
        dataframe[column_name] = dataframe[column_name].fillna(-1)
        dataframe[column_name] = dataframe[column_name].astype(int)
        dataframe[column_name] = dataframe[column_name].astype(str)
        dataframe[column_name] = dataframe[column_name].replace('-1', np.nan)
