import re
from rest_framework.exceptions import ValidationError

from foodgram.constants import DICT_ERRORS


def validate_username(value):
    regex = r"^[\w.@+-]+\Z"
    if re.search(regex, value) is None:
        result = set(re.findall(r"[^\w.@+-]", value))
        raise ValidationError(
            f'Cимвол {result} использовать запрещено.'
        )
    if value.lower() == DICT_ERRORS['forbidden_username']:
        raise ValidationError(
            (f'Использовать имя'
             f'{DICT_ERRORS.get("forbidden_username")} запрещено.')
        )
