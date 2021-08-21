# coding: utf-8
# Insert a new participant entry to database
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("addparticipant")
def addparticipant(payload):

    return
