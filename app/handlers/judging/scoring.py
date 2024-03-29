# coding: utf-8
# This is the main scoring portion
# Created by James Raphael Tiovalen (2020)

import slack
import settings
import config

from slackers.hooks import actions

conv_db = config.conv_handler


# Second stage of judging
@actions.on("block_actions:team_choice")
def score_team(payload):
    user_id = payload["user"]["id"]
    channel = payload["view"]["private_metadata"]
    view_id = payload["view"]["id"]
    selected_team = payload["actions"][0]["selected_option"]["value"]
    action_id = payload["actions"][0]["action_id"]

    if user_id in config.db.get_all_judges():
        state = conv_db.get_state(channel, user_id)

        # Validate action id and state
        if (str(action_id) == "team_choice") and (state == config.TEAM_CHOOSE):
            scoring_block = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Please enter the score for team *{selected_team}*. Do take note that the maximum score is {settings.MAX_CRITERIA_SCORE}.",
                    },
                }
            ]

            judged_categories = config.db.get_categories(user_id, selected_team)

            for category in judged_categories:
                category_block = [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*{category}* Category:"},
                    }
                ]

                for criteria in settings.CRITERIAS:
                    category_block.append(
                        {
                            "type": "input",
                            "block_id": f"{category}_{criteria}_scoring",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": f"{category}_{criteria}_score",
                                "multiline": False,
                                "initial_value": "0",
                                "max_length": settings.SCORE_DIGITS_LIMIT,
                            },
                            "label": {
                                "type": "plain_text",
                                "text": f"{criteria}",
                                "emoji": True,
                            },
                        }
                    )

                scoring_block.extend(category_block)

            try:
                config.web_client.views_update(
                    view_id=view_id,
                    view={
                        "type": "modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Judging Process",
                            "emoji": True,
                        },
                        "submit": {
                            "type": "plain_text",
                            "text": "Submit",
                            "emoji": True,
                        },
                        "close": {
                            "type": "plain_text",
                            "text": "Cancel",
                            "emoji": True,
                        },
                        "blocks": scoring_block,
                        "callback_id": "score_submission",
                        "notify_on_close": True,
                        # Pass on the channel id and group id
                        "private_metadata": f"{channel}, {selected_team}",
                    },
                )

                conv_db.change_state(channel, user_id, config.TEAM_SCORE)

            except slack.errors.SlackApiError as e:
                config.web_client.chat_postMessage(
                    channel=channel,
                    text=f"Hi <@{user_id}>! It seems that something went wrong. Feel free to retry the judging process. Apologies!",
                )

                status = config.db.check_score_existence(user_id)

                # Reset state
                if status:
                    conv_db.change_state(channel, user_id, config.CONVERSATION_END)
                else:
                    conv_db.change_state(channel, user_id, config.INITIAL_STATE)

        else:
            config.fallback.view_fallback(payload)

    else:
        print(f"Unauthorized access denied for user {user_id}.")
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! You do not seem to have enough privileges to execute that command. Apologies!",
        )

    return


# Handle view closure
@actions.on("view_closed:score_submission")
def cancel_score_selection(payload):
    user_id = payload["user"]["id"]
    channel = payload["view"]["private_metadata"].split(", ")[0]
    status = config.db.check_score_existence(user_id)

    if status:
        conv_db.change_state(channel, user_id, config.CONVERSATION_END)
    else:
        conv_db.change_state(channel, user_id, config.INITIAL_STATE)

    config.web_client.chat_postMessage(
        channel=channel,
        text=f"Your current judging process in this channel has been cancelled, <@{user_id}>!",
    )

    return
