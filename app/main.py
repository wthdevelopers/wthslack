# coding: utf-8
# SUTD WTH Automation Slack Bot
# Created by James Raphael Tiovalen (2020)

"""
To clear any confusion, Slack API provides 2 methods: Events & RTM.
Both the Events and RTM APIs could be used together for more redundancy and concern separation.
For functions using RTM (websocket connection), we will incorporate the RTMClient decorator.
For functions using Events (HTTP request), we will incorporate the events decorator from Slackers.
Other functions such as slash commands and interactive components (which includes block actions and views) will need the respective decorators from Slackers and require the specification of a Request URL as well.
For this bot, we will be using Async FastAPI instead of using Celery since we want to keep it simple (we do not need to initialize a message broker for this).
See here for more info: https://github.com/slackapi/python-slack-events-api/issues/29#issuecomment-361454133
"""

# Import libraries
import time
import requests
import json
import settings

from fastapi import FastAPI
from slackers.server import router

# Import global variables across modules
import config

# Import handlers
import handlers.utils.start
import handlers.utils.cancel
import handlers.viewing.leaderboard
import handlers.viewing.summary
import handlers.viewing.overall  # TODO
import handlers.judging.team
import handlers.judging.scoring
import handlers.judging.remark
import handlers.judging.end_judge
import handlers.editing.team
import handlers.editing.scoring
import handlers.editing.remark
import handlers.editing.end_edit

# Instantiate FastAPI app (run this using uvicorn)
# Disable public documentation to prevent exposure of SECRET_KEY
# Might want to consider basic authenticated access to docs
app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
app.include_router(
    router, prefix=f"/{settings.SECRET_KEY}"
)  # Protect the endpoint with the SECRET_KEY
