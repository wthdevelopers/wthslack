# coding: utf-8
# View a specific participant's assigned group details
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("viewgroupdeets")
def viewgroupdeets(payload):

    return
