# coding: utf-8
# Modify a specific participant entry in database
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("editparticipant")
def editparticipant(payload):

    return
