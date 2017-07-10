from random import choice
from string import ascii_uppercase, digits


def id_generator(size=6, chars=ascii_uppercase + digits):
    return ''.join(choice(chars) for x in range(size))
