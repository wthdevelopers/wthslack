# coding: utf-8
# View overall database
# Created by James Raphael Tiovalen (2020)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("viewdb")
def viewdb(payload):

    return
