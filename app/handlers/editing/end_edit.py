# coding: utf-8
# Store the image URL together with the score commit to the SQL database
# Change state to end editing session
# Created by James Raphael Tiovalen (2020)

import slack
import settings
import json
import config
import requests

from slackers.hooks import events, actions

conv_db = config.conv_handler


# This will run if there are no remarks submitted
# Remarks will be handled by the judging side
@actions.on("block_actions:editing_end")
def finalize_judging(payload):
    channel = payload["channel"]["id"]
    user_id = payload["user"]["id"]
    state = conv_db.get_state(channel, user_id)

    if state != config.EDIT_REMARKS:
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"You can only execute this command after submitting scores as a judge, <@{user_id}>!",
        )

    else:
        latest_message_ts = conv_db.get_ts(channel, user_id)
        message = f"Your judging process has been finalized, <@{user_id}>!"
        config.web_client.chat_update(
            channel=channel, text=message, ts=latest_message_ts, blocks=None
        )

        conv_db.change_state(channel, user_id, config.CONVERSATION_END)

    return
