# coding: utf-8
# Generate random groupings of 3-5 members for each group, taking into
# consideration their technology and category preferences
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("matchmaking")
def matchmaking(payload):

    return
