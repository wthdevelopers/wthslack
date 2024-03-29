# coding: utf-8
# View scoring summary
# Created by James Raphael Tiovalen (2020)

import slack
import ast
import settings
import config

from slackers.hooks import commands

conv_db = config.conv_handler


@commands.on("summary")
def summary(payload):
    channel = payload["channel_id"]
    user_id = payload["user_id"]
    trigger_id = payload["trigger_id"]

    if user_id in config.db.get_all_judges():
        state = conv_db.get_state(channel, user_id)

        if (state == config.TEAM_REMARKS) or (state == config.EDIT_REMARKS):
            config.web_client.chat_postMessage(
                channel=channel,
                text=f"You can only end your judging process or reply with a photo of your remarks at this point, <@{user_id}>!",
            )

        elif (state != config.INITIAL_STATE) or (state != config.CONVERSATION_END):
            presence_of_scores = False
            try:
                # Prepare scoreboard
                content = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Hello <@{user_id}>, this is your current scoring summary table so far:",
                        },
                    },
                    {"type": "divider"},
                ]
                # Only create a table for the categories that the judge has submitted
                for category in config.db.get_judged_categories(user_id):
                    category_name = config.db.get_category_name(category)
                    scoreboard = config.db.get_all_scores(user_id, category_name)
                    if scoreboard:
                        presence_of_scores = True
                    content.extend(
                        [
                            {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{category_name}* Category",
                                },
                            },
                            {"type": "divider"}
                        ]
                        
                    )
                    for idx, score in enumerate(scoreboard):
                        group_name = config.db.get_group_name(score[0])
                        content.append(
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*{group_name}*\r\n\r\n{settings.CRITERIAS[0]}: {score[1]}\r\n{settings.CRITERIAS[1]}: {score[2]}\r\n{settings.CRITERIAS[2]}: {score[3]}\r\n{settings.CRITERIAS[3]}: {score[4]}\r\n",
                                    },
                                }
                            )
                        # If there is remark image
                        if score[5] is not None:
                            content.append(
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"Remarks image for *{group_name}* is at: {score[5]}",
                                        },
                                    },
                            )
                        # If there are textual remarks
                        if score[6] is not None:
                            content.append(
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"Remarks text for *{group_name}* is: {score[6]}",
                                        },
                                    },
                            )
                        if idx != len(scoreboard) - 1:
                            content.append({"type": "divider"})
                    content.append({"type": "divider"})

                if not presence_of_scores:
                    content = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"Hello <@{user_id}>, you do not have any submitted scores yet. Submit a judging score to get started!",
                            },
                        },
                    ]

                # Send scoreboard message
                config.web_client.chat_postMessage(
                    channel=channel, user=user_id, blocks=content
                )

            # Catch expired trigger_id error
            except slack.errors.SlackApiError as e:
                config.web_client.chat_postMessage(
                    channel=channel,
                    text=f"Hi <@{user_id}>! It seems that something went wrong. Apologies!",
                )

        else:
            config.fallback.view_fallback(payload)

    else:
        print(f"Unauthorized access denied for user {user_id}.")
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! You do not seem to have enough privileges to execute that command. Apologies!",
        )

    return
