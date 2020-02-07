# coding: utf-8
# This handler will initiate and track multiple conversations by monitoring user_id
# Created by James Raphael Tiovalen (2020)

import slack
import settings
import config

from slackers.hooks import commands, actions

conv_db = config.conv_handler


# This serves as judging entry point
@commands.on("edit")
def choose_team(payload):
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

        elif (state == config.INITIAL_STATE) or (state == config.CONVERSATION_END):
            validated_teams = sorted(config.db.get_judged_teams(user_id))

            if not validated_teams:
                config.web_client.chat_postMessage(
                    channel=channel,
                    text=f"Hi <@{user_id}>! It seems that you are not qualified enough to judge any teams. Apologies!",
                )

            else:
                team_list = []

                # Take note that 3 seconds is all that we have to respond with the same trigger_id
                # This might take longer than 3 seconds
                # Do not expose any UUIDs to the web
                for team_name in validated_teams:
                    team_list.append(
                        {
                            "text": {
                                "type": "plain_text",
                                "text": str(team_name),
                                "emoji": True,
                            },
                            "value": str(team_name),
                        }
                    )

                try:
                    config.web_client.views_open(
                        trigger_id=trigger_id,
                        view={
                            "type": "modal",
                            "title": {
                                "type": "plain_text",
                                "text": "Judging Process",
                                "emoji": True,
                            },
                            "submit": {
                                "type": "plain_text",
                                "text": "Select",
                                "emoji": True,
                            },
                            "close": {
                                "type": "plain_text",
                                "text": "Cancel",
                                "emoji": True,
                            },
                            "blocks": [
                                {
                                    "type": "section",
                                    "block_id": "edit_team_selection_block",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Please select a team to edit:*",
                                    },
                                    "accessory": {
                                        "action_id": "edit_team_choice",
                                        "type": "static_select",
                                        "placeholder": {
                                            "type": "plain_text",
                                            "text": "Select a team name",
                                            "emoji": True,
                                        },
                                        "options": team_list,  # Max no. of "options" is 100, which is a Slack API limitation
                                    },
                                }
                            ],
                            "callback_id": "edit_team_choosing",
                            "notify_on_close": True,
                            "private_metadata": channel,  # Pass on the channel id
                        },
                    )

                    # Conduct the change of state after opening the modal view
                    conv_db.change_state(channel, user_id, config.EDIT_TEAM)

                # Catch expired trigger_id error
                except slack.errors.SlackApiError as e:
                    config.web_client.chat_postMessage(
                        channel=channel,
                        text=f"Hi <@{user_id}>! It seems that something went wrong. Feel free to retry the editing process. Apologies!",
                    )

                    status = config.db.check_score_existence(user_id)

                    if status:
                        conv_db.change_state(channel, user_id, config.CONVERSATION_END)
                    else:
                        conv_db.change_state(channel, user_id, config.INITIAL_STATE)

        else:
            config.fallback.fallback(payload)

    else:
        print(f"Unauthorized access denied for user {user_id}.")
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! You do not seem to have enough privileges to execute that command. Apologies!",
        )

    return


# Handle view closure
@actions.on("view_closed:edit_team_choosing")
def cancel_team_selection(payload):
    user_id = payload["user"]["id"]
    channel = payload["view"]["private_metadata"]
    status = config.db.check_score_existence(user_id)

    if status:
        conv_db.change_state(channel, user_id, config.CONVERSATION_END)
    else:
        conv_db.change_state(channel, user_id, config.INITIAL_STATE)

    config.web_client.chat_postMessage(
        channel=channel,
        text=f"Your current editing process in this channel has been cancelled, <@{user_id}>!",
    )

    return
