# coding: utf-8
# Generate random groupings of 3-5 members for each group, irrespective
# of technology and category preferences
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config
import math
import secrets
import numpy as np
import numpy.typing as npt

from slackers.hooks import commands
from typing import Generator, Callable

conv_db = config.conv_handler


@commands.on("randomizer")
def randomizer(payload):

    return


def get_eligible_integer_compositions(
    n: int, m: int, sigma: Callable, min_value: int, max_value: int
) -> Generator[np.ndarray, None, None]:
    """
    This algorithm was modified and obtained from
    https://stackoverflow.com/a/10399049.
    Generates all interpart restricted compositions of n with first
    part >= m using restriction function sigma (in lexicographic
    order and constant amortised time). See Kelleher 2006, 'Encoding
    partitions as ascending compositions' chapters 3 and 4 for details.

    In short:
    - For (strict) compositions, use the restriction function f(x) = 1.
    - For partitions, use the restriction function f(x) = x.

    We use NumPy arrays to use slightly less memory.

    Each group sizes configuration has an equal, uniform probability of
    being chosen. Hence, there would be no bias towards any specific
    grouping configuration (either balanced or maximum). Technically,
    there is still some inherent bias towards certain group sizes,
    depending on the magnitude of n. However, this bias has been
    reduced from its original magnitude. The remaining bias is
    unavoidable and is not necessarily a bad thing.

    For future reference, we might want to consider modifying Merca's
    Algorithm 6 (version 3) from
    https://link.springer.com/article/10.1007/s10852-011-9168-y to
    generate (ascending) compositions instead of partitions. It might
    result in potential performance gains/optimizations.
    """
    if n < 0:
        raise StopIteration("Invalid integer input.")
    elif n == 0:
        yield np.array([]).astype(int)
        raise StopIteration("Invalid integer input.")
    elif 0 < n < min_value:
        yield np.array([n]).astype(int)
    a = np.zeros(n + 1).astype(int)
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
        z = a[: k + 1]
        if z.min() >= min_value and z.max() <= max_value:
            yield np.array(z)


def get_balanced_grouping_allocation(w: int, min_value: int, max_value: int):
    """
    This algorithm is much less costly in terms of time complexity, but
    will result in less randomness. It will always prefer the balanced
    or nearly-balanced group configuration, while still accommodating
    for prime numbers of channel sizes, as well as achieving this goal
    in the least number of groups possible (just in case there is a
    limit on the total number of groups).

    Keep in mind that we would like as much entropy as possible, within
    relatively reasonable limits and boundaries.

    Note that while this algorithm will attempt to select the most
    balanced configuration, it will not always choose the most balanced
    due to the nature of the algorithm itself. Instead, it sacrifices
    the choice of being the most balanced in order to allow itself to
    self-adjust and select near-optimal configurations for prime
    numbers of channel sizes as well. Sometimes, this might lead to the
    configuration being nearly balanced, but not exactly. While it is
    true that the most balanced configuration would have the most
    entropy (proportional to number of ways of possible arrangements)
    due to the pattern seen in Pascal's triangle, an algorithm that
    prefers the most balanced configuration might not be able to
    configure itself for prime numbers of channel sizes to fit within
    the restrictions, which would be disastrous (assuming that such an
    algorithm would execute trial-and-error divisions for all positive
    integers >= 2 until either sqrt(w) or w as part of the usual
    factorization procedure). If there exists an algorithm out there
    that we find that would both accommodate for prime numbers of
    channel sizes and always prefer the most balanced configuration, we
    would modify this function to adopt such an algorithm instead. If
    such an algorithm exists, it should not rely on constant
    minute/minor readjustments and trial-and-errors of shaving off and
    topping up certain "buckets"/groups using a try-catch method or a
    conditional while loop procedure/mechanism which might take a much
    longer time to finish since that would completely defeat the point
    of this algorithm being fast/quick enough as compared to the other
    one. While it is true that multiples 3, 4, and 5 are more
    numerous/denser than multiples of prime numbers (at least for
    positive integers between 3 and 1000 inclusive), it is only about a
    10% difference or a 1.5x multiplier (~60:40). Hence, even if this
    difference offsets the amount of entropy lost by the "shaving-off
    and topping-up" sequence, sacrificing this possible time save in
    favor of more balanced configurations at the cost of slower
    performance for such a marginal gain/benefit does not seem to be
    acceptable enough, at least according to me (@jamestiotio). Hence,
    I deem that this approach would be the most appropriate, at least
    for this very specific case and for the time being.

    As long as the guarantee conditions of min_value being N and
    max_value being 2N - 1 are satisfied, no groups will violate either
    bound.

    Might want to consider introducing more randomness in some form by
    using some kind of method here.
    """
    x = math.ceil(w / max_value)
    q, mod = divmod(w, x)
    a = np.empty(x)
    a.fill(q)
    a[0:mod] += 1
    return np.array(a)


def get_random_groupings(list_of_channel_members):
    """
    Take note that the time spent managing the memory for the big list
    of all the compositions will definitely dominate the time cost of
    generating them. We only convert the selected NumPy array to a
    Python list here to save processing time.

    For all shufflings, the Fisher-Yates shuffle algorithm has a time
    complexity of O(n), which is the minimum time possible to shuffle
    any list in a completely random fashion.

    For smaller channel sizes, we select and use the more random method
    because of 2 reasons:
    - It would take much less time as compared to larger channel sizes.
    For larger channel sizes, we use the much faster and balanced
    algorithm, but sacrificing some entropy. This is acceptable since
    larger channel sizes would already have more entropy in the first
    place anyway.
    - Smaller channel sizes have less entropy in the first place due to
    the very nature of less people being involved. As such, the
    tradeoff of more time taken for more entropy is acceptable.
    """
    channel_size = len(list_of_channel_members)
    if channel_size <= 0:
        raise StopIteration("Impossible channel member size.")
    channel_members_copy = list_of_channel_members.copy()
    secrets.SystemRandom().shuffle(channel_members_copy)
    if channel_size <= settings.RANDOMIZER_CHANNEL_SIZE_THRESHOLD:
        possible_group_sizes_configurations = list(
            get_eligible_integer_compositions(
                channel_size,
                1,
                lambda x: 1,
                settings.MIN_GROUP_SIZE,
                settings.MAX_GROUP_SIZE,
            )
        )
        selected_group_sizes_configuration = (
            secrets.choice(possible_group_sizes_configurations).astype(int).tolist()
        )
        secrets.SystemRandom().shuffle(selected_group_sizes_configuration)
        curr = 0
        for chunk_size in selected_group_sizes_configuration:
            yield channel_members_copy[curr : curr + chunk_size]
            curr += chunk_size
    else:
        group_sizes_configuration = (
            get_balanced_grouping_allocation(
                channel_size,
                settings.MIN_GROUP_SIZE,
                settings.MAX_GROUP_SIZE,
            )
            .astype(int)
            .tolist()
        )
        secrets.SystemRandom().shuffle(group_sizes_configuration)
        curr = 0
        for chunk_size in group_sizes_configuration:
            yield channel_members_copy[curr : curr + chunk_size]
            curr += chunk_size
