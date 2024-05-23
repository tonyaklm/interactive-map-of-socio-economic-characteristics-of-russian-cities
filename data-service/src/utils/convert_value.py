def get_new_value(value: str, value_type: str):
    if value_type == 'Float':
        return float(value)
    if value_type == 'Integer':
        return int(value)
    raise ValueError
