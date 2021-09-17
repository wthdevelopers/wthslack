# coding: utf-8
# Store the image URL together with the score commit to the SQL database
# Change state to end judging session
# Created by James Raphael Tiovalen (2020)

import slack
import settings
import json
import config

from slackers.hooks import events, actions

conv_db = config.conv_handler


# This will run if there are no remarks submitted
@actions.on("block_actions:judging_end")
def finalize_judging(payload):
    channel = payload["channel"]["id"]
    user_id = payload["user"]["id"]
    state = conv_db.get_state(channel, user_id)

    if state != config.TEAM_REMARKS:
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


# Final stage of judging
@events.on("message")
async def handle_remarks(payload):
    channel = payload["event"]["channel"]
    user_id = payload["event"].get("user")
    ts = conv_db.get_ts(channel, user_id)

    # Filter only threaded replies of the correct parent timestamp that contain images
    if (
        (payload["event"].get("parent_user_id") == settings.BOT_ID)
        and (payload["event"].get("thread_ts") == ts)
        and ("files" in payload["event"])
        and (payload["event"].get("subtype") == "file_share")
    ):
        if user_id in config.db.get_all_judges():
            state = conv_db.get_state(channel, user_id)

            # Validate state
            if (state == config.TEAM_REMARKS) or (state == config.EDIT_REMARKS):
                # Store image URL and textual remarks in workspace to database
                # Image URL is still valid even after message deletion
                text = (
                    await config.web_client.conversations_history(
                        channel=channel, latest=ts, limit=1, inclusive=1
                    )
                )["messages"][0]["blocks"][0]["text"]["text"]
                group_name = text.split(": *", 1)[1].rsplit("*!", 1)[0]
                group_id = config.db.get_group_id(group_name)
                url = payload["event"]["files"][0]["url_private"]
                remarks_text = payload["event"]["blocks"][0]["elements"][0]["elements"][0]["text"]

                # Add filepath location and textual remarks to score table
                config.db.update_remarks(user_id, group_id, url, remarks_text)

                # Update parent message
                if state == config.TEAM_REMARKS:
                    config.web_client.chat_update(
                        channel=channel,
                        text=f"Remarks received! Your judging process has been finalized, <@{user_id}>!",
                        blocks=None,
                        ts=conv_db.get_ts(channel, user_id),
                    )
                elif state == config.EDIT_REMARKS:
                    config.web_client.chat_update(
                        channel=channel,
                        text=f"Remarks received! Your editing process has been finalized, <@{user_id}>!",
                        blocks=None,
                        ts=conv_db.get_ts(channel, user_id),
                    )

                conv_db.change_state(channel, user_id, config.CONVERSATION_END)

            else:
                config.web_client.chat_postMessage(
                    channel=channel,
                    text=f"You can only execute this command after submitting scores as a judge, <@{user_id}>!",
                )

        else:
            pass

    else:
        pass

    return
