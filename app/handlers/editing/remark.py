# coding: utf-8
# Provide the ability for judges to add remarks in the form of images
# Created by James Raphael Tiovalen (2020)

import slack
import settings
import json
import config
import ast
from itertools import zip_longest

from slackers.hooks import actions, emit, responder
from starlette.responses import Response, JSONResponse

conv_db = config.conv_handler


# Function recipe to loop through a list n items at a time
def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


# Score input validation utility
@responder("view_submission:edit_score_submission")
def score_validation(payload):
    error_block = {}

    for criteria in list(payload["view"]["state"]["values"].items()):
        # Check if string contains non-digits
        if not list(criteria[1].items())[0][1]["value"].isdecimal():
            error_block[
                f"{str(criteria[0])}"
            ] = "Please enter only non-negative integers in this field."
        # Check if string is not equal to "0" and contains leading zeros
        elif (list(criteria[1].items())[0][1]["value"] != "0") and (
            list(criteria[1].items())[0][1]["value"]
            != list(criteria[1].items())[0][1]["value"].lstrip("0")
        ):
            error_block[
                f"{str(criteria[0])}"
            ] = "Please remove any leading zeros in this field."
        # Check if score exceeds the upper limit
        elif int(list(criteria[1].items())[0][1]["value"]) > settings.MAX_CRITERIA_SCORE:
            error_block[
                f"{str(criteria[0])}"
            ] = f"Please enter a value between 0 and {settings.MAX_CRITERIA_SCORE} inclusive."

    # Return warnings if inputs are invalid
    if bool(error_block):
        return JSONResponse({"response_action": "errors", "errors": error_block})

    # Emit normal action if inputs are validated
    else:
        # f-string does not work here
        emit(
            actions, "{}:edit_validated_score".format(payload["type"]), payload=payload
        )
        return Response()


# Third stage of judging
@actions.on("view_submission:edit_validated_score")
async def remark_team(payload):
    user_id = payload["user"]["id"]
    channel = payload["view"]["private_metadata"].split(", ")[0]
    group_name = payload["view"]["private_metadata"].split(", ")[1]

    if user_id in config.db.get_all_judges():
        state = conv_db.get_state(channel, user_id)

        # Validate state
        if state == config.EDIT_SCORE:

            for c1, c2, c3, c4 in grouper(
                4, list(payload["view"]["state"]["values"].items())
            ):
                category_name = c1[0].split("_")[0]

                criteria_1_score = int(list(c1[1].items())[0][1]["value"])
                criteria_2_score = int(list(c2[1].items())[0][1]["value"])
                criteria_3_score = int(list(c3[1].items())[0][1]["value"])
                criteria_4_score = int(list(c4[1].items())[0][1]["value"])

                config.db.edit_score(
                    user_id,
                    group_name,
                    category_name,
                    criteria_1_score,
                    criteria_2_score,
                    criteria_3_score,
                    criteria_4_score,
                )

            remark = config.db.get_specific_remark(user_id, group_name)

            edit_remark_message_block = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Scores have been edited for team: *{group_name}*!\r\n\r\nIf you would like to edit the remarks for the team that you have judged, *reply* to this message with some textual remarks or/and *one* photo of your remarks as a *threaded reply*. Please note that other types of messages will be ignored.\r\n\r\nOtherwise, press the button to finalize your judging process.\r\n\r\n",
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Finish editing",
                            "emoji": True,
                        },
                        "action_id": "editing_end",
                        "style": "danger",
                        "value": "confirm_end_editing",
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Are you sure?",
                            },
                            "text": {
                                "type": "mrkdwn",
                                "text": "If you change your mind, feel free to edit your remarks entry later.",
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Yes, just do it!",
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "Stop, I've changed my mind!",
                            },
                        },
                    },
                }
            ]

            if remark[0] is not None:
                edit_remark_message_block.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Your current remarks image for *{group_name}* is at: {remark[0]}",
                        },
                    }
                )

            if remark[1] is not None:
                edit_remark_message_block.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Your current remarks text for *{group_name}* is: {remark[1]}",
                        },
                    }
                )

            timestamp = (
                await config.web_client.chat_postMessage(
                    channel=channel, blocks=edit_remark_message_block
                )
            )["ts"]

            # For message updating purposes; group together to prevent race condition
            conv_db.change_state_ts(channel, user_id, config.EDIT_REMARKS, timestamp)

        else:
            config.fallback.view_fallback(payload)

    else:
        print(f"Unauthorized access denied for user {user_id}.")
        config.web_client.chat_postMessage(
            channel=channel,
            text=f"Hi <@{user_id}>! You do not seem to have enough privileges to execute that command. Apologies!",
        )

    return
