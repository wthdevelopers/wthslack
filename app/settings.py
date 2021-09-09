# Put credentials and tokens here
# Created by James Raphael Tiovalen (2020)

import os
import ast

# Ultimate security for the whole bot lies with the SECRET_KEY
# SECRET_KEY = os.environ["API_KEY"]
SECRET_KEY = "xoxb-..."
OAUTH_KEY = "xoxp-..."

os.environ["SLACK_SIGNING_SECRET"] = ""
REQUEST_URL = ""

# Special characters would need to be escaped by following the ASCII URL Encoding Reference
DB_URL = "<rdbms>+<library>://<username>:<password>@<server>:<port>/sutdwth"

# DB_USER = os.environ["DB_USER"]
# DB_PASS = os.environ["DB_PASS"]

# Use this to manage bot-user conversations (instead of a multiprocessing.Manager)
# Read this for more info: https://stackoverflow.com/a/32825482
# Set environment variable to the path of Firestore JSON Service Account Certificate
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sample-firestore-authfile.json"

# Need to make these dynamic and editable from year to year instead of hardcoded (input using bash script provided)
# Note that these are user IDs (even for the bot), instead of bot/team/channel/enterprise IDs
BOT_ID = ""
MASTER_ID = ""
ORGANIZER_IDS = []

# This hardcoding method is hacky and stupid, but there is no Slack API endpoint to find the channel ID by channel name
# The alternative way is to do a for loop and check through all the channels obtained from this endpoint: https://api.slack.com/methods/conversations.list
# However, that would be inefficient, so nope
# It's a real shame, indeed
TAVERN_CHANNEL_ID = ""
RANDOMIZER_CHANNEL_ID = ""

# Define categories
CATEGORIES = (
    "Built Environment",
    "Waste Management",
    "Natural Environment",
    "Transportation",
)

# Define criterias
CRITERIAS = ("Creativity", "Execution", "Scalability", "Environmental Impact")

# Define percentages of the four criterias
PERCENTAGES = (0.25, 0.25, 0.25, 0.25)

# Define group size limits/bounds
# This following set of restrictions should ideally allow and accommodate for ALL integers >= MIN_GROUP_SIZE to be decomposed properly while still within the imposed boundaries
# This guaranteed condition would be satisfied for all integers >= N, where N is a positive integer, if MIN_GROUP_SIZE = N and MAX_GROUP_SIZE >= 2N - 1
MIN_GROUP_SIZE = 3
MAX_GROUP_SIZE = 5

# This threshold is arbitrarily chosen
RANDOMIZER_CHANNEL_SIZE_THRESHOLD = 23

# Limit to number of digits for scores
# Upper limit of INTEGER(11) has 10 digits, however maximum score is 100 (with 3 digits)
SCORE_DIGITS_LIMIT = 3

MAX_CRITERIA_SCORE = 100

# Random constants to serve as limits due to Slack API's limitations
NUMBER_OF_GROUPS_LIMIT = 100
MAX_LEADERBOARD_ENTRIES_PER_CATEGORY_LIMIT = 10
