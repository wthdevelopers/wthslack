# coding: utf-8
# Automatically create all group channels with their corresponding members
# Created by James Raphael Tiovalen (2021)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("create_all_group_channels")
def create_all_group_channels(payload):

    return
