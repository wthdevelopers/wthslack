# coding: utf-8
# This handler will handle fallback so that each user can only have one conversation at a time per channel with the bot
# Created by James Raphael Tiovalen (2020)

import slack
import config


def fallback(payload):
    channel = payload["channel_id"]
    user_id = payload["user_id"]

    message = f"Hi <@{user_id}>! Please finish your current conversation with the bot first before attempting another action. Thank you!\r\n"
    config.web_client.chat_postMessage(channel=channel, text=message)


def view_fallback(payload):
    channel = payload["view"]["private_metadata"].split(", ")[0]
    user_id = payload["user"]["id"]

    message = f"Hi <@{user_id}>! Please finish your current conversation with the bot first before attempting another action. Thank you!\r\n"
    config.web_client.chat_postMessage(channel=channel, text=message)
