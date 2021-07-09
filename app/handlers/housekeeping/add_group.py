# coding: utf-8
# Insert a new group entry to database
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("addgroup")
def addgroup(payload):

    return
