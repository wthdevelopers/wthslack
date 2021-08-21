# coding: utf-8
# View ownself's participant UUID
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("viewparticipantid")
def viewparticipantid(payload):

    return
