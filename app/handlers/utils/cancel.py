# coding: utf-8
# Cancel current conversation
# Created by James Raphael Tiovalen (2020)

import slack
import config
import settings

from slackers.hooks import commands, actions

conv_db = config.conv_handler


# Receive slash command
@commands.on("cancel")
def cancel(payload):
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
                config.web_client.views_open(
                    trigger_id=trigger_id,
                    view={
                        "type": "modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Cancel Conversation",
                            "emoji": True,
                        },
                        "submit": {"type": "plain_text", "text": "Yup!", "emoji": True},
                        "close": {"type": "plain_text", "text": "Nope.", "emoji": True},
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "You have asked me to abandon our current conversation in this channel. *Are you sure?*",
                                },
                            }
                        ],
                        "callback_id": "confirm_cancel",
                        "private_metadata": channel,  # Pass on the channel id
                    },
                )

            # Catch expired trigger_id error
            except slack.errors.SlackApiError as e:
                config.web_client.chat_postMessage(
                    channel=channel,
                    text=f"Hi <@{user_id}>! It seems that something went wrong. Apologies!",
                )

        else:
            config.web_client.chat_postMessage(
                channel=channel,
                text=f"Hi <@{user_id}>! You do not seem to have any ongoing conversations in this channel to cancel at the moment.",
            )

    else:
        print(f"Invalid cancel function invoked by user {user_id}.")
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! You do not seem to have enough privileges to have any prolonged conversations to cancel in the first place. Apologies!",
        )

    return


# Receive modal action
@actions.on("view_submission:confirm_cancel")
def destroy_conversation(payload):
    user_id = payload["user"]["id"]
    channel = payload["view"]["private_metadata"]
    status = config.db.check_score_existence(user_id)

    if status:
        conv_db.change_state(channel, user_id, config.CONVERSATION_END)
    else:
        conv_db.change_state(channel, user_id, config.INITIAL_STATE)

    config.web_client.chat_postMessage(
        channel=channel,
        text=f"Your current conversation in this channel has been cancelled, <@{user_id}>!",
    )

    return
