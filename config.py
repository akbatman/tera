from os import environ


# BOT CONFIG
API_ID = environ.get("API_ID", "28167530")  # api id
API_HASH = environ.get("API_HASH", "202a9e8b13b7663417ddacc671420ad9")  # api hash
BOT_TOKEN = environ.get("BOT_TOKEN", "6785693620:AAGeHHcw12M5qijCaTbEGV-Sge9gwdcrQwM")  # bot token

# REDIS
REDIS_HOST = environ.get("REDIS_HOST", "redis-13976.c239.us-east-1-2.ec2.cloud.redislabs.com")  # redis host uri
REDIS_PORT = environ.get("REDIS_PORT", "13976")  # redis port
REDIS_PASSWORD = environ.get(
    "REDIS_PASSWORD", "J3RaGqWkhOaE7wRQ49xvBTvZ3EZzHZAr"
)  # redis password


ADMINS = [6440245883,5015968435]
OWNER_ID = 6440245883  # Replace with your Telegram user ID
PRIVATE_CHAT_ID = -1002021142183  # CHAT WHERE YOU WANT TO STORE VIDEOS
USER_CHANNEL = -1001160455229
DUMP_CHANNEL = -1001160455229


# Config
COOKIE = environ.get("COOKIE", "csrfToken=xOP11j7onKx_cELYY_x2bnwM; browserid=4z1XCJy2wski9a4955nT9LNe_XhSFTALjRye3sC9ggZ1tkwuwwvd0opwssA=; lang=en; TSID=8ifhqzTGTQPakDH9L7crjhGvP2MC5nmx; __bid_n=18eef166c5bf0afa4f4207; _ga=GA1.1.1651334296.1715623398; ndus=Y48dhKyteHuiixsjZKwAv2HvNOUCith3i87C3R8G; ndut_fmt=04B36097FEFACABD1CF54F6C34EA07923739EEC667AA2C9BE0A0370C1C65701F; ab_sr=1.0.1_ZTg4MDFjOWE5YTFlYzI1YjY0OTliMjAyZmQ3Mzc2ODk5ZmUyOTgzNzA3MmEwZmJmOTRkODAwY2U3MzAzODE2ZDBjNjJjMDI1NjE3NTk5ODczOTMxMTM3ZjQ0MDQ2Nzg3NDFmOTk1OGQ4YmRjYjQzMjdiMzk5ZmVlYzFlMGUyYjNjOTc5MWIwMDdjNmFkMDhkNTc0OGZmZDA2ODI4ZmMyZQ==; _ga_06ZNKL8C2E=GS1.1.1715623398.1.1.1715625259.50.0.0")
