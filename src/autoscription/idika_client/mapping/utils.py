from src.autoscription.core.errors import MappingIdikaResponseUnexpectedValueException


def get_boolean_from_id_value(value: str) -> bool:
    if value == "0":
        return False
    elif value == "1":
        return True
    else:
        raise MappingIdikaResponseUnexpectedValueException()
