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
COOKIE = environ.get("COOKIE", "csrfToken=AhWwCNDsbsX9ki_Gcb5_S2bs; browserid=rpciNE6As5aDVVFLXzWe80bdnypLQjjUI56eGEwRP5mV6Ionz-lfpcmcwIk; lang=en; TSID=5yaylx5JMm6dwggb4b5OmbySjd3xPJSE; __bid_n=18f80fda1a05d02e3b4207; _ga=GA1.1.1773211503.1715858163; ndus=YuP2tCyteHui4XJOzokGFlMNqLkwl7ywSeW7eWUX; ndut_fmt=477AB88923932F1142166C855A7F99EE1D9C02AF9E96E652E86D3789899C53CC; _ga_06ZNKL8C2E=GS1.1.1715858162.1.0.1715858230.60.0.0")
