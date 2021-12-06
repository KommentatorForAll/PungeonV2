import random
from typing import Optional

_random: Optional[random.Random] = None
_calls: int = 0


def init_random(seed, calls=0):
    global _random, _calls
    _random = random.Random(seed)
    [get_random() for i in range(calls)]


def get_random():
    global _random, _calls
    if _random is None:
        raise ValueError("random must be initialized")
    _calls += 1
    return _random.random()


def choice(options):
    global _random, _calls
    if _random is None:
        raise ValueError("random must be initialized")
    _calls += 1
    return _random.choice(options)
