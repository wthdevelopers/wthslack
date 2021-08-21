# coding: utf-8
# Starting function
# Created by James Raphael Tiovalen (2020)

import slack
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("start")
def start(payload):
    channel = payload["channel_id"]
    user_id = payload["user_id"]
    state = conv_db.get_state(channel, user_id)

    if (state == config.TEAM_REMARKS) or (state == config.EDIT_REMARKS):
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"You can only end your judging process or reply with a photo of your remarks at this point, <@{user_id}>!",
        )

    else:
        message = (
            f"Hi <@{user_id}>! This Slack Bot provides helpful commands to assist SUTD What The Hack judges in collating candidate scores and judging notes.\r\n\r\n"
            "• /start to start the bot.\r\n"
            "• /judge to begin the judging sequence.\r\n"
            "• /edit to edit a previous judging decision.\r\n"
            "• /cancel to abandon the current ongoing conversation.\r\n"
            "• /summary to view your scoring progress so far.\r\n"
            "• /leaderboard to display the leaderboard.\r\n"
            "• /viewdb to display an overall view of the whole database.\r\n"
            "• /randomize to execute the group randomizer algorithm.\r\n\r\n"
            "For judges, please take note that your conversation state is different across different channels and workspaces.\r\n"
        )
        config.web_client.chat_postMessage(channel=channel, text=message)

    return
