import random
import re
import string

from django.utils.text import slugify


def multiple_replace(dictionary, text):
    """
    Replace in 'text' all occurences of any key in the given
    dictionary by its corresponding value.  Returns the new string.
    source: http://code.activestate.com/recipes/81330-single-pass-multiple-replace/
    """

    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dictionary.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dictionary[mo.string[mo.start() : mo.end()]], text)


def custom_slugify(value):
    mapping = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    value = multiple_replace(mapping, value)
    return slugify(value)


def random_token(length=15):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
