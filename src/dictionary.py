import json

def get_dictionary(filepath : str) -> dict:
    with open(filepath) as json_file:
        return json.load(json_file)