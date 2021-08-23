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

from slackers.hooks import commands
from typing import Generator, Callable, List

conv_db = config.conv_handler


@commands.on("randomize")
async def randomizer(payload):
    channel = payload["channel_id"]
    user_id = payload["user_id"]

    channel_name_checking_response = await config.web_client.conversations_info(
        channel=channel, include_locale=True, include_num_members=True
    )

    channel_name = channel_name_checking_response["channel"]["name"]

    if channel_name == "randomizer":
        await config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! Please give us some time to run the randomizer algorithm...",
        )

        channel_members_response = await config.web_client.conversations_members(
            channel=channel, limit=1000
        )

        channel_members = channel_members_response["members"]

        # Remove organizers, admin and the bot itself from the list
        channel_members.remove(settings.MASTER_ID)
        channel_members.remove(settings.BOT_ID)
        for organizer_id in settings.ORGANIZER_IDS:
            channel_members.remove(organizer_id)

        groups = list(get_random_groupings(channel_members))

        randomized_grouping_message = ""

        for idx, group in enumerate(groups):
            group_members = ["<@" + member + ">" for member in group]
            randomized_grouping_message += (
                f"Group {idx + 1}: {', '.join(group_members)}\r\n"
            )

        await config.web_client.chat_postMessage(
            channel=channel,
            text=(
                f"These are the generated random groups:\r\n\r\n{randomized_grouping_message}"
            ),
        )

        await config.web_client.chat_postMessage(
            channel=channel,
            text=(
                "Do note that the randomized groupings are not confirmed yet. "
                "Please communicate and coordinate with your randomly assigned new teammates to get to know each other more and check whether all of you accept this grouping or not. "
                "After that, do collectively decide and agree on the group particulars, assign a group leader, and register in the official form accordingly.\r\n\r\n"
                f"If you feel that your randomly assigned group is not the best fit for you, feel free to go to the <#{settings.TAVERN_CHANNEL_ID}> and talk to other people to form groups!"
            ),
        )

    else:
        await config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! Please run this command in the <#{settings.RANDOMIZER_CHANNEL_ID}> channel. Thank you!",
        )

    return


def get_eligible_integer_compositions(
    n: int, m: int, sigma: Callable, min_value: int, max_value: int
) -> Generator[List[int], None, None]:
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
        yield []
        raise StopIteration("Invalid integer input.")
    elif 0 < n < min_value:
        yield [n]
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
        z = a[: k + 1]
        if min(z) >= min_value and max(z) <= max_value:
            yield z


def get_balanced_grouping_allocation(
    w: int, min_value: int, max_value: int
) -> List[int]:
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
    for this very specific case and for the time being. Ideally, such
    an algorithm should also not skimp/slack off on keeping the number
    of groups as low as possible in the name of balance.

    As long as the guarantee conditions of min_value = N and
    max_value >= 2N - 1 are satisfied, no groups will violate either
    bound.

    Keep in mind that w > max_value most of the time.

    Might want to consider introducing more randomness in some form by
    using some kind of method here.
    """
    x = -(w // -max_value)
    q, mod = divmod(w, x)
    a = [q for _ in range(x)]
    for i in range(mod):
        a[i] += 1
    return a


def get_random_groupings(
    list_of_channel_members: List[str],
) -> Generator[List[str], None, None]:
    """
    Take note that the time spent managing the memory for the big list
    of all the compositions will definitely dominate the time cost of
    generating them.

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

    Do let @jamestiotio know if you are able to catch any other edge
    cases, caveats, loopholes or tricky configurations.
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
        selected_group_sizes_configuration = secrets.choice(
            possible_group_sizes_configurations
        )
        secrets.SystemRandom().shuffle(selected_group_sizes_configuration)
        curr = 0
        for chunk_size in selected_group_sizes_configuration:
            yield channel_members_copy[curr : curr + chunk_size]
            curr += chunk_size
    else:
        group_sizes_configuration = get_balanced_grouping_allocation(
            channel_size,
            settings.MIN_GROUP_SIZE,
            settings.MAX_GROUP_SIZE,
        )
        secrets.SystemRandom().shuffle(group_sizes_configuration)
        curr = 0
        for chunk_size in group_sizes_configuration:
            yield channel_members_copy[curr : curr + chunk_size]
            curr += chunk_size
