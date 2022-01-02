#!/bin/bash

echo "Setting up environmental variables"
export USER_MSG_ENDPOINT="http://0.0.0.0:8001/messages/"
export CACHED_USER_ENDPOINT="http://0.0.0.0:8001/users"
export TRACK_EVENTS_ENDPOINT="http://localhost:8001/trackevents"
export TOP_TRACKS_ENDPOINT="http://0.0.0.0:8001/toptracks/"
export ENV="dev"
echo "Please make sure to set BOT_TOKEN, otherwise this will fail to start"
echo "Also make sure that there exists a .config file in the root that contains your Auth0 credentials."

python -m bot.bot
