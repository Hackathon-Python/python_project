def str_to_bool(s: str) -> bool or None:
    if s == "true" or s == "True":
        return True
    elif s == "false" or s == "False":
        return False
    else:
        return None
