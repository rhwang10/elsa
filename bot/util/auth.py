import os
from configparser import ConfigParser

def get_auth_config():
    env = os.getenv("ENV")

    if env == "dev":
        config = ConfigParser()
        config.read(".config")
        config = config["AUTH0"]
    else:
        config = {
            "AUTH0_TOKEN_ENDPOINT": os.getenv("AUTH0_TOKEN_ENDPOINT", "https://your.domain.auth0.com/oauth/token"),
            "CLIENT_ID": os.getenv("CLIENT_ID", "client_id"),
            "CLIENT_SECRET": os.getenv("CLIENT_SECRET", "client_secret"),
            "AUDIENCE": os.getenv("AUDIENCE", "audience"),
            "GRANT_TYPE": os.getenv("GRANT_TYPE", "grant_type")
        }

    return config
