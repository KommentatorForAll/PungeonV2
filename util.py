import random
from typing import Optional

_random: Optional[random.Random] = None
_calls: int = 0


def _ensure_random(func):
    def wrapper(*args, **kwargs):
        global _random, _calls
        if _random is None:
            raise ValueError("random must be initialized")
        _calls += 1
        return func(*args, **kwargs)
    return wrapper


def init_random(seed, calls=0):
    global _random, _calls
    _random = random.Random(seed)
    [get_random() for i in range(calls)]


@_ensure_random
def get_random():
    """
    returns a random number between 0 (inclusive) and 1 (exclusive)
    :return:
    """
    return _random.random()


@_ensure_random
def choice(options):
    """
    chooses a random object from the list
    :param options:
    :return:
    """
    return _random.choice(options)


@_ensure_random
def choices(**kwargs):
    """
    chooses a random object of the population using the weights present in weights
    :param kwargs: population, weights and k
    :return:
    """
    return _random.choices(**kwargs)
