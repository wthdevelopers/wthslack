# coding: utf-8
# View all groups
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("viewgroups")
def viewgroups(payload):

    return
