from os import environ


# BOT CONFIG
API_ID = environ.get("API_ID", "25773387")  # api id
API_HASH = environ.get("API_HASH", "d6315808e7741b4d04bb95877e0a8468")  # api hash
BOT_TOKEN = environ.get("BOT_TOKEN", "7051688091:AAGnL-cHf3E0_MHj1RcJnFnE80sp77kIbkw")  # bot token

# REDIS
REDIS_HOST = environ.get("REDIS_HOST", "redis-13976.c239.us-east-1-2.ec2.cloud.redislabs.com")  # redis host uri
REDIS_PORT = environ.get("REDIS_PORT", "13976")  # redis port
REDIS_PASSWORD = environ.get(
    "REDIS_PASSWORD", "J3RaGqWkhOaE7wRQ49xvBTvZ3EZzHZAr"
)  # redis password


ADMINS = [6440245883,5015968435]
OWNER_ID = 5491085270  # Replace with your Telegram user ID
PRIVATE_CHAT_ID = -1002021142183  # CHAT WHERE YOU WANT TO STORE VIDEOS
USER_CHANNEL = -1001160455229
DUMP_CHANNEL = -1001160455229


# Config
COOKIE = environ.get("COOKIE", "csrfToken=2frCVtuUrczo9gnmNG-VQCDD; browserid=AWdJ6JsHuCMYu2wZbr0ZgA3vuDhcyqA3LpkP0EQXYL1GCKhnM7Krz5AI84g; lang=en; TSID=apzc84KzRMsxUFj3NoOKo1BYSkIebp1j; __bid_n=18f80cd998bcfbe1cd4207; _ga=GA1.1.890766573.1715852910; ndus=Y4LZtCyteHuiZfamxYQIdTpDDKgNXMi8HStph09f; ndut_fmt=DD74DDDD4B41DD03546B27A6CBCF86C1B8DCFF44DFCA8BCE1FC3F792436A819B; _ga_06ZNKL8C2E=GGS1.1.1715852909.1.1.1715853213.60.0.0")
