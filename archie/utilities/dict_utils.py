def try_get(the_dict: dict, key, fallback=None):
    if key not in the_dict \
            or the_dict[key] is None \
            or (isinstance(the_dict[key], str) and the_dict[key].strip() == ''):
        return fallback
    return the_dict[key]
