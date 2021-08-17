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
# Read this for more info: https://stackoverflow.com/a/32825482/10243394
# Set environment variable to the path of Firestore JSON Service Account Certificate
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sample-firestore-authfile.json"

# Need to make these dynamic and editable from year to year instead of hardcoded (input using bash script provided)
BOT_ID = ""
MASTER_ID = ""

# Define categories
CATEGORIES = (
    "Built Environment",
    "Transportation",
    "Waste Management",
    "Waste Reduction",
)

# Define criterias
CRITERIAS = ("Creativity", "Execution", "Scalability", "Environmental Impact")

# Define percentages of the four criterias
PERCENTAGES = (0.25, 0.25, 0.25, 0.25)

# Define group size limits
# This following set of restrictions should ideally allow and accommodate for ALL integers > MIN_GROUP_SIZE to be decomposed properly while still within the imposed limits
MIN_GROUP_SIZE = 3
MAX_GROUP_SIZE = 5
