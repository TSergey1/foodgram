import re
from django.core.exceptions import ValidationError

from foodgram.constants import DICT_ERRORS


def validate_color(value):
    regex = r"^#([A-Fa-f0-9]{6})$"
    if not re.match(regex, value):
        raise ValidationError('{0}'.format(DICT_ERRORS.get('validator_color')))
