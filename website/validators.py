import re

from django.utils import six
from django.utils.functional import SimpleLazyObject
from django.core.validators import RegexValidator, ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_max_list_length(value):
    _max = 3
    sep = ','
    if len(value.strip(sep).split(sep)) > _max:
        raise ValidationError(_('Enter no more than {} tags'.format(_max)))


def _lazy_re_compile(regex, flags=0):
    """Lazily compile a regex with flags."""
    def _compile():
        # Compile the regex if it was not passed pre-compiled.
        if isinstance(regex, six.string_types):
            return re.compile(regex, flags)
        else:
            assert not flags, "flags must be empty if regex is passed pre-compiled"
            return regex
    return SimpleLazyObject(_compile)


def tag_list_validator(sep=',', message=None, code='invalid', allow_negative=False):
    regexp = _lazy_re_compile(r'^(?:\s*\w+\s*%(sep)s[\s\w]*)+$' % {
        'sep': re.escape(sep),
    })

    return RegexValidator(regexp, message=message, code=code)


validate_comma_separated_tags_list = tag_list_validator(
    message=_('Enter tags (latin alphanumeric character and the underscore are only allowed) separated by commas.'),
)