# coding: utf-8
# View leaderboard
# Created by James Raphael Tiovalen (2020)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


def init(category):
    board = ast.literal_eval(config.db.build_leaderboard(category))
    field = []
    for i in range(len(board)):
        name = board[i][0]
        score = board[i][1]

        field.append({"type": "mrkdwn", "text": f"*{str(name)} - {str(score)}*"})

    # Check if there are no scores available for a particular category
    if not field:
        field.append(
            {
                "type": "mrkdwn",
                "text": "There are currently no scores available for this category.",
            }
        )

    return field


@commands.on("leaderboard")
def leaderboard(payload):
    channel = payload["channel_id"]
    user_id = payload["user_id"]

    if user_id == settings.MASTER_ID:
        state = conv_db.get_state(channel, user_id)

        if (state == config.TEAM_REMARKS) or (state == config.EDIT_REMARKS):
            config.web_client.chat_postMessage(
                channel=channel,
                text=f"You can only end your judging process or reply with a photo of your remarks at this point, <@{user_id}>!",
            )

        else:
            # Max no. of "fields" is 10, which is a Slack API limitation
            config.web_client.chat_postMessage(
                channel=channel,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Hello <@{user_id}>!\r\nThis is the Top 10 Leaderboard so far:",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{settings.CATEGORIES[0]} Category:*",
                        },
                    },
                    {"type": "section", "fields": init(settings.CATEGORIES[0])[:10]},
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{settings.CATEGORIES[1]} Category:*",
                        },
                    },
                    {"type": "section", "fields": init(settings.CATEGORIES[1])[:10]},
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{settings.CATEGORIES[2]} Category:*",
                        },
                    },
                    {"type": "section", "fields": init(settings.CATEGORIES[2])[:10]},
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{settings.CATEGORIES[3]} Category:*",
                        },
                    },
                    {"type": "section", "fields": init(settings.CATEGORIES[3])[:10]},
                ],
            )

    else:
        print(f"Unauthorized access denied for user {user_id}.")
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! You do not seem to have enough privileges to execute that command. Apologies!\r\n",
        )

    return
