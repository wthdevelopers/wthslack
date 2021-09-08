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
                    content.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{category_name}* Category",
                            },
                        }
                    )
                    for score in scoreboard:
                        group_name = config.db.get_group_name(score[0])
                        # If there are remarks
                        if bool(score[5]):
                            content.extend(
                                [
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"*{group_name}*\r\n\r\n{settings.CRITERIAS[0]}: {score[1]}\r\n{settings.CRITERIAS[1]}: {score[2]}\r\n{settings.CRITERIAS[2]}: {score[3]}\r\n{settings.CRITERIAS[3]}: {score[4]}\r\n",
                                        },
                                    },
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"Remarks for *{group_name}* is at: {score[5]}",
                                        },
                                    },
                                ]
                            )
                        # If there are no remarks
                        else:
                            content.append(
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*{group_name}*\r\n\r\n{settings.CRITERIAS[0]}: {score[1]}\r\n{settings.CRITERIAS[1]}: {score[2]}\r\n{settings.CRITERIAS[2]}: {score[3]}\r\n{settings.CRITERIAS[3]}: {score[4]}\r\n",
                                    },
                                }
                            )
                    content.append({"type": "divider"})

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
