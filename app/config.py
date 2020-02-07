# coding: utf-8
# We will store the global references to the Slack Bot, MySQL Database and Firestore Database here
# This will be accessed by main.py and the various command handlers
# Purpose of this separation from main.py is for modularity
# Created by James Raphael Tiovalen (2020)

# Do take note that Windows does not support uvloop at the moment
import asyncio
import uvloop

import slack
import settings
from databases.dbhelper import DBHelper
from databases.firebaser import FireConn
import handlers.utils.fallback
from slackers.hooks import commands
import logging

slack_bot_token = settings.SECRET_KEY

logger = logging.getLogger(__name__)

# Import database SQLAlchemy class (main instance)
db = DBHelper()

# Add category list to database
if not db.get_all_categories():
    db.add_all_categories()


# Conversation state tracking constants only for judging functions
# Read more here: https://api.slack.com/bot-users#tracking-conversations
# And here: https://stackoverflow.com/questions/36648795/how-to-build-a-slack-bot-to-have-multiple-conversations
(
    INITIAL_STATE,
    TEAM_CHOOSE,
    TEAM_SCORE,
    TEAM_REMARKS,
    EDIT_TEAM,
    EDIT_SCORE,
    EDIT_REMARKS,
    CONVERSATION_END,
) = range(8)

conv_handler = FireConn()

fallback = handlers.utils.fallback

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

# Set Slack's WebClient loop to uvloop to prevent it from managing its own event loop and causing a RuntimeError
# For more information: https://github.com/slackapi/python-slackclient/issues/429
# Remember to preserve original reference to this config's main symbol table
web_client = slack.WebClient(token=slack_bot_token, loop=loop, run_async=True)


# Log errors
@commands.on("error")
def log_error(exc):
    logger.error(str(exc))
