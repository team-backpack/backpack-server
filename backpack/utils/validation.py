import re

def is_name_valid(name: str):
    name_regex = re.compile(r'^[a-zA-Z0-9_.]+$')
    return bool(name_regex.match(name)) and (2 <= len(name) <= 20)