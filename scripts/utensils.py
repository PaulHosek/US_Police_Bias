

def load_json(filename):
    """
    Import json from folder "Data" and return as a dictionary.
    :param filename: name of the json (e.g. example.json
    :rtype dictionary
    :return: dictionary of json
    """
    from json import load
    from os.path import dirname, join
    script_dir = dirname(__file__)
    file_path = join(script_dir, '../Data', filename)
    with open(file_path) as json_file:
        dict_json = load(json_file)
    return dict_json
