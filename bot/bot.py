import discord
import os
import asyncio
import time
import requests
import psycopg2
import urllib.parse as urlparse

USER_MSG_ENDPOINT = os.environ['USER_MSG_ENDPOINT']

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

class PostgresConnection:

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                        dbname=dbname,
                        user=user,
                        password=password,
                        host=host,
                        port=port)
            return self.conn
        except psycopg2.OperationalError:
            pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            self.conn.rollback()
            self.conn.close()

client = discord.Client(intents=discord.Intents.all())

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    print("Connected")

# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    print("Disconnected")

# Called when a member updates their profile
# This is called when one or more of the following things change
# status, activity, nickname, roles, pending
@client.event
async def on_member_update(previous_member_state, current_member_state):
    pass

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    print(f"Checking for a message for {message.author.name}")
    discord_tag = f"{message.author.name}#{message.author.discriminator}"
    with PostgresConnection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE display_name = %s", (discord_tag,))
        target_user_id = cur.fetchone()[0]
    res = requests.get(USER_MSG_ENDPOINT + str(target_user_id))
    data = res.json()

    if data:
        await _type(message.channel, data['message'])



async def _type(channel, msg):
    await channel.trigger_typing()
    await asyncio.sleep(2)
    await channel.send(msg)

client.run(os.environ.get("BOT_TOKEN"))
