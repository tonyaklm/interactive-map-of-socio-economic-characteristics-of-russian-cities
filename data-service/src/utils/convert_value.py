from bs4 import BeautifulSoup


def get_new_value(value: str, value_type: str):
    if value_type == 'Float':
        try:
            value = float(value)
        except ValueError:
            return value
        return value
    if value_type == 'Integer':
        try:
            value = int(value)
        except ValueError:
            return value
        return value
    return value
