#!/bin/bash

echo "Setting up environmental variables"
export USER_MSG_ENDPOINT="http://0.0.0.0:8001/messages/"
export CACHED_USER_ENDPOINT="http://0.0.0.0:8001/users"
export DATABASE_URL="postgres://localhost:5432"

echo "Please make sure to set BOT_TOKEN, otherwise this will fail to start"

python -m bot.bot
