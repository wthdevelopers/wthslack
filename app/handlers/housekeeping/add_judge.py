# coding: utf-8
# Insert a new judge entry to database
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("addjudge")
def addjudge(payload):

    return
