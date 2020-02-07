# coding: utf-8
# Check initial connection to Slack bot
# Created by James Raphael Tiovalen (2020)

from starlette.testclient import TestClient

import slack
import asyncio
import app.settings


# assert res.status_code == 200
