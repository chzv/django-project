import re
from django import template

register = template.Library()

BAD_WORDS = ['редиска', 'дурак', 'грубиян']

@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise TypeError('Фильтр "censor" работает только со строками.')

    def replace_bad_word(match):
        word = match.group()
        return word[0] + '*' * (len(word) - 1)

    pattern = r'\b(' + '|'.join([w.capitalize() for w in BAD_WORDS] + BAD_WORDS) + r')\b'
    return re.sub(pattern, replace_bad_word, value, flags=re.IGNORECASE)

