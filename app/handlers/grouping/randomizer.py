# coding: utf-8
# Generate random groupings of 3-5 members for each group, irrespective
# of technology and category preferences
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config
import secrets

from slackers.hooks import commands
from typing import Generator, List, Callable

conv_db = config.conv_handler


@commands.on("randomizer")
def randomizer(payload):

    return


def get_all_integer_compositions(
    n: int, m: int, sigma: Callable
) -> Generator[List[int], None, None]:
    """
    This algorithm was modified and obtained from
    https://stackoverflow.com/a/10399049.
    Generates all interpart restricted compositions of n with first
    part >= m using restriction function sigma (in lexicographic
    order). See Kelleher 2006, 'Encoding partitions as ascending
    compositions' chapters 3 and 4 for details.

    In short:
    - For compositions, use the restriction function f(x) = 1.
    - For partitions, use the restriction function f(x) = x.

    For future reference, we might want to consider modifying Merca's
    Algorithm 6 (version 3) from
    https://link.springer.com/article/10.1007/s10852-011-9168-y to
    generate (ascending) compositions instead of partitions. It might
    result in potential performance gains/optimizations.
    """
    if n < 0:
        raise StopIteration("Invalid integer input.")
    elif n == 0:
        yield []
        raise StopIteration("Invalid integer input.")
    a = [0 for _ in range(n + 1)]
    k = 1
    a[0] = m - 1
    a[1] = n - m + 1
    while k != 0:
        x = a[k - 1] + 1
        y = a[k] - 1
        k -= 1
        while sigma(x) <= y:
            a[k] = x
            x = sigma(x)
            y -= x
            k += 1
        a[k] = x + y
        yield a[: k + 1]


def get_eligible_compositions(
    n: int,
    min_value: int = settings.MIN_GROUP_SIZE,
    max_value: int = settings.MAX_GROUP_SIZE,
) -> Generator[List[int], None, None]:
    if n <= 0:
        raise StopIteration("Invalid integer input.")
    elif 0 < n < settings.MIN_GROUP_SIZE:
        yield [n]
    list_of_compositions = list(get_all_integer_compositions(n, 1, lambda x: 1))
    for x in list_of_compositions:
        if min(x) >= min_value and max(x) <= max_value:
            yield x


def get_random_groupings(list_of_channel_members):
    """
    Each group sizes configuration has an equal, uniform probability of
    being chosen. Technically, there is an inherent bias towards
    certain group sizes, depending on the length of
    list_of_channel_members. However, this bias is unavoidable and is
    not necessarily a bad thing.
    """
    if len(list_of_channel_members) <= 0:
        raise StopIteration("Impossible channel member size.")
    channel_members_copy = list_of_channel_members.copy()
    secrets.SystemRandom().shuffle(channel_members_copy)
    possible_group_sizes_configurations = list(
        get_eligible_compositions(len(channel_members_copy))
    )
    selected_group_sizes_configuration = secrets.choice(
        possible_group_sizes_configurations
    )
    curr = 0
    for size in selected_group_sizes_configuration:
        yield channel_members_copy[curr : curr + size]
        curr += size
