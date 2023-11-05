import re
from rest_framework.exceptions import ValidationError


from foodgram.settings import CONST


def validate_username(value):
    regex = r"^[\w.@+-]+\Z"
    if re.search(regex, value) is None:
        result = set(re.findall(r"[^\w.@+-]", value))
        raise ValidationError(
            f'Cимвол {result} использовать запрещено.'
        )
    if value.lower() == CONST['forbidden_username']:
        raise ValidationError(
            f'Использовать имя {CONST["forbidden_username"]} запрещено.'
        )
