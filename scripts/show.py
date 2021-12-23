
from os.path import join
import pandas as pd


def show_file(filename, separator=';', columns=None):
    """
    Load a csv file as DataFrame in the notebook.
    :param filename: The file that should be loaded
    :param separator: The separator this CSV uses
    :param columns: A selection of columns. If left blank, select all columns.
    :return: pd.DataFrame of the CSV
    """
    fe_path = join('Data', filename)
    with open(fe_path) as file:
        my_data = pd.read_csv(file, sep=separator, low_memory=False, usecols=columns)
    return my_data
