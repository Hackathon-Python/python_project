import re


def str_to_bool(s: str) -> bool or None:
    if s == "true" or s == "True":
        return True
    elif s == "false" or s == "False":
        return False
    else:
        return None


def remove_special_characters(input_string):
    cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string)
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    return cleaned_string
